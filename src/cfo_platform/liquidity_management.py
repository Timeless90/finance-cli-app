from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from statistics import mean


ZERO = Decimal("0")


@dataclass(frozen=True, slots=True)
class WeeklyCashFlow:
    week: int
    bank_opening: Decimal
    ar_collections: Decimal = ZERO
    ap_payments: Decimal = ZERO
    payroll: Decimal = ZERO
    taxes: Decimal = ZERO
    capex: Decimal = ZERO
    financing: Decimal = ZERO
    other_cash_flow: Decimal = ZERO


@dataclass(frozen=True, slots=True)
class WeeklyCashPosition:
    week: int
    opening_cash: Decimal
    inflows: Decimal
    outflows: Decimal
    net_cash_flow: Decimal
    closing_cash: Decimal


class ThirteenWeekCashForecast:
    def forecast(self, flows: tuple[WeeklyCashFlow, ...]) -> tuple[WeeklyCashPosition, ...]:
        if len(flows) != 13:
            raise ValueError("13-week cash forecast requires exactly 13 weekly periods")
        expected = tuple(range(1, 14))
        actual = tuple(item.week for item in flows)
        if actual != expected:
            raise ValueError("weeks must be consecutive from 1 through 13")

        positions: list[WeeklyCashPosition] = []
        prior_close: Decimal | None = None
        for item in flows:
            opening = item.bank_opening if prior_close is None else prior_close
            if prior_close is not None and item.bank_opening != prior_close:
                raise ValueError("bank opening cash must reconcile to prior closing cash")
            inflows = item.ar_collections + max(item.financing, ZERO) + max(item.other_cash_flow, ZERO)
            outflows = (
                item.ap_payments
                + item.payroll
                + item.taxes
                + item.capex
                + max(-item.financing, ZERO)
                + max(-item.other_cash_flow, ZERO)
            )
            net = inflows - outflows
            closing = opening + net
            positions.append(
                WeeklyCashPosition(
                    week=item.week,
                    opening_cash=opening,
                    inflows=inflows,
                    outflows=outflows,
                    net_cash_flow=net,
                    closing_cash=closing,
                )
            )
            prior_close = closing
        return tuple(positions)


@dataclass(frozen=True, slots=True)
class MonthlyLiquidityInput:
    month: int
    opening_cash: Decimal
    operating_cash_flow: Decimal
    investing_cash_flow: Decimal
    financing_cash_flow: Decimal
    minimum_liquidity: Decimal = ZERO


@dataclass(frozen=True, slots=True)
class MonthlyLiquidityPosition:
    month: int
    opening_cash: Decimal
    closing_cash: Decimal
    minimum_liquidity: Decimal
    headroom: Decimal
    funding_gap: Decimal


class MonthlyLiquidityForecast:
    def forecast(
        self, periods: tuple[MonthlyLiquidityInput, ...]
    ) -> tuple[MonthlyLiquidityPosition, ...]:
        if not 12 <= len(periods) <= 24:
            raise ValueError("monthly liquidity forecast supports 12 to 24 months")
        positions: list[MonthlyLiquidityPosition] = []
        prior_close: Decimal | None = None
        for period in periods:
            opening = period.opening_cash if prior_close is None else prior_close
            if prior_close is not None and period.opening_cash != prior_close:
                raise ValueError("monthly opening cash must reconcile to prior closing cash")
            closing = (
                opening
                + period.operating_cash_flow
                + period.investing_cash_flow
                + period.financing_cash_flow
            )
            headroom = closing - period.minimum_liquidity
            positions.append(
                MonthlyLiquidityPosition(
                    month=period.month,
                    opening_cash=opening,
                    closing_cash=closing,
                    minimum_liquidity=period.minimum_liquidity,
                    headroom=headroom,
                    funding_gap=max(-headroom, ZERO),
                )
            )
            prior_close = closing
        return tuple(positions)


@dataclass(frozen=True, slots=True)
class WorkingCapitalAssumptions:
    annual_revenue: Decimal
    annual_cogs: Decimal
    dso: Decimal
    dpo: Decimal
    dio: Decimal


@dataclass(frozen=True, slots=True)
class WorkingCapitalPosition:
    receivables: Decimal
    payables: Decimal
    inventory: Decimal
    net_working_capital: Decimal


class WorkingCapitalModel:
    DAYS = Decimal("365")

    def calculate(self, assumptions: WorkingCapitalAssumptions) -> WorkingCapitalPosition:
        if min(assumptions.dso, assumptions.dpo, assumptions.dio) < ZERO:
            raise ValueError("working-capital days must be non-negative")
        receivables = assumptions.annual_revenue * assumptions.dso / self.DAYS
        payables = assumptions.annual_cogs * assumptions.dpo / self.DAYS
        inventory = assumptions.annual_cogs * assumptions.dio / self.DAYS
        return WorkingCapitalPosition(
            receivables=receivables,
            payables=payables,
            inventory=inventory,
            net_working_capital=receivables + inventory - payables,
        )

    def probabilistic_collection_days(
        self,
        base_dso: Decimal,
        shocks: tuple[Decimal, ...],
    ) -> tuple[Decimal, ...]:
        return tuple(max(base_dso + shock, ZERO) for shock in shocks)


@dataclass(frozen=True, slots=True)
class DebtInstrument:
    instrument_id: str
    opening_principal: Decimal
    annual_interest_rate: Decimal
    monthly_amortization: Decimal
    maturity_month: int
    committed_limit: Decimal | None = None


