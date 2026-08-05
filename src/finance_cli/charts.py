from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


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
