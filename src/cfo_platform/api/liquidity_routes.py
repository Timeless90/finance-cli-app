from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from cfo_platform.liquidity_management import (
    CashAccuracyObservation,
    CashForecastAccuracyService,
    CovenantDefinition,
    CovenantDirection,
    CovenantEngine,
    DebtInstrument,
    DebtScheduleEngine,
    LiquidityStressEngine,
    LiquidityStressScenario,
    MonthlyLiquidityForecast,
    MonthlyLiquidityInput,
    ThirteenWeekCashForecast,
    WeeklyCashFlow,
    WorkingCapitalAssumptions,
    WorkingCapitalModel,
)


class WeeklyCashFlowPayload(BaseModel):
    week: int = Field(ge=1, le=13)
    bank_opening: Decimal
    ar_collections: Decimal = Decimal("0")
    ap_payments: Decimal = Decimal("0")
    payroll: Decimal = Decimal("0")
    taxes: Decimal = Decimal("0")
    capex: Decimal = Decimal("0")
    financing: Decimal = Decimal("0")
    other_cash_flow: Decimal = Decimal("0")


class ThirteenWeekForecastRequest(BaseModel):
    flows: list[WeeklyCashFlowPayload]


class MonthlyLiquidityPayload(BaseModel):
    month: int = Field(ge=1, le=24)
    opening_cash: Decimal
    operating_cash_flow: Decimal
    investing_cash_flow: Decimal
    financing_cash_flow: Decimal
    minimum_liquidity: Decimal = Decimal("0")


class MonthlyLiquidityRequest(BaseModel):
    periods: list[MonthlyLiquidityPayload]


class WorkingCapitalRequest(BaseModel):
    annual_revenue: Decimal
    annual_cogs: Decimal
    dso: Decimal
    dpo: Decimal
    dio: Decimal


class DebtScheduleRequest(BaseModel):
    instrument_id: str
    opening_principal: Decimal
    annual_interest_rate: Decimal
    monthly_amortization: Decimal
    maturity_month: int = Field(ge=1)
    months: int = Field(ge=1)
    committed_limit: Decimal | None = None


class CovenantRequest(BaseModel):
    covenant_id: str
    metric: str
    threshold: Decimal
    direction: CovenantDirection
    actual: Decimal
    simulated_values: list[Decimal] = Field(default_factory=list)


class StressRequest(BaseModel):
    name: str
    base_cash: Decimal
    baseline_revenue_cash: Decimal
    baseline_cost_cash: Decimal
    minimum_liquidity: Decimal
    revenue_change_pct: Decimal = Decimal("0")
    collection_delay_pct: Decimal = Decimal("0")
    cost_change_pct: Decimal = Decimal("0")
    refinancing_shock: Decimal = Decimal("0")
    mitigation_cash: Decimal = Decimal("0")


class CashAccuracyPayload(BaseModel):
    horizon: int = Field(ge=1)
    actual: Decimal
    forecast: Decimal


class CashAccuracyRequest(BaseModel):
    observations: list[CashAccuracyPayload]


def build_liquidity_router(
    weekly_forecast: ThirteenWeekCashForecast,
    monthly_forecast: MonthlyLiquidityForecast,
    working_capital_model: WorkingCapitalModel,
    debt_schedule_engine: DebtScheduleEngine,
    covenant_engine: CovenantEngine,
    stress_engine: LiquidityStressEngine,
    accuracy_service: CashForecastAccuracyService,
) -> APIRouter:
    router = APIRouter(prefix="/liquidity", tags=["liquidity"])

    @router.post("/cash-forecast/13-week")
    def forecast_13_week(payload: ThirteenWeekForecastRequest) -> dict[str, object]:
        result = weekly_forecast.forecast(
            tuple(WeeklyCashFlow(**item.model_dump()) for item in payload.flows)
        )
        return {"positions": result}

    @router.post("/cash-forecast/monthly")
    def forecast_monthly(payload: MonthlyLiquidityRequest) -> dict[str, object]:
        result = monthly_forecast.forecast(
            tuple(MonthlyLiquidityInput(**item.model_dump()) for item in payload.periods)
        )
        return {"positions": result}

    @router.post("/working-capital")
    def calculate_working_capital(payload: WorkingCapitalRequest) -> dict[str, object]:
        position = working_capital_model.calculate(WorkingCapitalAssumptions(**payload.model_dump()))
        return {"position": position}

    @router.post("/debt-schedules")
    def build_debt_schedule(payload: DebtScheduleRequest) -> dict[str, object]:
        instrument = DebtInstrument(
            instrument_id=payload.instrument_id,
            opening_principal=payload.opening_principal,
            annual_interest_rate=payload.annual_interest_rate,
            monthly_amortization=payload.monthly_amortization,
            maturity_month=payload.maturity_month,
            committed_limit=payload.committed_limit,
        )
        return {"periods": debt_schedule_engine.schedule(instrument, payload.months)}

    @router.post("/covenants/evaluate")
    def evaluate_covenant(payload: CovenantRequest) -> dict[str, object]:
        definition = CovenantDefinition(
            covenant_id=payload.covenant_id,
            metric=payload.metric,
            threshold=payload.threshold,
            direction=payload.direction,
        )
        result = covenant_engine.evaluate(
            definition,
            payload.actual,
            tuple(payload.simulated_values),
        )
        return {"result": result}

    @router.post("/stress-tests")
    def run_stress(payload: StressRequest) -> dict[str, object]:
        scenario = LiquidityStressScenario(
            name=payload.name,
            revenue_change_pct=payload.revenue_change_pct,
            collection_delay_pct=payload.collection_delay_pct,
            cost_change_pct=payload.cost_change_pct,
            refinancing_shock=payload.refinancing_shock,
            mitigation_cash=payload.mitigation_cash,
        )
        result = stress_engine.apply(
            base_cash=payload.base_cash,
            baseline_revenue_cash=payload.baseline_revenue_cash,
            baseline_cost_cash=payload.baseline_cost_cash,
            minimum_liquidity=payload.minimum_liquidity,
            scenario=scenario,
        )
        return {"result": result}

    @router.post("/cash-forecast/accuracy")
    def summarize_accuracy(payload: CashAccuracyRequest) -> dict[str, object]:
        result = accuracy_service.summarize(
            tuple(CashAccuracyObservation(**item.model_dump()) for item in payload.observations)
        )
        return {"slices": result}

    return router
