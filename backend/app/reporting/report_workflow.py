"""Context-scoped lifecycle around immutable reporting artifacts."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from threading import RLock
from typing import Protocol

from app.data.data_store import DataSnapshotRepository
from app.reporting.reporting_factory import ReportArtifact, ReportingFactory
from app.shared.rbac import AccessControlService, Permission, Principal
from app.workspace.workspace_integration import ContextCatalogService, WorkspaceContext


class ReportRunStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"


@dataclass(frozen=True, slots=True)
class ReportRun:
    report_id: str
    status: ReportRunStatus
    context: WorkspaceContext
    source_snapshot_ids: tuple[str, ...]
    projection_version: int
    created_by: str
    created_at: datetime
    reviewed_by: str | None = None
    approved_by: str | None = None
    published_by: str | None = None


class ReportRunRepository(Protocol):
    def add(self, run: ReportRun) -> None: ...

    def get(self, report_id: str) -> ReportRun | None: ...

    def replace(self, run: ReportRun) -> None: ...

    def list_for_context(self, context: WorkspaceContext) -> tuple[ReportRun, ...]: ...


class InMemoryReportRunRepository:
    def __init__(self) -> None:
        self._runs: dict[str, ReportRun] = {}
        self._lock = RLock()

    def add(self, run: ReportRun) -> None:
        with self._lock:
            if run.report_id in self._runs:
                raise ValueError("report run already exists")
            self._runs[run.report_id] = run

    def get(self, report_id: str) -> ReportRun | None:
        with self._lock:
            return self._runs.get(report_id)

    def replace(self, run: ReportRun) -> None:
        with self._lock:
            if run.report_id not in self._runs:
                raise KeyError(run.report_id)
            self._runs[run.report_id] = run

    def list_for_context(self, context: WorkspaceContext) -> tuple[ReportRun, ...]:
        with self._lock:
            return tuple(
                sorted(
                    (
                        run
                        for run in self._runs.values()
                        if run.context.company_id == context.company_id
                        and run.context.period_id == context.period_id
                        and run.context.scenario_id == context.scenario_id
                    ),
                    key=lambda item: item.created_at,
                    reverse=True,
                )
            )


class ReportRunService:
    """Authorizes a report through draft, review, approval and publication.

    ``ReportingFactory`` remains the owner of report content and its immutable
    approved artifact. This service owns tenant scope and human workflow.
    """

    def __init__(
        self,
        contexts: ContextCatalogService,
        snapshots: DataSnapshotRepository,
        access: AccessControlService,
        factory: ReportingFactory,
        repository: ReportRunRepository,
    ) -> None:
        self._contexts = contexts
        self._snapshots = snapshots
        self._access = access
        self._factory = factory
        self._repository = repository

    def create(
        self,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
        template_id: str,
        template_version: int,
        source_snapshot_ids: tuple[str, ...],
        projection_version: int,
    ) -> tuple[ReportRun, ReportArtifact]:
        context = self._contexts.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        self._access.require(
            principal, Permission.CREATE_RUN, company=context.company_id
        )
        if not source_snapshot_ids:
            raise ValueError("at least one source snapshot is required")
        if projection_version < 1:
            raise ValueError("projection_version must be >= 1")
        if any(not self._snapshots.exists(item) for item in source_snapshot_ids):
            raise KeyError("source snapshot not found")
        artifact = self._factory.generate_from_published_sources(
            template_id,
            template_version,
            source_snapshot_ids,
        )
        run = ReportRun(
            report_id=artifact.report_id,
            status=ReportRunStatus.DRAFT,
            context=context,
            source_snapshot_ids=source_snapshot_ids,
            projection_version=projection_version,
            created_by=principal.user_id,
            created_at=artifact.generated_at,
        )
        self._repository.add(run)
        return run, artifact

    def get(
        self, principal: Principal, report_id: str
    ) -> tuple[ReportRun, ReportArtifact]:
        run = self._require(report_id)
        self._access.require(
            principal, Permission.READ_DATA, company=run.context.company_id
        )
        return run, self._factory.get(report_id)

    def list(
        self, principal: Principal, *, company_id: str, period_id: str, scenario_id: str
    ) -> tuple[tuple[ReportRun, ReportArtifact], ...]:
        context = self._contexts.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        self._access.require(
            principal, Permission.READ_DATA, company=context.company_id
        )
        return tuple(
            (run, self._factory.get(run.report_id))
            for run in self._repository.list_for_context(context)
        )

    def submit_review(
        self, principal: Principal, report_id: str
    ) -> tuple[ReportRun, ReportArtifact]:
        run = self._require(report_id)
        self._access.require(
            principal, Permission.VALIDATE_RUN, company=run.context.company_id
        )
        if run.status is not ReportRunStatus.DRAFT:
            raise ValueError("only draft reports can be submitted for review")
        updated = replace(
            run, status=ReportRunStatus.REVIEW, reviewed_by=principal.user_id
        )
        self._repository.replace(updated)
        return updated, self._factory.get(report_id)

    def approve(
        self, principal: Principal, report_id: str
    ) -> tuple[ReportRun, ReportArtifact]:
        run = self._require(report_id)
        self._access.require(
            principal, Permission.APPROVE_RUN, company=run.context.company_id
        )
        if run.status is not ReportRunStatus.REVIEW:
            raise ValueError("only reviewed reports can be approved")
        if principal.user_id == run.created_by:
            raise PermissionError("preparer and approver must be different users")
        artifact = self._factory.approve(report_id, principal.user_id)
        updated = replace(
            run, status=ReportRunStatus.APPROVED, approved_by=principal.user_id
        )
        self._repository.replace(updated)
        return updated, artifact

    def publish(
        self, principal: Principal, report_id: str
    ) -> tuple[ReportRun, ReportArtifact]:
        run = self._require(report_id)
        self._access.require(
            principal, Permission.APPROVE_RUN, company=run.context.company_id
        )
        if run.status is not ReportRunStatus.APPROVED:
            raise ValueError("only approved reports can be published")
        updated = replace(
            run, status=ReportRunStatus.PUBLISHED, published_by=principal.user_id
        )
        self._repository.replace(updated)
        return updated, self._factory.get(report_id)

    def _require(self, report_id: str) -> ReportRun:
        run = self._repository.get(report_id)
        if run is None:
            raise KeyError(report_id)
        return run
