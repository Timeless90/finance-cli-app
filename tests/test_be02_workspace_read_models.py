from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.composition import build_container
from cfo_platform.data_foundation import DataSnapshot, FinanceRecord
from cfo_platform.rbac import Principal, Role
from cfo_platform.workspace_integration import WorkspaceProjectionSnapshot


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
    return container


def _headers(companies: str = "ACME") -> dict[str, str]:
    return {
        "X-User": "cfo-user",
        "X-Roles": "cfo",
        "X-Companies": companies,
    }


def _context(container):
    principal = Principal(
        user_id="publisher",
        roles=frozenset({Role.CFO}),
        company_scopes=frozenset({"ACME"}),
    )
    return container.context_catalog_service.resolve(
        principal,
        company_id="ACME",
        period_id="2026-06",
        scenario_id="base",
    )


def _snapshot(
    container,
    *,
    data: dict,
    lineage: dict | None = None,
    projection_version: int = 1,
) -> WorkspaceProjectionSnapshot:
    return WorkspaceProjectionSnapshot(
        context=_context(container),
        as_of=datetime(2026, 8, 8, 11, 0, tzinfo=timezone.utc),
        data=data,
        lineage=lineage or {"generated_at": "2026-08-08T11:00:00Z"},
        assurance={
            "data_freshness": "current",
            "validation_status": "validated",
            "lineage_status": "complete",
        },
        source_snapshot_ids=("snap-1",),
        projection_version=projection_version,
    )


def _published_payloads() -> dict[str, dict]:
    return {
        "planning": {
            "scenarios": [{"scenario_id": "base", "label": "Base"}],
            "active_forecast": {
                "version_id": "fc-1",
                "snapshot_id": "snap-1",
                "assumption_set_id": "assumptions-1",
                "model_version": "forecast-v1",
                "status": "approved",
            },
            "forecast_series": [{"period": "2026-06", "forecast": 120.0}],
            "financial_statement": [{"line_item": "revenue", "forecast": 120.0}],
            "drivers": [{"driver_id": "price", "value": 1.05}],
            "thresholds": [{"metric_id": "ebitda", "status": "green"}],
            "forecast_assurance": {"confidence": 0.91, "bias": 0.02},
        },
        "performance": {
            "metrics": [{"metric_id": "ebitda", "value": 120.0}],
            "kpi_tree": [{"node_id": "ebitda"}],
            "variance_bridge": {"baseline": 110.0, "total": 120.0},
            "trend": [{"period": "2026-06", "value": 120.0}],
            "anomalies": [{"anomaly_id": "anom-1", "status": "reviewed"}],
            "commentary_requirements": [{"metric_id": "revenue", "required": True}],
        },
        "profitability": {
            "metrics": [{"metric_id": "contribution_margin", "value": 0.42}],
            "segments": [{"segment_id": "SEG-A", "revenue": 80.0, "ebitda": 20.0}],
            "margin_waterfall": [{"step": "gross_margin", "value": 45.0}],
            "profitability_matrix": [{"segment_id": "SEG-A", "status": "invest"}],
            "sensitivity_summary": [{"driver": "price", "impact": 4.0}],
            "allocation_assurance": {
                "allocation_version_id": "alloc-1",
                "snapshot_id": "snap-1",
                "reconciled": True,
            },
        },
        "liquidity": {
            "metrics": [{"metric_id": "cash", "value": 75.0}],
            "cash_forecast": {
                "positions": [{"period": "W1", "cash": 75.0}],
                "minimum_liquidity": 50.0,
            },
            "working_capital": [{"metric": "dso", "value": 43.0}],
            "debt": [{"instrument_id": "debt-1", "balance": 25.0}],
            "covenants": [{"covenant_id": "cov-1", "status": "headroom"}],
            "stresses": [{"stress_id": "stress-1", "minimum_cash": 55.0}],
        },
        "risk": {
            "portfolio": {
                "mean_net_loss": 8.0,
                "p95_net_loss": 15.0,
                "expected_shortfall_95": 18.0,
            },
            "percentile_curve": [{"percentile": 0.95, "loss": 15.0}],
            "risks": [{"risk_id": "R-1", "expected_loss": 5.0}],
            "categories": [{"category": "market", "expected_loss": 5.0}],
            "appetite_radar": [{"dimension": "market", "usage": 0.62}],
            "correlation": {"labels": ["R-1"], "matrix": [[1.0]]},
            "scenario": {"scenario_run_id": "scenario-run-1", "cash_at_risk": 12.0},
            "controls": [{"control_id": "C-1", "status": "effective"}],
        },
        "market-risk": {
            "assets": [
                {"asset_id": "EURUSD", "label": "EUR/USD", "asset_class": "fx"},
                {"asset_id": "DAX", "label": "DAX", "asset_class": "equity"},
            ],
            "selected_runs": {
                "volatility_run_id": "vol-1",
                "regime_run_id": "regime-1",
                "dependency_run_id": "dep-1",
                "simulation_run_id": "sim-1",
                "backtest_run_id": "backtest-1",
            },
            "threshold_states": [{"metric": "var_95", "status": "within_limit"}],
        },
        "actions": {
            "metrics": {"expected_cash": 12.0, "realized_cash": 8.0},
            "actions": [
                {
                    "action_id": "A-1",
                    "title": "Pricing action",
                    "expected_cash": 12.0,
                    "realized_cash": 8.0,
                }
            ],
            "benefit_series": [{"period": "2026-06", "realized_cash": 8.0}],
            "dependencies": [{"from_action_id": "A-1", "to_action_id": "A-2"}],
        },
        "capital": {
            "portfolio": {
                "budget": 100.0,
                "committed": 45.0,
                "unallocated": 55.0,
                "expected_portfolio_npv": 22.0,
            },
            "candidates": [{"candidate_id": "P-1", "npv": 12.0, "status": "approved"}],
            "constraints": [{"constraint_id": "budget", "limit": 100.0}],
            "allocation": [{"candidate_id": "P-1", "amount": 30.0}],
            "frontier_points": [{"risk": 0.2, "value": 20.0}],
            "approvals": [{"approval_id": "approval-1", "status": "approved"}],
            "selected_allocation_run_id": "capital-run-1",
        },
        "reporting": {
            "active_report": {
                "report_id": "report-1",
                "template_id": "board",
                "status": "review",
                "current_version_id": "report-version-1",
            },
            "sections": [{"section_id": "summary", "status": "complete"}],
            "versions": [{"version_id": "report-version-1", "status": "review"}],
            "source_pack": [{"source_id": "snap-1", "status": "validated"}],
            "findings": [{"finding_id": "finding-1", "severity": "warning"}],
            "export_targets": [{"format": "pdf", "available": True}],
        },
    }


