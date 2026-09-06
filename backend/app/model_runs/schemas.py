from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.model_runs.finance_model_runs import (
    FinanceModelRunDomain,
    MarketRiskModelType,
    MarketRiskVarMethod,
    ModelRunStatus,
)


class ModelRunContextResponse(BaseModel):
    company_id: str
    company_label: str
    period_id: str
    period_label: str
    scenario_id: str
    scenario_label: str
    currency: str | None


class FinanceModelRunResponse(BaseModel):
    run_id: str
    domain: FinanceModelRunDomain
    model_type: str
    status: ModelRunStatus
    input_context: ModelRunContextResponse
    input_payload: dict[str, Any] = Field(default_factory=dict)
    source_snapshot_ids: list[str] = Field(default_factory=list)
    projection_version: int
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class RiskModelRunRequest(BaseModel):
    company_id: str
    period_id: str
    scenario_id: str
    risk_ids: list[str] = Field(min_length=1)
    correlation_matrix: list[list[Decimal]]
    paths: int = Field(default=10_000, ge=100)
    seed: int = 42


class MarketRiskModelRunRequest(BaseModel):
    company_id: str
    period_id: str
    scenario_id: str
    model_type: MarketRiskModelType
    losses: list[float] = Field(default_factory=list)
    returns: list[float] = Field(default_factory=list)
    returns_matrix: list[list[float]] = Field(default_factory=list)
    realized_losses: list[float] = Field(default_factory=list)
    var_forecasts: list[float] = Field(default_factory=list)
    confidence: float = Field(default=0.99, gt=0.5, lt=1.0)
    method: MarketRiskVarMethod = MarketRiskVarMethod.HISTORICAL
    threshold_quantile: float = Field(default=0.95, ge=0.90, lt=0.995)
    significance: float = Field(default=0.05, gt=0.0, lt=1.0)

    def execution_payload(self) -> dict[str, Any]:
        return {
            "losses": tuple(self.losses),
            "returns": tuple(self.returns),
            "returns_matrix": tuple(tuple(row) for row in self.returns_matrix),
            "realized_losses": tuple(self.realized_losses),
            "var_forecasts": tuple(self.var_forecasts),
            "confidence": self.confidence,
            "method": self.method.value,
            "threshold_quantile": self.threshold_quantile,
            "significance": self.significance,
        }
