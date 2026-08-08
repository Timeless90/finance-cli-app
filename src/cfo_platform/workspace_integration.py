from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from threading import RLock
from typing import Any, Mapping, Protocol

from cfo_platform.data_store import DataSnapshotRepository
from cfo_platform.domain.value_objects import FiscalPeriod
from cfo_platform.governance_catalog import ScenarioRepository
from cfo_platform.rbac import AccessControlService, Permission, Principal


@dataclass(frozen=True, slots=True)
class CompanyContextOption:
    company_id: str
    label: str
    currency: str | None
    data_available: bool


@dataclass(frozen=True, slots=True)
class PeriodContextOption:
    period_id: str
    label: str


@dataclass(frozen=True, slots=True)
class ScenarioContextOption:
    scenario_id: str
    label: str
    kind: str | None
    status: str
    version: int | None
    source: str


@dataclass(frozen=True, slots=True)
class WorkspaceContext:
    company_id: str
    company_label: str
    period_id: str
    period_label: str
    scenario_id: str
    scenario_label: str
    currency: str | None


@dataclass(frozen=True, slots=True)
class WorkspaceContextKey:
    company_id: str
    period_id: str
    scenario_id: str

    @classmethod
    def from_context(cls, context: WorkspaceContext) -> WorkspaceContextKey:
        return cls(
            company_id=context.company_id,
            period_id=context.period_id,
            scenario_id=context.scenario_id,
        )


class ContextCatalogService:
    """Query-oriented context catalogue built from governed backend sources."""

    def __init__(
        self,
        snapshot_repository: DataSnapshotRepository,
        scenario_repository: ScenarioRepository,
        access_control: AccessControlService,
    ) -> None:
        self._snapshots = snapshot_repository
        self._scenarios = scenario_repository
        self._access = access_control

    def principal_view(self, principal: Principal) -> Mapping[str, Any]:
        self._access.require(principal, Permission.READ_DATA)
        return {
            "user_id": principal.user_id,
            "roles": sorted(role.value for role in principal.roles),
            "company_scopes": sorted(principal.company_scopes),
            "permissions": sorted(
                permission.value for permission in self._access.permissions_for(principal)
            ),
        }

    def list_companies(self, principal: Principal) -> tuple[CompanyContextOption, ...]:
        self._access.require(principal, Permission.READ_DATA)
        currencies: dict[str, set[str]] = {}
        for record in self._records():
            currencies.setdefault(record.company, set()).add(record.currency)

        company_ids = (
            sorted(principal.company_scopes)
            if principal.company_scopes
            else sorted(currencies)
        )
        return tuple(
            CompanyContextOption(
                company_id=company_id,
                label=company_id,
                currency=self._single_currency(currencies.get(company_id, set())),
                data_available=company_id in currencies,
            )
            for company_id in company_ids
        )

    def list_periods(
        self,
        principal: Principal,
        *,
        company_id: str,
    ) -> tuple[PeriodContextOption, ...]:
        self._access.require(principal, Permission.READ_DATA, company=company_id)
        periods: set[FiscalPeriod] = set()
        for record in self._records():
            if record.company != company_id:
                continue
            try:
                periods.add(FiscalPeriod.parse(record.period))
            except ValueError:
                continue
        return tuple(
            PeriodContextOption(period_id=str(period), label=str(period))
            for period in sorted(periods, reverse=True)
        )

    def list_scenarios(
        self,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
    ) -> tuple[ScenarioContextOption, ...]:
        self._access.require(principal, Permission.READ_DATA, company=company_id)
        if period_id not in {
            item.period_id for item in self.list_periods(principal, company_id=company_id)
        }:
            raise KeyError("period")

        options: dict[str, ScenarioContextOption] = {}
        for record in self._records():
            if record.company == company_id and record.period == period_id:
                options.setdefault(
                    record.scenario,
                    ScenarioContextOption(
                        scenario_id=record.scenario,
                        label=record.scenario,
                        kind=None,
                        status="available",
                        version=None,
                        source="finance_data",
                    ),
                )

        latest = {}
        for scenario in self._scenarios.list_all():
            current = latest.get(scenario.scenario_id)
            if current is None or scenario.version > current.version:
                latest[scenario.scenario_id] = scenario
        for scenario in latest.values():
            options[scenario.scenario_id] = ScenarioContextOption(
                scenario_id=scenario.scenario_id,
                label=scenario.name,
                kind=scenario.kind.value,
                status=scenario.status.value,
                version=scenario.version,
                source="governance",
            )

        return tuple(sorted(options.values(), key=lambda item: (item.label, item.scenario_id)))

    def resolve(
        self,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
    ) -> WorkspaceContext:
        self._access.require(principal, Permission.READ_DATA, company=company_id)
        companies = {item.company_id: item for item in self.list_companies(principal)}
        company = companies.get(company_id)
        if company is None:
            raise KeyError("company")

        periods = {
            item.period_id: item
            for item in self.list_periods(principal, company_id=company_id)
        }
        period = periods.get(period_id)
        if period is None:
            raise KeyError("period")

        scenarios = {
            item.scenario_id: item
            for item in self.list_scenarios(
                principal,
                company_id=company_id,
                period_id=period_id,
            )
        }
        scenario = scenarios.get(scenario_id)
        if scenario is None:
            raise KeyError("scenario")

        return WorkspaceContext(
            company_id=company.company_id,
            company_label=company.label,
            period_id=period.period_id,
            period_label=period.label,
            scenario_id=scenario.scenario_id,
            scenario_label=scenario.label,
            currency=company.currency,
        )

    def _records(self):
        for snapshot in self._snapshots.list_all():
            yield from snapshot.records

    @staticmethod
    def _single_currency(currencies: set[str]) -> str | None:
        if len(currencies) == 1:
            return next(iter(currencies))
        return None


