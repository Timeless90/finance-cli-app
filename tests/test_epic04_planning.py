from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.forecast_backtesting import ForecastObservation, RollingOriginBacktester
from cfo_platform.forecast_thresholds import (
    ForecastThreshold,
    GoalThresholdEngine,
    ThresholdDirection,
    ThresholdStatus,
)
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
from cfo_platform.planning_workflow import (
    InMemoryRollingForecastRepository,
    RollingForecastService,
)
from cfo_platform.probabilistic_forecast import (
    ForecastDistribution,
    ProbabilisticForecastEngine,
    ProbabilisticForecastRequest,
)


def _period(period: str, opening_cash: str = "1000") -> PlanningPeriodInput:
    return PlanningPeriodInput(
        period=period,
        revenue_drivers=(RevenueDriver(volume=Decimal("100"), unit_price=Decimal("10")),),
        cost_driver=CostDriver(
            variable_cost_rate=Decimal("0.4"),
            fixed_operating_cost=Decimal("100"),
            personnel_cost=Decimal("200"),
            depreciation=Decimal("10"),
        ),
        working_capital=WorkingCapitalDriver(
            dso_days=Decimal("30"), dpo_days=Decimal("20"), inventory_days=Decimal("15")
        ),
        capex=Decimal("20"),
        tax_rate=Decimal("0.3"),
        opening_cash=Decimal(opening_cash),
        opening_equity=Decimal("500"),
        opening_debt=Decimal("100"),
    )


def _version(version_id: str, as_of: str = "2027-01") -> RollingForecastVersion:
    return RollingForecastVersion(
        version_id=version_id,
        as_of_period=as_of,
        horizon=ForecastHorizon.MONTHS_12,
        snapshot_id="sha256:data",
        scenario_id="scenario-base-v1",
        assumption_set_id="assumptions-v3",
        model_version="integrated-planning@1.0.0",
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
        opening_fte=Decimal("100"), hires=Decimal("10"), leavers=Decimal("4"),
        average_salary=Decimal("60000"), payroll_oncost_rate=Decimal("0.2"),
    )
    assert workforce.closing_fte == Decimal("106")
    assert workforce.monthly_personnel_cost == Decimal("618000.0")


def test_integrated_statements_reconcile() -> None:
    result = IntegratedPlanningEngine().calculate(_period("2027-01"))
    assert result.revenue == Decimal("1000")
    assert result.balance_sheet_difference == Decimal("0")
    assert result.closing_cash == Decimal("1000") + result.operating_cash_flow + result.investing_cash_flow


def test_forecast_horizons_are_explicit() -> None:
    assert [item.months for item in ForecastHorizon] == [12, 18, 24]


def test_rolling_forecast_requires_governed_references() -> None:
    assert _version("rf-1").horizon.months == 12
    with pytest.raises(ValueError, match="snapshot_id"):
        RollingForecastVersion(
            version_id="rf-1", as_of_period="2027-01", horizon=ForecastHorizon.MONTHS_12,
            snapshot_id="", scenario_id="scenario", assumption_set_id="assumptions",
            model_version="1.0.0",
        )


def test_multi_period_roll_forward_uses_prior_closing_balances() -> None:
    service = RollingForecastService(InMemoryRollingForecastRepository())
    periods = tuple(_period(f"2027-{month:02d}", opening_cash="0") for month in range(1, 13))
    forecast = service.create(version=_version("rf-1"), period_inputs=periods)
    assert len(forecast.results) == 12
    assert forecast.period_inputs[1].opening_cash == forecast.results[0].closing_cash
    assert all(result.balance_sheet_difference == Decimal("0") for result in forecast.results)


def test_month_close_refresh_creates_new_version_and_lineage() -> None:
    service = RollingForecastService(InMemoryRollingForecastRepository())
    periods = tuple(_period(f"2027-{month:02d}") for month in range(1, 13))
    first = service.create(version=_version("rf-1"), period_inputs=periods)
    refreshed = service.refresh_after_close(
        prior_version_id=first.version.version_id,
        new_version=_version("rf-2", as_of="2027-02"),
        closed_period_actual=_period("2027-01"),
        extension_periods=(_period("2028-01"),),
    )
    assert refreshed.predecessor_version_id == "rf-1"
    assert len(refreshed.results) == 12


def test_probabilistic_forecast_is_reproducible_and_ordered() -> None:
    engine = ProbabilisticForecastEngine()
    request = ProbabilisticForecastRequest(
        deterministic_values=(100.0, 110.0),
        historical_residuals=(-10.0, -5.0, 0.0, 4.0, 8.0, 12.0),
        paths=1000,
        seed=7,
        method=ForecastDistribution.STUDENT_T,
    )
    first = engine.generate(request)
    second = engine.generate(request)
    assert first == second
    assert all(low <= median <= high for low, median, high in zip(first.p10, first.p50, first.p90))


def test_block_bootstrap_preserves_complete_horizon() -> None:
    result = ProbabilisticForecastEngine().generate(
        ProbabilisticForecastRequest(
            deterministic_values=(1.0, 2.0, 3.0, 4.0),
            historical_residuals=(-2.0, -1.0, 0.0, 1.0, 2.0),
            paths=200,
            seed=3,
            method=ForecastDistribution.MOVING_BLOCK_BOOTSTRAP,
            block_length=2,
        )
    )
    assert len(result.p50) == 4


def test_rolling_origin_metrics_and_leakage_guard() -> None:
    backtester = RollingOriginBacktester()
    metrics = backtester.evaluate(
        [100.0, 110.0, 120.0, 130.0],
        (
            ForecastObservation(0, 1, 108.0, 110.0, 100.0, 120.0),
            ForecastObservation(1, 1, 125.0, 120.0, 110.0, 130.0),
        ),
    )
    assert metrics.observations == 2
    assert metrics.mae == pytest.approx(3.5)
    assert metrics.coverage == 1.0
    with pytest.raises(ValueError, match="future leakage"):
        backtester.assert_no_future_leakage(training_end_index=4, origin_index=3)


def test_goal_threshold_returns_shortfall_probability() -> None:
    evaluation = GoalThresholdEngine().evaluate(
        ForecastThreshold("ebitda-min", "ebitda", 100.0, 110.0, ThresholdDirection.MINIMUM),
        deterministic_value=105.0,
        simulated_values=[90.0, 100.0, 120.0, 80.0],
    )
    assert evaluation.status == ThresholdStatus.WARNING
    assert evaluation.shortfall_probability == 0.5


def test_planning_api_contracts_are_exposed() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/planning/probabilistic",
        json={
            "deterministic_values": [100.0],
            "historical_residuals": [-5.0, 0.0, 5.0, 10.0],
            "paths": 200,
            "seed": 11,
            "method": "student_t",
        },
    )
    assert response.status_code == 200
    assert response.json()["paths"] == 200

    threshold = client.post(
        "/api/v1/planning/thresholds/evaluate",
        json={
            "threshold_id": "cash-min",
            "kpi": "cash",
            "target": 100.0,
            "warning": 120.0,
            "direction": "minimum",
            "deterministic_value": 110.0,
            "simulated_values": [90.0, 130.0],
        },
    )
    assert threshold.status_code == 200
    assert threshold.json()["shortfall_probability"] == 0.5
