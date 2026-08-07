from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from statistics import mean, pstdev
from typing import Iterable

import numpy as np


class ForecastDistribution(StrEnum):
    STUDENT_T = "student_t"
    MOVING_BLOCK_BOOTSTRAP = "moving_block_bootstrap"
    MARKOV_REGIME = "markov_regime"


@dataclass(frozen=True, slots=True)
class ForecastBands:
    p10: tuple[float, ...]
    p50: tuple[float, ...]
    p90: tuple[float, ...]
    mean: tuple[float, ...]
    paths: int
    method: ForecastDistribution


@dataclass(frozen=True, slots=True)
class ProbabilisticForecastRequest:
    deterministic_values: tuple[float, ...]
    historical_residuals: tuple[float, ...]
    paths: int = 10_000
    seed: int = 42
    method: ForecastDistribution = ForecastDistribution.STUDENT_T
    block_length: int = 3
    student_df: float = 6.0
    markov_transition: tuple[tuple[float, float], tuple[float, float]] | None = None

    def __post_init__(self) -> None:
        if not self.deterministic_values:
            raise ValueError("deterministic_values must not be empty")
        if len(self.historical_residuals) < 3:
            raise ValueError("at least three historical residuals are required")
        if self.paths < 100:
            raise ValueError("paths must be at least 100")
        if self.block_length < 1:
            raise ValueError("block_length must be positive")
        if self.student_df <= 2:
            raise ValueError("student_df must be greater than 2")


class ProbabilisticForecastEngine:
    def generate(self, request: ProbabilisticForecastRequest) -> ForecastBands:
        rng = np.random.default_rng(request.seed)
        horizon = len(request.deterministic_values)
        residuals = np.asarray(request.historical_residuals, dtype=float)

        if request.method == ForecastDistribution.STUDENT_T:
            shocks = self._student_t_shocks(
                rng,
                residuals,
                request.paths,
                horizon,
                request.student_df,
            )
        elif request.method == ForecastDistribution.MOVING_BLOCK_BOOTSTRAP:
            shocks = self._block_bootstrap_shocks(
                rng,
                residuals,
                request.paths,
                horizon,
                request.block_length,
            )
        else:
            shocks = self._markov_shocks(
                rng,
                residuals,
                request.paths,
                horizon,
                request.markov_transition,
            )

        deterministic = np.asarray(request.deterministic_values, dtype=float)
        simulated = deterministic[None, :] + shocks
        return ForecastBands(
            p10=tuple(np.quantile(simulated, 0.10, axis=0).tolist()),
            p50=tuple(np.quantile(simulated, 0.50, axis=0).tolist()),
            p90=tuple(np.quantile(simulated, 0.90, axis=0).tolist()),
            mean=tuple(np.mean(simulated, axis=0).tolist()),
            paths=request.paths,
            method=request.method,
        )

    @staticmethod
    def _student_t_shocks(
        rng: np.random.Generator,
        residuals: np.ndarray,
        paths: int,
        horizon: int,
        degrees_of_freedom: float,
    ) -> np.ndarray:
        center = float(np.mean(residuals))
        scale = float(np.std(residuals, ddof=1))
        variance_adjustment = np.sqrt(
            (degrees_of_freedom - 2.0) / degrees_of_freedom
        )
        return center + scale * variance_adjustment * rng.standard_t(
            degrees_of_freedom,
            size=(paths, horizon),
        )

    @staticmethod
    def _block_bootstrap_shocks(
        rng: np.random.Generator,
        residuals: np.ndarray,
        paths: int,
        horizon: int,
        block_length: int,
    ) -> np.ndarray:
        n = len(residuals)
        if block_length > n:
            raise ValueError("block_length cannot exceed residual history")
        output = np.empty((paths, horizon), dtype=float)
        for path_index in range(paths):
            position = 0
            while position < horizon:
                start = int(rng.integers(0, n - block_length + 1))
                block = residuals[start : start + block_length]
                take = min(block_length, horizon - position)
                output[path_index, position : position + take] = block[:take]
                position += take
        return output

    @staticmethod
    def _markov_shocks(
        rng: np.random.Generator,
        residuals: np.ndarray,
        paths: int,
        horizon: int,
        transition: tuple[tuple[float, float], tuple[float, float]] | None,
    ) -> np.ndarray:
        matrix = np.asarray(
            transition or ((0.95, 0.05), (0.25, 0.75)),
            dtype=float,
        )
        if matrix.shape != (2, 2) or not np.allclose(matrix.sum(axis=1), 1.0):
            raise ValueError("markov_transition must be a 2x2 row-stochastic matrix")
        split = float(np.quantile(residuals, 0.25))
        normal = residuals[residuals > split]
        stressed = residuals[residuals <= split]
        if len(normal) < 2 or len(stressed) < 2:
            raise ValueError("residual history is insufficient for two regimes")
        output = np.empty((paths, horizon), dtype=float)
        for path_index in range(paths):
            state = 0
            for step in range(horizon):
                pool = normal if state == 0 else stressed
                output[path_index, step] = float(rng.choice(pool))
                state = int(rng.choice((0, 1), p=matrix[state]))
        return output


def residual_summary(values: Iterable[float]) -> dict[str, float]:
    residuals = tuple(float(value) for value in values)
    if not residuals:
        raise ValueError("values must not be empty")
    return {
        "mean": mean(residuals),
        "volatility": pstdev(residuals),
        "minimum": min(residuals),
        "maximum": max(residuals),
    }
