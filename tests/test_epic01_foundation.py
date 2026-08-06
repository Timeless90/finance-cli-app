from __future__ import annotations

import time
from typing import cast

import numpy as np
from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.api.settings import ApiSettings
from cfo_platform.composition import build_container
from cfo_platform.quant.interfaces import QuantModelInput
from cfo_platform.quant.legacy_portfolio import LegacyPortfolioSimulationModel
from finance_cli.calibration import CalibrationResult
from finance_cli.models import ContributionTiming, SimulationMethod
from finance_cli.simulation import generate_log_returns, simulate_portfolio


def _settings() -> ApiSettings:
    return ApiSettings(environment="test", build_version="test")


def test_versioned_module_foundations_are_available() -> None:
    container = build_container()
    with TestClient(create_app(_settings(), container)) as client:
        assert client.get("/api/v1/forecast").json()["module"] == "forecast"
        assert client.get("/api/v1/risk").json()["module"] == "risk"
        assert client.get("/api/v1/data").json()["module"] == "data"


def test_background_job_is_non_blocking_and_reproducible() -> None:
    container = build_container()
    with TestClient(create_app(_settings(), container)) as client:
        response = client.post(
            "/api/v1/jobs",
            json={
                "model_id": "echo-forecast",
                "model_version": "1.0.0",
                "input_snapshot_id": "snapshot-001",
                "parameters": {"revenue": 100.0},
                "random_seed": 42,
            },
        )
        assert response.status_code == 202
        job_id = response.json()["job_id"]
        terminal = None
        for _ in range(50):
            terminal = client.get(f"/api/v1/jobs/{job_id}").json()
            if terminal["status"] in {"succeeded", "failed", "cancelled"}:
                break
            time.sleep(0.01)
        assert terminal is not None
        assert terminal["status"] == "succeeded"
        result = container.run_repository.get_result(terminal["run_id"])
        assert result is not None
        assert result.outputs["random_seed"] == 42
        assert result.outputs["parameters"] == {"revenue": 100.0}


def test_job_cancel_and_resume_contract() -> None:
    container = build_container()
    record = container.job_manager.submit(
        __import__("cfo_platform.application.services", fromlist=["ModelRunCommand"]).ModelRunCommand(
            model_id="echo-forecast",
            model_version="1.0.0",
            input_snapshot_id="snapshot-002",
            parameters={},
            random_seed=7,
        )
    )
    cancelled = container.job_manager.cancel(record.job_id)
    assert cancelled is not None
    resumed = container.job_manager.resume(record.job_id)
    assert resumed is not None
    assert resumed.attempt in {1, 2}
    container.shutdown()


def test_legacy_adapter_matches_existing_simulation() -> None:
    calibration = CalibrationResult(
        observations=120,
        annualized_log_mean_raw=0.06,
        annualized_log_mean_shrunk=0.05,
        annualized_log_volatility=0.15,
        monthly_log_mean_raw=0.06 / 12.0,
        monthly_log_mean_shrunk=0.05 / 12.0,
        monthly_log_volatility=0.15 / np.sqrt(12.0),
        student_t_df=8.0,
        student_t_location=0.0,
        student_t_scale=0.04,
    )
    parameters = {
        "method": "normal",
        "n_paths": 50,
        "n_months": 24,
        "block_length": 12,
        "student_t_df": None,
        "initial_value": 1000.0,
        "monthly_contribution": 100.0,
        "contribution_timing": "month_end",
        "annual_inflation": 0.02,
        "annual_external_fee": 0.001,
    }
    direct_returns = generate_log_returns(
        method=SimulationMethod.NORMAL,
        calibration=calibration,
        historical_log_returns=None,
        n_paths=50,
        n_months=24,
        seed=123,
        block_length=12,
        student_t_df=None,
    )
    direct = simulate_portfolio(
        direct_returns,
        initial_value=1000.0,
        monthly_contribution=100.0,
        timing=ContributionTiming.MONTH_END,
        annual_inflation=0.02,
        annual_external_fee=0.001,
    )
    adapted = LegacyPortfolioSimulationModel().execute(
        QuantModelInput(
            values={"calibration": calibration, "historical_log_returns": None},
            parameters=parameters,
            random_seed=123,
        )
    )
    np.testing.assert_allclose(cast(np.ndarray, adapted.values["values"]), direct.values)
    np.testing.assert_allclose(cast(np.ndarray, adapted.values["paid_in"]), direct.paid_in)
