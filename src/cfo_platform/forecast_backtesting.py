from __future__ import annotations

from dataclasses import dataclass
from math import log, pi
from statistics import mean
from typing import Sequence


@dataclass(frozen=True, slots=True)
class ForecastObservation:
    origin_index: int
    horizon: int
    forecast: float
    actual: float
    lower: float | None = None
    upper: float | None = None


@dataclass(frozen=True, slots=True)
class ForecastBacktestMetrics:
    observations: int
    mae: float
    wape: float
    bias: float
    coverage: float | None
    log_score: float | None


class RollingOriginBacktester:
    def evaluate(
        self,
        actuals: Sequence[float],
        forecasts: Sequence[ForecastObservation],
    ) -> ForecastBacktestMetrics:
        if not forecasts:
            raise ValueError("forecasts must not be empty")
        errors: list[float] = []
        absolute_errors: list[float] = []
        actual_values: list[float] = []
        covered: list[bool] = []
        log_scores: list[float] = []

        for observation in forecasts:
            target_index = observation.origin_index + observation.horizon
            if observation.origin_index < 0 or observation.horizon < 1:
                raise ValueError("origin_index and horizon must be valid")
            if target_index >= len(actuals):
                raise ValueError("forecast target lies outside actual history")
            actual = float(actuals[target_index])
            if abs(actual - observation.actual) > 1e-12:
                raise ValueError("observation actual does not match target history")
            error = observation.forecast - actual
            errors.append(error)
            absolute_errors.append(abs(error))
            actual_values.append(abs(actual))

            if observation.lower is not None or observation.upper is not None:
                if observation.lower is None or observation.upper is None:
                    raise ValueError("both lower and upper bounds are required")
                if observation.lower > observation.upper:
                    raise ValueError("lower bound cannot exceed upper bound")
                covered.append(observation.lower <= actual <= observation.upper)
                sigma = max((observation.upper - observation.lower) / 3.289707, 1e-9)
                standardized = (actual - observation.forecast) / sigma
                log_scores.append(0.5 * log(2.0 * pi * sigma * sigma) + 0.5 * standardized**2)

        denominator = sum(actual_values)
        return ForecastBacktestMetrics(
            observations=len(forecasts),
            mae=mean(absolute_errors),
            wape=sum(absolute_errors) / denominator if denominator else 0.0,
            bias=mean(errors),
            coverage=mean(1.0 if item else 0.0 for item in covered) if covered else None,
            log_score=mean(log_scores) if log_scores else None,
        )

    @staticmethod
    def assert_no_future_leakage(
        *,
        training_end_index: int,
        origin_index: int,
    ) -> None:
        if training_end_index > origin_index:
            raise ValueError("future leakage detected: training data extends past origin")
