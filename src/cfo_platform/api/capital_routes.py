from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from cfo_platform.capital_allocation import (
    CapitalPortfolioOptimizer,
    CapitalProject,
    FundingOption,
    FundingScenarioEngine,
    MonteCarloNpvEngine,
    PortfolioConstraints,
    ProjectValuationService,
)


class ProjectPayload(BaseModel):
    project_id: str
    name: str
    initial_investment: float = Field(gt=0)
    cash_flows: list[float] = Field(min_length=1)
    annual_nopat: list[float] = []
    terminal_value: float = 0.0
    strategic_score: float = 0.0
    cash_headroom_impact: float = 0.0
    leverage_delta: float = 0.0
    interest_cover_delta: float = 0.0


class ProjectValuationRequest(BaseModel):
    project: ProjectPayload
    discount_rate: float


class MonteCarloRequest(ProjectValuationRequest):
    paths: int = Field(default=10_000, ge=100)
    seed: int = 42
    cash_flow_volatility: float = Field(default=0.15, ge=0.0)
    risk_event_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_event_impact: float = 0.0
    scenario_multiplier: float = Field(default=1.0, gt=0.0)


class PortfolioConstraintsPayload(BaseModel):
    budget: float = Field(ge=0.0)
    opening_cash_headroom: float
    minimum_cash_headroom: float
    base_leverage: float
    maximum_leverage: float
    base_interest_cover: float
    minimum_interest_cover: float


class PortfolioRequest(BaseModel):
    projects: list[ProjectPayload]
    risk_adjusted_npvs: dict[str, float]
    constraints: PortfolioConstraintsPayload
    strategic_weight: float = 0.0


class FundingOptionPayload(BaseModel):
    option_id: str
    amount: float = Field(gt=0.0)
    annual_rate: float = Field(ge=0.0)
    term_years: int = Field(gt=0)
    upfront_fee: float = Field(default=0.0, ge=0.0)
    amortizing: bool = True


class FundingRequest(BaseModel):
    option: FundingOptionPayload
    base_debt: float = Field(ge=0.0)
    base_ebitda: float = Field(gt=0.0)
    base_interest_expense: float = Field(ge=0.0)
    maximum_leverage: float


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
        result = valuation_service.evaluate(_project(request.project), request.discount_rate)
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