@dataclass(frozen=True, slots=True)
class DebtPeriod:
    month: int
    opening_principal: Decimal
    interest: Decimal
    repayment: Decimal
    closing_principal: Decimal
    refinancing_need: Decimal


class DebtScheduleEngine:
    def schedule(
        self,
        instrument: DebtInstrument,
        months: int,
    ) -> tuple[DebtPeriod, ...]:
        if months < 1:
            raise ValueError("months must be positive")
        principal = instrument.opening_principal
        result: list[DebtPeriod] = []
        for month in range(1, months + 1):
            interest = principal * instrument.annual_interest_rate / Decimal("12")
            repayment = min(instrument.monthly_amortization, principal)
            if month == instrument.maturity_month:
                repayment = principal
            closing = principal - repayment
            refinancing_need = ZERO
            if month == instrument.maturity_month and closing == ZERO:
                refinancing_need = principal - repayment
            result.append(
                DebtPeriod(
                    month=month,
                    opening_principal=principal,
                    interest=interest,
                    repayment=repayment,
                    closing_principal=closing,
                    refinancing_need=max(refinancing_need, ZERO),
                )
            )
            principal = closing
        return tuple(result)


class CovenantDirection(StrEnum):
    MAXIMUM = "maximum"
    MINIMUM = "minimum"


@dataclass(frozen=True, slots=True)
class CovenantDefinition:
    covenant_id: str
    metric: str
    threshold: Decimal
    direction: CovenantDirection


@dataclass(frozen=True, slots=True)
class CovenantResult:
    covenant_id: str
    actual: Decimal
    threshold: Decimal
    headroom: Decimal
    breached: bool
    breach_probability: Decimal = ZERO


class CovenantEngine:
    def leverage_ratio(self, net_debt: Decimal, ebitda: Decimal) -> Decimal:
        if ebitda <= ZERO:
            raise ValueError("EBITDA must be positive for leverage ratio")
        return net_debt / ebitda

    def interest_cover(self, ebit: Decimal, net_interest: Decimal) -> Decimal:
        if net_interest <= ZERO:
            raise ValueError("net interest must be positive for interest cover")
        return ebit / net_interest

    def evaluate(
        self,
        definition: CovenantDefinition,
        actual: Decimal,
        simulated_values: tuple[Decimal, ...] = (),
    ) -> CovenantResult:
        if definition.direction == CovenantDirection.MAXIMUM:
            headroom = definition.threshold - actual
            breached = actual > definition.threshold
            breaches = sum(value > definition.threshold for value in simulated_values)
        else:
            headroom = actual - definition.threshold
            breached = actual < definition.threshold
            breaches = sum(value < definition.threshold for value in simulated_values)
        probability = (
            Decimal(breaches) / Decimal(len(simulated_values)) if simulated_values else ZERO
        )
        return CovenantResult(
            covenant_id=definition.covenant_id,
            actual=actual,
            threshold=definition.threshold,
            headroom=headroom,
            breached=breached,
            breach_probability=probability,
        )


@dataclass(frozen=True, slots=True)
class LiquidityStressScenario:
    name: str
    revenue_change_pct: Decimal = ZERO
    collection_delay_pct: Decimal = ZERO
    cost_change_pct: Decimal = ZERO
    refinancing_shock: Decimal = ZERO
    mitigation_cash: Decimal = ZERO


@dataclass(frozen=True, slots=True)
class LiquidityStressResult:
    scenario: str
    stressed_cash: Decimal
    funding_gap: Decimal
    minimum_liquidity: Decimal


class LiquidityStressEngine:
    def apply(
        self,
        base_cash: Decimal,
        baseline_revenue_cash: Decimal,
        baseline_cost_cash: Decimal,
        minimum_liquidity: Decimal,
        scenario: LiquidityStressScenario,
    ) -> LiquidityStressResult:
        revenue_effect = baseline_revenue_cash * scenario.revenue_change_pct
        collection_effect = baseline_revenue_cash * scenario.collection_delay_pct
        cost_effect = baseline_cost_cash * scenario.cost_change_pct
        stressed = (
            base_cash
            + revenue_effect
            - collection_effect
            - cost_effect
            - scenario.refinancing_shock
            + scenario.mitigation_cash
        )
        return LiquidityStressResult(
            scenario=scenario.name,
            stressed_cash=stressed,
            funding_gap=max(minimum_liquidity - stressed, ZERO),
            minimum_liquidity=minimum_liquidity,
        )


@dataclass(frozen=True, slots=True)
class CashAccuracyObservation:
    horizon: int
    actual: Decimal
    forecast: Decimal


@dataclass(frozen=True, slots=True)
class CashAccuracySlice:
    horizon: int
    mae: Decimal
    bias: Decimal
    observations: int


class CashForecastAccuracyService:
    def summarize(
        self, observations: tuple[CashAccuracyObservation, ...]
    ) -> tuple[CashAccuracySlice, ...]:
        grouped: dict[int, list[CashAccuracyObservation]] = {}
        for observation in observations:
            grouped.setdefault(observation.horizon, []).append(observation)
        output: list[CashAccuracySlice] = []
        for horizon, values in sorted(grouped.items()):
            errors = [value.forecast - value.actual for value in values]
            mae = Decimal(str(mean(abs(error) for error in errors)))
            bias = Decimal(str(mean(errors)))
            output.append(
                CashAccuracySlice(
                    horizon=horizon,
                    mae=mae,
                    bias=bias,
                    observations=len(values),
                )
            )
        return tuple(output)
