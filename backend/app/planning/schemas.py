from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.planning.forecast_thresholds import (
    ThresholdDirection,
)
from app.planning.planning import (
    ForecastHorizon,
)
from app.planning.probabilistic_forecast import (
    ForecastDistribution,
)


class RevenueDriverPayload(BaseModel):
    volume: Decimal
    unit_price: Decimal
    conversion_rate: Decimal = Decimal(1)
    mix_factor: Decimal = Decimal(1)


class CostDriverPayload(BaseModel):
    variable_cost_rate: Decimal
    fixed_operating_cost: Decimal
    personnel_cost: Decimal
    depreciation: Decimal = Decimal(0)


class WorkingCapitalPayload(BaseModel):
    dso_days: Decimal
    dpo_days: Decimal
    inventory_days: Decimal


class PlanningPeriodPayload(BaseModel):
    period: str
    revenue_drivers: list[RevenueDriverPayload]
    cost_driver: CostDriverPayload
    working_capital: WorkingCapitalPayload
    capex: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(0)
    opening_cash: Decimal = Decimal(0)
    opening_equity: Decimal = Decimal(0)
    opening_debt: Decimal = Decimal(0)


class ForecastVersionPayload(BaseModel):
    version_id: str
    as_of_period: str
    horizon: ForecastHorizon
    snapshot_id: str
    scenario_id: str
    assumption_set_id: str
    model_version: str


class CreateForecastRequest(BaseModel):
    version: ForecastVersionPayload
    periods: list[PlanningPeriodPayload]
    predecessor_version_id: str | None = None


class ProbabilisticRequest(BaseModel):
    deterministic_values: list[float]
    historical_residuals: list[float]
    paths: int = Field(default=10_000, ge=100)
    seed: int = 42
    method: ForecastDistribution = ForecastDistribution.STUDENT_T
    block_length: int = 3
    student_df: float = 6.0


class BacktestObservationPayload(BaseModel):
    origin_index: int
    horizon: int
    forecast: float
    actual: float
    lower: float | None = None
    upper: float | None = None


class BacktestRequest(BaseModel):
    actuals: list[float]
    forecasts: list[BacktestObservationPayload]


class ThresholdRequest(BaseModel):
    threshold_id: str
    kpi: str
    target: float
    warning: float
    direction: ThresholdDirection
    deterministic_value: float
    simulated_values: list[float] | None = None
