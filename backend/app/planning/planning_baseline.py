from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import LiteralString, Protocol, cast
from uuid import uuid4

from app.data.data_foundation import DataSnapshot
from app.data.data_publication import FinanceImportRepository, ImportStatus
from app.data.data_store import DataSnapshotRepository
from app.shared.rbac import AccessControlService, Permission, Principal


class PlanningAccountCategory(StrEnum):
    REVENUE = "revenue"
    VARIABLE_COST = "variable_cost"
    PERSONNEL_COST = "personnel_cost"
    FIXED_OPERATING_COST = "fixed_operating_cost"
    DEPRECIATION = "depreciation"
    CASH = "cash"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    INVENTORY = "inventory"
    ACCOUNTS_PAYABLE = "accounts_payable"
    DEBT = "debt"
    OTHER = "other"


class PlanningMappingStatus(StrEnum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"


@dataclass(frozen=True, slots=True)
class PlanningAccountMapping:
    source_account: str
    category: PlanningAccountCategory
    sign_multiplier: Decimal = Decimal(1)

    def __post_init__(self) -> None:
        if not self.source_account.strip():
            raise ValueError("source_account must not be empty")
        if self.sign_multiplier not in {Decimal(1), Decimal(-1)}:
            raise ValueError("sign_multiplier must be 1 or -1")


@dataclass(frozen=True, slots=True)
class PlanningMappingSet:
    mapping_set_id: str
    company_id: str
    source_snapshot_id: str
    version_label: str
    mappings: tuple[PlanningAccountMapping, ...]
    created_by: str
    created_at: datetime
    status: PlanningMappingStatus = PlanningMappingStatus.DRAFT
    reviewed_by: str | None = None
    approved_by: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        if not self.company_id.strip() or not self.source_snapshot_id.strip():
            raise ValueError("company_id and source_snapshot_id must not be empty")
        if not self.version_label.strip():
            raise ValueError("version_label must not be empty")
        if not self.mappings:
            raise ValueError("at least one account mapping is required")
        accounts = [item.source_account for item in self.mappings]
        if len(accounts) != len(set(accounts)):
            raise ValueError("source accounts must be unique within a mapping set")


@dataclass(frozen=True, slots=True)
class PlanningBaseline:
    baseline_id: str
    company_id: str
    period_id: str
    scenario_id: str
    source_snapshot_id: str
    mapping_set_id: str
    values: tuple[tuple[PlanningAccountCategory, Decimal], ...]
    missing_categories: tuple[PlanningAccountCategory, ...]
    created_at: datetime
    published_by: str

    @property
    def forecast_eligible(self) -> bool:
        return not self.missing_categories

    def values_by_category(self) -> dict[str, Decimal]:
        return {category.value: value for category, value in self.values}


class PlanningBaselineRepository(Protocol):
    def add_mapping(self, item: PlanningMappingSet) -> None: ...

    def get_mapping(self, mapping_set_id: str) -> PlanningMappingSet | None: ...

    def replace_mapping(self, item: PlanningMappingSet) -> None: ...

    def list_mappings(
        self, company_id: str | None = None
    ) -> tuple[PlanningMappingSet, ...]: ...

    def add_baseline(self, item: PlanningBaseline) -> None: ...

    def list_baselines(
        self,
        *,
        company_id: str | None = None,
        period_id: str | None = None,
        scenario_id: str | None = None,
    ) -> tuple[PlanningBaseline, ...]: ...


class InMemoryPlanningBaselineRepository:
    def __init__(self) -> None:
        self._mappings: dict[str, PlanningMappingSet] = {}
        self._baselines: dict[str, PlanningBaseline] = {}

    def add_mapping(self, item: PlanningMappingSet) -> None:
        if item.mapping_set_id in self._mappings:
            raise ValueError("planning mapping already exists")
        self._mappings[item.mapping_set_id] = item

    def get_mapping(self, mapping_set_id: str) -> PlanningMappingSet | None:
        return self._mappings.get(mapping_set_id)

    def replace_mapping(self, item: PlanningMappingSet) -> None:
        if item.mapping_set_id not in self._mappings:
            raise KeyError(item.mapping_set_id)
        self._mappings[item.mapping_set_id] = item

    def list_mappings(
        self, company_id: str | None = None
    ) -> tuple[PlanningMappingSet, ...]:
        items = self._mappings.values()
        if company_id is not None:
            items = (item for item in items if item.company_id == company_id)
        return tuple(sorted(items, key=lambda item: item.created_at, reverse=True))

    def add_baseline(self, item: PlanningBaseline) -> None:
        if item.baseline_id in self._baselines:
            raise ValueError("planning baseline already exists")
        self._baselines[item.baseline_id] = item

    def list_baselines(
        self,
        *,
        company_id: str | None = None,
        period_id: str | None = None,
        scenario_id: str | None = None,
    ) -> tuple[PlanningBaseline, ...]:
        items = self._baselines.values()
        if company_id is not None:
            items = (item for item in items if item.company_id == company_id)
        if period_id is not None:
            items = (item for item in items if item.period_id == period_id)
        if scenario_id is not None:
            items = (item for item in items if item.scenario_id == scenario_id)
        return tuple(sorted(items, key=lambda item: item.created_at, reverse=True))


class PostgresPlanningBaselineRepository:
    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS planning_mapping_sets (
        mapping_set_id TEXT PRIMARY KEY,
        company_id TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        payload JSONB NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_planning_mapping_sets_company_created
        ON planning_mapping_sets(company_id, created_at DESC);
    CREATE TABLE IF NOT EXISTS planning_baselines (
        baseline_id TEXT PRIMARY KEY,
        company_id TEXT NOT NULL,
        period_id TEXT NOT NULL,
        scenario_id TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        payload JSONB NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_planning_baselines_context_created
        ON planning_baselines(company_id, period_id, scenario_id, created_at DESC);
    """

    def __init__(self, database_url: str) -> None:
        import psycopg

        self._database_url = database_url
        with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
            cursor.execute(self._SCHEMA)

    def _connect(self):  # type: ignore[no-untyped-def]
        import psycopg

        return psycopg.connect(self._database_url)

    def add_mapping(self, item: PlanningMappingSet) -> None:
        try:
            with self._connect() as connection, connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO planning_mapping_sets(mapping_set_id, company_id, created_at, payload) VALUES (%s, %s, %s, %s::jsonb)",
                    (
                        item.mapping_set_id,
                        item.company_id,
                        item.created_at,
                        _json(item),
                    ),
                )
        except Exception as exc:
            if "unique" in str(exc).lower():
                raise ValueError("planning mapping already exists") from exc
            raise

    def get_mapping(self, mapping_set_id: str) -> PlanningMappingSet | None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM planning_mapping_sets WHERE mapping_set_id = %s",
                (mapping_set_id,),
            )
            row = cursor.fetchone()
        return None if row is None else _mapping_from_payload(row[0])

    def replace_mapping(self, item: PlanningMappingSet) -> None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE planning_mapping_sets SET payload = %s::jsonb WHERE mapping_set_id = %s",
                (_json(item), item.mapping_set_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(item.mapping_set_id)

    def list_mappings(
        self, company_id: str | None = None
    ) -> tuple[PlanningMappingSet, ...]:
        query = "SELECT payload FROM planning_mapping_sets"
        values: tuple[str, ...] = ()
        if company_id is not None:
            query += " WHERE company_id = %s"
            values = (company_id,)
        query += " ORDER BY created_at DESC"
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(query, values)
            rows = cursor.fetchall()
        return tuple(_mapping_from_payload(row[0]) for row in rows)

    def add_baseline(self, item: PlanningBaseline) -> None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO planning_baselines(baseline_id, company_id, period_id, scenario_id, created_at, payload) VALUES (%s, %s, %s, %s, %s, %s::jsonb)",
                (
                    item.baseline_id,
                    item.company_id,
                    item.period_id,
                    item.scenario_id,
                    item.created_at,
                    _json(item),
                ),
            )

    def list_baselines(
        self,
        *,
        company_id: str | None = None,
        period_id: str | None = None,
        scenario_id: str | None = None,
    ) -> tuple[PlanningBaseline, ...]:
        filters: list[str] = []
        values: list[str] = []
        for column, value in (
            ("company_id", company_id),
            ("period_id", period_id),
            ("scenario_id", scenario_id),
        ):
            if value is not None:
                filters.append(f"{column} = %s")
                values.append(value)
        query = "SELECT payload FROM planning_baselines"
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY created_at DESC"
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(cast(LiteralString, query), tuple(values))
            rows = cursor.fetchall()
        return tuple(_baseline_from_payload(row[0]) for row in rows)


class PlanningBaselineService:
    _REQUIRED_CATEGORIES = frozenset(
        {
            PlanningAccountCategory.REVENUE,
            PlanningAccountCategory.VARIABLE_COST,
            PlanningAccountCategory.FIXED_OPERATING_COST,
        }
    )

    def __init__(
        self,
        snapshots: DataSnapshotRepository,
        imports: FinanceImportRepository,
        repository: PlanningBaselineRepository,
        access: AccessControlService,
    ) -> None:
        self._snapshots = snapshots
        self._imports = imports
        self._repository = repository
        self._access = access

    def source_accounts(
        self, principal: Principal, import_id: str
    ) -> tuple[tuple[str, Decimal], ...]:
        self._access.require(principal, Permission.READ_DATA)
        item = self._require_import(import_id)
        self._require_company_scope(principal, item.company_ids)
        if item.snapshot_id is None:
            raise ValueError("import has no eligible snapshot")
        snapshot = self._require_snapshot(item.snapshot_id)
        totals: dict[str, Decimal] = {}
        for record in snapshot.records:
            totals[record.account] = (
                totals.get(record.account, Decimal(0)) + record.value
            )
        return tuple(sorted(totals.items()))

    def create_mapping(
        self,
        principal: Principal,
        *,
        company_id: str,
        source_snapshot_id: str,
        version_label: str,
        mappings: tuple[PlanningAccountMapping, ...],
    ) -> PlanningMappingSet:
        self._access.require(principal, Permission.WRITE_DATA, company=company_id)
        if not self._is_published_snapshot(source_snapshot_id):
            raise ValueError("planning mapping requires a published source snapshot")
        snapshot = self._require_snapshot(source_snapshot_id)
        accounts = {
            record.account
            for record in snapshot.records
            if record.company == company_id
        }
        if not accounts:
            raise ValueError("source snapshot contains no records for company")
        submitted = {mapping.source_account for mapping in mappings}
        if submitted != accounts:
            missing = sorted(accounts - submitted)
            unknown = sorted(submitted - accounts)
            detail = []
            if missing:
                detail.append(f"missing accounts: {', '.join(missing)}")
            if unknown:
                detail.append(f"unknown accounts: {', '.join(unknown)}")
            raise ValueError(
                "mapping must cover every source account; " + "; ".join(detail)
            )
        item = PlanningMappingSet(
            mapping_set_id=str(uuid4()),
            company_id=company_id,
            source_snapshot_id=source_snapshot_id,
            version_label=version_label,
            mappings=mappings,
            created_by=principal.user_id,
            created_at=datetime.now(UTC),
        )
        self._repository.add_mapping(item)
        return item

    def list_mappings(
        self, principal: Principal, *, company_id: str
    ) -> tuple[PlanningMappingSet, ...]:
        self._access.require(principal, Permission.READ_DATA, company=company_id)
        return self._repository.list_mappings(company_id)

    def review_mapping(
        self, principal: Principal, mapping_set_id: str, note: str | None
    ) -> PlanningMappingSet:
        item = self._require_mapping(mapping_set_id)
        self._access.require(
            principal, Permission.VALIDATE_RUN, company=item.company_id
        )
        if item.created_by == principal.user_id:
            raise PermissionError("mapping preparer cannot review the same mapping")
        if item.status is not PlanningMappingStatus.DRAFT:
            raise ValueError("only a draft mapping can be reviewed")
        return self._replace_mapping(
            item,
            status=PlanningMappingStatus.REVIEWED,
            reviewed_by=principal.user_id,
            note=note,
        )

    def approve_mapping(
        self, principal: Principal, mapping_set_id: str, note: str | None
    ) -> PlanningMappingSet:
        item = self._require_mapping(mapping_set_id)
        self._access.require(principal, Permission.APPROVE_RUN, company=item.company_id)
        if principal.user_id in {item.created_by, item.reviewed_by}:
            raise PermissionError(
                "mapping preparer or reviewer cannot approve the same mapping"
            )
        if item.status is not PlanningMappingStatus.REVIEWED:
            raise ValueError("only a reviewed mapping can be approved")
        return self._replace_mapping(
            item,
            status=PlanningMappingStatus.APPROVED,
            approved_by=principal.user_id,
            note=note,
        )

    def publish_baseline(
        self,
        principal: Principal,
        *,
        mapping_set_id: str,
        period_id: str,
        scenario_id: str,
    ) -> PlanningBaseline:
        mapping = self._require_mapping(mapping_set_id)
        self._access.require(
            principal, Permission.APPROVE_RUN, company=mapping.company_id
        )
        if mapping.status is not PlanningMappingStatus.APPROVED:
            raise ValueError("only an approved mapping can publish a planning baseline")
        if not self._is_published_snapshot(mapping.source_snapshot_id):
            raise ValueError("planning baseline requires a published source snapshot")
        snapshot = self._require_snapshot(mapping.source_snapshot_id)
        values = {category: Decimal(0) for category in PlanningAccountCategory}
        mapping_index = {item.source_account: item for item in mapping.mappings}
        matched = 0
        for record in snapshot.records:
            if (
                record.company != mapping.company_id
                or record.period != period_id
                or record.scenario != scenario_id
            ):
                continue
            account = mapping_index.get(record.account)
            if account is None:
                raise ValueError(f"mapping no longer covers account: {record.account}")
            values[account.category] += record.value * account.sign_multiplier
            matched += 1
        if matched == 0:
            raise ValueError(
                "source snapshot contains no records for the selected company, period and scenario"
            )
        missing = tuple(
            sorted(
                self._REQUIRED_CATEGORIES
                - {category for category, amount in values.items() if amount != 0},
                key=lambda item: item.value,
            )
        )
        baseline = PlanningBaseline(
            baseline_id=str(uuid4()),
            company_id=mapping.company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            source_snapshot_id=snapshot.snapshot_id,
            mapping_set_id=mapping.mapping_set_id,
            values=tuple(
                (category, values[category]) for category in PlanningAccountCategory
            ),
            missing_categories=missing,
            created_at=datetime.now(UTC),
            published_by=principal.user_id,
        )
        self._repository.add_baseline(baseline)
        return baseline

    def list_baselines(
        self, principal: Principal, *, company_id: str, period_id: str, scenario_id: str
    ) -> tuple[PlanningBaseline, ...]:
        self._access.require(principal, Permission.READ_DATA, company=company_id)
        return self._repository.list_baselines(
            company_id=company_id, period_id=period_id, scenario_id=scenario_id
        )

    def _is_published_snapshot(self, snapshot_id: str) -> bool:
        return any(
            item.snapshot_id == snapshot_id and item.status is ImportStatus.PUBLISHED
            for item in self._imports.list_all()
        )

    def _require_import(self, import_id: str):  # type: ignore[no-untyped-def]
        item = self._imports.get(import_id)
        if item is None:
            raise KeyError(import_id)
        return item

    def _require_mapping(self, mapping_set_id: str) -> PlanningMappingSet:
        item = self._repository.get_mapping(mapping_set_id)
        if item is None:
            raise KeyError(mapping_set_id)
        return item

    def _replace_mapping(
        self, item: PlanningMappingSet, **changes: object
    ) -> PlanningMappingSet:
        updated = replace(item, **changes)
        self._repository.replace_mapping(updated)
        return updated

    def _require_snapshot(self, snapshot_id: str) -> DataSnapshot:
        snapshot = self._snapshots.get(snapshot_id)
        if snapshot is None:
            raise KeyError(snapshot_id)
        return snapshot

    def _require_company_scope(
        self, principal: Principal, company_ids: tuple[str, ...]
    ) -> None:
        for company_id in company_ids:
            self._access.require(principal, Permission.READ_DATA, company=company_id)


def _json(item: PlanningMappingSet | PlanningBaseline) -> str:
    return json.dumps(asdict(item), default=str, sort_keys=True)


def _mapping_from_payload(payload: object) -> PlanningMappingSet:
    raw = payload if isinstance(payload, dict) else json.loads(str(payload))
    return PlanningMappingSet(
        mapping_set_id=str(raw["mapping_set_id"]),
        company_id=str(raw["company_id"]),
        source_snapshot_id=str(raw["source_snapshot_id"]),
        version_label=str(raw["version_label"]),
        mappings=tuple(
            PlanningAccountMapping(
                source_account=str(item["source_account"]),
                category=PlanningAccountCategory(item["category"]),
                sign_multiplier=Decimal(str(item["sign_multiplier"])),
            )
            for item in raw["mappings"]
        ),
        created_by=str(raw["created_by"]),
        created_at=datetime.fromisoformat(raw["created_at"]),
        status=PlanningMappingStatus(raw["status"]),
        reviewed_by=raw.get("reviewed_by"),
        approved_by=raw.get("approved_by"),
        note=raw.get("note"),
    )


def _baseline_from_payload(payload: object) -> PlanningBaseline:
    raw = payload if isinstance(payload, dict) else json.loads(str(payload))
    return PlanningBaseline(
        baseline_id=str(raw["baseline_id"]),
        company_id=str(raw["company_id"]),
        period_id=str(raw["period_id"]),
        scenario_id=str(raw["scenario_id"]),
        source_snapshot_id=str(raw["source_snapshot_id"]),
        mapping_set_id=str(raw["mapping_set_id"]),
        values=tuple(
            (PlanningAccountCategory(category), Decimal(str(value)))
            for category, value in raw["values"]
        ),
        missing_categories=tuple(
            PlanningAccountCategory(item) for item in raw["missing_categories"]
        ),
        created_at=datetime.fromisoformat(raw["created_at"]),
        published_by=str(raw["published_by"]),
    )
