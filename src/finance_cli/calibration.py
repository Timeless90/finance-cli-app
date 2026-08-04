from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class CalibrationResult:
    n_obs: int
    monthly_log_mean_historical: float
    monthly_log_mean_assumed: float
    monthly_log_mean_shrunk: float
    monthly_log_volatility: float
    annual_geometric_return_historical: float
    annual_geometric_return_shrunk: float
    annual_volatility: float
    simple_return_skewness: float
    simple_return_excess_kurtosis: float
    student_t_df: float


def annual_return_to_monthly_log(annual_return: float) -> float:
    return np.log1p(annual_return) / 12.0


def calibrate(
    simple_returns: np.ndarray,
    log_returns: np.ndarray,
    *,
    assumed_annual_return: float,
    mean_shrinkage_months: float,
) -> CalibrationResult:
    if len(simple_returns) != len(log_returns):
        raise ValueError("Simple and log return arrays must have equal length")
    if len(log_returns) < 12:
        raise ValueError("At least 12 monthly returns are required for calibration")

    n = len(log_returns)
    hist_mean = float(np.mean(log_returns))
    assumed_mean = float(annual_return_to_monthly_log(assumed_annual_return))
    weight = n / (n + mean_shrinkage_months)
    shrunk_mean = weight * hist_mean + (1.0 - weight) * assumed_mean
    monthly_vol = float(np.std(log_returns, ddof=1))

    centered = (log_returns - hist_mean) / monthly_vol
    try:
        fitted_df, _, _ = stats.t.fit(centered, floc=0)
        student_t_df = float(np.clip(fitted_df, 2.1, 200.0))
    except Exception:
        student_t_df = 8.0

    return CalibrationResult(
        n_obs=n,
        monthly_log_mean_historical=hist_mean,
        monthly_log_mean_assumed=assumed_mean,
        monthly_log_mean_shrunk=float(shrunk_mean),
        monthly_log_volatility=monthly_vol,
        annual_geometric_return_historical=float(np.expm1(12.0 * hist_mean)),
        annual_geometric_return_shrunk=float(np.expm1(12.0 * shrunk_mean)),
        annual_volatility=float(monthly_vol * np.sqrt(12.0)),
        simple_return_skewness=float(stats.skew(simple_returns, bias=False)),
        simple_return_excess_kurtosis=float(
            stats.kurtosis(simple_returns, fisher=True, bias=False)
        ),
        student_t_df=student_t_df,
    )
