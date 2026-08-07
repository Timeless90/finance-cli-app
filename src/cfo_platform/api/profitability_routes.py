from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from cfo_platform.profitability_management import (
    ActivityBasedCostingService,
    ActivityConsumption,
    AllocationDriver,
    AllocationMethod,
    CostAllocationService,
    CostPool,
    MarginAtRiskService,
    MarginScenario,
    MarginSensitivityService,
    ProfitabilityDimension,
    ProfitabilityKey,
    ProfitabilityRecord,
    ProfitabilityReconciliationService,
    ProfitabilityService,
    SensitivityInput,
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
    price_change_pct: Decimal = Decimal("0")
    volume_change_pct: Decimal = Decimal("0")
    variable_cost_change_pct: Decimal = Decimal("0")
    fixed_cost_change_pct: Decimal = Decimal("0")


class MarginScenarioPayload(BaseModel):
    scenario_id: str
    probability: Decimal = Field(ge=0, le=1)
    margin: Decimal


class MarginAtRiskRequest(BaseModel):
    scenarios: list[MarginScenarioPayload]
    confidence_level: Decimal = Field(default=Decimal("0.95"), gt=0, lt=1)
    target_margin: Decimal = Decimal("0")


def build_profitability_router(
    profitability_service: ProfitabilityService,
    allocation_service: CostAllocationService,
    abc_service: ActivityBasedCostingService,
    reconciliation_service: ProfitabilityReconciliationService,
    sensitivity_service: MarginSensitivityService,
    margin_at_risk_service: MarginAtRiskService,
) -> APIRouter:
    router = APIRouter(prefix="/profitability", tags=["profitability"])

    @router.post("/summary")
    def summarize(payload: ProfitabilitySummaryRequest) -> dict[str, object]:
        records = tuple(item.to_domain() for item in payload.records)
        if payload.group_by is None:
            return {"summary": profitability_service.summarize(records)}
        return {
            "dimension": payload.group_by,
            "groups": profitability_service.group_by(records, payload.group_by),
        }

    @router.post("/allocations")
    def allocate_costs(payload: CostAllocationRequest) -> dict[str, object]:
        run = allocation_service.allocate(
            pool=CostPool(
                pool_id=payload.pool_id,
                amount=payload.amount,
                source_snapshot_id=payload.source_snapshot_id,
            ),
            drivers=tuple(AllocationDriver(**item.model_dump()) for item in payload.drivers),
            allocation_version_id=payload.allocation_version_id,
            method=payload.method,
        )
        return {
            "pool_id": run.pool_id,
            "allocation_version_id": run.allocation_version_id,
            "method": run.method,
            "source_amount": run.source_amount,
            "allocated_amount": run.allocated_amount,
            "reconciliation_difference": run.reconciliation_difference,
            "is_reconciled": run.is_reconciled,
            "allocations": run.allocations,
        }

    @router.post("/activity-based-costing")
    def activity_based_costing(payload: ActivityBasedCostingRequest) -> dict[str, object]:
        result = abc_service.allocate(
            activity_cost_pools=payload.activity_cost_pools,
            consumption=tuple(
                ActivityConsumption(
                    target_id=item.target_id,
                    activity_units=item.activity_units,
                )
                for item in payload.consumption
            ),
            allocation_version_id=payload.allocation_version_id,
        )
        return {
            "allocation_version_id": result.allocation_version_id,
            "rates": result.rates,
            "target_costs": result.target_costs,
            "source_cost": result.source_cost,
            "allocated_cost": result.allocated_cost,
            "reconciliation_difference": result.reconciliation_difference,
        }

    @router.post("/reconcile")
    def reconcile(payload: ReconciliationRequest) -> dict[str, object]:
        return {"result": reconciliation_service.reconcile(**payload.model_dump())}

    @router.post("/sensitivity")
    def sensitivity(payload: SensitivityRequest) -> dict[str, object]:
        result = sensitivity_service.evaluate(SensitivityInput(**payload.model_dump()))
        return {"result": result}

    @router.post("/margin-at-risk")
    def margin_at_risk(payload: MarginAtRiskRequest) -> dict[str, object]:
        result = margin_at_risk_service.evaluate(
            tuple(MarginScenario(**item.model_dump()) for item in payload.scenarios),
            confidence_level=payload.confidence_level,
            target_margin=payload.target_margin,
        )
        return {"result": result}

    return router
