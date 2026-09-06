from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.actions.action_management import (
    ActionStatus,
    ImpactMetric,
)


class ActionImpactPayload(BaseModel):
    period: int = Field(ge=1)
    metric: ImpactMetric
    amount: Decimal
    impact_key: str
    covenant_id: str | None = None


class ActionRequest(BaseModel):
    action_id: str
    title: str
    owner: str
    due_period: int = Field(ge=1)
    cost: Decimal = Field(ge=0)
    impacts: list[ActionImpactPayload]
    confidence: Decimal = Field(default=Decimal(1), ge=0, le=1)
    status: ActionStatus = ActionStatus.DRAFT
    description: str = ""


class ActionSelectionRequest(BaseModel):
    action_ids: list[str]


class StatusChangeRequest(BaseModel):
    status: ActionStatus


class ReviewRequest(BaseModel):
    current_period: int = Field(ge=1)


class BenefitObservationPayload(BaseModel):
    action_id: str
    metric: ImpactMetric
    period: int = Field(ge=1)
    planned_amount: Decimal
    realized_amount: Decimal
    covenant_id: str | None = None


class BenefitTrackingRequest(BaseModel):
    observations: list[BenefitObservationPayload]
