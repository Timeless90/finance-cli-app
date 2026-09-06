from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.governance.governance_catalog import (
    ScenarioKind,
)


class RunCreateRequest(BaseModel):
    model_id: str
    model_version: str
    code_version: str
    snapshot_id: str
    parameters: dict[str, Any]
    random_seed: int
    output: dict[str, Any] | None = None


class TransitionRequest(BaseModel):
    reason: str = Field(min_length=1)


class ScenarioCreateRequest(BaseModel):
    name: str
    kind: ScenarioKind
    assumptions: list[dict[str, Any]]


class ModelCreateRequest(BaseModel):
    model_id: str
    version: str
    owner: str
    description: str
    limitations: list[str] = []
