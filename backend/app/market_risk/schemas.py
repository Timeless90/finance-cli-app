from __future__ import annotations

from pydantic import BaseModel, Field

from app.market_risk.market_treasury_risk import (
    ExposureType,
)


class ExposurePayload(BaseModel):
    exposure_id: str
    exposure_type: ExposureType
    risk_factor: str
    amount: float
    currency: str
    delta: float = 1.0


class ExposureRequest(BaseModel):
    exposures: list[ExposurePayload]


class SensitivityRequest(ExposureRequest):
    shocks: dict[str, float]


class RiskMetricRequest(BaseModel):
    losses: list[float] = Field(min_length=30)
    confidence: float = 0.99
    method: str = "historical"


class SeriesRequest(BaseModel):
    returns: list[float]


class EvtRequest(BaseModel):
    losses: list[float]
    threshold_quantile: float = 0.95


class CopulaRequest(BaseModel):
    returns: list[list[float]]


class HedgeRequest(BaseModel):
    exposure_returns: list[float]
    hedge_returns: list[float]
    hedge_ratio: float | None = None


class BacktestRequest(BaseModel):
    realized_losses: list[float]
    var_forecasts: list[float]
    confidence: float = 0.99
    significance: float = 0.05
