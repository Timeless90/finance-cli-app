from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.decisions.decision_workflow import (
    DecisionRunKind,
)


class DecisionContextRequest(BaseModel):
    company_id: str
    period_id: str
    scenario_id: str
    source_snapshot_ids: list[str] = Field(min_length=1)
    projection_version: int = Field(default=1, ge=1)
    model_version: str = Field(min_length=1)


class ActionDecisionRunRequest(DecisionContextRequest):
    action_ids: list[str] = Field(min_length=1)
    kind: DecisionRunKind


class ActionBenefitTrackingRunRequest(DecisionContextRequest):
    action_ids: list[str] = Field(min_length=1)


class CapitalDecisionRunRequest(DecisionContextRequest):
    candidate_ids: list[str] = Field(min_length=1)


class CapitalMonteCarloRunRequest(CapitalDecisionRunRequest):
    paths: int = Field(default=10_000, ge=100)
    seed: int = 42
    cash_flow_volatility: float = Field(default=0.15, ge=0.0)
    risk_event_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_event_impact: float = 0.0
    scenario_multiplier: float = Field(default=1.0, gt=0.0)


class CapitalAllocationRunRequest(CapitalDecisionRunRequest):
    strategic_weight: float = 0.0


class FundingScenarioRunRequest(DecisionContextRequest):
    funding_option_id: str = Field(min_length=1)


class RejectDecisionRunRequest(BaseModel):
    reason: str = Field(min_length=1)


class DecisionContextResponse(BaseModel):
    company_id: str
    company_label: str
    period_id: str
    period_label: str
    scenario_id: str
    scenario_label: str
    currency: str | None


class DecisionRunResponse(BaseModel):
    run_id: str
    kind: DecisionRunKind
    status: str
    context: DecisionContextResponse
    references: list[str]
    source_snapshot_ids: list[str]
    projection_version: int
    model_version: str
    parameters: dict[str, Any]
    result: dict[str, Any]
    created_by: str
    created_at: datetime
    validated_by: str | None = None
    approved_by: str | None = None
    rejected_by: str | None = None
    rejection_reason: str | None = None


class DecisionRunEventResponse(BaseModel):
    event_type: str
    actor: str
    correlation_id: str
    occurred_at: datetime
    reason: str | None = None
