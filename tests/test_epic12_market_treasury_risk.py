from __future__ import annotations

import numpy as np
from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.market_treasury_risk import (
    CopulaDependenceModel,
    EvtTailOverlay,
    ExposureManagementService,
    ExposureType,
    GaussianHmmRegimeModel,
    GarchTModel,
    HedgeScenarioEngine,
    MarketExposure,
    MarketRiskMetrics,
    VarBacktester,
)


def test_exposure_aggregation_reconciles_long_and_short() -> None:
    service = ExposureManagementService()
    result = service.aggregate(
        [
            MarketExposure("a", ExposureType.FX, "EURUSD", 1_000_000.0, "EUR"),
            MarketExposure("b", ExposureType.FX, "EURUSD", -400_000.0, "EUR"),
        ]
    )
    assert len(result) == 1
    assert result[0].gross_long == 1_000_000.0
    assert result[0].gross_short == 400_000.0
    assert result[0].net_amount == 600_000.0


def test_var_and_expected_shortfall_are_ordered() -> None:
    rng = np.random.default_rng(11)
    losses = rng.standard_t(df=5, size=2_000)
    metrics = MarketRiskMetrics()
    result = metrics.student_t(losses, 0.99)
    assert result.expected_shortfall >= result.value_at_risk
    assert result.sample_size == 2_000


def test_garch_fit_is_stationary_and_forecasts_positive_variance() -> None:
    rng = np.random.default_rng(7)
    observations = 700
    returns = np.zeros(observations)
    variance = np.zeros(observations)
    variance[0] = 0.0001
    for index in range(1, observations):
        variance[index] = 0.000005 + 0.08 * returns[index - 1] ** 2 + 0.88 * variance[index - 1]
        returns[index] = rng.standard_t(df=7) * np.sqrt(variance[index] * 5.0 / 7.0)
    model = GarchTModel()
    fit = model.fit(returns)
    assert fit.alpha + fit.beta < 0.999
    assert fit.degrees_of_freedom > 2.0
    assert model.forecast_variance(fit, float(returns[-1])) > 0.0


def test_hmm_separates_low_and_high_volatility_states() -> None:
    rng = np.random.default_rng(19)
    low = rng.normal(0.0, 0.005, size=300)
    high = rng.normal(0.0, 0.03, size=180)
    returns = np.concatenate([low, high, low])
    fit = GaussianHmmRegimeModel().fit(returns)
    assert fit.state_variances[1] > fit.state_variances[0]
    assert fit.state_variances[1] / fit.state_variances[0] > 2.0
    assert abs(sum(fit.transition_matrix[0]) - 1.0) < 1e-8
    assert abs(sum(fit.transition_matrix[1]) - 1.0) < 1e-8


def test_evt_overlay_requires_and_uses_sufficient_tail_data() -> None:
    rng = np.random.default_rng(23)
    body = rng.lognormal(mean=-2.0, sigma=0.4, size=1_500)
    tail = rng.pareto(a=3.0, size=150) + 1.5
    losses = np.concatenate([body, tail])
    overlay = EvtTailOverlay()
    fit = overlay.fit(losses, threshold_quantile=0.95)
    assert fit.enabled
    assert fit.exceedances >= 30
    assert overlay.quantile(fit, 0.99, len(losses)) > fit.threshold


def test_copula_fit_returns_valid_dependence_model() -> None:
    rng = np.random.default_rng(31)
    correlation = np.array([[1.0, 0.7], [0.7, 1.0]])
    normals = rng.multivariate_normal([0.0, 0.0], correlation, size=500)
    scale = np.sqrt(5.0 / rng.chisquare(df=5, size=500))[:, None]
    returns = normals * scale
    fit = CopulaDependenceModel().fit(returns)
    assert fit.family in {"gaussian", "student_t"}
    assert len(fit.correlation) == 2
    assert abs(fit.correlation[0][0] - 1.0) < 1e-8


def test_optimal_hedge_reduces_variance() -> None:
    rng = np.random.default_rng(41)
    hedge = rng.normal(0.0, 0.01, size=800)
    exposure = 0.8 * hedge + rng.normal(0.0, 0.004, size=800)
    engine = HedgeScenarioEngine()
    ratio = engine.optimal_ratio(exposure, hedge)
    result = engine.evaluate(exposure, hedge, hedge_ratio=ratio)
    assert result.variance_reduction > 0.0
    assert result.hedged_variance < result.unhedged_variance


def test_var_backtest_accepts_well_spaced_expected_exceptions() -> None:
    losses = np.zeros(500)
    forecasts = np.ones(500)
    losses[[50, 150, 250, 350, 450]] = 2.0
    result = VarBacktester().evaluate(losses, forecasts, confidence=0.99)
    assert result.exceptions == 5
    assert result.passed_unconditional_coverage
    assert result.passed_independence


def test_market_risk_api_exposes_aggregation_and_var() -> None:
    client = TestClient(create_app())
    aggregate_response = client.post(
        "/api/v1/market-risk/exposures/aggregate",
        json={
            "exposures": [
                {
                    "exposure_id": "fx-1",
                    "exposure_type": "fx",
                    "risk_factor": "EURUSD",
                    "amount": 1000.0,
                    "currency": "EUR",
                    "delta": 1.0,
                }
            ]
        },
    )
    assert aggregate_response.status_code == 200
    assert aggregate_response.json()[0]["net_amount"] == 1000.0

    losses = np.linspace(-1.0, 3.0, 100).tolist()
    risk_response = client.post(
        "/api/v1/market-risk/var-es",
        json={"losses": losses, "confidence": 0.95, "method": "historical"},
    )
    assert risk_response.status_code == 200
    payload = risk_response.json()
    assert payload["expected_shortfall"] >= payload["value_at_risk"]
