from __future__ import annotations

from fastapi import APIRouter

from app.liquidity.liquidity_management import (
    CashAccuracyObservation,
    CashForecastAccuracyService,
    CovenantDefinition,
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
from app.liquidity.schemas import (
    CashAccuracyPayload,
    CashAccuracyRequest,
    CovenantRequest,
    DebtScheduleRequest,
    MonthlyLiquidityPayload,
    MonthlyLiquidityRequest,
    StressRequest,
    ThirteenWeekForecastRequest,
    WeeklyCashFlowPayload,
    WorkingCapitalRequest,
)


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
            tuple(
                MonthlyLiquidityInput(**item.model_dump()) for item in payload.periods
            )
        )
        return {"positions": result}

    @router.post("/working-capital")
    def calculate_working_capital(payload: WorkingCapitalRequest) -> dict[str, object]:
        position = working_capital_model.calculate(
            WorkingCapitalAssumptions(**payload.model_dump())
        )
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
            tuple(
                CashAccuracyObservation(**item.model_dump())
                for item in payload.observations
            )
        )
        return {"slices": result}

    return router


__all__ = [
    "CashAccuracyPayload",
    "CashAccuracyRequest",
    "CovenantRequest",
    "DebtScheduleRequest",
    "MonthlyLiquidityPayload",
    "MonthlyLiquidityRequest",
    "StressRequest",
    "ThirteenWeekForecastRequest",
    "WeeklyCashFlowPayload",
    "WorkingCapitalRequest",
    "build_liquidity_router",
]