def test_all_be02_workspaces_return_published_backend_projections() -> None:
    container = _seed_container()
    service = container.workspace_read_model_service

    for workspace, data in _published_payloads().items():
        lineage = {"generated_at": "2026-08-08T11:00:00Z"}
        if workspace == "risk":
            lineage["aggregation_run_id"] = "risk-run-1"
        service.publish_workspace(
            workspace,
            _snapshot(container, data=data, lineage=lineage),
        )

    client = TestClient(create_app(container=container))
    params = {
        "company_id": "ACME",
        "period_id": "2026-06",
        "scenario_id": "base",
    }
    endpoints = {
        "planning": "/api/v1/planning/workspace",
        "performance": "/api/v1/performance/workspace",
        "profitability": "/api/v1/profitability/workspace",
        "liquidity": "/api/v1/liquidity/workspace",
        "risk": "/api/v1/risk/workspace",
        "market-risk": "/api/v1/market-risk/workspace",
        "actions": "/api/v1/actions/workspace",
        "capital": "/api/v1/capital/workspace",
        "reporting": "/api/v1/reporting/workspace",
    }

    for workspace, endpoint in endpoints.items():
        response = client.get(endpoint, params=params, headers=_headers())
        assert response.status_code == 200, (workspace, response.text)
        body = response.json()
        assert body["context"]["company_id"] == "ACME"
        assert body["source_snapshot_ids"] == ["snap-1"]
        assert body["projection_version"] == 1
        assert body["assurance"]["validation_status"] == "validated"

    action_response = client.get(
        "/api/v1/actions/workspace",
        params=params,
        headers=_headers(),
    )
    assert action_response.json()["actions"][0]["action_id"] == "A-1"

    filtered_market = client.get(
        "/api/v1/market-risk/workspace",
        params={**params, "asset_id": "DAX"},
        headers=_headers(),
    )
    assert filtered_market.status_code == 200
    assert [item["asset_id"] for item in filtered_market.json()["assets"]] == ["DAX"]

    reporting = client.get(
        "/api/v1/reporting/workspace",
        params={**params, "report_id": "report-1"},
        headers=_headers(),
    )
    assert reporting.status_code == 200
    assert reporting.json()["active_report"]["report_id"] == "report-1"

    alias = client.get(
        "/api/v1/reports/workspace",
        params=params,
        headers=_headers(),
    )
    assert alias.status_code == 200


