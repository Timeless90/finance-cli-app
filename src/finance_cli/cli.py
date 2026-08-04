from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Annotated

import numpy as np
import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .calibration import CalibrationResult, calibrate
from .data import load_price_csv, to_monthly_returns
from .models import AppConfig, SimulationMethod
from .reporting import build_horizon_summary, build_path_percentiles, export_results
from .simulation import generate_log_returns, simulate_portfolio

app = typer.Typer(help="ETF calibration and Monte Carlo planning CLI")
config_app = typer.Typer(help="Configuration utilities")
app.add_typer(config_app, name="config")
console = Console()


def _load_config(path: Path) -> AppConfig:
    return AppConfig.model_validate_json(path.read_text(encoding="utf-8"))


def _fallback_calibration(config: AppConfig) -> CalibrationResult:
    assumed_monthly_log = np.log1p(config.calibration.assumed_annual_return) / 12.0
    return CalibrationResult(
        n_obs=0,
        monthly_log_mean_historical=assumed_monthly_log,
        monthly_log_mean_assumed=assumed_monthly_log,
        monthly_log_mean_shrunk=assumed_monthly_log,
        monthly_log_volatility=0.15 / np.sqrt(12.0),
        annual_geometric_return_historical=config.calibration.assumed_annual_return,
        annual_geometric_return_shrunk=config.calibration.assumed_annual_return,
        annual_volatility=0.15,
        simple_return_skewness=0.0,
        simple_return_excess_kurtosis=0.0,
        student_t_df=8.0,
    )


@config_app.command("example")
def write_example_config(
    output: Annotated[Path, typer.Option(help="Output JSON path")] = Path(
        "config.example.json"
    ),
) -> None:
    config = AppConfig()
    output.write_text(config.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"Wrote example configuration to [bold]{output}[/bold]")


@app.command()
def simulate(
    config: Annotated[
        Path,
        typer.Option(exists=True, dir_okay=False, help="JSON config path"),
    ],
) -> None:
    cfg = _load_config(config)
    historical_log_returns: np.ndarray | None = None

    if cfg.data.csv_path:
        prices = load_price_csv(
            cfg.data.csv_path, cfg.data.date_column, cfg.data.price_column
        )
        returns = to_monthly_returns(prices)
        if cfg.calibration.lookback_years:
            count = cfg.calibration.lookback_years * 12
            simple = returns.simple_returns.tail(count).to_numpy()
            log = returns.log_returns.tail(count).to_numpy()
        else:
            simple = returns.simple_returns.to_numpy()
            log = returns.log_returns.to_numpy()
        calibration = calibrate(
            simple,
            log,
            assumed_annual_return=cfg.calibration.assumed_annual_return,
            mean_shrinkage_months=cfg.calibration.mean_shrinkage_months,
        )
        historical_log_returns = log
    else:
        if cfg.simulation.method in {
            SimulationMethod.HISTORICAL_BOOTSTRAP,
            SimulationMethod.BLOCK_BOOTSTRAP,
        }:
            raise typer.BadParameter("Bootstrap methods require data.csv_path")
        calibration = _fallback_calibration(cfg)

    n_months = cfg.simulation.years * 12
    log_returns = generate_log_returns(
        method=cfg.simulation.method,
        calibration=calibration,
        historical_log_returns=historical_log_returns,
        n_paths=cfg.simulation.paths,
        n_months=n_months,
        seed=cfg.simulation.seed,
        block_length=cfg.simulation.block_length_months,
        student_t_df=cfg.simulation.student_t_degrees_of_freedom,
    )
    output = simulate_portfolio(
        log_returns,
        initial_value=cfg.portfolio.initial_value,
        monthly_contribution=cfg.portfolio.monthly_contribution,
        timing=cfg.portfolio.contribution_timing,
        annual_inflation=cfg.portfolio.annual_inflation,
        annual_external_fee=cfg.portfolio.annual_external_fee,
    )
    horizon = build_horizon_summary(output, cfg.simulation.years)
    paths = build_path_percentiles(output)
    manifest = {
        "finance_cli_version": __version__,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "method": cfg.simulation.method,
        "seed": cfg.simulation.seed,
        "paths": cfg.simulation.paths,
        "months": n_months,
        "config": cfg.model_dump(mode="json"),
    }
    export_results(cfg.output_dir, calibration, horizon, paths, manifest)

    table = Table(title="ETF Simulation Summary")
    table.add_column("Years", justify="right")
    table.add_column("Paid in", justify="right")
    table.add_column("P5", justify="right")
    table.add_column("Median", justify="right")
    table.add_column("P95", justify="right")
    table.add_column("P(< paid in)", justify="right")
    for row in horizon.to_dict(orient="records"):
        table.add_row(
            str(row["horizon_years"]),
            f"€{row['paid_in_capital']:,.0f}",
            f"€{row['p05_nominal']:,.0f}",
            f"€{row['median_nominal']:,.0f}",
            f"€{row['p95_nominal']:,.0f}",
            f"{row['prob_below_paid_in']:.1%}",
        )
    console.print(table)
    console.print(f"Results written to [bold]{cfg.output_dir}[/bold]")


@app.command()
def version() -> None:
    console.print(json.dumps({"version": __version__}, indent=2))


if __name__ == "__main__":
    app()
