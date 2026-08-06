from __future__ import annotations

from .interfaces import QuantModelInput, QuantModelOutput


class EchoForecastModel:
    """Small deterministic model used to validate orchestration and job contracts."""

    model_id = "echo-forecast"
    model_version = "1.0.0"

    def execute(self, model_input: QuantModelInput) -> QuantModelOutput:
        return QuantModelOutput(
            values={
                "parameters": dict(model_input.parameters),
                "random_seed": model_input.random_seed,
            }
        )