def test_be02_selectors_scope_and_unpublished_state_fail_closed() -> None:
    container = _seed_container()
    service = container.workspace_read_model_service
    service.publish_workspace(
        "risk",
        _snapshot(
            container,
            data={"portfolio": {"p95_net_loss": 15.0}},
            lineage={"aggregation_run_id": "risk-run-1"},
        ),
    )
    service.publish_workspace(
        "market-risk",
        _snapshot(
            container,
            data={"assets": [{"asset_id": "EURUSD"}], "selected_runs": {}},
        ),
    )
    service.publish_workspace(
        "reporting",
        _snapshot(
            container,
            data={"active_report": {"report_id": "report-1"}},
        ),
    )
    client = TestClient(create_app(container=container))
    params = {
        "company_id": "ACME",
        "period_id": "2026-06",
        "scenario_id": "base",
    }

    assert client.get(
        "/api/v1/risk/workspace",
        params=params,
        headers=_headers("OTHER"),
    ).status_code == 403

    assert client.get(
        "/api/v1/risk/workspace",
        params={**params, "aggregation_run_id": "risk-run-2"},
        headers=_headers(),
    ).status_code == 404

    assert client.get(
        "/api/v1/market-risk/workspace",
        params={**params, "asset_id": "DAX"},
        headers=_headers(),
    ).status_code == 404

    assert client.get(
        "/api/v1/reporting/workspace",
        params={**params, "report_id": "report-2"},
        headers=_headers(),
    ).status_code == 404

    unpublished = client.get(
        "/api/v1/planning/workspace",
        params=params,
        headers=_headers(),
    )
    assert unpublished.status_code == 404
    assert unpublished.json()["detail"] == "planning workspace snapshot not found"


def test_workspace_projection_versions_are_monotonic() -> None:
    container = _seed_container()
    service = container.workspace_read_model_service
    first = _snapshot(
        container,
        data={"metrics": [{"metric_id": "cash", "value": 75.0}]},
    )
    service.publish_workspace("liquidity", first)

    with pytest.raises(ValueError, match="projection_version must increase"):
        service.publish_workspace("liquidity", first)

    service.publish_workspace(
        "liquidity",
        _snapshot(
            container,
            data={"metrics": [{"metric_id": "cash", "value": 80.0}]},
            projection_version=2,
        ),
    )
    client = TestClient(create_app(container=container))
    response = client.get(
        "/api/v1/liquidity/workspace",
        params={
            "company_id": "ACME",
            "period_id": "2026-06",
            "scenario_id": "base",
        },
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json()["projection_version"] == 2
    assert response.json()["metrics"][0]["value"] == 80.0


def test_be02_workspace_contracts_are_exposed_in_openapi() -> None:
    schema = TestClient(create_app()).get("/openapi.json").json()
    expected_paths = {
        "/api/v1/planning/workspace",
        "/api/v1/performance/workspace",
        "/api/v1/profitability/workspace",
        "/api/v1/liquidity/workspace",
        "/api/v1/risk/workspace",
        "/api/v1/market-risk/workspace",
        "/api/v1/actions/workspace",
        "/api/v1/capital/workspace",
        "/api/v1/reporting/workspace",
    }
    assert expected_paths <= set(schema["paths"])
    assert "/api/v1/reports/workspace" not in schema["paths"]
