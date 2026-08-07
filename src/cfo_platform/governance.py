from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Iterable, Mapping, Protocol
from uuid import uuid4


class GovernanceStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    RETIRED = "retired"


class AuditAction(StrEnum):
    CREATED = "created"
    VALIDATED = "validated"
    APPROVED = "approved"
    RETIRED = "retired"
    SUPERSEDED = "superseded"


@dataclass(frozen=True, slots=True)
class RunLineage:
    model_id: str
    model_version: str
    code_version: str
    snapshot_id: str
    parameters_hash: str
    random_seed: int

    @classmethod
    def from_parameters(
        cls,
        *,
        model_id: str,
        model_version: str,
        code_version: str,
        snapshot_id: str,
        parameters: Mapping[str, Any],
        random_seed: int,
    ) -> RunLineage:
        canonical = json.dumps(parameters, sort_keys=True, separators=(",", ":"), default=str)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(
            model_id=model_id,
            model_version=model_version,
            code_version=code_version,
            snapshot_id=snapshot_id,
            parameters_hash=digest,
            random_seed=random_seed,
        )


@dataclass(frozen=True, slots=True)
class GovernedRun:
    run_id: str
    lineage: RunLineage
    status: GovernanceStatus
    created_by: str
    created_at: datetime
    validated_by: str | None = None
    approved_by: str | None = None
    retired_by: str | None = None
    supersedes_run_id: str | None = None
    output_hash: str | None = None

    @property
    def immutable(self) -> bool:
        return self.status in {GovernanceStatus.APPROVED, GovernanceStatus.RETIRED}


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    aggregate_type: str
    aggregate_id: str
    action: AuditAction
    actor: str
    occurred_at: datetime
    reason: str
    correlation_id: str
    before_hash: str | None
    after_hash: str


class GovernedRunRepository(Protocol):
    def add(self, run: GovernedRun) -> None: ...

    def get(self, run_id: str) -> GovernedRun | None: ...

    def replace(self, run: GovernedRun) -> None: ...

    def list_all(self) -> tuple[GovernedRun, ...]: ...


class AuditEventRepository(Protocol):
    def append(self, event: AuditEvent) -> None: ...

    def list_for(self, aggregate_type: str, aggregate_id: str) -> tuple[AuditEvent, ...]: ...


class InMemoryGovernedRunRepository:
    def __init__(self) -> None:
        self._runs: dict[str, GovernedRun] = {}

    def add(self, run: GovernedRun) -> None:
        if run.run_id in self._runs:
            raise ValueError("run already exists")
        self._runs[run.run_id] = run

    def get(self, run_id: str) -> GovernedRun | None:
        return self._runs.get(run_id)

    def replace(self, run: GovernedRun) -> None:
        current = self._runs.get(run.run_id)
        if current is None:
            raise KeyError(run.run_id)
        if current.immutable and current != run:
            raise ValueError("approved or retired runs cannot be overwritten")
        self._runs[run.run_id] = run

    def list_all(self) -> tuple[GovernedRun, ...]:
        return tuple(self._runs.values())


class InMemoryAuditEventRepository:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        if any(existing.event_id == event.event_id for existing in self._events):
            raise ValueError("audit event already exists")
        self._events.append(event)

    def list_for(self, aggregate_type: str, aggregate_id: str) -> tuple[AuditEvent, ...]:
        return tuple(
            event
            for event in self._events
            if event.aggregate_type == aggregate_type and event.aggregate_id == aggregate_id
        )


class GovernedRunService:
    def __init__(
        self,
        run_repository: GovernedRunRepository,
        audit_repository: AuditEventRepository,
    ) -> None:
        self._runs = run_repository
        self._audit = audit_repository

    def create(
        self,
        *,
        lineage: RunLineage,
        actor: str,
        correlation_id: str,
        output: Mapping[str, Any] | None = None,
        supersedes_run_id: str | None = None,
    ) -> GovernedRun:
        output_hash = _hash_payload(output) if output is not None else None
        run = GovernedRun(
            run_id=str(uuid4()),
            lineage=lineage,
            status=GovernanceStatus.DRAFT,
            created_by=actor,
            created_at=datetime.now(timezone.utc),
            supersedes_run_id=supersedes_run_id,
            output_hash=output_hash,
        )
        self._runs.add(run)
        self._append_event(None, run, AuditAction.CREATED, actor, correlation_id, "run created")
        return run

    def validate(self, run_id: str, *, actor: str, correlation_id: str) -> GovernedRun:
        current = self._require(run_id)
        if current.status != GovernanceStatus.DRAFT:
            raise ValueError("only draft runs can be validated")
        updated = replace(current, status=GovernanceStatus.VALIDATED, validated_by=actor)
        self._runs.replace(updated)
        self._append_event(current, updated, AuditAction.VALIDATED, actor, correlation_id, "run validated")
        return updated

    def approve(self, run_id: str, *, actor: str, correlation_id: str) -> GovernedRun:
        current = self._require(run_id)
        if current.status != GovernanceStatus.VALIDATED:
            raise ValueError("only validated runs can be approved")
        if actor == current.created_by:
            raise PermissionError("preparer and approver must be different users")
        updated = replace(current, status=GovernanceStatus.APPROVED, approved_by=actor)
        self._runs.replace(updated)
        self._append_event(current, updated, AuditAction.APPROVED, actor, correlation_id, "run approved")
        return updated

    def retire(self, run_id: str, *, actor: str, correlation_id: str, reason: str) -> GovernedRun:
        current = self._require(run_id)
        if current.status != GovernanceStatus.APPROVED:
            raise ValueError("only approved runs can be retired")
        updated = replace(current, status=GovernanceStatus.RETIRED, retired_by=actor)
        self._runs.replace(updated)
        self._append_event(current, updated, AuditAction.RETIRED, actor, correlation_id, reason)
        return updated

    def lineage(self, run_id: str) -> Mapping[str, Any]:
        run = self._require(run_id)
        return {**asdict(run.lineage), "run_id": run.run_id, "status": run.status.value}

    def _require(self, run_id: str) -> GovernedRun:
        run = self._runs.get(run_id)
        if run is None:
            raise KeyError(run_id)
        return run

    def _append_event(
        self,
        before: GovernedRun | None,
        after: GovernedRun,
        action: AuditAction,
        actor: str,
        correlation_id: str,
        reason: str,
    ) -> None:
        event = AuditEvent(
            event_id=str(uuid4()),
            aggregate_type="governed_run",
            aggregate_id=after.run_id,
            action=action,
            actor=actor,
            occurred_at=datetime.now(timezone.utc),
            reason=reason,
            correlation_id=correlation_id,
            before_hash=_hash_payload(asdict(before)) if before is not None else None,
            after_hash=_hash_payload(asdict(after)),
        )
        self._audit.append(event)


def _hash_payload(payload: Mapping[str, Any] | None) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
