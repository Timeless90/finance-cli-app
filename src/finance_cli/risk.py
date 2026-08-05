from __future__ import annotations

import numpy as np

METRICS = (
    "annual_return",
    "annual_volatility",
    "sharpe",
    "sortino",
    "omega",
    "max_drawdown",
    "ulcer_index",
    "var",
    "expected_shortfall",
)


def _safe_ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.divide(
        numerator,
        denominator,
        out=np.full_like(numerator, np.nan, dtype=float),
        where=denominator > 0,
    )


def path_risk_metrics(
    log_returns: np.ndarray,
    *,
    annual_risk_free_rate: float = 0.0,
    annual_omega_threshold: float = 0.0,
    confidence_level: float = 0.95,
) -> dict[str, np.ndarray]:
    if log_returns.ndim != 2 or log_returns.shape[1] < 2:
        raise ValueError("log_returns must be a two-dimensional array with at least two months")
    if not 0.5 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between 0.5 and 1.0")

    simple = np.expm1(log_returns)
    monthly_rf = np.expm1(np.log1p(annual_risk_free_rate) / 12.0)
    monthly_threshold = np.expm1(np.log1p(annual_omega_threshold) / 12.0)
    excess = simple - monthly_rf

    annual_return = np.expm1(np.mean(log_returns, axis=1) * 12.0)
    annual_volatility = np.std(simple, axis=1, ddof=1) * np.sqrt(12.0)
    sharpe = _safe_ratio(np.mean(excess, axis=1) * 12.0, annual_volatility)

    downside = np.minimum(excess, 0.0)
    downside_deviation = np.sqrt(np.mean(np.square(downside), axis=1)) * np.sqrt(12.0)
    sortino = _safe_ratio(np.mean(excess, axis=1) * 12.0, downside_deviation)

    gains = np.maximum(simple - monthly_threshold, 0.0).sum(axis=1)
    losses = np.maximum(monthly_threshold - simple, 0.0).sum(axis=1)
    omega = _safe_ratio(gains, losses)

    wealth = np.exp(np.cumsum(log_returns, axis=1))
    wealth = np.concatenate([np.ones((wealth.shape[0], 1)), wealth], axis=1)
    running_peak = np.maximum.accumulate(wealth, axis=1)
    drawdowns = wealth / running_peak - 1.0
    max_drawdown = np.min(drawdowns, axis=1)
    ulcer_index = np.sqrt(np.mean(np.square(np.minimum(drawdowns, 0.0)), axis=1))

    losses_monthly = -simple
    var = np.quantile(losses_monthly, confidence_level, axis=1)
    expected_shortfall = np.empty(log_returns.shape[0], dtype=float)
    for index in range(log_returns.shape[0]):
        tail = losses_monthly[index][losses_monthly[index] >= var[index]]
        expected_shortfall[index] = float(np.mean(tail)) if tail.size else float(var[index])

    return {
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe": sharpe,
        "sortino": sortino,
        "omega": omega,
        "max_drawdown": max_drawdown,
        "ulcer_index": ulcer_index,
        "var": var,
        "expected_shortfall": expected_shortfall,
    }


def summarize_risk_metrics(metrics: dict[str, np.ndarray]) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for name in METRICS:
        values = metrics[name]
        finite = values[np.isfinite(values)]
        if finite.size == 0:
            rows.append(
                {"metric": name, "p05": float("nan"), "median": float("nan"), "p95": float("nan")}
            )
            continue
        rows.append(
            {
                "metric": name,
                "p05": float(np.quantile(finite, 0.05)),
                "median": float(np.quantile(finite, 0.50)),
                "p95": float(np.quantile(finite, 0.95)),
            }
        )
    return rows
