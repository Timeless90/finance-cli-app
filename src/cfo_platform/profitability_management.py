from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from statistics import mean
from typing import Iterable, Mapping, Sequence


class ProfitabilityDimension(StrEnum):
    PRODUCT = "product"
    CUSTOMER = "customer"
    CHANNEL = "channel"
    COST_CENTER = "cost_center"
    PROFIT_CENTER = "profit_center"


class AllocationMethod(StrEnum):
    DIRECT = "direct"
    DRIVER = "driver"
    ACTIVITY_BASED = "activity_based"


@dataclass(frozen=True, slots=True)
class ProfitabilityKey:
    entity: str = "group"
    segment: str = "all"
    product: str = "all"
    customer: str = "all"
    channel: str = "all"
    cost_center: str = "all"
    profit_center: str = "all"

    def __post_init__(self) -> None:
        if not all(value.strip() for value in self.as_tuple()):
            raise ValueError("profitability dimensions must not be empty")

    def as_tuple(self) -> tuple[str, str, str, str, str, str, str]:
        return (
            self.entity,
            self.segment,
            self.product,
            self.customer,
            self.channel,
            self.cost_center,
            self.profit_center,
        )


@dataclass(frozen=True, slots=True)
class ProfitabilityRecord:
    period: str
    revenue: Decimal
    variable_cost: Decimal
    direct_fixed_cost: Decimal
    allocated_cost: Decimal
    snapshot_id: str
    version_id: str
    dimensions: ProfitabilityKey

    def __post_init__(self) -> None:
        for value in (self.period, self.snapshot_id, self.version_id):
            if not value.strip():
                raise ValueError("record references must not be empty")

    @property
    def contribution_margin_1(self) -> Decimal:
        return self.revenue - self.variable_cost

    @property
    def contribution_margin_2(self) -> Decimal:
        return self.contribution_margin_1 - self.direct_fixed_cost

    @property
    def operating_margin(self) -> Decimal:
        return self.contribution_margin_2 - self.allocated_cost

    @property
    def operating_margin_pct(self) -> Decimal:
        if self.revenue == Decimal("0"):
            return Decimal("0")
        return self.operating_margin / self.revenue


@dataclass(frozen=True, slots=True)
class ProfitabilitySummary:
    revenue: Decimal
    variable_cost: Decimal
    direct_fixed_cost: Decimal
    allocated_cost: Decimal
    contribution_margin_1: Decimal
    contribution_margin_2: Decimal
    operating_margin: Decimal
    operating_margin_pct: Decimal
    snapshot_ids: tuple[str, ...]
    version_ids: tuple[str, ...]


class ProfitabilityService:
    def summarize(self, records: Iterable[ProfitabilityRecord]) -> ProfitabilitySummary:
        items = tuple(records)
        revenue = sum((item.revenue for item in items), Decimal("0"))
        variable_cost = sum((item.variable_cost for item in items), Decimal("0"))
        direct_fixed_cost = sum((item.direct_fixed_cost for item in items), Decimal("0"))
        allocated_cost = sum((item.allocated_cost for item in items), Decimal("0"))
        cm1 = revenue - variable_cost
        cm2 = cm1 - direct_fixed_cost
        margin = cm2 - allocated_cost
        margin_pct = margin / revenue if revenue else Decimal("0")
        return ProfitabilitySummary(
            revenue=revenue,
            variable_cost=variable_cost,
            direct_fixed_cost=direct_fixed_cost,
            allocated_cost=allocated_cost,
            contribution_margin_1=cm1,
            contribution_margin_2=cm2,
            operating_margin=margin,
            operating_margin_pct=margin_pct,
            snapshot_ids=tuple(sorted({item.snapshot_id for item in items})),
            version_ids=tuple(sorted({item.version_id for item in items})),
        )

    def group_by(
        self,
        records: Iterable[ProfitabilityRecord],
        dimension: ProfitabilityDimension,
    ) -> Mapping[str, ProfitabilitySummary]:
        grouped: dict[str, list[ProfitabilityRecord]] = {}
        for item in records:
            value = getattr(item.dimensions, dimension.value)
            grouped.setdefault(value, []).append(item)
        return {key: self.summarize(values) for key, values in sorted(grouped.items())}


@dataclass(frozen=True, slots=True)
class CostPool:
    pool_id: str
    amount: Decimal
    source_snapshot_id: str

    def __post_init__(self) -> None:
        if not self.pool_id.strip() or not self.source_snapshot_id.strip():
            raise ValueError("cost-pool references must not be empty")
        if self.amount < Decimal("0"):
            raise ValueError("cost pool amount must be non-negative")


