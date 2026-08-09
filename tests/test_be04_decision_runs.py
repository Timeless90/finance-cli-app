from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.composition import build_container
from cfo_platform.data_foundation import DataSnapshot, FinanceRecord


def _seed_container():
    container = build_container()
    records = (
        FinanceRecord(
            company="ACME",
            account="revenue",
            period="2026-06",
            scenario="base",
            value=Decimal("100"),
            currency="EUR",
        ),
    )
    container.data_snapshot_repository.save(
        DataSnapshot(
            snapshot_id="snap-be04",
            content_hash="hash-be04",
            row_count=len(records),
            records=records,
        )
    )
    return container


def _headers(role: str = "cfo", companies: str = "ACME") -> dict[str, str]:
    return {
        "X-User": f"{role}-user",
        "X-Roles": role,
        "X-Companies": companies,
    }


def _context() -> dict[str, str]:
    return {
        "company_id": "ACME",
        "period_id": "2026-06",
        "scenario_id": "base",
    }


def _register_action(client: TestClient, action_id: str = "A-BE04") -> None:
    response = client.post(
        "/api/v1/actions/register",
        json={
            "action_id": action_id,
            "title": "Pricing action",
            "owner": "CFO",
            "due_period": 2,
            "cost": "20",
            "confidence": "0.8",
            "status": "planned",
            "impacts": [
                {
                    "period": 1,
                    "metric": "ebitda",
                    "amount": "100",
                    "impact_key": f"{action_id}-ebitda",
                },
                {
                    "period": 1,
                    "metric": "cash",
                    "amount": "50",
                    "impact_key": f"{action_id}-cash",
                },
            ],
        },
    )
    assert response.status_code == 200


def _project(project_id: str, investment: float = 100.0) -> dict[str, object]:
    return {
        "project_id": project_id,
        "name": f"Project {project_id}",
        "initial_investment": investment,
        "cash_flows": [60.0, 70.0],
        "annual_nopat": [20.0, 25.0],
        "strategic_score": 0.8,
        "cash_headroom_impact": 20.0,
        "leverage_delta": 0.1,
        "interest_cover_delta": -0.1,
    }


def test_action_simulation_run_executes_is_scoped_and_governed() -> None:
    container = _seed_container()
    with TestClient(create_app(container=container)) as client:
        _register_action(client)
        created = client.post(
            "/api/v1/actions/runs",
            headers=_headers(),
            json={
                **_context(),
                "run_type": "simulation",
                "action_ids": ["A-BE04"],
                "upstream_run_ids": ["risk-run-123"],
            },
        )
        assert created.status_code == 202
        created_payload = created.json()
        assert created_payload["status"] == "pending"
        assert created_payload["validation_status"] == "draft"
        assert created_payload["source_snapshot_ids"] == ["snap-be04"]
        assert created_payload["upstream_run_ids"] == ["risk-run-123"]
        assert created_payload["engine_version"] == "action-simulation-v1"
        run_id = created_payload["run_id"]

        fetched = client.get(f"/api/v1/actions/runs/{run_id}", headers=_headers())
        assert fetched.status_code == 200
        payload = fetched.json()
        assert payload["status"] == "succeeded"
        assert Decimal(str(payload["result"]["expected_ebitda_effect"])) == Decimal("80")
        assert Decimal(str(payload["result"]["expected_cash_effect"])) == Decimal("40")

        denied = client.get(
            f"/api/v1/actions/runs/{run_id}",
            headers=_headers(companies="OTHER"),
        )
        assert denied.status_code == 403

        cannot_validate = client.post(
            f"/api/v1/actions/runs/{run_id}/validate",
            headers=_headers("cfo"),
            json={"rationale": "reviewed"},
        )
        assert cannot_validate.status_code == 403

        validated = client.post(
            f"/api/v1/actions/runs/{run_id}/validate",
            headers=_headers("fp_and_a"),
            json={"rationale": "finance validation complete"},
        )
        assert validated.status_code == 200
        assert validated.json()["validation_status"] == "validated"
        assert validated.json()["validated_by"] == "fp_and_a-user"

        approved = client.post(
            f"/api/v1/actions/runs/{run_id}/approve",
            headers=_headers("cfo"),
            json={"rationale": "approved for execution"},
        )
        assert approved.status_code == 200
        assert approved.json()["validation_status"] == "approved"
        assert approved.json()["approved_by"] == "cfo-user"

        invalid_reject = client.post(
            f"/api/v1/actions/runs/{run_id}/reject",
            headers=_headers("cfo"),
            json={"rationale": "too late"},
        )
        assert invalid_reject.status_code == 409

        listed = client.get(
            "/api/v1/actions/runs",
            headers=_headers(),
            params=_context(),
        )
        assert listed.status_code == 200
        assert [item["run_id"] for item in listed.json()] == [run_id]


