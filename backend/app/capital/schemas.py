from __future__ import annotations

from pydantic import BaseModel, Field


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