@dataclass(frozen=True, slots=True)
class AllocationDriver:
    target_id: str
    driver_value: Decimal

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id must not be empty")
        if self.driver_value < Decimal("0"):
            raise ValueError("driver_value must be non-negative")


@dataclass(frozen=True, slots=True)
class CostAllocation:
    pool_id: str
    target_id: str
    amount: Decimal
    allocation_method: AllocationMethod
    allocation_version_id: str
    source_snapshot_id: str
    driver_value: Decimal
    driver_total: Decimal


@dataclass(frozen=True, slots=True)
class AllocationRun:
    pool_id: str
    allocation_version_id: str
    method: AllocationMethod
    source_amount: Decimal
    allocations: tuple[CostAllocation, ...]

    @property
    def allocated_amount(self) -> Decimal:
        return sum((item.amount for item in self.allocations), Decimal("0"))

    @property
    def reconciliation_difference(self) -> Decimal:
        return self.source_amount - self.allocated_amount

    @property
    def is_reconciled(self) -> bool:
        return self.reconciliation_difference == Decimal("0")


class CostAllocationService:
    def allocate(
        self,
        *,
        pool: CostPool,
        drivers: Sequence[AllocationDriver],
        allocation_version_id: str,
        method: AllocationMethod = AllocationMethod.DRIVER,
    ) -> AllocationRun:
        if not allocation_version_id.strip():
            raise ValueError("allocation_version_id must not be empty")
        if not drivers:
            raise ValueError("at least one allocation driver is required")
        total_driver = sum((item.driver_value for item in drivers), Decimal("0"))
        if total_driver <= Decimal("0"):
            raise ValueError("allocation driver total must be positive")

        allocations: list[CostAllocation] = []
        allocated = Decimal("0")
        last_index = len(drivers) - 1
        for index, driver in enumerate(drivers):
            if index == last_index:
                amount = pool.amount - allocated
            else:
                amount = pool.amount * driver.driver_value / total_driver
                allocated += amount
            allocations.append(
                CostAllocation(
                    pool_id=pool.pool_id,
                    target_id=driver.target_id,
                    amount=amount,
                    allocation_method=method,
                    allocation_version_id=allocation_version_id,
                    source_snapshot_id=pool.source_snapshot_id,
                    driver_value=driver.driver_value,
                    driver_total=total_driver,
                )
            )
        run = AllocationRun(
            pool_id=pool.pool_id,
            allocation_version_id=allocation_version_id,
            method=method,
            source_amount=pool.amount,
            allocations=tuple(allocations),
        )
        if not run.is_reconciled:
            raise ValueError("allocated costs do not reconcile to source pool")
        return run


@dataclass(frozen=True, slots=True)
class ActivityConsumption:
    target_id: str
    activity_units: Mapping[str, Decimal]

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id must not be empty")
        if any(value < Decimal("0") for value in self.activity_units.values()):
            raise ValueError("activity units must be non-negative")


@dataclass(frozen=True, slots=True)
class ActivityRate:
    activity: str
    rate: Decimal
    cost_pool_amount: Decimal
    total_units: Decimal


@dataclass(frozen=True, slots=True)
class ActivityBasedCostingResult:
    allocation_version_id: str
    rates: tuple[ActivityRate, ...]
    target_costs: Mapping[str, Decimal]
    source_cost: Decimal
    allocated_cost: Decimal

    @property
    def reconciliation_difference(self) -> Decimal:
        return self.source_cost - self.allocated_cost


class ActivityBasedCostingService:
    def allocate(
        self,
        *,
        activity_cost_pools: Mapping[str, Decimal],
        consumption: Sequence[ActivityConsumption],
        allocation_version_id: str,
    ) -> ActivityBasedCostingResult:
        if not allocation_version_id.strip():
            raise ValueError("allocation_version_id must not be empty")
        if not consumption:
            raise ValueError("consumption must not be empty")
        target_costs = {item.target_id: Decimal("0") for item in consumption}
        rates: list[ActivityRate] = []
        for activity, pool_amount in sorted(activity_cost_pools.items()):
            if pool_amount < Decimal("0"):
                raise ValueError("activity cost pools must be non-negative")
            total_units = sum(
                (item.activity_units.get(activity, Decimal("0")) for item in consumption),
                Decimal("0"),
            )
            if total_units <= Decimal("0") and pool_amount != Decimal("0"):
                raise ValueError(f"activity {activity} has cost but no consumption")
            rate = pool_amount / total_units if total_units else Decimal("0")
            rates.append(ActivityRate(activity, rate, pool_amount, total_units))
            allocated = Decimal("0")
            for index, item in enumerate(consumption):
                units = item.activity_units.get(activity, Decimal("0"))
                if index == len(consumption) - 1:
                    amount = pool_amount - allocated
                else:
                    amount = rate * units
                    allocated += amount
                target_costs[item.target_id] += amount
        source_cost = sum(activity_cost_pools.values(), Decimal("0"))
        allocated_cost = sum(target_costs.values(), Decimal("0"))
        return ActivityBasedCostingResult(
            allocation_version_id=allocation_version_id,
            rates=tuple(rates),
            target_costs=target_costs,
            source_cost=source_cost,
            allocated_cost=allocated_cost,
        )


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    expected: Decimal
    actual: Decimal
    difference: Decimal
    reconciled: bool


