from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from app.data.data_foundation import DataQualityReport, DataSnapshot
from app.data.data_reconciliation import ReconciliationReport, ReconciliationRule
from app.data.data_workflow import FinanceDataWorkflow, FinanceImportCommand
from app.shared.rbac import AccessControlService, Permission, Principal
from app.workspace.workspace_integration import (
    CommandCenterSnapshot,
    WorkspaceContext,
    WorkspaceProjectionSnapshot,
    WorkspaceReadModelService,
)


class ImportStatus(StrEnum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class FinanceImport:
    import_id: str
    file_name: str
    file_type: str
    object_key: str
    company_ids: tuple[str, ...]
    snapshot_id: str | None
    quality_report: DataQualityReport
    reconciliation_report: ReconciliationReport
    unmapped_accounts: tuple[str, ...]
    created_by: str
    created_at: datetime
    status: ImportStatus = ImportStatus.DRAFT
    reviewed_by: str | None = None
    approved_by: str | None = None
    published_by: str | None = None
    note: str | None = None

    @property
    def run_eligible(self) -> bool:
        return (
            self.snapshot_id is not None
            and not self.quality_report.blocking
            and not self.reconciliation_report.blocking
            and not self.unmapped_accounts
        )


class FinanceImportRepository(Protocol):
    def add(self, item: FinanceImport) -> None: ...

    def get(self, import_id: str) -> FinanceImport | None: ...

    def replace(self, item: FinanceImport) -> None: ...

    def list_all(self) -> tuple[FinanceImport, ...]: ...


class InMemoryFinanceImportRepository:
    def __init__(self) -> None:
        self._items: dict[str, FinanceImport] = {}

    def add(self, item: FinanceImport) -> None:
        if item.import_id in self._items:
            raise ValueError("import already exists")
        self._items[item.import_id] = item

    def get(self, import_id: str) -> FinanceImport | None:
        return self._items.get(import_id)

    def replace(self, item: FinanceImport) -> None:
        if item.import_id not in self._items:
            raise KeyError(item.import_id)
        self._items[item.import_id] = item

    def list_all(self) -> tuple[FinanceImport, ...]:
        return tuple(
            sorted(self._items.values(), key=lambda item: item.created_at, reverse=True)
        )


class PostgresFinanceImportRepository:
    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS finance_imports (
        import_id TEXT PRIMARY KEY,
        payload JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_finance_imports_created_at ON finance_imports(created_at DESC);
    """

    def __init__(self, database_url: str) -> None:
        import psycopg

        self._database_url = database_url
        with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
            cursor.execute(self._SCHEMA)

    def _connect(self):  # type: ignore[no-untyped-def]
        import psycopg

        return psycopg.connect(self._database_url)

    def add(self, item: FinanceImport) -> None:
        try:
            with self._connect() as connection, connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO finance_imports(import_id, payload, created_at) VALUES (%s, %s::jsonb, %s)",
                    (
                        item.import_id,
                        json.dumps(asdict(item), default=str, sort_keys=True),
                        item.created_at,
                    ),
                )
        except Exception as exc:
            if "unique" in str(exc).lower():
                raise ValueError("import already exists") from exc
            raise

    def get(self, import_id: str) -> FinanceImport | None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM finance_imports WHERE import_id = %s", (import_id,)
            )
            row = cursor.fetchone()
        return None if row is None else _import_from_payload(row[0])

    def replace(self, item: FinanceImport) -> None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE finance_imports SET payload = %s::jsonb WHERE import_id = %s",
                (json.dumps(asdict(item), default=str, sort_keys=True), item.import_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(item.import_id)

    def list_all(self) -> tuple[FinanceImport, ...]:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM finance_imports ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
        return tuple(_import_from_payload(row[0]) for row in rows)


class LocalImportObjectStore:
    """Keeps originals outside PostgreSQL while metadata and hashes remain governed."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, *, import_id: str, file_name: str, content: bytes) -> str:
        safe_name = Path(file_name).name or "upload"
        key = f"{import_id}-{safe_name}"
        path = self._root / key
        path.write_bytes(content)
        return key

    def read(self, object_key: str) -> bytes:
        return (self._root / Path(object_key).name).read_bytes()


class FinanceImportPublicationService:
    def __init__(
        self,
        workflow: FinanceDataWorkflow,
        repository: FinanceImportRepository,
        objects: LocalImportObjectStore,
        access: AccessControlService,
        read_models: WorkspaceReadModelService,
    ) -> None:
        self._workflow = workflow
        self._repository = repository
        self._objects = objects
        self._access = access
        self._read_models = read_models

    def create(
        self,
        principal: Principal,
        *,
        file_name: str,
        content: bytes,
        file_type: str,
        column_mapping: dict[str, str],
        allowed_currencies: set[str] | None,
        required_dimensions: set[str] | None,
        reconciliation_rules: tuple[ReconciliationRule, ...],
        sheet_name: str | None,
    ) -> FinanceImport:
        self._access.require(principal, Permission.WRITE_DATA)
        result = self._workflow.execute(
            FinanceImportCommand(
                content=content,
                file_type=file_type,
                column_mapping=column_mapping,
                allowed_currencies=allowed_currencies,
                required_dimensions=required_dimensions,
                reconciliation_rules=reconciliation_rules,
                sheet_name=sheet_name,
            )
        )
        companies = tuple(sorted({record.company for record in result.records}))
        for company in companies:
            self._access.require(principal, Permission.WRITE_DATA, company=company)
        import_id = str(uuid4())
        item = FinanceImport(
            import_id=import_id,
            file_name=file_name or f"import.{file_type}",
            file_type=file_type.lower().lstrip("."),
            object_key=self._objects.save(
                import_id=import_id, file_name=file_name, content=content
            ),
            company_ids=companies,
            snapshot_id=result.snapshot.snapshot_id if result.snapshot else None,
            quality_report=result.quality_report,
            reconciliation_report=result.reconciliation_report,
            unmapped_accounts=result.unmapped_accounts,
            created_by=principal.user_id,
            created_at=datetime.now(UTC),
        )
        self._repository.add(item)
        return item

    def list(self, principal: Principal) -> tuple[FinanceImport, ...]:
        self._access.require(principal, Permission.READ_DATA)
        return tuple(
            item
            for item in self._repository.list_all()
            if not principal.company_scopes
            or set(item.company_ids).issubset(principal.company_scopes)
        )

    def get(self, principal: Principal, import_id: str) -> FinanceImport:
        self._access.require(principal, Permission.READ_DATA)
        item = self._require(import_id)
        self._require_scope(principal, item)
        return item

    def review(
        self, principal: Principal, import_id: str, note: str | None
    ) -> FinanceImport:
        item = self.get(principal, import_id)
        self._access.require(principal, Permission.VALIDATE_RUN)
        self._require_scope(principal, item)
        if not item.run_eligible:
            raise ValueError("only a run-eligible import can be reviewed")
        if item.created_by == principal.user_id:
            raise PermissionError("import preparer cannot review the same import")
        if item.status is not ImportStatus.DRAFT:
            raise ValueError("only a draft import can be reviewed")
        return self._replace(
            item, status=ImportStatus.REVIEWED, reviewed_by=principal.user_id, note=note
        )

    def approve(
        self, principal: Principal, import_id: str, note: str | None
    ) -> FinanceImport:
        item = self.get(principal, import_id)
        self._access.require(principal, Permission.APPROVE_RUN)
        self._require_scope(principal, item)
        if item.status is not ImportStatus.REVIEWED:
            raise ValueError("only a reviewed import can be approved")
        if principal.user_id in {item.created_by, item.reviewed_by}:
            raise PermissionError("preparer or reviewer cannot approve the same import")
        return self._replace(
            item, status=ImportStatus.APPROVED, approved_by=principal.user_id, note=note
        )

    def publish(self, principal: Principal, import_id: str) -> FinanceImport:
        item = self.get(principal, import_id)
        self._access.require(principal, Permission.APPROVE_RUN)
        self._require_scope(principal, item)
        if item.status is not ImportStatus.APPROVED:
            raise ValueError("only an approved import can be published")
        self._publish_snapshot(item)
        return self._replace(
            item, status=ImportStatus.PUBLISHED, published_by=principal.user_id
        )

    def source(
        self, principal: Principal, import_id: str
    ) -> tuple[FinanceImport, bytes]:
        item = self.get(principal, import_id)
        return item, self._objects.read(item.object_key)

    def snapshot(self, principal: Principal, snapshot_id: str) -> DataSnapshot:
        self._access.require(principal, Permission.READ_DATA)
        snapshot = self._workflow.require_snapshot(snapshot_id)
        for company in {record.company for record in snapshot.records}:
            self._access.require(principal, Permission.READ_DATA, company=company)
        return snapshot

    def snapshot_metadata(self, snapshot_id: str | None) -> DataSnapshot | None:
        return self._workflow.require_snapshot(snapshot_id) if snapshot_id else None

    def _publish_snapshot(self, item: FinanceImport) -> None:
        assert item.snapshot_id is not None
        snapshot = self._workflow.require_snapshot(item.snapshot_id)
        grouped: dict[tuple[str, str, str], list[Any]] = {}
        for record in snapshot.records:
            grouped.setdefault(
                (record.company, record.period, record.scenario), []
            ).append(record)
        for (company, period, scenario), records in grouped.items():
            context = WorkspaceContext(
                company,
                company,
                period,
                period,
                scenario,
                scenario,
                records[0].currency,
            )
            account_rows = [
                {
                    "account": record.account,
                    "value": str(record.value),
                    "currency": record.currency,
                    "dimensions": dict(record.dimensions),
                }
                for record in sorted(records, key=lambda row: row.account)
            ]
            version = self._next_projection_version(company, period, scenario)
            lineage = {
                "import_id": item.import_id,
                "snapshot_id": snapshot.snapshot_id,
                "content_hash": snapshot.content_hash,
            }
            assurance = {
                "status": "PUBLISHED",
                "quality_score": item.quality_report.score,
                "reconciliation": "PASSED",
            }
            command = CommandCenterSnapshot(
                context=context,
                as_of=datetime.now(UTC),
                metrics=tuple(
                    {
                        "metric_id": row["account"],
                        "label": row["account"],
                        "value": row["value"],
                        "currency": row["currency"],
                    }
                    for row in account_rows
                ),
                briefing=f"Published import {item.file_name}: {len(records)} finance records.",
                assurance=assurance,
                source_snapshot_ids=(snapshot.snapshot_id,),
                projection_version=version,
            )
            self._read_models.publish_command_center(command)
            common = {
                "metrics": command.metrics,
                "financial_statement": account_rows,
                "scenarios": [{"scenario_id": scenario, "status": "PUBLISHED"}],
            }
            for workspace in self._read_models.WORKSPACE_KEYS:
                data: dict[str, Any] = (
                    dict(common)
                    if workspace
                    in {"planning", "performance", "profitability", "liquidity"}
                    else {}
                )
                if workspace == "data-governance":
                    data = {
                        "snapshots": [
                            {
                                "snapshot_id": snapshot.snapshot_id,
                                "content_hash": snapshot.content_hash,
                                "row_count": snapshot.row_count,
                                "status": "PUBLISHED",
                            }
                        ],
                        "quality_findings": [],
                        "governed_runs": [],
                        "models": [],
                        "governance_approvals": [
                            {
                                "approval_id": item.import_id,
                                "status": "PUBLISHED",
                                "actor": item.approved_by,
                            }
                        ],
                        "governance_lineage": lineage,
                    }
                self._read_models.publish_workspace(
                    workspace,
                    WorkspaceProjectionSnapshot(
                        context=context,
                        as_of=command.as_of,
                        data=data,
                        lineage=lineage,
                        assurance=assurance,
                        source_snapshot_ids=(snapshot.snapshot_id,),
                        projection_version=version,
                    ),
                )

    def _next_projection_version(self, company: str, period: str, scenario: str) -> int:
        # The repository guards version monotonicity. Imports are content-addressed and each publish starts at 1;
        # a later import for the same context advances from existing published data via its own timestamp-based version.
        return int(datetime.now(UTC).timestamp())

    def _replace(self, item: FinanceImport, **changes: object) -> FinanceImport:
        updated = replace(item, **changes)
        self._repository.replace(updated)
        return updated

    def _require(self, import_id: str) -> FinanceImport:
        item = self._repository.get(import_id)
        if item is None:
            raise KeyError(import_id)
        return item

    def _require_scope(self, principal: Principal, item: FinanceImport) -> None:
        for company in item.company_ids:
            self._access.require(principal, Permission.READ_DATA, company=company)


def _import_from_payload(payload: object) -> FinanceImport:
    raw = payload if isinstance(payload, dict) else json.loads(str(payload))
    quality = raw["quality_report"]
    reconciliation = raw["reconciliation_report"]
    from app.data.data_foundation import DataQualityFinding, FindingSeverity
    from app.data.data_reconciliation import ReconciliationResult, ReconciliationStatus

    return FinanceImport(
        import_id=str(raw["import_id"]),
        file_name=str(raw["file_name"]),
        file_type=str(raw["file_type"]),
        object_key=str(raw["object_key"]),
        company_ids=tuple(raw["company_ids"]),
        snapshot_id=raw.get("snapshot_id"),
        quality_report=DataQualityReport(
            row_count=int(quality["row_count"]),
            findings=tuple(
                DataQualityFinding(
                    code=item["code"],
                    severity=FindingSeverity(item["severity"]),
                    message=item["message"],
                    row_number=item.get("row_number"),
                )
                for item in quality["findings"]
            ),
        ),
        reconciliation_report=ReconciliationReport(
            results=tuple(
                ReconciliationResult(
                    rule_id=item["rule_id"],
                    actual_total=Decimal(str(item["actual_total"])),
                    expected_total=Decimal(str(item["expected_total"])),
                    variance=Decimal(str(item["variance"])),
                    status=ReconciliationStatus(item["status"]),
                    blocking=item["blocking"],
                )
                for item in reconciliation["results"]
            )
        ),
        unmapped_accounts=tuple(raw.get("unmapped_accounts", [])),
        created_by=str(raw["created_by"]),
        created_at=datetime.fromisoformat(raw["created_at"]),
        status=ImportStatus(raw["status"]),
        reviewed_by=raw.get("reviewed_by"),
        approved_by=raw.get("approved_by"),
        published_by=raw.get("published_by"),
        note=raw.get("note"),
    )
