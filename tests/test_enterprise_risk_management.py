from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.risk_management import (
    FinancialStatement,
    FrequencyModel,
    InMemoryRiskRegister,
    LimitScope,
    LimitStatus,
    RiskAggregationEngine,
    RiskAppetiteEngine,
    RiskCategory,
    RiskControl,
    RiskLimit,
    RiskPlanMapping,
    RiskQuantification,
    RiskQuantificationEngine,
    RiskRecord,
    RiskRegisterService,
    RiskReportingService,
    RiskToPlanEngine,
    SeverityDistribution,
)


def _risk(
    risk_id: str,
    *,
    probability: str = "0.25",
    losses: tuple[str, ...] = ("100000", "250000", "500000"),
    control_effectiveness: str = "0.40",
    double_count_group: str | None = None,
) -> RiskRecord:
    controls = ()
    if Decimal(control_effectiveness) > 0:
        controls = (
            RiskControl(
                control_id=f"CTRL-{risk_id}",
                name="Primary mitigation",
                owner="Risk Owner",
                effectiveness=Decimal(control_effectiveness),
                annual_cost=Decimal("10000"),
            ),
        )
    return RiskRecord(
        risk_id=risk_id,
        title=f"Risk {risk_id}",
        cause="External or operational driver",
        event="Financial loss event",
        owner="Risk Owner",
        category=RiskCategory.OPERATIONAL,
        horizon_months=12,
        quantification=RiskQuantification(
            distribution=SeverityDistribution.EMPIRICAL,
            frequency_model=FrequencyModel.BERNOULLI,
            occurrence_probability=Decimal(probability),
            empirical_losses=tuple(Decimal(value) for value in losses),
        ),
        controls=controls,
        double_count_group=double_count_group,
    )


def test_risk_register_and_expected_loss_separate_gross_and_net() -> None:
    register = RiskRegisterService(InMemoryRiskRegister())
    risk = _risk("R-001", probability="0.20", control_effectiveness="0.50")
    register.register(risk)

    assert register.get("R-001") == risk
    assert register.list() == (risk,)

    engine = RiskQuantificationEngine()
    gross = engine.expected_gross_loss(risk)
    mitigation = engine.mitigation(risk, gross)

    assert gross == Decimal("56666.66666666666666666666666")
    assert mitigation.residual_loss == gross * Decimal("0.50")
    assert mitigation.avoided_loss == gross * Decimal("0.50")
    assert mitigation.annual_control_cost == Decimal("10000")


def test_supported_severity_models_have_valid_expected_values() -> None:
    engine = RiskQuantificationEngine()
    lognormal = RiskQuantification(
        distribution=SeverityDistribution.LOGNORMAL,
        lognormal_mu=Decimal("10"),
        lognormal_sigma=Decimal("0.5"),
    )
    pareto = RiskQuantification(
        distribution=SeverityDistribution.PARETO,
        pareto_scale=Decimal("100000"),
        pareto_shape=Decimal("2.5"),
    )
    custom = RiskQuantification(
        distribution=SeverityDistribution.CUSTOM,
        custom_losses=(Decimal("10"), Decimal("20"), Decimal("30")),
    )

    assert engine.expected_severity(lognormal) > 0
    assert engine.expected_severity(pareto) == Decimal("166666.6666666666666666666667")
    assert engine.expected_severity(custom) == Decimal("20")


def test_monte_carlo_aggregation_is_reproducible_and_traceable() -> None:
    risks = (_risk("R-001"), _risk("R-002", probability="0.15"))
    correlations = (
        (Decimal("1"), Decimal("0.30")),
        (Decimal("0.30"), Decimal("1")),
    )
    engine = RiskAggregationEngine()

    first = engine.aggregate(risks, correlations, paths=2_000, seed=2026)
    second = engine.aggregate(risks, correlations, paths=2_000, seed=2026)

    assert first == second
    assert first.mean_gross_loss >= first.mean_net_loss
    assert first.p99_net_loss >= first.p95_net_loss >= first.p90_net_loss
    assert first.expected_shortfall_95 >= first.p95_net_loss
    assert {item.risk_id for item in first.contributions} == {"R-001", "R-002"}
    assert sum((item.expected_loss_share for item in first.contributions), Decimal("0")) == pytest.approx(
        Decimal("1"), abs=Decimal("0.0000000001")
    )