class ProfitabilityReconciliationService:
    def reconcile(self, *, expected: Decimal, actual: Decimal) -> ReconciliationResult:
        difference = expected - actual
        return ReconciliationResult(
            expected=expected,
            actual=actual,
            difference=difference,
            reconciled=difference == Decimal("0"),
        )


@dataclass(frozen=True, slots=True)
class SensitivityInput:
    revenue: Decimal
    variable_cost: Decimal
    fixed_cost: Decimal
    price_change_pct: Decimal = Decimal("0")
    volume_change_pct: Decimal = Decimal("0")
    variable_cost_change_pct: Decimal = Decimal("0")
    fixed_cost_change_pct: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class SensitivityResult:
    baseline_margin: Decimal
    stressed_revenue: Decimal
    stressed_cost: Decimal
    stressed_margin: Decimal
    margin_change: Decimal


class MarginSensitivityService:
    def evaluate(self, item: SensitivityInput) -> SensitivityResult:
        baseline_margin = item.revenue - item.variable_cost - item.fixed_cost
        stressed_revenue = (
            item.revenue
            * (Decimal("1") + item.price_change_pct)
            * (Decimal("1") + item.volume_change_pct)
        )
        stressed_variable_cost = (
            item.variable_cost
            * (Decimal("1") + item.volume_change_pct)
            * (Decimal("1") + item.variable_cost_change_pct)
        )
        stressed_fixed_cost = item.fixed_cost * (
            Decimal("1") + item.fixed_cost_change_pct
        )
        stressed_cost = stressed_variable_cost + stressed_fixed_cost
        stressed_margin = stressed_revenue - stressed_cost
        return SensitivityResult(
            baseline_margin=baseline_margin,
            stressed_revenue=stressed_revenue,
            stressed_cost=stressed_cost,
            stressed_margin=stressed_margin,
            margin_change=stressed_margin - baseline_margin,
        )


@dataclass(frozen=True, slots=True)
class MarginScenario:
    scenario_id: str
    probability: Decimal
    margin: Decimal

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ValueError("scenario_id must not be empty")
        if self.probability < Decimal("0") or self.probability > Decimal("1"):
            raise ValueError("probability must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class MarginAtRiskResult:
    confidence_level: Decimal
    expected_margin: Decimal
    threshold_margin: Decimal
    margin_at_risk: Decimal
    shortfall_probability: Decimal


class MarginAtRiskService:
    def evaluate(
        self,
        scenarios: Sequence[MarginScenario],
        *,
        confidence_level: Decimal = Decimal("0.95"),
        target_margin: Decimal = Decimal("0"),
    ) -> MarginAtRiskResult:
        if not scenarios:
            raise ValueError("scenarios must not be empty")
        if confidence_level <= Decimal("0") or confidence_level >= Decimal("1"):
            raise ValueError("confidence_level must be between 0 and 1")
        probability_total = sum((item.probability for item in scenarios), Decimal("0"))
        if probability_total != Decimal("1"):
            raise ValueError("scenario probabilities must sum to 1")
        expected_margin = sum(
            (item.probability * item.margin for item in scenarios), Decimal("0")
        )
        tail_probability = Decimal("1") - confidence_level
        cumulative = Decimal("0")
        threshold_margin = min(item.margin for item in scenarios)
        for item in sorted(scenarios, key=lambda scenario: scenario.margin):
            cumulative += item.probability
            threshold_margin = item.margin
            if cumulative >= tail_probability:
                break
        margin_at_risk = expected_margin - threshold_margin
        shortfall_probability = sum(
            (item.probability for item in scenarios if item.margin < target_margin),
            Decimal("0"),
        )
        return MarginAtRiskResult(
            confidence_level=confidence_level,
            expected_margin=expected_margin,
            threshold_margin=threshold_margin,
            margin_at_risk=margin_at_risk,
            shortfall_probability=shortfall_probability,
        )


def average_operating_margin(records: Sequence[ProfitabilityRecord]) -> Decimal:
    if not records:
        raise ValueError("records must not be empty")
    return Decimal(str(mean(float(item.operating_margin_pct) for item in records)))
