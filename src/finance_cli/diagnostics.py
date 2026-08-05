from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class DistributionFit:
    model: str
    n_parameters: int
    log_likelihood: float
    aic: float
    bic: float
    gof_statistic: float
    gof_pvalue: float


@dataclass(frozen=True)
class CoverageResult:
    model: str
    nominal_coverage: float
    observed_coverage: float
    average_interval_width: float
    observations: int


def compare_distribution_fits(
    returns: np.ndarray,
    *,
    monte_carlo_samples: int = 999,
    seed: int = 20260805,
) -> pd.DataFrame:
    values = np.asarray(returns, dtype=float)
    if values.ndim != 1 or values.size < 24:
        raise ValueError("At least 24 one-dimensional return observations are required")
    if monte_carlo_samples < 99:
        raise ValueError("monte_carlo_samples must be at least 99")

    rows: list[DistributionFit] = []
    candidates: list[tuple[str, object, int]] = [
        ("normal", stats.norm, 2),
        ("student_t", stats.t, 3),
    ]
    rng = np.random.default_rng(seed)

    for name, distribution, parameter_count in candidates:
        fitted = distribution.fit(values)  # type: ignore[attr-defined]
        log_likelihood = float(np.sum(distribution.logpdf(values, *fitted)))  # type: ignore[attr-defined]
        aic = 2.0 * parameter_count - 2.0 * log_likelihood
        bic = np.log(values.size) * parameter_count - 2.0 * log_likelihood
        gof = stats.goodness_of_fit(
            distribution,  # type: ignore[arg-type]
            values,
            statistic="ad",
            n_mc_samples=monte_carlo_samples,
            rng=rng,
        )
        rows.append(
            DistributionFit(
                model=name,
                n_parameters=parameter_count,
                log_likelihood=log_likelihood,
                aic=float(aic),
                bic=float(bic),
                gof_statistic=float(gof.statistic),
                gof_pvalue=float(gof.pvalue),
            )
        )
    return pd.DataFrame([asdict(row) for row in rows]).sort_values("bic").reset_index(drop=True)


def rolling_origin_backtest(
    returns: np.ndarray,
    *,
    training_window: int = 60,
    confidence_level: float = 0.90,
) -> pd.DataFrame:
    values = np.asarray(returns, dtype=float)
    if values.ndim != 1:
        raise ValueError("returns must be one-dimensional")
    if training_window < 24 or values.size <= training_window:
        raise ValueError("training_window must be at least 24 and smaller than the sample")
    if not 0.5 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between 0.5 and 1.0")

    alpha = 1.0 - confidence_level
    observations: dict[str, list[tuple[bool, float]]] = {"normal": [], "student_t": []}

    for origin in range(training_window, values.size):
        train = values[origin - training_window : origin]
        actual = values[origin]

        normal_params = stats.norm.fit(train)
        normal_lower, normal_upper = stats.norm.ppf(
            [alpha / 2.0, 1.0 - alpha / 2.0], *normal_params
        )
        observations["normal"].append(
            (bool(normal_lower <= actual <= normal_upper), float(normal_upper - normal_lower))
        )

        t_params = stats.t.fit(train)
        t_lower, t_upper = stats.t.ppf([alpha / 2.0, 1.0 - alpha / 2.0], *t_params)
        observations["student_t"].append(
            (bool(t_lower <= actual <= t_upper), float(t_upper - t_lower))
        )

    rows: list[CoverageResult] = []
    for model, model_observations in observations.items():
        hits = np.array([hit for hit, _ in model_observations], dtype=float)
        widths = np.array([width for _, width in model_observations], dtype=float)
        rows.append(
            CoverageResult(
                model=model,
                nominal_coverage=confidence_level,
                observed_coverage=float(np.mean(hits)),
                average_interval_width=float(np.mean(widths)),
                observations=len(model_observations),
            )
        )
    return pd.DataFrame([asdict(row) for row in rows])
