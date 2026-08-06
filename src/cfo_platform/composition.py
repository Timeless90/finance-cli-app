from __future__ import annotations

from dataclasses import dataclass

from cfo_platform.application.services import ExecuteModelRun
from cfo_platform.infrastructure.in_memory import (
    InMemoryModelRunRepository,
    RegisteredModelExecutor,
)
from cfo_platform.infrastructure.jobs import InMemoryJobManager
from cfo_platform.quant.builtin import EchoForecastModel
from cfo_platform.quant.legacy_portfolio import LegacyPortfolioSimulationModel
from cfo_platform.quant.registry import QuantModelRegistry


@dataclass(slots=True)
class ApplicationContainer:
    model_registry: QuantModelRegistry
    run_repository: InMemoryModelRunRepository
    model_executor: RegisteredModelExecutor
    execute_model_run: ExecuteModelRun
    job_manager: InMemoryJobManager

    def shutdown(self) -> None:
        self.job_manager.shutdown()


def build_container() -> ApplicationContainer:
    registry = QuantModelRegistry(
        [EchoForecastModel(), LegacyPortfolioSimulationModel()]
    )
    repository = InMemoryModelRunRepository()
    executor = RegisteredModelExecutor(registry)
    service = ExecuteModelRun(executor, repository)
    jobs = InMemoryJobManager(service)
    return ApplicationContainer(
        model_registry=registry,
        run_repository=repository,
        model_executor=executor,
        execute_model_run=service,
        job_manager=jobs,
    )
