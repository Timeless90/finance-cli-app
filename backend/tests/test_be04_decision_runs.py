from fastapi.testclient import TestClient

from app.factory import create_app
from app.shared.config import ApiSettings


def _headers(user: str, roles: str, companies: str = "AURELIA") -> dict[str, str]:
    return {
        "X-User": user,
        "X-Roles": roles,
        "X-Companies": companies,
    }


def _context() -> dict[str, object]:
    return {
        "company_id": "AURELIA",
        "period_id": "2026-08",
        "scenario_id": "downside",
        "source_snapshot_ids": ["uat-snapshot-v1"],
        "projection_version": 1,
    }


def test_be04_action_run_is_idempotent_scoped_and_requires_segregated_approval() -> (
    None
):
    client = TestClient(create_app(settings=ApiSettings(environment="uat")))
    payload = {
        **_context(),
        "model_version": "action-simulation-v1",
        "kind": "action_simulation",
        "action_ids": ["UAT-ACT-AURELIA-DOWNSIDE"],
    }
    headers = {**_headers("preparer", "fp_and_a"), "Idempotency-Key": "action-uat-001"}

    created = client.post("/api/v1/actions/runs", headers=headers, json=payload)
    assert created.status_code == 201, created.text
    run_id = created.json()["run_id"]
    assert created.json()["status"] == "draft"
    assert created.json()["result"]["selected_action_ids"] == [
        "UAT-ACT-AURELIA-DOWNSIDE"
    ]

    listed = client.get(
        "/api/v1/decision-runs",
        params={
            "company_id": "AURELIA",
            "period_id": "2026-08",
            "scenario_id": "downside",
        },
        headers=_headers("reviewer", "reviewer"),
    )
    assert listed.status_code == 200
    assert [item["run_id"] for item in listed.json()] == [run_id]

    replayed = client.post("/api/v1/actions/runs", headers=headers, json=payload)
    assert replayed.status_code == 201
    assert replayed.json()["run_id"] == run_id

    conflict = client.post(
        "/api/v1/actions/runs",
        headers=headers,
        json={**payload, "kind": "action_prioritization"},
    )
    assert conflict.status_code == 409

    validated = client.post(
        f"/api/v1/decision-runs/{run_id}/validate",
        headers=_headers("preparer", "fp_and_a"),
    )
    assert validated.status_code == 200
    assert validated.json()["status"] == "validated"

    denied = client.post(
        f"/api/v1/decision-runs/{run_id}/approve",
        headers=_headers("preparer", "fp_and_a"),
    )
    assert denied.status_code == 403

    approved = client.post(
        f"/api/v1/decision-runs/{run_id}/approve",
        headers=_headers("reviewer", "reviewer"),
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["approved_by"] == "reviewer"

    events = client.get(
        f"/api/v1/decision-runs/{run_id}/events",
        headers=_headers("reviewer", "reviewer"),
    )
    assert events.status_code == 200
    assert [event["event_type"] for event in events.json()] == [
        "created",
        "validated",
        "approved",
    ]

    inaccessible = client.get(
        f"/api/v1/decision-runs/{run_id}",
        headers=_headers("outsider", "cfo", "EUROPE"),
    )
    assert inaccessible.status_code == 403

    benefits = client.post(
        "/api/v1/actions/runs/benefit-tracking",
        headers={
            **_headers("preparer", "fp_and_a"),
            "Idempotency-Key": "action-benefits-001",
        },
        json={
            **_context(),
            "model_version": "benefit-tracking-v1",
            "action_ids": ["UAT-ACT-AURELIA-DOWNSIDE"],
        },
    )
    assert benefits.status_code == 201, benefits.text
    assert benefits.json()["kind"] == "action_benefit_tracking"
    assert benefits.json()["result"]["results"][0]["planned_amount"] == "5.00"


def test_be04_capital_runs_use_server_side_candidate_definitions_and_support_rejection() -> (
    None
):
    client = TestClient(create_app(settings=ApiSettings(environment="uat")))
    valuation = client.post(
        "/api/v1/capital/runs/valuation",
        headers={
            **_headers("preparer", "fp_and_a"),
            "Idempotency-Key": "capital-valuation-001",
        },
        json={
            **_context(),
            "model_version": "capital-valuation-v1",
            "candidate_ids": ["INV-104"],
        },
    )
    assert valuation.status_code == 201, valuation.text
    assert valuation.json()["references"] == ["INV-104"]
    assert "npv" in valuation.json()["result"]

    allocation = client.post(
        "/api/v1/capital/runs/allocation",
        headers={
            **_headers("preparer", "fp_and_a"),
            "Idempotency-Key": "capital-allocation-001",
        },
        json={
            **_context(),
            "model_version": "capital-allocation-v1",
            "candidate_ids": ["INV-104", "INV-118"],
            "strategic_weight": 0.2,
        },
    )
    assert allocation.status_code == 201, allocation.text
    run_id = allocation.json()["run_id"]
    assert allocation.json()["result"]["constraints_satisfied"] is True

    assert (
        client.post(
            f"/api/v1/decision-runs/{run_id}/validate",
            headers=_headers("preparer", "fp_and_a"),
        ).status_code
        == 200
    )
    rejected = client.post(
        f"/api/v1/decision-runs/{run_id}/reject",
        headers=_headers("reviewer", "reviewer"),
        json={"reason": "Liquidity committee requested a refreshed cash source."},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"
    assert rejected.json()["rejection_reason"].startswith("Liquidity committee")

    funding = client.post(
        "/api/v1/capital/runs/funding",
        headers={
            **_headers("preparer", "fp_and_a"),
            "Idempotency-Key": "capital-funding-001",
        },
        json={
            **_context(),
            "model_version": "funding-scenario-v1",
            "funding_option_id": "RCF-2026",
        },
    )
    assert funding.status_code == 201, funding.text
    assert funding.json()["kind"] == "funding_scenario"
    assert funding.json()["result"]["option_id"] == "RCF-2026"
