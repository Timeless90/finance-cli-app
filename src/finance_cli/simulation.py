from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .calibration import CalibrationResult
from .models import ContributionTiming, SimulationMethod


@dataclass(frozen=True)
class SimulationOutput:
    values: np.ndarray
    paid_in: np.ndarray
    real_values: np.ndarray


def _normal_log_returns(
    calibration: CalibrationResult, n_paths: int, n_months: int, rng: np.random.Generator
) -> np.ndarray:
    return rng.normal(
        calibration.monthly_log_mean_shrunk,
        calibration.monthly_log_volatility,
        size=(n_paths, n_months),
    )


def _student_t_log_returns(
    calibration: CalibrationResult,
    n_paths: int,
    n_months: int,
    rng: np.random.Generator,
    degrees_of_freedom: float | None,
) -> np.ndarray:
    df = degrees_of_freedom or calibration.student_t_df
    standardized_scale = np.sqrt((df - 2.0) / df)
    shocks = rng.standard_t(df, size=(n_paths, n_months)) * standardized_scale
    return calibration.monthly_log_mean_shrunk + calibration.monthly_log_volatility * shocks


def _historical_bootstrap_log_returns(
    historical_log_returns: np.ndarray,
    calibration: CalibrationResult,
    n_paths: int,
    n_months: int,
    rng: np.random.Generator,
) -> np.ndarray:
    residuals = historical_log_returns - np.mean(historical_log_returns)
    indices = rng.integers(0, len(residuals), size=(n_paths, n_months))
    return residuals[indices] + calibration.monthly_log_mean_shrunk


def _block_bootstrap_log_returns(
    historical_log_returns: np.ndarray,
    calibration: CalibrationResult,
    n_paths: int,
    n_months: int,
    rng: np.random.Generator,
    block_length: int,
) -> np.ndarray:
    residuals = historical_log_returns - np.mean(historical_log_returns)
    n = len(residuals)
    blocks_needed = int(np.ceil(n_months / block_length))
    output = np.empty((n_paths, blocks_needed * block_length), dtype=float)
    for path in range(n_paths):
        starts = rng.integers(0, n, size=blocks_needed)
        pos = 0
        for start in starts:
            idx = (start + np.arange(block_length)) % n
            output[path, pos : pos + block_length] = residuals[idx]
            pos += block_length
    return output[:, :n_months] + calibration.monthly_log_mean_shrunk


def generate_log_returns(
    *,
    method: SimulationMethod,
    calibration: CalibrationResult,
    historical_log_returns: np.ndarray | None,
    n_paths: int,
    n_months: int,
    seed: int,
    block_length: int,
    student_t_df: float | None,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if method == SimulationMethod.NORMAL:
        return _normal_log_returns(calibration, n_paths, n_months, rng)
    if method == SimulationMethod.STUDENT_T:
        return _student_t_log_returns(
            calibration, n_paths, n_months, rng, student_t_df
        )
    if historical_log_returns is None:
        raise ValueError(f"{method.value} requires historical log returns")
    if method == SimulationMethod.HISTORICAL_BOOTSTRAP:
        return _historical_bootstrap_log_returns(
            historical_log_returns, calibration, n_paths, n_months, rng
        )
    if method == SimulationMethod.BLOCK_BOOTSTRAP:
        return _block_bootstrap_log_returns(
            historical_log_returns,
            calibration,
            n_paths,
            n_months,
            rng,
            block_length,
        )
    raise ValueError(f"Unsupported simulation method: {method}")


def simulate_portfolio(
    log_returns: np.ndarray,
    *,
    initial_value: float,
    monthly_contribution: float,
    timing: ContributionTiming,
    annual_inflation: float,
    annual_external_fee: float,
) -> SimulationOutput:
    n_paths, n_months = log_returns.shape
    values = np.empty((n_paths, n_months + 1), dtype=float)
    paid_in = np.empty(n_months + 1, dtype=float)
    values[:, 0] = initial_value
    paid_in[0] = initial_value
    monthly_fee = (1.0 + annual_external_fee) ** (1.0 / 12.0) - 1.0

    for month in range(1, n_months + 1):
        if timing == ContributionTiming.MONTH_START:
            before_return = values[:, month - 1] + monthly_contribution
            values[:, month] = before_return * np.exp(log_returns[:, month - 1])
        else:
            values[:, month] = (
                values[:, month - 1] * np.exp(log_returns[:, month - 1])
                + monthly_contribution
            )
        values[:, month] *= 1.0 - monthly_fee
        paid_in[month] = paid_in[month - 1] + monthly_contribution

    months = np.arange(n_months + 1)
    inflation_factor = (1.0 + annual_inflation) ** (months / 12.0)
    real_values = values / inflation_factor[None, :]
    return SimulationOutput(values=values, paid_in=paid_in, real_values=real_values)