def test_capital_runs_dispatch_existing_engines() -> None:
    container = _seed_container()
    with TestClient(create_app(container=container)) as client:
        valuation = client.post(
            "/api/v1/capital/runs",
            headers=_headers(),
            json={
                **_context(),
                "run_type": "project_valuation",
                "project": _project("P1"),
                "discount_rate": 0.1,
            },
        )
        assert valuation.status_code == 202
        valuation_run = client.get(
            f"/api/v1/capital/runs/{valuation.json()['run_id']}",
            headers=_headers(),
        ).json()
        assert valuation_run["status"] == "succeeded"
        assert valuation_run["result"]["project_id"] == "P1"
        assert valuation_run["engine_version"] == "capital-project-valuation-v1"

        monte_carlo = client.post(
            "/api/v1/capital/runs",
            headers=_headers(),
            json={
                **_context(),
                "run_type": "monte_carlo_npv",
                "project": _project("P1"),
                "discount_rate": 0.1,
                "paths": 100,
                "seed": 2026,
            },
        )
        assert monte_carlo.status_code == 202
        mc_run = client.get(
            f"/api/v1/capital/runs/{monte_carlo.json()['run_id']}",
            headers=_headers(),
        ).json()
        assert mc_run["status"] == "succeeded"
        assert mc_run["result"]["paths"] == 100
        assert mc_run["result"]["seed"] == 2026

        allocation = client.post(
            "/api/v1/capital/runs",
            headers=_headers(),
            json={
                **_context(),
                "run_type": "portfolio_allocation",
                "projects": [_project("P1", 100.0), _project("P2", 80.0)],
                "risk_adjusted_npvs": {"P1": 50.0, "P2": 35.0},
                "constraints": {
                    "budget": 200.0,
                    "opening_cash_headroom": 500.0,
                    "minimum_cash_headroom": 100.0,
                    "base_leverage": 2.0,
                    "maximum_leverage": 3.0,
                    "base_interest_cover": 5.0,
                    "minimum_interest_cover": 2.0,
                },
            },
        )
        assert allocation.status_code == 202
        allocation_run = client.get(
            f"/api/v1/capital/runs/{allocation.json()['run_id']}",
            headers=_headers(),
        ).json()
        assert allocation_run["status"] == "succeeded"
        assert allocation_run["result"]["constraints_satisfied"] is True
        assert set(allocation_run["result"]["selected_project_ids"]) == {"P1", "P2"}

        funding = client.post(
            "/api/v1/capital/runs",
            headers=_headers(),
            json={
                **_context(),
                "run_type": "funding_scenario",
                "option": {
                    "option_id": "TERM-A",
                    "amount": 100.0,
                    "annual_rate": 0.05,
                    "term_years": 5,
                },
                "base_debt": 200.0,
                "base_ebitda": 150.0,
                "base_interest_expense": 10.0,
                "maximum_leverage": 3.0,
            },
        )
        assert funding.status_code == 202
        funding_run = client.get(
            f"/api/v1/capital/runs/{funding.json()['run_id']}",
            headers=_headers(),
        ).json()
        assert funding_run["status"] == "succeeded"
        assert funding_run["result"]["option_id"] == "TERM-A"
        assert funding_run["result"]["covenant_headroom"] > 0


def test_failed_action_run_is_retained_and_cannot_be_validated() -> None:
    container = _seed_container()
    with TestClient(create_app(container=container)) as client:
        created = client.post(
            "/api/v1/actions/runs",
            headers=_headers(),
            json={
                **_context(),
                "run_type": "simulation",
                "action_ids": ["DOES-NOT-EXIST"],
            },
        )
        assert created.status_code == 202
        run_id = created.json()["run_id"]
        fetched = client.get(f"/api/v1/actions/runs/{run_id}", headers=_headers())
        assert fetched.status_code == 200
        assert fetched.json()["status"] == "failed"
        assert "unknown action" in fetched.json()["error"]

        validate = client.post(
            f"/api/v1/actions/runs/{run_id}/validate",
            headers=_headers("fp_and_a"),
            json={"rationale": "should fail"},
        )
        assert validate.status_code == 409


def test_be04_decision_run_contract_is_published_in_openapi() -> None:
    app = create_app(container=_seed_container())
    paths = app.openapi()["paths"]
    required = {
        "/api/v1/actions/runs",
        "/api/v1/actions/runs/{run_id}",
        "/api/v1/actions/runs/{run_id}/validate",
        "/api/v1/actions/runs/{run_id}/approve",
        "/api/v1/actions/runs/{run_id}/reject",
        "/api/v1/capital/runs",
        "/api/v1/capital/runs/{run_id}",
        "/api/v1/capital/runs/{run_id}/validate",
        "/api/v1/capital/runs/{run_id}/approve",
        "/api/v1/capital/runs/{run_id}/reject",
    }
    assert required <= set(paths)
