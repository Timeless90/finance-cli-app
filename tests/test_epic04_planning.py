from decimal import Decimal

import pytest

from cfo_platform.planning import (
    CostDriver,
    ForecastHorizon,
    IntegratedPlanningEngine,
    PlanningPeriodInput,
    RevenueDriver,
    RollingForecastVersion,
    WorkforceDriver,
    WorkingCapitalDriver,
)


def test_revenue_driver_calculates_volume_price_mix_and_conversion() -> None:
    driver = RevenueDriver(
        volume=Decimal("100"),
        unit_price=Decimal("20"),
        conversion_rate=Decimal("0.8"),
        mix_factor=Decimal("1.1"),
    )

    assert driver.revenue == Decimal("1760.0")


def test_workforce_driver_calculates_closing_fte_and_monthly_cost() -> None:
    workforce = WorkforceDriver(
        opening_fte=Decimal("100"),
        hires=Decimal("10"),
        leavers=Decimal("4"),
        average_salary=Decimal("60000"),
        payroll_oncost_rate=Decimal("0.2"),
    )

    assert workforce.closing_fte == Decimal("106")
    assert workforce.monthly_personnel_cost == Decimal("618000.0")


def test_integrated_statements_reconcile() -> None:
    plan = PlanningPeriodInput(
        period="2027-01",
        revenue_drivers=(
            RevenueDriver(volume=Decimal("1000"), unit_price=Decimal("100")),
        ),
        cost_driver=CostDriver(
            variable_cost_rate=Decimal("0.4"),
            fixed_operating_cost=Decimal("10000"),
            personnel_cost=Decimal("20000"),
            depreciation=Decimal("2000"),
        ),
        working_capital=WorkingCapitalDriver(
            dso_days=Decimal("30"),
            dpo_days=Decimal("45"),
            inventory_days=Decimal("20"),
        ),
        capex=Decimal("5000"),
        tax_rate=Decimal("0.3"),
        opening_cash=Decimal("50000"),
        opening_equity=Decimal("20000"),
        opening_debt=Decimal("10000"),
    )

    result = IntegratedPlanningEngine().calculate(plan)

    assert result.revenue == Decimal("100000")
    assert result.ebitda == Decimal("30000.0")
    assert result.ebit == Decimal("28000.0")
    assert result.tax == Decimal("8400.00")
    assert result.balance_sheet_difference == Decimal("0")
    assert (
        result.closing_cash
        == plan.opening_cash
        + result.operating_cash_flow
        + result.investing_cash_flow
        + result.financing_cash_flow
    )


def test_forecast_horizons_are_explicit() -> None:
    assert ForecastHorizon.MONTHS_12.months == 12
    assert ForecastHorizon.MONTHS_18.months == 18
    assert ForecastHorizon.MONTHS_24.months == 24


def test_rolling_forecast_requires_governed_references() -> None:
    version = RollingForecastVersion(
        version_id="rf-2027-01",
        as_of_period="2027-01",
        horizon=ForecastHorizon.MONTHS_18,
        snapshot_id="sha256:data",
        scenario_id="scenario-base-v1",
        assumption_set_id="assumptions-v3",
        model_version="integrated-planning@1.0.0",
    )

    assert version.horizon.months == 18

    with pytest.raises(ValueError, match="snapshot_id"):
        RollingForecastVersion(
            version_id="rf-1",
            as_of_period="2027-01",
            horizon=ForecastHorizon.MONTHS_12,
            snapshot_id="",
            scenario_id="scenario",
            assumption_set_id="assumptions",
            model_version="1.0.0",
        )