def _validate_projection_version(version: int) -> None:
    if version < 1:
        raise ValueError("projection_version must be >= 1")


@dataclass(frozen=True, slots=True)
class CommandCenterSnapshot:
    context: WorkspaceContext
    as_of: datetime
    metrics: tuple[Mapping[str, Any], ...] = ()
    forecast: Mapping[str, Any] | None = None
    liquidity: Mapping[str, Any] | None = None
    risk: Mapping[str, Any] | None = None
    variance_drivers: tuple[Mapping[str, Any], ...] = ()
    actions: tuple[Mapping[str, Any], ...] = ()
    briefing: str | None = None
    assurance: Mapping[str, Any] = field(default_factory=dict)
    source_snapshot_ids: tuple[str, ...] = ()
    projection_version: int = 1

    def __post_init__(self) -> None:
        _validate_projection_version(self.projection_version)


@dataclass(frozen=True, slots=True)
class WorkspaceProjectionSnapshot:
    """Published query projection; domain engines own all financial calculations."""

    context: WorkspaceContext
    as_of: datetime
    data: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)
    assurance: Mapping[str, Any] = field(default_factory=dict)
    source_snapshot_ids: tuple[str, ...] = ()
    projection_version: int = 1

    def __post_init__(self) -> None:
        _validate_projection_version(self.projection_version)


class WorkspaceReadModelRepository(Protocol):
    def save_command_center(self, snapshot: CommandCenterSnapshot) -> None: ...

    def get_command_center(
        self,
        key: WorkspaceContextKey,
    ) -> CommandCenterSnapshot | None: ...

    def save_workspace(
        self,
        workspace: str,
        snapshot: WorkspaceProjectionSnapshot,
    ) -> None: ...

    def get_workspace(
        self,
        workspace: str,
        key: WorkspaceContextKey,
    ) -> WorkspaceProjectionSnapshot | None: ...


class InMemoryWorkspaceReadModelRepository:
    def __init__(self) -> None:
        self._command_center: dict[WorkspaceContextKey, CommandCenterSnapshot] = {}
        self._workspaces: dict[
            str,
            dict[WorkspaceContextKey, WorkspaceProjectionSnapshot],
        ] = {}
        self._lock = RLock()

    def save_command_center(self, snapshot: CommandCenterSnapshot) -> None:
        key = WorkspaceContextKey.from_context(snapshot.context)
        with self._lock:
            current = self._command_center.get(key)
            self._require_newer_projection(
                current.projection_version if current is not None else None,
                snapshot.projection_version,
            )
            self._command_center[key] = snapshot

    def get_command_center(
        self,
        key: WorkspaceContextKey,
    ) -> CommandCenterSnapshot | None:
        with self._lock:
            return self._command_center.get(key)

    def save_workspace(
        self,
        workspace: str,
        snapshot: WorkspaceProjectionSnapshot,
    ) -> None:
        if not workspace:
            raise ValueError("workspace must not be empty")
        key = WorkspaceContextKey.from_context(snapshot.context)
        with self._lock:
            snapshots = self._workspaces.setdefault(workspace, {})
            current = snapshots.get(key)
            self._require_newer_projection(
                current.projection_version if current is not None else None,
                snapshot.projection_version,
            )
            snapshots[key] = snapshot

    def get_workspace(
        self,
        workspace: str,
        key: WorkspaceContextKey,
    ) -> WorkspaceProjectionSnapshot | None:
        with self._lock:
            return self._workspaces.get(workspace, {}).get(key)

    @staticmethod
    def _require_newer_projection(
        current_version: int | None,
        new_version: int,
    ) -> None:
        if current_version is not None and new_version <= current_version:
            raise ValueError(
                "projection_version must increase when replacing a read model"
            )


class WorkspaceReadModelService:
    WORKSPACE_KEYS = frozenset(
        {
            "planning",
            "performance",
            "profitability",
            "liquidity",
            "risk",
            "market-risk",
            "actions",
            "capital",
            "reporting",
        }
    )

    def __init__(
        self,
        context_catalog: ContextCatalogService,
        repository: WorkspaceReadModelRepository,
    ) -> None:
        self._context_catalog = context_catalog
        self._repository = repository

    def publish_command_center(self, snapshot: CommandCenterSnapshot) -> None:
        self._repository.save_command_center(snapshot)

    def publish_workspace(
        self,
        workspace: str,
        snapshot: WorkspaceProjectionSnapshot,
    ) -> None:
        self._require_workspace(workspace)
        self._repository.save_workspace(workspace, snapshot)

    def command_center(
        self,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
    ) -> CommandCenterSnapshot:
        context = self._resolve_context(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        key = WorkspaceContextKey(
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        snapshot = self._repository.get_command_center(key)
        if snapshot is None:
            raise KeyError("command_center")
        return replace(snapshot, context=context)

    def workspace(
        self,
        workspace: str,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
    ) -> WorkspaceProjectionSnapshot:
        self._require_workspace(workspace)
        context = self._resolve_context(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        key = WorkspaceContextKey(
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        snapshot = self._repository.get_workspace(workspace, key)
        if snapshot is None:
            raise KeyError(workspace)
        return replace(snapshot, context=context)

    def _resolve_context(
        self,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
    ) -> WorkspaceContext:
        return self._context_catalog.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )

    @classmethod
    def _require_workspace(cls, workspace: str) -> None:
        if workspace not in cls.WORKSPACE_KEYS:
            raise ValueError(f"unsupported workspace: {workspace}")
