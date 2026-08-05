from __future__ import annotations

import numpy as np

from finance_cli.diagnostics import compare_distribution_fits, rolling_origin_backtest
from finance_cli.risk import path_risk_metrics
from finance_cli.stress import sensitivity_grid
from finance_cli.tax import GermanTaxPolicy, apply_terminal_tax


def test_risk_metrics_capture_drawdown_and_tail_order() -> None:
    returns = np.array(
        [
            [0.02, -0.30, 0.10, 0.05],
            [0.01, 0.01, 0.01, 0.01],
        ]
    )
    metrics = path_risk_metrics(returns, confidence_level=0.75)
    assert metrics["max_drawdown"][0] < metrics["max_drawdown"][1]
    assert metrics["expected_shortfall"][0] >= metrics["var"][0]


def test_distribution_fit_and_rolling_coverage() -> None:
    rng = np.random.default_rng(7)
    returns = rng.normal(0.005, 0.04, size=96)
    fits = compare_distribution_fits(returns, monte_carlo_samples=99, seed=7)
    coverage = rolling_origin_backtest(returns, training_window=36, confidence_level=0.90)
    assert set(fits["model"]) == {"normal", "student_t"}
    assert set(coverage["model"]) == {"normal", "student_t"}
    assert coverage["observed_coverage"].between(0.0, 1.0).all()


def test_simplified_german_tax_respects_exemption_and_allowance() -> None:
    policy = GermanTaxPolicy(enabled=True, partial_exemption=0.30, saver_allowance=1000.0)
    after_tax, tax = apply_terminal_tax(np.array([11000.0, 20000.0]), 10000.0, policy)
    assert tax[0] == 0.0
    assert 0.0 < tax[1] < 10000.0
    assert np.all(after_tax <= np.array([11000.0, 20000.0]))


def test_sensitivity_grid_has_full_cartesian_product() -> None:
    grid = sensitivity_grid(
        initial_value=10000.0,
        monthly_contribution=500.0,
        years=10,
        annual_returns=[0.03, 0.07],
        annual_inflations=[0.01, 0.02, 0.03],
    )
    assert len(grid) == 6
    assert (grid["terminal_nominal"] >= grid["terminal_real"]).all()
