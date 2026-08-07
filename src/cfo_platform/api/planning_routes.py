from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from cfo_platform.forecast_backtesting import ForecastObservation, RollingOriginBacktester
from cfo_platform.forecast_thresholds import (
    ForecastThreshold,
    GoalThresholdEngine,
    ThresholdDirection,
)
from cfo_platform.planning import (
    CostDriver,
    ForecastHorizon,
    PlanningPeriodInput,
    RevenueDriver,
    RollingForecastVersion,
    WorkingCapitalDriver,
)
from cfo_platform.planning_workflow import RollingForecastService
from cfo_platform.probabilistic_forecast import (
    ForecastDistribution,
    ProbabilisticForecastEngine,
    ProbabilisticForecastRequest,
)


class RevenueDriverPayload(BaseModel):
    volume: Decimal
    unit_price: Decimal
    conversion_rate: Decimal = Decimal("1")
    mix_factor: Decimal = Decimal("1")


class CostDriverPayload(BaseModel):
    variable_cost_rate: Decimal
    fixed_operating_cost: Decimal
    personnel_cost: Decimal
    depreciation: Decimal = Decimal("0")


class WorkingCapitalPayload(BaseModel):
    dso_days: Decimal
    dpo_days: Decimal
    inventory_days: Decimal


class PlanningPeriodPayload(BaseModel):
    period: str
    revenue_drivers: list[RevenueDriverPayload]
    cost_driver: CostDriverPayload
    working_capital: WorkingCapitalPayload
    capex: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0")
    opening_cash: Decimal = Decimal("0")
    opening_equity: Decimal = Decimal("0")
    opening_debt: Decimal = Decimal("0")


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


def build_planning_router(
    workflow: RollingForecastService,
    probabilistic_engine: ProbabilisticForecastEngine,
    backtester: RollingOriginBacktester,
    threshold_engine: GoalThresholdEngine,
) -> APIRouter:
    router = APIRouter(prefix="/planning", tags=["planning"])

    @router.post("/forecasts")
    def create_forecast(payload: CreateForecastRequest) -> dict[str, Any]:
        try:
            forecast = workflow.create(
                version=_version(payload.version),
                period_inputs=tuple(_period(period) for period in payload.periods),
                predecessor_version_id=payload.predecessor_version_id,
            )
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {
            "version": asdict(forecast.version),
            "predecessor_version_id": forecast.predecessor_version_id,
            "results": [asdict(result) for result in forecast.results],
        }

    @router.get("/forecasts/{version_id}")
    def get_forecast(version_id: str) -> dict[str, Any]:
        try:
            forecast = workflow.get(version_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="forecast not found") from exc
        return {
            "version": asdict(forecast.version),
            "predecessor_version_id": forecast.predecessor_version_id,
            "results": [asdict(result) for result in forecast.results],
        }

    @router.post("/probabilistic")
    def probabilistic(payload: ProbabilisticRequest) -> dict[str, Any]:
        try:
            result = probabilistic_engine.generate(
                ProbabilisticForecastRequest(
                    deterministic_values=tuple(payload.deterministic_values),
                    historical_residuals=tuple(payload.historical_residuals),
                    paths=payload.paths,
                    seed=payload.seed,
                    method=payload.method,
                    block_length=payload.block_length,
                    student_df=payload.student_df,
                )
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return asdict(result)

    @router.post("/backtests")
    def backtest(payload: BacktestRequest) -> dict[str, Any]:
        try:
            metrics = backtester.evaluate(
                payload.actuals,
                tuple(ForecastObservation(**item.model_dump()) for item in payload.forecasts),
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return asdict(metrics)

    @router.post("/thresholds/evaluate")
    def evaluate_threshold(payload: ThresholdRequest) -> dict[str, Any]:
        try:
            evaluation = threshold_engine.evaluate(
                ForecastThreshold(
                    threshold_id=payload.threshold_id,
                    kpi=payload.kpi,
                    target=payload.target,
                    warning=payload.warning,
                    direction=payload.direction,
                ),
                payload.deterministic_value,
                payload.simulated_values,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return asdict(evaluation)

    return router


def _version(payload: ForecastVersionPayload) -> RollingForecastVersion:
    return RollingForecastVersion(**payload.model_dump())


def _period(payload: PlanningPeriodPayload) -> PlanningPeriodInput:
    return PlanningPeriodInput(
        period=payload.period,
        revenue_drivers=tuple(RevenueDriver(**item.model_dump()) for item in payload.revenue_drivers),
        cost_driver=CostDriver(**payload.cost_driver.model_dump()),
        working_capital=WorkingCapitalDriver(**payload.working_capital.model_dump()),
        capex=payload.capex,
        tax_rate=payload.tax_rate,
        opening_cash=payload.opening_cash,
        opening_equity=payload.opening_equity,
        opening_debt=payload.opening_debt,
    )
