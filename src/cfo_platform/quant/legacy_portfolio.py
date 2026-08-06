from __future__ import annotations

from typing import cast

import numpy as np

from finance_cli.calibration import CalibrationResult
from finance_cli.models import ContributionTiming, SimulationMethod
from finance_cli.simulation import generate_log_returns, simulate_portfolio

from .interfaces import QuantModelInput, QuantModelOutput


class LegacyPortfolioSimulationModel:
    """Adapter exposing the existing ETF simulation through the generic model contract."""

    model_id = "legacy-portfolio-simulation"
    model_version = "1.0.0"

    def execute(self, model_input: QuantModelInput) -> QuantModelOutput:
        values = model_input.values
        parameters = model_input.parameters
        calibration = cast(CalibrationResult, values["calibration"])
        historical = cast(np.ndarray | None, values.get("historical_log_returns"))
        method = SimulationMethod(str(parameters["method"]))
        seed = model_input.random_seed
        if seed is None:
            raise ValueError("legacy portfolio simulation requires a random seed")

        log_returns = generate_log_returns(
            method=method,
            calibration=calibration,
            historical_log_returns=historical,
            n_paths=int(parameters["n_paths"]),
            n_months=int(parameters["n_months"]),
            seed=seed,
            block_length=int(parameters.get("block_length", 12)),
            student_t_df=cast(float | None, parameters.get("student_t_df")),
        )
        output = simulate_portfolio(
            log_returns,
            initial_value=float(parameters["initial_value"]),
            monthly_contribution=float(parameters["monthly_contribution"]),
            timing=ContributionTiming(str(parameters["contribution_timing"])),
            annual_inflation=float(parameters.get("annual_inflation", 0.0)),
            annual_external_fee=float(parameters.get("annual_external_fee", 0.0)),
        )
        return QuantModelOutput(
            values={
                "log_returns": log_returns,
                "values": output.values,
                "paid_in": output.paid_in,
                "real_values": output.real_values,
            }
        )
