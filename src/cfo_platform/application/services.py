from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from uuid import UUID, uuid4

from .ports import (
    ModelExecutionRequest,
    ModelExecutionResult,
    ModelExecutor,
    ModelRunRepository,
)


@dataclass(frozen=True, slots=True)
class ModelRunCommand:
    model_id: str
    model_version: str
    input_snapshot_id: str
    parameters: Mapping[str, object]
    random_seed: int | None = None

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id must not be empty")
        if not self.model_version.strip():
            raise ValueError("model_version must not be empty")
        if not self.input_snapshot_id.strip():
            raise ValueError("input_snapshot_id must not be empty")


@dataclass(frozen=True, slots=True)
class ModelRunReceipt:
    run_id: UUID
    result: ModelExecutionResult


class ExecuteModelRun:
    def __init__(self, executor: ModelExecutor, repository: ModelRunRepository) -> None:
        self._executor = executor
        self._repository = repository

    def execute(self, command: ModelRunCommand) -> ModelRunReceipt:
        request = ModelExecutionRequest(
            run_id=uuid4(),
            model_id=command.model_id,
            model_version=command.model_version,
            input_snapshot_id=command.input_snapshot_id,
            parameters=command.parameters,
            random_seed=command.random_seed,
        )
        self._repository.save_request(request)
        result = self._executor.execute(request)
        if result.run_id != request.run_id:
            raise ValueError("Model executor returned a result for a different run")
        self._repository.save_result(result)
        return ModelRunReceipt(run_id=request.run_id, result=result)
