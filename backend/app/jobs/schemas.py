from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.infrastructure.jobs import JobStatus


class JobCreateRequest(BaseModel):
    model_id: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    input_snapshot_id: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    random_seed: int | None = None


class JobResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    progress: float
    attempt: int
    created_at: datetime
    updated_at: datetime
    run_id: UUID | None
    error_message: str | None
