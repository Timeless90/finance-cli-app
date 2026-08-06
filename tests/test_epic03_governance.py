from __future__ import annotations

import pytest

from cfo_platform.governance import (
    GovernanceStatus,
    GovernedRunService,
    InMemoryAuditEventRepository,
    InMemoryGovernedRunRepository,
    RunLineage,
)


def _service() -> tuple[
    GovernedRunService,
    InMemoryGovernedRunRepository,
    InMemoryAuditEventRepository,
]:
    runs = InMemoryGovernedRunRepository()
    audit = InMemoryAuditEventRepository()
    return GovernedRunService(runs, audit), runs, audit


def _lineage() -> RunLineage:
    return RunLineage.from_parameters(
        model_id="forecast.ebitda",
        model_version="1.0.0",
        code_version="abc123",
        snapshot_id="sha256:data",
        parameters={"horizon": 12, "paths": 10000},
        random_seed=42,
    )


def test_run_lifecycle_is_audited_and_approved_run_is_immutable() -> None:
    service, runs, audit = _service()
    run = service.create(
        lineage=_lineage(),
        actor="planner@example.com",
        correlation_id="corr-1",
        output={"p50": 100.0},
    )
    validated = service.validate(
        run.run_id,
        actor="validator@example.com",
        correlation_id="corr-2",
    )
    approved = service.approve(
        run.run_id,
        actor="reviewer@example.com",
        correlation_id="corr-3",
    )

    assert validated.status == GovernanceStatus.VALIDATED
    assert approved.status == GovernanceStatus.APPROVED
    assert approved.immutable is True
    assert len(audit.list_for("governed_run", run.run_id)) == 3

    with pytest.raises(ValueError, match="cannot be overwritten"):
        runs.replace(validated)


def test_preparer_cannot_approve_own_run() -> None:
    service, _, _ = _service()
    run = service.create(
        lineage=_lineage(),
        actor="planner@example.com",
        correlation_id="corr-1",
    )
    service.validate(
        run.run_id,
        actor="validator@example.com",
        correlation_id="corr-2",
    )

    with pytest.raises(PermissionError, match="must be different"):
        service.approve(
            run.run_id,
            actor="planner@example.com",
            correlation_id="corr-3",
        )


def test_parameter_hash_is_order_independent() -> None:
    first = RunLineage.from_parameters(
        model_id="model",
        model_version="1",
        code_version="code",
        snapshot_id="snapshot",
        parameters={"a": 1, "b": 2},
        random_seed=7,
    )
    second = RunLineage.from_parameters(
        model_id="model",
        model_version="1",
        code_version="code",
        snapshot_id="snapshot",
        parameters={"b": 2, "a": 1},
        random_seed=7,
    )

    assert first.parameters_hash == second.parameters_hash
