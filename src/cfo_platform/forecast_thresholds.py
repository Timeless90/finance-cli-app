from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from statistics import mean
from typing import Iterable, Sequence


class ThresholdDirection(StrEnum):
    MINIMUM = "minimum"
    MAXIMUM = "maximum"


class ThresholdStatus(StrEnum):
    HEALTHY = "healthy"
    WARNING = "warning"
    BREACHED = "breached"


@dataclass(frozen=True, slots=True)
class ForecastThreshold:
    threshold_id: str
    kpi: str
    target: float
    warning: float
    direction: ThresholdDirection

    def __post_init__(self) -> None:
        if not self.threshold_id.strip() or not self.kpi.strip():
            raise ValueError("threshold_id and kpi must not be empty")
        if self.direction == ThresholdDirection.MINIMUM and self.warning < self.target:
            raise ValueError("minimum warning must be at or above target")
        if self.direction == ThresholdDirection.MAXIMUM and self.warning > self.target:
            raise ValueError("maximum warning must be at or below target")


@dataclass(frozen=True, slots=True)
class ThresholdEvaluation:
    threshold_id: str
    kpi: str
    deterministic_value: float
    status: ThresholdStatus
    shortfall_probability: float | None


class GoalThresholdEngine:
    def evaluate(
        self,
        threshold: ForecastThreshold,
        deterministic_value: float,
        simulated_values: Sequence[float] | None = None,
    ) -> ThresholdEvaluation:
        status = self._status(threshold, deterministic_value)
        probability: float | None = None
        if simulated_values:
            breaches = [self._is_breach(threshold, value) for value in simulated_values]
            probability = mean(1.0 if breached else 0.0 for breached in breaches)
        return ThresholdEvaluation(
            threshold_id=threshold.threshold_id,
            kpi=threshold.kpi,
            deterministic_value=float(deterministic_value),
            status=status,
            shortfall_probability=probability,
        )

    def evaluate_many(
        self,
        items: Iterable[tuple[ForecastThreshold, float, Sequence[float] | None]],
    ) -> tuple[ThresholdEvaluation, ...]:
        return tuple(
            self.evaluate(threshold, value, simulations)
            for threshold, value, simulations in items
        )

    @staticmethod
    def _is_breach(threshold: ForecastThreshold, value: float) -> bool:
        if threshold.direction == ThresholdDirection.MINIMUM:
            return value < threshold.target
        return value > threshold.target

    def _status(self, threshold: ForecastThreshold, value: float) -> ThresholdStatus:
        if self._is_breach(threshold, value):
            return ThresholdStatus.BREACHED
        if threshold.direction == ThresholdDirection.MINIMUM and value < threshold.warning:
            return ThresholdStatus.WARNING
        if threshold.direction == ThresholdDirection.MAXIMUM and value > threshold.warning:
            return ThresholdStatus.WARNING
        return ThresholdStatus.HEALTHY
