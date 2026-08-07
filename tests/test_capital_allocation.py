from __future__ import annotations

import math

from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.capital_allocation import (
    CapitalPortfolioOptimizer,
    CapitalProject,
    FundingOption,
    FundingScenarioEngine,
    MonteCarloNpvEngine,
    PortfolioConstraints,
    ProjectValuationService,
)


def _reference_project() -> CapitalProject:
    return CapitalProject(
        project_id="P1",
        name="Reference",
        initial_investment=1000.0,
        cash_flows=(600.0, 600.0),
        annual_nopat=(150.0, 170.0),
    )


def test_reference_project_npv_irr_roic_and_payback() -> None:
    result = ProjectValuationService().evaluate(_reference_project(), 0.10)

    assert math.isclose(result.npv, 41.32231404958668, rel_tol=1e-9)
    assert result.irr is not None
    assert math.isclose(result.irr, 0.1306623863, rel_tol=1e-8)
    assert result.roic is not None
    assert math.isclose(result.roic, 0.16, rel_tol=1e-12)
    assert result.payback_years is not None
    assert math.isclose(result.payback_years, 1.6666666667, rel_tol=1e-8)


def test_monte_carlo_npv_is_reproducible() -> None:
    engine = MonteCarloNpvEngine()
    first = engine.simulate(
        _reference_project(),
        discount_rate=0.10,
        paths=2000,
        seed=7,
        cash_flow_volatility=0.20,
        risk_event_probability=0.10,
        risk_event_impact=-0.25,
    )
    second = engine.simulate(
        _reference_project(),
        discount_rate=0.10,
        paths=2000,
        seed=7,
        cash_flow_volatility=0.20,
        risk_event_probability=0.10,
        risk_event_impact=-0.25,
    )

    assert first == second
    assert first.p10 <= first.p50 <= first.p90
    assert 0.0 <= first.probability_negative_npv <= 1.0


def test_portfolio_optimizer_never_breaks_constraints() -> None:
    projects = [
        CapitalProject(
            project_id="A",
            name="A",
            initial_investment=50.0,
            cash_flows=(30.0, 30.0),
            cash_headroom_impact=10.0,
            leverage_delta=0.10,
            interest_cover_delta=-0.20,
        ),
        CapitalProject(
            project_id="B",
            name="B",
            initial_investment=70.0,
            cash_flows=(50.0, 50.0),
            cash_headroom_impact=20.0,
            leverage_delta=0.20,
            interest_cover_delta=-0.30,
        ),
        CapitalProject(
            project_id="C",
            name="C",
            initial_investment=40.0,
            cash_flows=(20.0, 30.0),
            cash_headroom_impact=5.0,
            leverage_delta=0.05,
            interest_cover_delta=-0.10,
        ),
    ]
    constraints = PortfolioConstraints(
        budget=100.0,
        opening_cash_headroom=120.0,
        minimum_cash_headroom=50.0,
        base_leverage=2.0,
        maximum_leverage=2.25,
        base_interest_cover=4.0,
        minimum_interest_cover=3.5,
    )
    result = CapitalPortfolioOptimizer().optimize(
        projects,
        risk_adjusted_npvs={"A": 35.0, "B": 60.0, "C": 25.0},
        constraints=constraints,
    )

    assert result.constraints_satisfied is True
    assert result.total_investment <= constraints.budget
    assert result.ending_cash_headroom >= constraints.minimum_cash_headroom
    assert result.ending_leverage <= constraints.maximum_leverage
    assert result.ending_interest_cover >= constraints.minimum_interest_cover
    assert result.selected_project_ids == ("B",)


def test_funding_scenario_integrates_cash_and_covenants() -> None:
    result = FundingScenarioEngine().evaluate(
        FundingOption(
            option_id="TERM-A",
            amount=200.0,
            annual_rate=0.05,
            term_years=4,
            upfront_fee=2.0,
        ),
        base_debt=300.0,
        base_ebitda=250.0,
        base_interest_expense=15.0,
        maximum_leverage=2.5,
    )

    assert result.net_proceeds == 198.0
    assert result.annual_interest == 10.0
    assert result.annual_principal == 50.0
    assert result.annual_debt_service == 60.0
    assert result.leverage_after == 2.0
    assert result.interest_cover_after == 10.0
    assert result.covenant_headroom == 0.5


def test_capital_api_contracts() -> None:
    client = TestClient(create_app())
    project = {
        "project_id": "P1",
        "name": "Reference",
        "initial_investment": 1000.0,
        "cash_flows": [600.0, 600.0],
        "annual_nopat": [150.0, 170.0],
    }

    valuation = client.post(
        "/api/v1/capital/projects/value",
        json={"project": project, "discount_rate": 0.10},
    )
    assert valuation.status_code == 200
    assert valuation.json()["project_id"] == "P1"

    simulation = client.post(
        "/api/v1/capital/projects/monte-carlo",
        json={"project": project, "discount_rate": 0.10, "paths": 500, "seed": 3},
    )
    assert simulation.status_code == 200
    assert simulation.json()["paths"] == 500

    funding = client.post(
        "/api/v1/capital/funding/evaluate",
        json={
            "option": {
                "option_id": "TERM-A",
                "amount": 200.0,
                "annual_rate": 0.05,
                "term_years": 4,
            },
            "base_debt": 300.0,
            "base_ebitda": 250.0,
            "base_interest_expense": 15.0,
            "maximum_leverage": 2.5,
        },
    )
    assert funding.status_code == 200
    assert funding.json()["leverage_after"] == 2.0
