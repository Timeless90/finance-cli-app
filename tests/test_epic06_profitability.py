from decimal import Decimal

from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
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


def _record(
    *,
    product: str,
    customer: str,
    channel: str,
    revenue: str,
    variable_cost: str,
    direct_fixed_cost: str,
    allocated_cost: str,
) -> ProfitabilityRecord:
    return ProfitabilityRecord(
        period="2026-07",
        revenue=Decimal(revenue),
        variable_cost=Decimal(variable_cost),
        direct_fixed_cost=Decimal(direct_fixed_cost),
        allocated_cost=Decimal(allocated_cost),
        snapshot_id="snap-2026-07",
        version_id="actual-2026-07",
        dimensions=ProfitabilityKey(
            entity="de01",
            segment="industrial",
            product=product,
            customer=customer,
            channel=channel,
            cost_center="cc100",
            profit_center="pc10",
        ),
    )


def test_contribution_margin_and_dimension_profitability() -> None:
    service = ProfitabilityService()
    records = (
        _record(
            product="p1",
            customer="c1",
            channel="direct",
            revenue="1000",
            variable_cost="400",
            direct_fixed_cost="100",
            allocated_cost="50",
        ),
        _record(
            product="p2",
            customer="c2",
            channel="partner",
            revenue="500",
            variable_cost="250",
            direct_fixed_cost="50",
            allocated_cost="25",
        ),
    )

    summary = service.summarize(records)
    assert summary.revenue == Decimal("1500")
    assert summary.contribution_margin_1 == Decimal("850")
    assert summary.contribution_margin_2 == Decimal("700")
    assert summary.operating_margin == Decimal("625")
    assert summary.operating_margin_pct == Decimal("625") / Decimal("1500")
    assert summary.snapshot_ids == ("snap-2026-07",)
    assert summary.version_ids == ("actual-2026-07",)

    by_product = service.group_by(records, ProfitabilityDimension.PRODUCT)
    assert by_product["p1"].operating_margin == Decimal("450")
    assert by_product["p2"].operating_margin == Decimal("175")


def test_cost_allocation_is_versioned_reconciled_and_traceable() -> None:
    service = CostAllocationService()
    run = service.allocate(
        pool=CostPool("shared-it", Decimal("100"), "snap-costs"),
        drivers=(
            AllocationDriver("product-a", Decimal("1")),
            AllocationDriver("product-b", Decimal("2")),
        ),
        allocation_version_id="alloc-v1",
        method=AllocationMethod.DRIVER,
    )

    assert run.is_reconciled is True
    assert run.allocated_amount == Decimal("100")
    assert run.reconciliation_difference == Decimal("0")
    assert all(item.allocation_version_id == "alloc-v1" for item in run.allocations)
    assert all(item.source_snapshot_id == "snap-costs" for item in run.allocations)
    assert run.allocations[0].amount == Decimal("100") / Decimal("3")
    assert run.allocations[1].amount == Decimal("100") - run.allocations[0].amount


def test_activity_based_costing_reconciles_all_activity_pools() -> None:
    service = ActivityBasedCostingService()
    result = service.allocate(
        activity_cost_pools={
            "orders": Decimal("120"),
            "support_tickets": Decimal("80"),
        },
        consumption=(
            ActivityConsumption(
                "customer-a",
                {"orders": Decimal("3"), "support_tickets": Decimal("1")},
            ),
            ActivityConsumption(
                "customer-b",
                {"orders": Decimal("1"), "support_tickets": Decimal("3")},
            ),
        ),
        allocation_version_id="abc-v1",
    )

    assert result.source_cost == Decimal("200")
    assert result.allocated_cost == Decimal("200")
    assert result.reconciliation_difference == Decimal("0")
    assert result.target_costs["customer-a"] == Decimal("110")
    assert result.target_costs["customer-b"] == Decimal("90")


def test_profitability_reconciliation_matches_financial_reference() -> None:
    result = ProfitabilityReconciliationService().reconcile(
        expected=Decimal("625"),
        actual=Decimal("625"),
    )
    assert result.reconciled is True
    assert result.difference == Decimal("0")


def test_price_and_cost_sensitivity_changes_margin() -> None:
    result = MarginSensitivityService().evaluate(
        SensitivityInput(
            revenue=Decimal("1000"),
            variable_cost=Decimal("500"),
            fixed_cost=Decimal("200"),
            price_change_pct=Decimal("0.05"),
            volume_change_pct=Decimal("0.10"),
            variable_cost_change_pct=Decimal("0.02"),
            fixed_cost_change_pct=Decimal("0.03"),
        )
    )

    assert result.baseline_margin == Decimal("300")
    assert result.stressed_revenue == Decimal("1155.0000")
    assert result.stressed_cost == Decimal("767.0000")
    assert result.stressed_margin == Decimal("388.0000")
    assert result.margin_change == Decimal("88.0000")


def test_margin_at_risk_uses_probability_weighted_distribution() -> None:
    result = MarginAtRiskService().evaluate(
        (
            MarginScenario("stress", Decimal("0.05"), Decimal("100")),
            MarginScenario("downside", Decimal("0.20"), Decimal("250")),
            MarginScenario("base", Decimal("0.60"), Decimal("400")),
            MarginScenario("upside", Decimal("0.15"), Decimal("550")),
        ),
        confidence_level=Decimal("0.95"),
        target_margin=Decimal("300"),
    )

    assert result.expected_margin == Decimal("377.5")
    assert result.threshold_margin == Decimal("100")
    assert result.margin_at_risk == Decimal("277.5")
    assert result.shortfall_probability == Decimal("0.25")


def test_profitability_api_contracts() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/profitability/allocations",
            json={
                "pool_id": "shared",
                "amount": "90",
                "source_snapshot_id": "snap-1",
                "allocation_version_id": "alloc-v1",
                "method": "driver",
                "drivers": [
                    {"target_id": "p1", "driver_value": "1"},
                    {"target_id": "p2", "driver_value": "2"},
                ],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_reconciled"] is True
        assert body["reconciliation_difference"] == "0"

        response = client.post(
            "/api/v1/profitability/margin-at-risk",
            json={
                "confidence_level": "0.95",
                "target_margin": "300",
                "scenarios": [
                    {"scenario_id": "stress", "probability": "0.05", "margin": "100"},
                    {"scenario_id": "base", "probability": "0.95", "margin": "400"},
                ],
            },
        )
        assert response.status_code == 200
        assert response.json()["result"]["shortfall_probability"] == "0.05"
