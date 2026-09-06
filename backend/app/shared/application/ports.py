from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class ModelRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class ModelExecutionRequest:
    run_id: UUID
    model_id: str
    model_version: str
    input_snapshot_id: str
    parameters: Mapping[str, object]
    random_seed: int | None


@dataclass(frozen=True, slots=True)
class ModelExecutionResult:
    run_id: UUID
    status: ModelRunStatus
    outputs: Mapping[str, object]
    started_at: datetime
    completed_at: datetime
    error_message: str | None = None


class ModelExecutor(Protocol):
    def execute(self, request: ModelExecutionRequest) -> ModelExecutionResult: ...


class ModelRunRepository(Protocol):
    def save_request(self, request: ModelExecutionRequest) -> None: ...

    def save_result(self, result: ModelExecutionResult) -> None: ...

    def get_result(self, run_id: UUID) -> ModelExecutionResult | None: ...
