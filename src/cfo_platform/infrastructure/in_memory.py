from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from uuid import UUID

from cfo_platform.application.ports import (
    ModelExecutionRequest,
    ModelExecutionResult,
    ModelRunRepository,
    ModelRunStatus,
)
from cfo_platform.quant.interfaces import QuantModelInput
from cfo_platform.quant.registry import QuantModelRegistry


class InMemoryModelRunRepository(ModelRunRepository):
    def __init__(self) -> None:
        self._requests: dict[UUID, ModelExecutionRequest] = {}
        self._results: dict[UUID, ModelExecutionResult] = {}
        self._lock = RLock()

    def save_request(self, request: ModelExecutionRequest) -> None:
        with self._lock:
            self._requests[request.run_id] = request

    def save_result(self, result: ModelExecutionResult) -> None:
        with self._lock:
            self._results[result.run_id] = result

    def get_result(self, run_id: UUID) -> ModelExecutionResult | None:
        with self._lock:
            return self._results.get(run_id)

    def get_request(self, run_id: UUID) -> ModelExecutionRequest | None:
        with self._lock:
            return self._requests.get(run_id)


class RegisteredModelExecutor:
    def __init__(self, registry: QuantModelRegistry) -> None:
        self._registry = registry

    def execute(self, request: ModelExecutionRequest) -> ModelExecutionResult:
        started_at = datetime.now(UTC)
        try:
            model = self._registry.get(request.model_id, request.model_version)
            output = model.execute(
                QuantModelInput(
                    values={},
                    parameters=request.parameters,
                    random_seed=request.random_seed,
                )
            )
            status = ModelRunStatus.SUCCEEDED
            outputs = output.values
            error_message = None
        except Exception as exc:  # noqa: BLE001 - boundary translates model failures
            status = ModelRunStatus.FAILED
            outputs = {}
            error_message = str(exc)
        return ModelExecutionResult(
            run_id=request.run_id,
            status=status,
            outputs=outputs,
            started_at=started_at,
            completed_at=datetime.now(UTC),
            error_message=error_message,
        )
