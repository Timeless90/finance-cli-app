"""Governed, context-scoped lifecycles for management decision runs.

Calculation engines remain separate.  This service records the authoritative
inputs, result, source snapshots and approval state around those engines.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from threading import RLock
from typing import Any, Protocol
from uuid import uuid4

from app.data.data_store import DataSnapshotRepository
from app.shared.rbac import AccessControlService, Permission, Principal
from app.workspace.workspace_integration import ContextCatalogService, WorkspaceContext


class DecisionRunKind(StrEnum):
    ACTION_SIMULATION = "action_simulation"
    ACTION_PRIORITIZATION = "action_prioritization"
    ACTION_BENEFIT_TRACKING = "action_benefit_tracking"
    CAPITAL_VALUATION = "capital_valuation"
    CAPITAL_MONTE_CARLO_NPV = "capital_monte_carlo_npv"
    CAPITAL_ALLOCATION = "capital_allocation"
    FUNDING_SCENARIO = "funding_scenario"


class DecisionRunStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    REJECTED = "rejected"


class DecisionRunEventType(StrEnum):
    CREATED = "created"
    VALIDATED = "validated"
    APPROVED = "approved"
    REJECTED = "rejected"


class IdempotencyConflict(ValueError):
    """An idempotency key was reused for a different decision request."""


@dataclass(frozen=True, slots=True)
class DecisionRun:
    run_id: str
    kind: DecisionRunKind
    status: DecisionRunStatus
    context: WorkspaceContext
    references: tuple[str, ...]
    source_snapshot_ids: tuple[str, ...]
    projection_version: int
    model_version: str
    parameters: Mapping[str, Any]
    result: Mapping[str, Any]
    created_by: str
    created_at: datetime
    idempotency_key: str
    request_hash: str
    validated_by: str | None = None
    validated_at: datetime | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    rejected_by: str | None = None
    rejected_at: datetime | None = None
    rejection_reason: str | None = None


@dataclass(frozen=True, slots=True)
class DecisionRunEvent:
    event_id: str
    run_id: str
    event_type: DecisionRunEventType
    actor: str
    correlation_id: str
    occurred_at: datetime
    reason: str | None = None


class DecisionRunRepository(Protocol):
    def add(self, run: DecisionRun) -> None: ...

    def get(self, run_id: str) -> DecisionRun | None: ...

    def replace(self, run: DecisionRun) -> None: ...

    def get_by_idempotency(self, user_id: str, key: str) -> DecisionRun | None: ...

    def list_for_context(
        self,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
    ) -> tuple[DecisionRun, ...]: ...

    def append_event(self, event: DecisionRunEvent) -> None: ...

    def events_for(self, run_id: str) -> tuple[DecisionRunEvent, ...]: ...


class InMemoryDecisionRunRepository:
    def __init__(self) -> None:
        self._runs: dict[str, DecisionRun] = {}
        self._idempotency: dict[tuple[str, str], str] = {}
        self._events: list[DecisionRunEvent] = []
        self._lock = RLock()

    def add(self, run: DecisionRun) -> None:
        with self._lock:
            if run.run_id in self._runs:
                raise ValueError("decision run already exists")
            key = (run.created_by, run.idempotency_key)
            if key in self._idempotency:
                raise ValueError("idempotency key already exists")
            self._runs[run.run_id] = run
            self._idempotency[key] = run.run_id

    def get(self, run_id: str) -> DecisionRun | None:
        with self._lock:
            return self._runs.get(run_id)

    def replace(self, run: DecisionRun) -> None:
        with self._lock:
            if run.run_id not in self._runs:
                raise KeyError(run.run_id)
            self._runs[run.run_id] = run

    def get_by_idempotency(self, user_id: str, key: str) -> DecisionRun | None:
        with self._lock:
            run_id = self._idempotency.get((user_id, key))
            return self._runs.get(run_id) if run_id is not None else None

    def list_for_context(
        self,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
    ) -> tuple[DecisionRun, ...]:
        with self._lock:
            return tuple(
                run
                for run in sorted(
                    self._runs.values(), key=lambda item: item.created_at, reverse=True
                )
                if (
                    run.context.company_id == company_id
                    and run.context.period_id == period_id
                    and run.context.scenario_id == scenario_id
                )
            )

    def append_event(self, event: DecisionRunEvent) -> None:
        with self._lock:
            self._events.append(event)

    def events_for(self, run_id: str) -> tuple[DecisionRunEvent, ...]:
        with self._lock:
            return tuple(event for event in self._events if event.run_id == run_id)


class DecisionRunService:
    def __init__(
        self,
        context_catalog: ContextCatalogService,
        snapshots: DataSnapshotRepository,
        access: AccessControlService,
        repository: DecisionRunRepository,
    ) -> None:
        self._contexts = context_catalog
        self._snapshots = snapshots
        self._access = access
        self._repository = repository

    def create(
        self,
        principal: Principal,
        *,
        kind: DecisionRunKind,
        company_id: str,
        period_id: str,
        scenario_id: str,
        references: tuple[str, ...],
        source_snapshot_ids: tuple[str, ...],
        projection_version: int,
        model_version: str,
        parameters: Mapping[str, Any],
        result: Mapping[str, Any],
        idempotency_key: str,
        correlation_id: str,
    ) -> DecisionRun:
        if not idempotency_key.strip():
            raise ValueError("Idempotency-Key is required")
        if not references:
            raise ValueError("at least one business reference is required")
        if not source_snapshot_ids:
            raise ValueError("at least one source snapshot is required")
        if projection_version < 1:
            raise ValueError("projection_version must be >= 1")
        if not model_version.strip():
            raise ValueError("model_version is required")

        context = self._contexts.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        self._access.require(
            principal, Permission.CREATE_RUN, company=context.company_id
        )
        unknown = [
            snapshot_id
            for snapshot_id in source_snapshot_ids
            if not self._snapshots.exists(snapshot_id)
        ]
        if unknown:
            raise KeyError(f"source snapshot not found: {unknown[0]}")

        request_hash = _request_hash(
            kind=kind,
            context=context,
            references=references,
            source_snapshot_ids=source_snapshot_ids,
            projection_version=projection_version,
            model_version=model_version,
            parameters=parameters,
        )
        existing = self._repository.get_by_idempotency(
            principal.user_id, idempotency_key
        )
        if existing is not None:
            if existing.request_hash != request_hash:
                raise IdempotencyConflict(
                    "Idempotency-Key was already used for another request"
                )
            return existing

        run = DecisionRun(
            run_id=str(uuid4()),
            kind=kind,
            status=DecisionRunStatus.DRAFT,
            context=context,
            references=references,
            source_snapshot_ids=source_snapshot_ids,
            projection_version=projection_version,
            model_version=model_version,
            parameters=dict(parameters),
            result=dict(result),
            created_by=principal.user_id,
            created_at=datetime.now(UTC),
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )
        self._repository.add(run)
        self._event(
            run, DecisionRunEventType.CREATED, principal.user_id, correlation_id
        )
        return run

    def get(self, principal: Principal, run_id: str) -> DecisionRun:
        run = self._require(run_id)
        self._access.require(
            principal, Permission.READ_DATA, company=run.context.company_id
        )
        return run

    def list(
        self,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
    ) -> tuple[DecisionRun, ...]:
        context = self._contexts.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        self._access.require(
            principal, Permission.READ_DATA, company=context.company_id
        )
        return self._repository.list_for_context(
            company_id=context.company_id,
            period_id=context.period_id,
            scenario_id=context.scenario_id,
        )

    def events(self, principal: Principal, run_id: str) -> tuple[DecisionRunEvent, ...]:
        run = self._require(run_id)
        self._access.require(
            principal, Permission.READ_AUDIT, company=run.context.company_id
        )
        return self._repository.events_for(run_id)

    def validate(
        self, principal: Principal, run_id: str, *, correlation_id: str
    ) -> DecisionRun:
        run = self._require(run_id)
        self._access.require(
            principal, Permission.VALIDATE_RUN, company=run.context.company_id
        )
        if run.status is not DecisionRunStatus.DRAFT:
            raise ValueError("only draft decision runs can be validated")
        updated = replace(
            run,
            status=DecisionRunStatus.VALIDATED,
            validated_by=principal.user_id,
            validated_at=datetime.now(UTC),
        )
        self._repository.replace(updated)
        self._event(
            updated, DecisionRunEventType.VALIDATED, principal.user_id, correlation_id
        )
        return updated

    def approve(
        self, principal: Principal, run_id: str, *, correlation_id: str
    ) -> DecisionRun:
        run = self._require(run_id)
        self._access.require(
            principal, Permission.APPROVE_RUN, company=run.context.company_id
        )
        if run.status is not DecisionRunStatus.VALIDATED:
            raise ValueError("only validated decision runs can be approved")
        if run.created_by == principal.user_id:
            raise PermissionError("preparer cannot approve own decision run")
        updated = replace(
            run,
            status=DecisionRunStatus.APPROVED,
            approved_by=principal.user_id,
            approved_at=datetime.now(UTC),
        )
        self._repository.replace(updated)
        self._event(
            updated, DecisionRunEventType.APPROVED, principal.user_id, correlation_id
        )
        return updated

    def reject(
        self, principal: Principal, run_id: str, *, reason: str, correlation_id: str
    ) -> DecisionRun:
        run = self._require(run_id)
        self._access.require(
            principal, Permission.APPROVE_RUN, company=run.context.company_id
        )
        if run.status is not DecisionRunStatus.VALIDATED:
            raise ValueError("only validated decision runs can be rejected")
        if run.created_by == principal.user_id:
            raise PermissionError("preparer cannot reject own decision run")
        if not reason.strip():
            raise ValueError("rejection reason is required")
        updated = replace(
            run,
            status=DecisionRunStatus.REJECTED,
            rejected_by=principal.user_id,
            rejected_at=datetime.now(UTC),
            rejection_reason=reason.strip(),
        )
        self._repository.replace(updated)
        self._event(
            updated,
            DecisionRunEventType.REJECTED,
            principal.user_id,
            correlation_id,
            reason=updated.rejection_reason,
        )
        return updated

    def _require(self, run_id: str) -> DecisionRun:
        run = self._repository.get(run_id)
        if run is None:
            raise KeyError("decision_run")
        return run

    def _event(
        self,
        run: DecisionRun,
        event_type: DecisionRunEventType,
        actor: str,
        correlation_id: str,
        *,
        reason: str | None = None,
    ) -> None:
        self._repository.append_event(
            DecisionRunEvent(
                event_id=str(uuid4()),
                run_id=run.run_id,
                event_type=event_type,
                actor=actor,
                correlation_id=correlation_id,
                occurred_at=datetime.now(UTC),
                reason=reason,
            )
        )


def _request_hash(
    *,
    kind: DecisionRunKind,
    context: WorkspaceContext,
    references: tuple[str, ...],
    source_snapshot_ids: tuple[str, ...],
    projection_version: int,
    model_version: str,
    parameters: Mapping[str, Any],
) -> str:
    payload = {
        "kind": kind.value,
        "context": {
            "company_id": context.company_id,
            "period_id": context.period_id,
            "scenario_id": context.scenario_id,
        },
        "references": references,
        "source_snapshot_ids": source_snapshot_ids,
        "projection_version": projection_version,
        "model_version": model_version,
        "parameters": parameters,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
