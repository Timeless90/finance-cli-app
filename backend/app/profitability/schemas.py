from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.profitability.profitability_management import (
    AllocationMethod,
    ProfitabilityDimension,
    ProfitabilityKey,
    ProfitabilityRecord,
)


class ProfitabilityKeyPayload(BaseModel):
    entity: str = "group"
    segment: str = "all"
    product: str = "all"
    customer: str = "all"
    channel: str = "all"
    cost_center: str = "all"
    profit_center: str = "all"

    def to_domain(self) -> ProfitabilityKey:
        return ProfitabilityKey(**self.model_dump())


class ProfitabilityRecordPayload(BaseModel):
    period: str
    revenue: Decimal
    variable_cost: Decimal
    direct_fixed_cost: Decimal
    allocated_cost: Decimal
    snapshot_id: str
    version_id: str
    dimensions: ProfitabilityKeyPayload = Field(default_factory=ProfitabilityKeyPayload)

    def to_domain(self) -> ProfitabilityRecord:
        return ProfitabilityRecord(
            period=self.period,
            revenue=self.revenue,
            variable_cost=self.variable_cost,
            direct_fixed_cost=self.direct_fixed_cost,
            allocated_cost=self.allocated_cost,
            snapshot_id=self.snapshot_id,
            version_id=self.version_id,
            dimensions=self.dimensions.to_domain(),
        )


class ProfitabilitySummaryRequest(BaseModel):
    records: list[ProfitabilityRecordPayload]
    group_by: ProfitabilityDimension | None = None


class AllocationDriverPayload(BaseModel):
    target_id: str
    driver_value: Decimal = Field(ge=0)


class CostAllocationRequest(BaseModel):
    pool_id: str
    amount: Decimal = Field(ge=0)
    source_snapshot_id: str
    allocation_version_id: str
    method: AllocationMethod = AllocationMethod.DRIVER
    drivers: list[AllocationDriverPayload]


class ActivityConsumptionPayload(BaseModel):
    target_id: str
    activity_units: dict[str, Decimal]


class ActivityBasedCostingRequest(BaseModel):
    activity_cost_pools: dict[str, Decimal]
    consumption: list[ActivityConsumptionPayload]
    allocation_version_id: str


class ReconciliationRequest(BaseModel):
    expected: Decimal
    actual: Decimal


class SensitivityRequest(BaseModel):
    revenue: Decimal
    variable_cost: Decimal
    fixed_cost: Decimal
    price_change_pct: Decimal = Decimal(0)
    volume_change_pct: Decimal = Decimal(0)
    variable_cost_change_pct: Decimal = Decimal(0)
    fixed_cost_change_pct: Decimal = Decimal(0)


class MarginScenarioPayload(BaseModel):
    scenario_id: str
    probability: Decimal = Field(ge=0, le=1)
    margin: Decimal


class MarginAtRiskRequest(BaseModel):
    scenarios: list[MarginScenarioPayload]
    confidence_level: Decimal = Field(default=Decimal("0.95"), gt=0, lt=1)
    target_margin: Decimal = Decimal(0)
