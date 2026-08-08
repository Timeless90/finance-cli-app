from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.composition import build_container
from cfo_platform.data_foundation import DataSnapshot, FinanceRecord
from cfo_platform.governance_catalog import Assumption, ScenarioKind
from cfo_platform.rbac import Principal, Role
from cfo_platform.workspace_integration import CommandCenterSnapshot


def _seed_context():
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
        FinanceRecord(
            company="ACME",
            account="cash",
            period="2026-05",
            scenario="base",
            value=Decimal("50"),
            currency="EUR",
        ),
        FinanceRecord(
            company="OTHER",
            account="revenue",
            period="2026-06",
            scenario="base",
            value=Decimal("80"),
            currency="USD",
        ),
    )
    container.data_snapshot_repository.save(
        DataSnapshot(
            snapshot_id="snap-1",
            content_hash="hash-1",
            row_count=len(records),
            records=records,
        )
    )
    governed = container.scenario_service.create(
        name="Downside",
        kind=ScenarioKind.DOWNSIDE,
        assumptions=(
            Assumption(
                assumption_id="revenue_growth",
                name="Revenue growth",
                value=-0.10,
                owner="planner",
            ),
        ),
        actor="planner",
    )
    return container, governed.scenario_id


def _headers(companies: str = "ACME") -> dict[str, str]:
    return {
        "X-User": "cfo-user",
        "X-Roles": "cfo",
        "X-Companies": companies,
    }


def test_context_endpoints_are_scoped_and_queryable() -> None:
    container, governed_scenario_id = _seed_context()
    client = TestClient(create_app(container=container))

    principal = client.get("/api/v1/context/principal", headers=_headers())
    assert principal.status_code == 200
    assert principal.json()["user_id"] == "cfo-user"
    assert principal.json()["company_scopes"] == ["ACME"]
    assert "read_data" in principal.json()["permissions"]

    companies = client.get("/api/v1/context/companies", headers=_headers())
    assert companies.status_code == 200
    assert companies.json() == [
        {
            "company_id": "ACME",
            "label": "ACME",
            "currency": "EUR",
            "data_available": True,
        }
    ]

    periods = client.get(
        "/api/v1/context/periods",
        params={"company_id": "ACME"},
        headers=_headers(),
    )
    assert periods.status_code == 200
    assert [item["period_id"] for item in periods.json()] == [
        "2026-06",
        "2026-05",
    ]

    scenarios = client.get(
        "/api/v1/context/scenarios",
        params={"company_id": "ACME", "period_id": "2026-06"},
        headers=_headers(),
    )
    assert scenarios.status_code == 200
    ids = {item["scenario_id"] for item in scenarios.json()}
    assert "base" in ids
    assert governed_scenario_id in ids

    resolved = client.get(
        "/api/v1/context/resolve",
        params={
            "company_id": "ACME",
            "period_id": "2026-06",
            "scenario_id": "base",
        },
        headers=_headers(),
    )
    assert resolved.status_code == 200
    assert resolved.json()["currency"] == "EUR"

    forbidden = client.get(
        "/api/v1/context/periods",
        params={"company_id": "OTHER"},
        headers=_headers(),
    )
    assert forbidden.status_code == 403


def test_context_returns_not_found_for_unknown_period_or_scenario() -> None:
    container, _ = _seed_context()
    client = TestClient(create_app(container=container))

    missing_period = client.get(
        "/api/v1/context/scenarios",
        params={"company_id": "ACME", "period_id": "2027-01"},
        headers=_headers(),
    )
    assert missing_period.status_code == 404

    missing_scenario = client.get(
        "/api/v1/context/resolve",
        params={
            "company_id": "ACME",
            "period_id": "2026-06",
            "scenario_id": "missing",
        },
        headers=_headers(),
    )
    assert missing_scenario.status_code == 404


def test_command_center_returns_only_published_backend_read_models() -> None:
    container, _ = _seed_context()
    principal = Principal(
        user_id="publisher",
        roles=frozenset({Role.CFO}),
        company_scopes=frozenset({"ACME"}),
    )
    context = container.context_catalog_service.resolve(
        principal,
        company_id="ACME",
        period_id="2026-06",
        scenario_id="base",
    )
    container.workspace_read_model_service.publish_command_center(
        CommandCenterSnapshot(
            context=context,
            as_of=datetime(2026, 8, 8, 9, 0, tzinfo=timezone.utc),
            metrics=(
                {
                    "metric_id": "ebitda",
                    "label": "EBITDA",
                    "value": 120.0,
                    "unit": "EURm",
                },
            ),
            forecast={"p10": 100.0, "p50": 120.0, "p90": 140.0},
            liquidity={"cash": 75.0, "status": "healthy"},
            risk={"score": 0.32, "appetite_usage": 0.64},
            variance_drivers=(
                {"driver": "price", "impact": 8.0},
            ),
            actions=(
                {"action_id": "A-1", "status": "open"},
            ),
            briefing="EBITDA remains above the base-plan threshold.",
            assurance={
                "data_freshness": "current",
                "coverage": "complete",
                "model_status": "approved",
                "lineage_status": "complete",
            },
            source_snapshot_ids=("snap-1",),
        )
    )
    client = TestClient(create_app(container=container))

    response = client.get(
        "/api/v1/command-center/overview",
        params={
            "company_id": "ACME",
            "period_id": "2026-06",
            "scenario_id": "base",
        },
        headers=_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["context"]["company_id"] == "ACME"
    assert payload["metrics"][0]["metric_id"] == "ebitda"
    assert payload["source_snapshot_ids"] == ["snap-1"]
    assert payload["projection_version"] == 1

    missing = client.get(
        "/api/v1/command-center/overview",
        params={
            "company_id": "ACME",
            "period_id": "2026-05",
            "scenario_id": "base",
        },
        headers=_headers(),
    )
    assert missing.status_code == 404
    assert missing.json()["detail"] == "command center snapshot not found"


def test_workspace_contracts_are_part_of_openapi() -> None:
    client = TestClient(create_app())
    schema = client.get("/openapi.json").json()

    assert "/api/v1/context/principal" in schema["paths"]
    assert "/api/v1/context/companies" in schema["paths"]
    assert "/api/v1/context/periods" in schema["paths"]
    assert "/api/v1/context/scenarios" in schema["paths"]
    assert "/api/v1/context/resolve" in schema["paths"]
    assert "/api/v1/command-center/overview" in schema["paths"]
