from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.governance import (
    GovernanceStatus,
    GovernedRunService,
    InMemoryAuditEventRepository,
    InMemoryGovernedRunRepository,
    RunLineage,
)
from cfo_platform.governance_catalog import (
    Assumption,
    InMemoryModelRegistryRepository,
    InMemoryScenarioRepository,
    ModelLifecycle,
    ModelRegistration,
    ModelRegistryService,
    ScenarioKind,
    ScenarioService,
)
from cfo_platform.governance_persistence import (
    SqliteAuditEventRepository,
    SqliteGovernedRunRepository,
)
from cfo_platform.rbac import AccessControlService, Permission, Principal, Role


def _service() -> tuple[GovernedRunService, InMemoryGovernedRunRepository, InMemoryAuditEventRepository]:
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
    run = service.create(lineage=_lineage(), actor="planner", correlation_id="corr-1")
    validated = service.validate(run.run_id, actor="validator", correlation_id="corr-2")
    approved = service.approve(run.run_id, actor="reviewer", correlation_id="corr-3")
    assert validated.status == GovernanceStatus.VALIDATED
    assert approved.status == GovernanceStatus.APPROVED
    assert len(audit.list_for("governed_run", run.run_id)) == 3
    with pytest.raises(ValueError, match="cannot be overwritten"):
        runs.replace(validated)


def test_preparer_cannot_approve_own_run() -> None:
    service, _, _ = _service()
    run = service.create(lineage=_lineage(), actor="planner", correlation_id="corr-1")
    service.validate(run.run_id, actor="validator", correlation_id="corr-2")
    with pytest.raises(PermissionError, match="must be different"):
        service.approve(run.run_id, actor="planner", correlation_id="corr-3")


def test_parameter_hash_is_order_independent() -> None:
    first = RunLineage.from_parameters(model_id="m", model_version="1", code_version="c", snapshot_id="s", parameters={"a": 1, "b": 2}, random_seed=7)
    second = RunLineage.from_parameters(model_id="m", model_version="1", code_version="c", snapshot_id="s", parameters={"b": 2, "a": 1}, random_seed=7)
    assert first.parameters_hash == second.parameters_hash


def test_sqlite_run_and_audit_repositories_are_durable(tmp_path) -> None:
    database = tmp_path / "governance.db"
    service = GovernedRunService(SqliteGovernedRunRepository(database), SqliteAuditEventRepository(database))
    run = service.create(lineage=_lineage(), actor="planner", correlation_id="corr")
    assert SqliteGovernedRunRepository(database).get(run.run_id) == run
    assert len(SqliteAuditEventRepository(database).list_for("governed_run", run.run_id)) == 1


def test_scenario_and_model_governance() -> None:
    scenarios = ScenarioService(InMemoryScenarioRepository())
    base = scenarios.create(
        name="Base",
        kind=ScenarioKind.BASE,
        assumptions=(Assumption("growth", "Growth", 0.05, "finance"),),
        actor="planner",
    )
    clone = scenarios.clone(base.scenario_id, actor="planner-2", name="Upside")
    assert clone.parent_scenario_id == base.scenario_id
    assert scenarios.approve(base.scenario_id, actor="reviewer").status == GovernanceStatus.APPROVED

    models = ModelRegistryService(InMemoryModelRegistryRepository())
    model = ModelRegistration(
        model_id="cash-risk",
        version="1.0.0",
        owner="quant-owner",
        description="Cash risk model",
        limitations=("monthly frequency",),
        lifecycle=ModelLifecycle.DEVELOPMENT,
        created_at=datetime.now(timezone.utc),
    )
    models.register(model)
    models.validate(model.model_id, model.version, run_ids=("backtest-1",))
    assert models.approve(model.model_id, model.version, actor="reviewer").lifecycle == ModelLifecycle.APPROVED


def test_rbac_enforces_permissions_and_company_scope() -> None:
    access = AccessControlService()
    principal = Principal("controller", frozenset({Role.CONTROLLER}), frozenset({"DE01"}))
    access.require(principal, Permission.CREATE_RUN, company="DE01")
    with pytest.raises(PermissionError):
        access.require(principal, Permission.APPROVE_RUN, company="DE01")
    with pytest.raises(PermissionError):
        access.require(principal, Permission.READ_DATA, company="US01")


def test_governance_api_run_lifecycle() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/governance/runs",
        headers={"x-user": "planner", "x-roles": "fp_and_a"},
        json={
            "model_id": "forecast",
            "model_version": "1.0",
            "code_version": "sha",
            "snapshot_id": "snapshot",
            "parameters": {"paths": 100},
            "random_seed": 7,
        },
    )
    assert response.status_code == 201
    run_id = response.json()["run_id"]
    assert client.post(f"/api/v1/governance/runs/{run_id}/validate", headers={"x-user": "validator", "x-roles": "risk"}).status_code == 200
    assert client.post(f"/api/v1/governance/runs/{run_id}/approve", headers={"x-user": "reviewer", "x-roles": "reviewer"}).status_code == 200
    lineage = client.get(f"/api/v1/governance/runs/{run_id}/lineage", headers={"x-user": "auditor", "x-roles": "reviewer"})
    assert lineage.status_code == 200
    assert lineage.json()["snapshot_id"] == "snapshot"
