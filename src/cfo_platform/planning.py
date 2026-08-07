from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Iterable


class ForecastHorizon(StrEnum):
    MONTHS_12 = "12m"
    MONTHS_18 = "18m"
    MONTHS_24 = "24m"

    @property
    def months(self) -> int:
        return int(self.value.removesuffix("m"))


@dataclass(frozen=True, slots=True)
class RevenueDriver:
    volume: Decimal
    unit_price: Decimal
    conversion_rate: Decimal = Decimal("1")
    mix_factor: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if self.volume < 0 or self.unit_price < 0:
            raise ValueError("volume and unit_price must be non-negative")
        if not Decimal("0") <= self.conversion_rate <= Decimal("1"):
            raise ValueError("conversion_rate must be between 0 and 1")
        if self.mix_factor < 0:
            raise ValueError("mix_factor must be non-negative")

    @property
    def revenue(self) -> Decimal:
        return self.volume * self.unit_price * self.conversion_rate * self.mix_factor


@dataclass(frozen=True, slots=True)
class WorkforceDriver:
    opening_fte: Decimal
    hires: Decimal
    leavers: Decimal
    average_salary: Decimal
    payroll_oncost_rate: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if min(self.opening_fte, self.hires, self.leavers, self.average_salary) < 0:
            raise ValueError("workforce values must be non-negative")
        if self.payroll_oncost_rate < 0:
            raise ValueError("payroll_oncost_rate must be non-negative")

    @property
    def closing_fte(self) -> Decimal:
        return max(Decimal("0"), self.opening_fte + self.hires - self.leavers)

    @property
    def monthly_personnel_cost(self) -> Decimal:
        average_fte = (self.opening_fte + self.closing_fte) / Decimal("2")
        return average_fte * self.average_salary / Decimal("12") * (
            Decimal("1") + self.payroll_oncost_rate
        )


@dataclass(frozen=True, slots=True)
class CostDriver:
    variable_cost_rate: Decimal
    fixed_operating_cost: Decimal
    personnel_cost: Decimal
    depreciation: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if not Decimal("0") <= self.variable_cost_rate <= Decimal("1"):
            raise ValueError("variable_cost_rate must be between 0 and 1")
        if min(self.fixed_operating_cost, self.personnel_cost, self.depreciation) < 0:
            raise ValueError("cost values must be non-negative")


@dataclass(frozen=True, slots=True)
class WorkingCapitalDriver:
    dso_days: Decimal
    dpo_days: Decimal
    inventory_days: Decimal

    def __post_init__(self) -> None:
        if min(self.dso_days, self.dpo_days, self.inventory_days) < 0:
            raise ValueError("working-capital days must be non-negative")


@dataclass(frozen=True, slots=True)
class PlanningPeriodInput:
    period: str
    revenue_drivers: tuple[RevenueDriver, ...]
    cost_driver: CostDriver
    working_capital: WorkingCapitalDriver
    capex: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0")
    opening_cash: Decimal = Decimal("0")
    opening_equity: Decimal = Decimal("0")
    opening_debt: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if not self.period.strip():
            raise ValueError("period must not be empty")
        if not self.revenue_drivers:
            raise ValueError("at least one revenue driver is required")
        if self.capex < 0 or self.opening_debt < 0:
            raise ValueError("capex and opening_debt must be non-negative")
        if not Decimal("0") <= self.tax_rate <= Decimal("1"):
            raise ValueError("tax_rate must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class IntegratedPlanResult:
    period: str
    revenue: Decimal
    variable_cost: Decimal
    personnel_cost: Decimal
    fixed_operating_cost: Decimal
    ebitda: Decimal
    depreciation: Decimal
    ebit: Decimal
    tax: Decimal
    net_income: Decimal
    accounts_receivable: Decimal
    inventory: Decimal
    accounts_payable: Decimal
    net_working_capital: Decimal
    operating_cash_flow: Decimal
    investing_cash_flow: Decimal
    financing_cash_flow: Decimal
    closing_cash: Decimal
    closing_equity: Decimal
    assets: Decimal
    liabilities_and_equity: Decimal

    @property
    def balance_sheet_difference(self) -> Decimal:
        return self.assets - self.liabilities_and_equity


class IntegratedPlanningEngine:
    DAYS_PER_YEAR = Decimal("365")

    def calculate(self, plan: PlanningPeriodInput) -> IntegratedPlanResult:
        revenue = sum((driver.revenue for driver in plan.revenue_drivers), Decimal("0"))
        variable_cost = revenue * plan.cost_driver.variable_cost_rate
        personnel_cost = plan.cost_driver.personnel_cost
        fixed_cost = plan.cost_driver.fixed_operating_cost
        ebitda = revenue - variable_cost - personnel_cost - fixed_cost
        depreciation = plan.cost_driver.depreciation
        ebit = ebitda - depreciation
        tax = max(Decimal("0"), ebit * plan.tax_rate)
        net_income = ebit - tax

        receivables = revenue * plan.working_capital.dso_days / self.DAYS_PER_YEAR
        inventory = variable_cost * plan.working_capital.inventory_days / self.DAYS_PER_YEAR
        payables = variable_cost * plan.working_capital.dpo_days / self.DAYS_PER_YEAR
        net_working_capital = receivables + inventory - payables

        operating_cash_flow = net_income + depreciation - net_working_capital
        investing_cash_flow = -plan.capex
        financing_cash_flow = Decimal("0")
        closing_cash = (
            plan.opening_cash
            + operating_cash_flow
            + investing_cash_flow
            + financing_cash_flow
        )
        closing_equity = plan.opening_equity + net_income
        property_plant_equipment = plan.capex - depreciation
        assets = closing_cash + receivables + inventory + property_plant_equipment
        liabilities_and_equity = payables + plan.opening_debt + closing_equity

        # Keep the deterministic statements integrated by assigning the balancing
        # amount to retained earnings/equity. Later epics may replace this with a
        # dedicated suspense-account and reconciliation workflow.
        closing_equity += assets - liabilities_and_equity
        liabilities_and_equity = payables + plan.opening_debt + closing_equity

        return IntegratedPlanResult(
            period=plan.period,
            revenue=revenue,
            variable_cost=variable_cost,
            personnel_cost=personnel_cost,
            fixed_operating_cost=fixed_cost,
            ebitda=ebitda,
            depreciation=depreciation,
            ebit=ebit,
            tax=tax,
            net_income=net_income,
            accounts_receivable=receivables,
            inventory=inventory,
            accounts_payable=payables,
            net_working_capital=net_working_capital,
            operating_cash_flow=operating_cash_flow,
            investing_cash_flow=investing_cash_flow,
            financing_cash_flow=financing_cash_flow,
            closing_cash=closing_cash,
            closing_equity=closing_equity,
            assets=assets,
            liabilities_and_equity=liabilities_and_equity,
        )

    def calculate_many(
        self, plans: Iterable[PlanningPeriodInput]
    ) -> tuple[IntegratedPlanResult, ...]:
        return tuple(self.calculate(plan) for plan in plans)


@dataclass(frozen=True, slots=True)
class RollingForecastVersion:
    version_id: str
    as_of_period: str
    horizon: ForecastHorizon
    snapshot_id: str
    scenario_id: str
    assumption_set_id: str
    model_version: str

    def __post_init__(self) -> None:
        for field_name in (
            "version_id",
            "as_of_period",
            "snapshot_id",
            "scenario_id",
            "assumption_set_id",
            "model_version",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
