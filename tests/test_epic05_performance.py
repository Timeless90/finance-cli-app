from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.api.settings import ApiSettings
from cfo_platform.composition import build_container
from cfo_platform.performance_management import (
    AccuracyObservation,
    AnomalyDetectionService,
    AnomalyObservation,
    CommentaryStatus,
    ComparisonType,
    ForecastAccuracyService,
    ManagementCommentaryService,
    VarianceAnalysisEngine,
    VarianceContribution,
    default_cfo_kpi_tree,
)


def test_kpi_tree_calculates_ebit_and_free_cash_flow() -> None:
    tree = default_cfo_kpi_tree()
    ebit = tree.evaluate(
        "ebit",
        {
            "revenue": Decimal("1000"),
            "variable_cost": Decimal("300"),
            "personnel_cost": Decimal("200"),
            "fixed_operating_cost": Decimal("100"),
            "depreciation": Decimal("50"),
        },
    )
    assert ebit.value == Decimal("350")
    free_cash_flow = tree.evaluate(
        "free_cash_flow",
        {"operating_cash_flow": Decimal("220"), "capex": Decimal("70")},
    )
    assert free_cash_flow.value == Decimal("150")


def test_price_volume_mix_bridge_explains_full_variance() -> None:
    engine = VarianceAnalysisEngine()
    contributions = engine.price_volume_mix(
        baseline_price=Decimal("10"),
        actual_price=Decimal("12"),
        baseline_volume=Decimal("100"),
        actual_volume=Decimal("110"),
        baseline_mix=Decimal("1"),
        actual_mix=Decimal("1.1"),
        source_snapshot_id="actual-2027-01",
    )
    bridge = engine.build_bridge(
        comparison_type=ComparisonType.PLAN_ACTUAL,
        kpi="revenue",
        baseline_version_id="plan-1",
        comparison_version_id="actual-1",
        baseline_value=Decimal("1000"),
        comparison_value=Decimal("1452"),
        contributions=contributions,
    )
    assert bridge.is_fully_explained
    assert bridge.explained_variance == Decimal("452.00")
    assert all(item.source_snapshot_id == "actual-2027-01" for item in contributions)


def test_incomplete_variance_bridge_is_rejected() -> None:
    with pytest.raises(ValueError, match="incomplete"):
        VarianceAnalysisEngine().build_bridge(
            comparison_type=ComparisonType.FORECAST_ACTUAL,
            kpi="ebitda",
            baseline_version_id="forecast-1",
            comparison_version_id="actual-1",
            baseline_value=Decimal("100"),
            comparison_value=Decimal("80"),
            contributions=(VarianceContribution("price", Decimal("-10"), "snapshot-1"),),
        )


def test_forecast_accuracy_is_sliced_by_kpi_unit_horizon_and_model() -> None:
    slices = ForecastAccuracyService().summarize(
        (
            AccuracyObservation("revenue", 1, Decimal("100"), Decimal("110"), "DE", "m1"),
            AccuracyObservation("revenue", 1, Decimal("120"), Decimal("114"), "DE", "m1"),
            AccuracyObservation("revenue", 3, Decimal("100"), Decimal("90"), "DE", "m1"),
        )
    )
    assert len(slices) == 2
    one_month = next(item for item in slices if item.horizon == 1)
    assert one_month.metrics.mae == Decimal("8")
    assert one_month.metrics.bias == Decimal("2")
    assert one_month.metrics.wape == Decimal("16") / Decimal("220")


def test_anomaly_detection_combines_robust_and_rule_based_signals() -> None:
    service = AnomalyDetectionService()
    signals = service.detect(
        (
            AnomalyObservation("2027-01", "cost", Decimal("10")),
            AnomalyObservation("2027-02", "cost", Decimal("11")),
            AnomalyObservation("2027-03", "cost", Decimal("10")),
            AnomalyObservation("2027-04", "cost", Decimal("50")),
        ),
        upper_bound=Decimal("40"),
    )
    assert len(signals) == 1
    assert signals[0].period == "2027-04"
    assert set(signals[0].rule_breaches) == {"robust_z_score", "upper_bound"}


def test_material_variance_requires_commentary() -> None:
    result = ManagementCommentaryService().evaluate(
        kpi="ebitda",
        period="2027-01",
        variance=Decimal("-25"),
        materiality_threshold=Decimal("20"),
    )
    assert result.status == CommentaryStatus.REQUIRED


def test_performance_api_contracts() -> None:
    settings = ApiSettings(api_prefix="/api/v1", allowed_origins=["http://localhost"])
    container = build_container()
    with TestClient(create_app(settings, container)) as client:
        bridge = client.post(
            "/api/v1/performance/variance-bridges",
            json={
                "comparison_type": "plan_actual",
                "kpi": "revenue",
                "baseline_version_id": "plan-1",
                "comparison_version_id": "actual-1",
                "baseline_value": "100",
                "comparison_value": "120",
                "contributions": [
                    {
                        "driver": "volume",
                        "amount": "20",
                        "source_snapshot_id": "snapshot-1",
                    }
                ],
            },
        )
        assert bridge.status_code == 200
        assert bridge.json()["is_fully_explained"] is True

        commentary = client.post(
            "/api/v1/performance/commentary/requirements",
            json={
                "kpi": "ebitda",
                "period": "2027-01",
                "variance": "-30",
                "materiality_threshold": "20",
            },
        )
        assert commentary.status_code == 200
        assert commentary.json()["status"] == "required"
