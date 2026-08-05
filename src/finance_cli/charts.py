from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .regime import RegimeCalibrationResult


def export_percentile_chart(path_percentiles: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    years = path_percentiles["month"] / 12.0
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.fill_between(
        years,
        path_percentiles["p05_nominal"],
        path_percentiles["p95_nominal"],
        alpha=0.2,
        label="P5-P95",
    )
    axis.fill_between(
        years,
        path_percentiles["p25_nominal"],
        path_percentiles["p75_nominal"],
        alpha=0.3,
        label="P25-P75",
    )
    axis.plot(years, path_percentiles["median_nominal"], label="Median")
    axis.plot(years, path_percentiles["paid_in_capital"], linestyle="--", label="Paid in")
    axis.set_xlabel("Years")
    axis.set_ylabel("Portfolio value")
    axis.set_title("Monte Carlo percentile paths")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def export_regime_probability_chart(
    result: RegimeCalibrationResult, output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    months = np.arange(result.smoothed_probabilities.shape[0])
    figure, axis = plt.subplots(figsize=(11, 4.5))
    axis.plot(months, result.smoothed_probabilities[:, 1], label="Crisis probability")
    axis.set_ylim(0.0, 1.0)
    axis.set_xlabel("Historical month")
    axis.set_ylabel("Probability")
    axis.set_title("Smoothed crisis-regime probability")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def export_transition_heatmap(
    result: RegimeCalibrationResult, output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(5, 4))
    image = axis.imshow(result.transition_matrix, vmin=0.0, vmax=1.0)
    axis.set_xticks([0, 1], labels=["Normal", "Crisis"])
    axis.set_yticks([0, 1], labels=["Normal", "Crisis"])
    axis.set_xlabel("To regime")
    axis.set_ylabel("From regime")
    axis.set_title("Regime transition matrix")
    for row in range(2):
        for column in range(2):
            axis.text(
                column,
                row,
                f"{result.transition_matrix[row, column]:.3f}",
                ha="center",
                va="center",
            )
    figure.colorbar(image, ax=axis)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
