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
            snapshot_id="snap-be03",
            content_hash="hash-be03",
            row_count=len(records),
            records=records,
        )
    )
    return container


def _headers(companies: str = "ACME") -> dict[str, str]:
    return {
        "X-User": "cfo-user",
        "X-Roles": "cfo",
        "X-Companies": companies,
    }


def _register_risk(client: TestClient, risk_id: str = "R-BE03") -> None:
    response = client.post(
        "/api/v1/risk/register",
        json={
            "risk_id": risk_id,
            "title": "Supplier disruption",
            "cause": "Single-source dependency",
            "event": "Production interruption",
            "owner": "COO",
            "category": "operational",
            "horizon_months": 12,
            "quantification": {
                "distribution": "empirical",
                "frequency_model": "bernoulli",
                "occurrence_probability": "0.25",
                "empirical_losses": ["100000", "250000", "500000"],
            },
            "controls": [],
        },
    )
    assert response.status_code == 200


def test_risk_model_run_is_persisted_executed_and_company_scoped() -> None:
    container = _seed_container()
    with TestClient(create_app(container=container)) as client:
        _register_risk(client)
        created = client.post(
            "/api/v1/risk/model-runs",
            headers=_headers(),
            json={
                "company_id": "ACME",
                "period_id": "2026-06",
                "scenario_id": "base",
                "risk_ids": ["R-BE03"],
                "correlation_matrix": [[1]],
                "paths": 500,
                "seed": 2026,
            },
        )
        assert created.status_code == 202
        created_payload = created.json()
        assert created_payload["status"] == "pending"
        assert created_payload["model_type"] == "aggregation"
        assert created_payload["source_snapshot_ids"] == ["snap-be03"]
        run_id = created_payload["run_id"]

        fetched = client.get(
            f"/api/v1/risk/model-runs/{run_id}",
            headers=_headers(),
        )
        assert fetched.status_code == 200
        payload = fetched.json()
        assert payload["status"] == "succeeded"
        assert payload["input_context"]["company_id"] == "ACME"
        assert payload["result"]["paths"] == 500
        assert payload["result"]["seed"] == 2026
        assert Decimal(payload["result"]["p95_net_loss"]) >= 0

        denied = client.get(
            f"/api/v1/risk/model-runs/{run_id}",
            headers=_headers("OTHER"),
        )
        assert denied.status_code == 403


def test_market_risk_var_run_persists_result_and_rejects_wrong_domain_lookup() -> None:
    container = _seed_container()
    with TestClient(create_app(container=container)) as client:
        losses = [(-1.0 + index * 0.04) for index in range(100)]
        created = client.post(
            "/api/v1/market-risk/model-runs",
            headers=_headers(),
            json={
                "company_id": "ACME",
                "period_id": "2026-06",
                "scenario_id": "base",
                "model_type": "var_es",
                "losses": losses,
                "confidence": 0.95,
                "method": "historical",
            },
        )
        assert created.status_code == 202
        run_id = created.json()["run_id"]

        fetched = client.get(
            f"/api/v1/market-risk/model-runs/{run_id}",
            headers=_headers(),
        )
        assert fetched.status_code == 200
        payload = fetched.json()
        assert payload["status"] == "succeeded"
        assert payload["result"]["method"] == "historical"
        assert (
            payload["result"]["expected_shortfall"]
            >= payload["result"]["value_at_risk"]
        )

        wrong_domain = client.get(
            f"/api/v1/risk/model-runs/{run_id}",
            headers=_headers(),
        )
        assert wrong_domain.status_code == 404


def test_failed_market_model_run_is_retained_with_error_details() -> None:
    container = _seed_container()
    with TestClient(create_app(container=container)) as client:
        created = client.post(
            "/api/v1/market-risk/model-runs",
            headers=_headers(),
            json={
                "company_id": "ACME",
                "period_id": "2026-06",
                "scenario_id": "base",
                "model_type": "garch_t",
                "returns": [0.01, -0.01, 0.005],
            },
        )
        assert created.status_code == 202
        run_id = created.json()["run_id"]

        fetched = client.get(
            f"/api/v1/market-risk/model-runs/{run_id}",
            headers=_headers(),
        )
        assert fetched.status_code == 200
        payload = fetched.json()
        assert payload["status"] == "failed"
        assert payload["result"] is None
        assert "GARCH requires at least 100 observations" in payload["error"]
        assert payload["started_at"] is not None
        assert payload["completed_at"] is not None


def test_model_run_context_and_missing_run_errors_are_fail_closed() -> None:
    container = _seed_container()
    with TestClient(create_app(container=container)) as client:
        missing_context = client.post(
            "/api/v1/risk/model-runs",
            headers=_headers(),
            json={
                "company_id": "ACME",
                "period_id": "2099-01",
                "scenario_id": "base",
                "risk_ids": ["R-MISSING"],
                "correlation_matrix": [[1]],
                "paths": 100,
            },
        )
        assert missing_context.status_code == 404

        missing_run = client.get(
            "/api/v1/market-risk/model-runs/does-not-exist",
            headers=_headers(),
        )
        assert missing_run.status_code == 404


def test_be03_model_run_contract_is_published_in_openapi() -> None:
    app = create_app(container=_seed_container())
    schema = app.openapi()
    paths = schema["paths"]
    assert "/api/v1/risk/model-runs" in paths
    assert "/api/v1/risk/model-runs/{run_id}" in paths
    assert "/api/v1/market-risk/model-runs" in paths
    assert "/api/v1/market-risk/model-runs/{run_id}" in paths

    assert set(schema["components"]["schemas"]["MarketRiskModelType"]["enum"]) == {
        "var_es",
        "garch_t",
        "regime_hmm",
        "evt",
        "copula",
        "var_backtest",
    }
