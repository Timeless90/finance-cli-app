from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Iterable, Protocol

from cfo_platform.planning import (
    ForecastHorizon,
    IntegratedPlanResult,
    IntegratedPlanningEngine,
    PlanningPeriodInput,
    RollingForecastVersion,
)


@dataclass(frozen=True, slots=True)
class RollingForecast:
    version: RollingForecastVersion
    period_inputs: tuple[PlanningPeriodInput, ...]
    results: tuple[IntegratedPlanResult, ...]
    predecessor_version_id: str | None = None


class RollingForecastRepository(Protocol):
    def add(self, forecast: RollingForecast) -> None: ...

    def get(self, version_id: str) -> RollingForecast | None: ...

    def list_all(self) -> tuple[RollingForecast, ...]: ...


class InMemoryRollingForecastRepository:
    def __init__(self) -> None:
        self._forecasts: dict[str, RollingForecast] = {}

    def add(self, forecast: RollingForecast) -> None:
        if forecast.version.version_id in self._forecasts:
            raise ValueError("forecast version already exists")
        self._forecasts[forecast.version.version_id] = forecast

    def get(self, version_id: str) -> RollingForecast | None:
        return self._forecasts.get(version_id)

    def list_all(self) -> tuple[RollingForecast, ...]:
        return tuple(self._forecasts.values())


class RollingForecastService:
    def __init__(
        self,
        repository: RollingForecastRepository,
        engine: IntegratedPlanningEngine | None = None,
    ) -> None:
        self._repository = repository
        self._engine = engine or IntegratedPlanningEngine()

    def create(
        self,
        *,
        version: RollingForecastVersion,
        period_inputs: Iterable[PlanningPeriodInput],
        predecessor_version_id: str | None = None,
    ) -> RollingForecast:
        inputs = tuple(period_inputs)
        if len(inputs) != version.horizon.months:
            raise ValueError("period count must equal forecast horizon")
        if predecessor_version_id is not None and self._repository.get(predecessor_version_id) is None:
            raise KeyError(predecessor_version_id)
        rolled_inputs = self._roll_forward(inputs)
        results = self._engine.calculate_many(rolled_inputs)
        forecast = RollingForecast(
            version=version,
            period_inputs=rolled_inputs,
            results=results,
            predecessor_version_id=predecessor_version_id,
        )
        self._repository.add(forecast)
        return forecast

    def refresh_after_close(
        self,
        *,
        prior_version_id: str,
        new_version: RollingForecastVersion,
        closed_period_actual: PlanningPeriodInput,
        extension_periods: Iterable[PlanningPeriodInput],
    ) -> RollingForecast:
        prior = self._require(prior_version_id)
        if new_version.as_of_period == prior.version.as_of_period:
            raise ValueError("refresh must advance the as-of period")
        remaining = prior.period_inputs[1:]
        extension = tuple(extension_periods)
        combined = (closed_period_actual,) + remaining + extension
        combined = combined[-new_version.horizon.months :]
        if len(combined) != new_version.horizon.months:
            raise ValueError("refresh does not provide a complete horizon")
        return self.create(
            version=new_version,
            period_inputs=combined,
            predecessor_version_id=prior_version_id,
        )

    def get(self, version_id: str) -> RollingForecast:
        return self._require(version_id)

    def _require(self, version_id: str) -> RollingForecast:
        forecast = self._repository.get(version_id)
        if forecast is None:
            raise KeyError(version_id)
        return forecast

    def _roll_forward(
        self,
        inputs: tuple[PlanningPeriodInput, ...],
    ) -> tuple[PlanningPeriodInput, ...]:
        rolled: list[PlanningPeriodInput] = []
        previous: IntegratedPlanResult | None = None
        for plan in inputs:
            if previous is not None:
                plan = replace(
                    plan,
                    opening_cash=previous.closing_cash,
                    opening_equity=previous.closing_equity,
                    opening_debt=max(Decimal("0"), plan.opening_debt),
                )
            rolled.append(plan)
            previous = self._engine.calculate(plan)
        return tuple(rolled)


def supported_horizons() -> tuple[ForecastHorizon, ...]:
    return tuple(ForecastHorizon)
