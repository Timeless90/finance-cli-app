from __future__ import annotations

from fastapi import APIRouter

from app.profitability.profitability_management import (
    ActivityBasedCostingService,
    ActivityConsumption,
    AllocationDriver,
    CostAllocationService,
    CostPool,
    MarginAtRiskService,
    MarginScenario,
    MarginSensitivityService,
    ProfitabilityReconciliationService,
    ProfitabilityService,
    SensitivityInput,
)
from app.profitability.schemas import (
    ActivityBasedCostingRequest,
    ActivityConsumptionPayload,
    AllocationDriverPayload,
    CostAllocationRequest,
    MarginAtRiskRequest,
    MarginScenarioPayload,
    ProfitabilityKeyPayload,
    ProfitabilityRecordPayload,
    ProfitabilitySummaryRequest,
    ReconciliationRequest,
    SensitivityRequest,
)


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
            drivers=tuple(
                AllocationDriver(**item.model_dump()) for item in payload.drivers
            ),
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
    def activity_based_costing(
        payload: ActivityBasedCostingRequest,
    ) -> dict[str, object]:
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


__all__ = [
    "ActivityBasedCostingRequest",
    "ActivityConsumptionPayload",
    "AllocationDriverPayload",
    "CostAllocationRequest",
    "MarginAtRiskRequest",
    "MarginScenarioPayload",
    "ProfitabilityKeyPayload",
    "ProfitabilityRecordPayload",
    "ProfitabilitySummaryRequest",
    "ReconciliationRequest",
    "SensitivityRequest",
    "build_profitability_router",
]
