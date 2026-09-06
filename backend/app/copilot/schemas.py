from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field

from app.copilot.ai_foundry import (
    AIWorkload,
    CopilotRequest,
    FinanceModule,
)
from app.shared.rbac import Principal, Role


class PrincipalPayload(BaseModel):
    user_id: str = Field(min_length=1)
    roles: list[Role] = Field(min_length=1)
    company_scopes: list[str] = Field(default_factory=list)


class GroundedFactPayload(BaseModel):
    fact_id: str = Field(min_length=1)
    value: str
    source_ref: str = Field(min_length=1)
    approved: bool = True
    company: str | None = None


class CopilotRequestPayload(BaseModel):
    module: FinanceModule
    workload: AIWorkload
    question: str = Field(min_length=1)
    facts: list[GroundedFactPayload] = Field(min_length=1)
    principal: PrincipalPayload


class CopilotSessionRequest(BaseModel):
    module: FinanceModule = FinanceModule.GENERAL
    workload: AIWorkload = AIWorkload.GENERAL_QA
    company_id: str
    period_id: str
    scenario_id: str


class CopilotMessageRequest(BaseModel):
    question: str = Field(min_length=1)


@dataclass(frozen=True, slots=True)
class _Session:
    session_id: str
    principal: Principal
    request: CopilotRequest
