from fastapi.testclient import TestClient

from app.factory import create_app
from app.shared.config import ApiSettings


def _headers(companies: str = "AURELIA,EUROPE") -> dict[str, str]:
    return {
        "X-User": "uat-cfo",
        "X-Roles": "cfo",
        "X-Companies": companies,
    }


def test_uat_environment_seeds_two_companies_and_published_workspaces() -> None:
    client = TestClient(create_app(settings=ApiSettings(environment="uat")))

    companies = client.get("/api/v1/context/companies", headers=_headers())
    assert companies.status_code == 200
    assert [item["company_id"] for item in companies.json()] == ["AURELIA", "EUROPE"]

    params = {
        "company_id": "AURELIA",
        "period_id": "2026-08",
        "scenario_id": "downside",
    }
    for endpoint in (
        "/api/v1/command-center/overview",
        "/api/v1/planning/workspace",
        "/api/v1/performance/workspace",
        "/api/v1/profitability/workspace",
        "/api/v1/liquidity/workspace",
        "/api/v1/risk/workspace",
        "/api/v1/market-risk/workspace",
        "/api/v1/actions/workspace",
        "/api/v1/capital/workspace",
        "/api/v1/reporting/workspace",
        "/api/v1/data-governance/workspace",
    ):
        response = client.get(endpoint, params=params, headers=_headers())
        assert response.status_code == 200, response.text
        assert response.json()["context"]["company_id"] == "AURELIA"
        assert response.json()["source_snapshot_ids"] == ["uat-snapshot-v1"]

    profitability = client.get(
        "/api/v1/profitability/workspace", params=params, headers=_headers()
    )
    assert profitability.json()["segments"][0]["segment_id"] == "core"
    assert (
        profitability.json()["allocation_assurance"]["snapshot_id"] == "uat-snapshot-v1"
    )

    liquidity = client.get(
        "/api/v1/liquidity/workspace", params=params, headers=_headers()
    )
    assert liquidity.json()["cash_forecast"]["minimum_liquidity"] == "€20.0M"
    assert liquidity.json()["stresses"][0]["breach"] is True

    actions = client.get("/api/v1/actions/workspace", params=params, headers=_headers())
    assert actions.json()["metrics"]["items"][0]["metric_id"] == "impact"
    assert actions.json()["actions"][0]["action_id"] == "UAT-ACT-AURELIA-DOWNSIDE"

    capital = client.get("/api/v1/capital/workspace", params=params, headers=_headers())
    assert capital.json()["portfolio"]["liquidity_reserve"] == "€20.0M"
    assert capital.json()["constraints"][0]["status"] == "BREACH"
    assert capital.json()["funding_options"][0]["option_id"] == "RCF-2026"

    governance = client.get(
        "/api/v1/data-governance/workspace", params=params, headers=_headers()
    )
    assert governance.json()["snapshots"][0]["snapshot_id"] == "uat-snapshot-v1"


def test_uat_seed_does_not_bypass_company_scope() -> None:
    client = TestClient(create_app(settings=ApiSettings(environment="uat")))

    response = client.get(
        "/api/v1/planning/workspace",
        params={
            "company_id": "EUROPE",
            "period_id": "2026-08",
            "scenario_id": "base",
        },
        headers=_headers("AURELIA"),
    )

    assert response.status_code == 403


def test_uat_environment_supports_reproducible_be03_risk_and_market_runs() -> None:
    client = TestClient(create_app(settings=ApiSettings(environment="uat")))
    context = {
        "company_id": "AURELIA",
        "period_id": "2026-08",
        "scenario_id": "downside",
    }

    risk_created = client.post(
        "/api/v1/risk/model-runs",
        headers=_headers(),
        json={
            **context,
            "risk_ids": ["UAT-R-ENERGY", "UAT-R-VOLUME"],
            "correlation_matrix": [[1, 0.3], [0.3, 1]],
            "paths": 500,
            "seed": 20260809,
        },
    )
    assert risk_created.status_code == 202, risk_created.text
    risk_run = client.get(
        f"/api/v1/risk/model-runs/{risk_created.json()['run_id']}",
        headers=_headers(),
    )
    assert risk_run.status_code == 200
    assert risk_run.json()["status"] == "succeeded"
    assert risk_run.json()["result"]["seed"] == 20260809
    assert risk_run.json()["source_snapshot_ids"] == ["uat-snapshot-v1"]

    market_created = client.post(
        "/api/v1/market-risk/model-runs",
        headers=_headers(),
        json={
            **context,
            "model_type": "var_es",
            "losses": [float(index) / 100 for index in range(1, 101)],
            "confidence": 0.95,
            "method": "historical",
        },
    )
    assert market_created.status_code == 202, market_created.text
    market_run = client.get(
        f"/api/v1/market-risk/model-runs/{market_created.json()['run_id']}",
        headers=_headers(),
    )
    assert market_run.status_code == 200
    assert market_run.json()["status"] == "succeeded"
    assert market_run.json()["result"]["method"] == "historical"
