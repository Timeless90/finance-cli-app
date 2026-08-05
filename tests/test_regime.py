from __future__ import annotations

import numpy as np
import pytest

from finance_cli.models import InitialRegime, RegimeConfig, RegimeInnovation
from finance_cli.regime import calibrate_regime_model, simulate_regime_log_returns


def _synthetic_regime_returns(seed: int = 7, n_months: int = 360) -> np.ndarray:
    rng = np.random.default_rng(seed)
    transition = np.array([[0.97, 0.03], [0.18, 0.82]])
    states = np.empty(n_months, dtype=np.int8)
    states[0] = 0
    for month in range(1, n_months):
        states[month] = rng.choice(2, p=transition[states[month - 1]])
    means = np.array([0.006, -0.018])
    stds = np.array([0.025, 0.085])
    return means[states] + stds[states] * rng.standard_normal(n_months)


def test_regime_calibration_rejects_short_series() -> None:
    cfg = RegimeConfig(minimum_observations=120, random_starts=2, max_iterations=50)
    with pytest.raises(ValueError, match="at least 120"):
        calibrate_regime_model(np.zeros(60), cfg, seed=1)


def test_gaussian_regime_fit_orders_states_by_volatility() -> None:
    cfg = RegimeConfig(
        minimum_observations=180,
        random_starts=8,
        max_iterations=300,
        innovation=RegimeInnovation.GAUSSIAN,
    )
    result = calibrate_regime_model(_synthetic_regime_returns(), cfg, seed=9)

    assert result.standard_deviations[0] < result.standard_deviations[1]
    assert np.allclose(result.transition_matrix.sum(axis=1), 1.0)
    assert np.allclose(result.smoothed_probabilities.sum(axis=1), 1.0)
    assert np.isfinite(result.log_likelihood)
    assert np.isfinite(result.aic)
    assert np.isfinite(result.bic)
    assert np.all(result.expected_durations_months > 1.0)


def test_regime_simulation_is_reproducible() -> None:
    cfg = RegimeConfig(
        minimum_observations=180,
        random_starts=5,
        max_iterations=200,
        parallel_streams=3,
    )
    result = calibrate_regime_model(_synthetic_regime_returns(), cfg, seed=4)
    first_returns, first_states = simulate_regime_log_returns(
        result, cfg, n_paths=101, n_months=24, seed=99
    )
    second_returns, second_states = simulate_regime_log_returns(
        result, cfg, n_paths=101, n_months=24, seed=99
    )

    assert np.array_equal(first_returns, second_returns)
    assert np.array_equal(first_states, second_states)


def test_crisis_initial_state_and_persistence_override() -> None:
    calibration_cfg = RegimeConfig(
        minimum_observations=180,
        random_starts=5,
        max_iterations=200,
    )
    result = calibrate_regime_model(
        _synthetic_regime_returns(), calibration_cfg, seed=13
    )
    scenario_cfg = calibration_cfg.model_copy(
        update={
            "initial_regime": InitialRegime.CRISIS,
            "crisis_persistence_override": 0.999,
        }
    )
    _, states = simulate_regime_log_returns(
        result, scenario_cfg, n_paths=200, n_months=12, seed=22
    )

    assert np.all(states[:, 0] == 1)
    assert float(np.mean(states[:, 1:] == 1)) > 0.95


def test_student_t_regime_fit_is_finite() -> None:
    cfg = RegimeConfig(
        minimum_observations=180,
        random_starts=5,
        max_iterations=200,
        innovation=RegimeInnovation.STUDENT_T,
        student_t_degrees_of_freedom=6.0,
    )
    result = calibrate_regime_model(_synthetic_regime_returns(), cfg, seed=15)

    assert result.innovation == "student_t"
    assert result.student_t_df == 6.0
    assert np.all(result.standard_deviations > 0.0)
    assert np.isfinite(result.log_likelihood)