def test_correlation_and_double_counting_controls_are_enforced() -> None:
    engine = RiskAggregationEngine()
    risks = (_risk("R-001"), _risk("R-002"))

    with pytest.raises(ValueError, match="symmetric"):
        engine.aggregate(
            risks,
            ((Decimal("1"), Decimal("0.8")), (Decimal("0.2"), Decimal("1"))),
            paths=100,
        )

    duplicate_group = (
        _risk("R-003", double_count_group="supplier-outage"),
        _risk("R-004", double_count_group="supplier-outage"),
    )
    with pytest.raises(ValueError, match="double counting"):
        engine.aggregate(
            duplicate_group,
            ((Decimal("1"), Decimal("0")), (Decimal("0"), Decimal("1"))),
            paths=100,
        )


def test_risk_appetite_limit_states_are_explicit() -> None:
    engine = RiskAppetiteEngine()
    limit = RiskLimit(
        limit_id="L-EBITDA",
        scope=LimitScope.KPI,
        scope_key="EBITDA-at-risk",
        maximum=Decimal("1000000"),
        warning_ratio=Decimal("0.80"),
    )

    assert engine.evaluate(limit, Decimal("500000")).status == LimitStatus.HEALTHY
    assert engine.evaluate(limit, Decimal("850000")).status == LimitStatus.WARNING
    breached = engine.evaluate(limit, Decimal("1200000"))
    assert breached.status == LimitStatus.BREACHED
    assert breached.headroom == Decimal("-200000")


def test_risk_to_plan_integration_blocks_duplicate_impact_keys() -> None:
    engine = RiskToPlanEngine()
    mapping = RiskPlanMapping(
        risk_id="R-001",
        statement=FinancialStatement.INCOME_STATEMENT,
        metric="EBITDA",
        period="2027-01",
        loss_factor=Decimal("1"),
        impact_key="risk:R-001:ebitda:2027-01",
    )
    impacts = engine.integrate({"R-001": Decimal("250000")}, (mapping,))

    assert impacts[0].amount == Decimal("-250000")
    with pytest.raises(ValueError, match="duplicate plan impact"):
        engine.integrate({"R-001": Decimal("250000")}, (mapping, mapping))


def test_reporting_contains_top_risks_heatmap_methodology_and_mitigation() -> None:
    risks = (_risk("R-001"), _risk("R-002", probability="0.40"))
    correlations = (
        (Decimal("1"), Decimal("0.10")),
        (Decimal("0.10"), Decimal("1")),
    )
    portfolio = RiskAggregationEngine().aggregate(risks, correlations, paths=1_000, seed=7)
    report = RiskReportingService().build(risks, portfolio, top_n=1)

    assert len(report.top_risks) == 1
    assert len(report.heatmap) == 2
    assert report.mitigation_total > 0
    assert any("Copula" in item for item in report.methodology)


def test_risk_api_register_aggregation_limits_plan_and_reporting() -> None:
    with TestClient(create_app()) as client:
        risk_payload = {
            "risk_id": "R-API-1",
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
            "controls": [
                {
                    "control_id": "CTRL-1",
                    "name": "Dual sourcing",
                    "owner": "Procurement",
                    "effectiveness": "0.35",
                    "annual_cost": "25000",
                    "status": "active",
                }
            ],
        }
        register_response = client.post("/api/v1/risk/register", json=risk_payload)
        assert register_response.status_code == 200

        aggregation_response = client.post(
            "/api/v1/risk/aggregation",
            json={
                "risk_ids": ["R-API-1"],
                "correlation_matrix": [["1"]],
                "paths": 500,
                "seed": 123,
            },
        )
        assert aggregation_response.status_code == 200
        assert aggregation_response.json()["portfolio"]["seed"] == 123

        limit_response = client.post(
            "/api/v1/risk/limits/evaluate",
            json={
                "limit_id": "L-1",
                "scope": "risk_capacity",
                "scope_key": "group",
                "maximum": "1000000",
                "warning_ratio": "0.8",
                "exposure": "850000",
            },
        )
        assert limit_response.status_code == 200
        assert limit_response.json()["result"]["status"] == "warning"

        plan_response = client.post(
            "/api/v1/risk/plan/integrate",
            json={
                "losses": {"R-API-1": "250000"},
                "mappings": [
                    {
                        "risk_id": "R-API-1",
                        "statement": "cash_flow",
                        "metric": "operating_cash_flow",
                        "period": "2027-01",
                        "loss_factor": "1",
                    }
                ],
            },
        )
        assert plan_response.status_code == 200
        assert Decimal(plan_response.json()["impacts"][0]["amount"]) == Decimal("-250000")

        report_response = client.post(
            "/api/v1/risk/reports",
            json={
                "risk_ids": ["R-API-1"],
                "correlation_matrix": [["1"]],
                "paths": 500,
                "seed": 123,
                "top_n": 1,
            },
        )
        assert report_response.status_code == 200
        assert report_response.json()["report"]["top_risks"][0]["risk_id"] == "R-API-1"
