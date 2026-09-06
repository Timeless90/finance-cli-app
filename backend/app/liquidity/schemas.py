from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.liquidity.liquidity_management import (
    CovenantDirection,
)


class WeeklyCashFlowPayload(BaseModel):
    week: int = Field(ge=1, le=13)
    bank_opening: Decimal
    ar_collections: Decimal = Decimal(0)
    ap_payments: Decimal = Decimal(0)
    payroll: Decimal = Decimal(0)
    taxes: Decimal = Decimal(0)
    capex: Decimal = Decimal(0)
    financing: Decimal = Decimal(0)
    other_cash_flow: Decimal = Decimal(0)


class ThirteenWeekForecastRequest(BaseModel):
    flows: list[WeeklyCashFlowPayload]


class MonthlyLiquidityPayload(BaseModel):
    month: int = Field(ge=1, le=24)
    opening_cash: Decimal
    operating_cash_flow: Decimal
    investing_cash_flow: Decimal
    financing_cash_flow: Decimal
    minimum_liquidity: Decimal = Decimal(0)


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
    revenue_change_pct: Decimal = Decimal(0)
    collection_delay_pct: Decimal = Decimal(0)
    cost_change_pct: Decimal = Decimal(0)
    refinancing_shock: Decimal = Decimal(0)
    mitigation_cash: Decimal = Decimal(0)


class CashAccuracyPayload(BaseModel):
    horizon: int = Field(ge=1)
    actual: Decimal
    forecast: Decimal


class CashAccuracyRequest(BaseModel):
    observations: list[CashAccuracyPayload]
