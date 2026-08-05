from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StressScenario:
    name: str
    immediate_shock: float
    annual_return_shift: float
    annual_volatility_multiplier: float


DEFAULT_STRESS_SCENARIOS = (
    StressScenario("equity_correction", -0.20, -0.01, 1.25),
    StressScenario("severe_bear_market", -0.40, -0.02, 1.60),
    StressScenario("lost_decade", -0.10, -0.04, 1.10),
)


def apply_stress_scenario(
    log_returns: np.ndarray,
    scenario: StressScenario,
) -> np.ndarray:
    stressed = np.array(log_returns, dtype=float, copy=True)
    if stressed.ndim != 2 or stressed.shape[1] == 0:
        raise ValueError("log_returns must be a non-empty two-dimensional array")
    centered = stressed - np.mean(stressed, axis=1, keepdims=True)
    stressed = (
        np.mean(stressed, axis=1, keepdims=True)
        + centered * scenario.annual_volatility_multiplier
        + scenario.annual_return_shift / 12.0
    )
    stressed[:, 0] += np.log1p(scenario.immediate_shock)
    return stressed


def scenario_catalog() -> pd.DataFrame:
    return pd.DataFrame([asdict(item) for item in DEFAULT_STRESS_SCENARIOS])


def future_value(
    *,
    initial_value: float,
    monthly_contribution: float,
    years: int,
    annual_return: float,
) -> float:
    months = years * 12
    monthly_rate = np.expm1(np.log1p(annual_return) / 12.0)
    if abs(monthly_rate) < 1e-12:
        return initial_value + monthly_contribution * months
    growth = (1.0 + monthly_rate) ** months
    annuity = monthly_contribution * (growth - 1.0) / monthly_rate
    return float(initial_value * growth + annuity)


def sensitivity_grid(
    *,
    initial_value: float,
    monthly_contribution: float,
    years: int,
    annual_returns: list[float],
    annual_inflations: list[float],
) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for annual_return in annual_returns:
        terminal = future_value(
            initial_value=initial_value,
            monthly_contribution=monthly_contribution,
            years=years,
            annual_return=annual_return,
        )
        for inflation in annual_inflations:
            real_terminal = terminal / ((1.0 + inflation) ** years)
            rows.append(
                {
                    "years": years,
                    "annual_return": annual_return,
                    "annual_inflation": inflation,
                    "terminal_nominal": terminal,
                    "terminal_real": float(real_terminal),
                }
            )
    return pd.DataFrame(rows)
