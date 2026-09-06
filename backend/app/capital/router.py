from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from app.capital.capital_allocation import (
    CapitalPortfolioOptimizer,
    CapitalProject,
    FundingOption,
    FundingScenarioEngine,
    MonteCarloNpvEngine,
    PortfolioConstraints,
    ProjectValuationService,
)
from app.capital.schemas import (
    FundingOptionPayload,
    FundingRequest,
    MonteCarloRequest,
    PortfolioConstraintsPayload,
    PortfolioRequest,
    ProjectPayload,
    ProjectValuationRequest,
)


def _project(payload: ProjectPayload) -> CapitalProject:
    return CapitalProject(
        project_id=payload.project_id,
        name=payload.name,
        initial_investment=payload.initial_investment,
        cash_flows=tuple(payload.cash_flows),
        annual_nopat=tuple(payload.annual_nopat),
        terminal_value=payload.terminal_value,
        strategic_score=payload.strategic_score,
        cash_headroom_impact=payload.cash_headroom_impact,
        leverage_delta=payload.leverage_delta,
        interest_cover_delta=payload.interest_cover_delta,
    )


def build_capital_router(
    valuation_service: ProjectValuationService,
    monte_carlo_engine: MonteCarloNpvEngine,
    portfolio_optimizer: CapitalPortfolioOptimizer,
    funding_engine: FundingScenarioEngine,
) -> APIRouter:
    router = APIRouter(prefix="/capital", tags=["capital-allocation"])

    @router.post("/projects/value")
    def value_project(request: ProjectValuationRequest) -> dict[str, object]:
        result = valuation_service.evaluate(
            _project(request.project), request.discount_rate
        )
        return asdict(result)

    @router.post("/projects/monte-carlo")
    def monte_carlo(request: MonteCarloRequest) -> dict[str, object]:
        result = monte_carlo_engine.simulate(
            _project(request.project),
            discount_rate=request.discount_rate,
            paths=request.paths,
            seed=request.seed,
            cash_flow_volatility=request.cash_flow_volatility,
            risk_event_probability=request.risk_event_probability,
            risk_event_impact=request.risk_event_impact,
            scenario_multiplier=request.scenario_multiplier,
        )
        return asdict(result)

    @router.post("/portfolio/optimize")
    def optimize_portfolio(request: PortfolioRequest) -> dict[str, object]:
        constraints = PortfolioConstraints(**request.constraints.model_dump())
        result = portfolio_optimizer.optimize(
            [_project(project) for project in request.projects],
            risk_adjusted_npvs=request.risk_adjusted_npvs,
            constraints=constraints,
            strategic_weight=request.strategic_weight,
        )
        return asdict(result)

    @router.post("/funding/evaluate")
    def evaluate_funding(request: FundingRequest) -> dict[str, object]:
        option = FundingOption(**request.option.model_dump())
        result = funding_engine.evaluate(
            option,
            base_debt=request.base_debt,
            base_ebitda=request.base_ebitda,
            base_interest_expense=request.base_interest_expense,
            maximum_leverage=request.maximum_leverage,
        )
        return asdict(result)

    return router


__all__ = [
    "FundingOptionPayload",
    "FundingRequest",
    "MonteCarloRequest",
    "PortfolioConstraintsPayload",
    "PortfolioRequest",
    "ProjectPayload",
    "ProjectValuationRequest",
    "_project",
    "build_capital_router",
]
