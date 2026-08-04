from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from .calibration import CalibrationResult
from .simulation import SimulationOutput

PERCENTILES = [5, 25, 50, 75, 95]


def build_horizon_summary(output: SimulationOutput, years: int) -> pd.DataFrame:
    horizons = sorted({1, 5, 15, years})
    rows: list[dict[str, float | int]] = []
    for horizon in horizons:
        month = min(horizon * 12, output.values.shape[1] - 1)
        terminal = output.values[:, month]
        terminal_real = output.real_values[:, month]
        paid_in = float(output.paid_in[month])
        q = np.percentile(terminal, PERCENTILES)
        q_real = np.percentile(terminal_real, PERCENTILES)
        shortfall = paid_in - terminal
        losses = shortfall[shortfall > 0]
        var95 = float(np.percentile(shortfall, 95))
        es95_threshold = np.percentile(shortfall, 95)
        es95 = float(shortfall[shortfall >= es95_threshold].mean())
        rows.append(
            {
                "horizon_years": horizon,
                "paid_in_capital": paid_in,
                "p05_nominal": q[0],
                "p25_nominal": q[1],
                "median_nominal": q[2],
                "p75_nominal": q[3],
                "p95_nominal": q[4],
                "p05_real": q_real[0],
                "median_real": q_real[2],
                "p95_real": q_real[4],
                "prob_below_paid_in": float(np.mean(terminal < paid_in)),
                "terminal_var95_vs_paid_in": max(var95, 0.0),
                "terminal_es95_vs_paid_in": max(es95, 0.0),
                "mean_shortfall_if_any": float(losses.mean()) if len(losses) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def build_path_percentiles(output: SimulationOutput) -> pd.DataFrame:
    q = np.percentile(output.values, PERCENTILES, axis=0)
    q_real = np.percentile(output.real_values, PERCENTILES, axis=0)
    return pd.DataFrame(
        {
            "month": np.arange(output.values.shape[1]),
            "paid_in_capital": output.paid_in,
            "p05_nominal": q[0],
            "p25_nominal": q[1],
            "median_nominal": q[2],
            "p75_nominal": q[3],
            "p95_nominal": q[4],
            "p05_real": q_real[0],
            "median_real": q_real[2],
            "p95_real": q_real[4],
        }
    )


def export_results(
    output_dir: Path,
    calibration: CalibrationResult,
    horizon_summary: pd.DataFrame,
    path_percentiles: pd.DataFrame,
    manifest: dict[str, object],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    horizon_summary.to_csv(output_dir / "horizon-summary.csv", index=False)
    path_percentiles.to_csv(output_dir / "path-percentiles.csv", index=False)
    (output_dir / "calibration.json").write_text(
        json.dumps(asdict(calibration), indent=2), encoding="utf-8"
    )
    (output_dir / "run-manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8"
    )
