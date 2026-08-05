from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Annotated

import numpy as np
import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .calibration import CalibrationResult, calibrate
from .charts import (
    export_percentile_chart,
    export_regime_probability_chart,
    export_transition_heatmap,
)
from .data import load_price_csv, to_monthly_returns
from .diagnostics import compare_distribution_fits, rolling_origin_backtest
from .models import AppConfig, SimulationMethod
from .regime import calibrate_regime_model, export_regime_results
from .reporting import build_horizon_summary, build_path_percentiles, export_results
from .risk import path_risk_metrics, summarize_risk_metrics
from .simulation import generate_log_returns, simulate_portfolio
from .stress import sensitivity_grid
from .tax import GermanTaxPolicy, apply_terminal_tax

app = typer.Typer(help="ETF calibration and Monte Carlo planning CLI")
config_app = typer.Typer(help="Configuration utilities")
app.add_typer(config_app, name="config")
console = Console()


def _load_config(path: Path) -> AppConfig:
    return AppConfig.model_validate_json(path.read_text(encoding="utf-8"))


def _historical_returns(cfg: AppConfig) -> tuple[np.ndarray, np.ndarray]:
    if cfg.data.csv_path is None:
        raise typer.BadParameter("This command requires data.csv_path")
    prices = load_price_csv(cfg.data.csv_path, cfg.data.date_column, cfg.data.price_column)
    returns = to_monthly_returns(prices)
    if cfg.calibration.lookback_years:
        count = cfg.calibration.lookback_years * 12
        return (
            returns.simple_returns.tail(count).to_numpy(),
            returns.log_returns.tail(count).to_numpy(),
        )
    return returns.simple_returns.to_numpy(), returns.log_returns.to_numpy()


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
    simple_returns: np.ndarray | None = None
    regime_calibration = None

    if cfg.data.csv_path:
        simple_returns, historical_log_returns = _historical_returns(cfg)
        calibration = calibrate(
            simple_returns,
            historical_log_returns,
            assumed_annual_return=cfg.calibration.assumed_annual_return,
            mean_shrinkage_months=cfg.calibration.mean_shrinkage_months,
        )
        if cfg.simulation.method == SimulationMethod.MARKOV_REGIME:
            regime_calibration = calibrate_regime_model(
                historical_log_returns,
                cfg.simulation.regime,
                seed=cfg.simulation.seed,
            )
    else:
        if cfg.simulation.method in {
            SimulationMethod.HISTORICAL_BOOTSTRAP,
            SimulationMethod.BLOCK_BOOTSTRAP,
            SimulationMethod.MARKOV_REGIME,
        }:
            raise typer.BadParameter(f"{cfg.simulation.method.value} requires data.csv_path")
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
        regime_calibration=regime_calibration,
        regime_config=cfg.simulation.regime,
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

    metrics = path_risk_metrics(
        log_returns,
        annual_risk_free_rate=cfg.risk.annual_risk_free_rate,
        annual_omega_threshold=cfg.risk.annual_omega_threshold,
        confidence_level=cfg.risk.confidence_level,
    )
    pd.DataFrame(summarize_risk_metrics(metrics)).to_csv(
        cfg.output_dir / "risk-summary.csv", index=False
    )

    tax_policy = GermanTaxPolicy(**cfg.tax.model_dump())
    after_tax, taxes = apply_terminal_tax(output.values[:, -1], output.paid_in[-1], tax_policy)
    tax_summary = {
        "enabled": tax_policy.enabled,
        "median_tax": float(np.median(taxes)),
        "median_terminal_after_tax": float(np.median(after_tax)),
        "model_scope": "simplified terminal-gain taxation only",
    }
    (cfg.output_dir / "tax-summary.json").write_text(
        json.dumps(tax_summary, indent=2), encoding="utf-8"
    )

    if simple_returns is not None and cfg.diagnostics.enabled:
        compare_distribution_fits(
            historical_log_returns,
            monte_carlo_samples=cfg.diagnostics.monte_carlo_samples,
            seed=cfg.simulation.seed,
        ).to_csv(cfg.output_dir / "distribution-fit.csv", index=False)
        if historical_log_returns.size > cfg.diagnostics.rolling_training_months:
            rolling_origin_backtest(
                historical_log_returns,
                training_window=cfg.diagnostics.rolling_training_months,
                confidence_level=cfg.diagnostics.interval_coverage,
            ).to_csv(cfg.output_dir / "coverage-backtest.csv", index=False)

    if regime_calibration is not None and cfg.simulation.regime.export_diagnostics:
        export_regime_results(cfg.output_dir, regime_calibration)

    if cfg.output.export_charts:
        export_percentile_chart(paths, cfg.output_dir / "percentile-paths.png")
        if regime_calibration is not None:
            export_regime_probability_chart(
                regime_calibration, cfg.output_dir / "regime-probabilities.png"
            )
            export_transition_heatmap(
                regime_calibration, cfg.output_dir / "regime-transition-heatmap.png"
            )

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
    if regime_calibration is not None:
        console.print(
            "Regime fit: "
            f"normal vol={regime_calibration.standard_deviations[0] * np.sqrt(12):.1%}, "
            f"crisis vol={regime_calibration.standard_deviations[1] * np.sqrt(12):.1%}, "
            f"crisis duration={regime_calibration.expected_durations_months[1]:.1f} months"
        )
    console.print(f"Results written to [bold]{cfg.output_dir}[/bold]")


@app.command("regime-diagnose")
def regime_diagnose(
    config: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
) -> None:
    cfg = _load_config(config)
    _, log_returns = _historical_returns(cfg)
    result = calibrate_regime_model(
        log_returns,
        cfg.simulation.regime,
        seed=cfg.simulation.seed,
    )
    export_regime_results(cfg.output_dir, result)
    if cfg.output.export_charts:
        export_regime_probability_chart(result, cfg.output_dir / "regime-probabilities.png")
        export_transition_heatmap(result, cfg.output_dir / "regime-transition-heatmap.png")
    table = Table(title="Markov Regime Diagnostics")
    table.add_column("Regime")
    table.add_column("Annual mean", justify="right")
    table.add_column("Annual volatility", justify="right")
    table.add_column("Occupancy", justify="right")
    table.add_column("Expected duration", justify="right")
    for index, label in enumerate(("normal", "crisis")):
        table.add_row(
            label,
            f"{result.means[index] * 12:.2%}",
            f"{result.standard_deviations[index] * np.sqrt(12):.2%}",
            f"{result.occupancy[index]:.1%}",
            f"{result.expected_durations_months[index]:.1f} months",
        )
    console.print(table)
    console.print(f"Log likelihood: {result.log_likelihood:.3f}")
    console.print(f"AIC: {result.aic:.3f}; BIC: {result.bic:.3f}")


@app.command()
def diagnose(
    config: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
) -> None:
    cfg = _load_config(config)
    _, log_returns = _historical_returns(cfg)
    result = compare_distribution_fits(
        log_returns,
        monte_carlo_samples=cfg.diagnostics.monte_carlo_samples,
        seed=cfg.simulation.seed,
    )
    console.print(result.to_string(index=False))


@app.command()
def backtest(
    config: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
) -> None:
    cfg = _load_config(config)
    _, log_returns = _historical_returns(cfg)
    result = rolling_origin_backtest(
        log_returns,
        training_window=cfg.diagnostics.rolling_training_months,
        confidence_level=cfg.diagnostics.interval_coverage,
    )
    console.print(result.to_string(index=False))


@app.command()
def sensitivity(
    config: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
) -> None:
    cfg = _load_config(config)
    grid = sensitivity_grid(
        initial_value=cfg.portfolio.initial_value,
        monthly_contribution=cfg.portfolio.monthly_contribution,
        years=cfg.simulation.years,
        annual_returns=[0.03, 0.05, 0.07, 0.09],
        annual_inflations=[0.01, 0.02, 0.03],
    )
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    grid.to_csv(cfg.output_dir / "sensitivity-grid.csv", index=False)
    console.print(grid.to_string(index=False))


@app.command()
def wizard(
    output: Annotated[Path, typer.Option(help="Output JSON path")] = Path("config.json"),
) -> None:
    config = AppConfig()
    config.portfolio.initial_value = typer.prompt(
        "Current portfolio value", default=config.portfolio.initial_value, type=float
    )
    config.portfolio.monthly_contribution = typer.prompt(
        "Monthly contribution", default=config.portfolio.monthly_contribution, type=float
    )
    config.simulation.years = typer.prompt(
        "Planning horizon in years", default=config.simulation.years, type=int
    )
    config.simulation.paths = typer.prompt(
        "Simulation paths", default=config.simulation.paths, type=int
    )
    if typer.confirm("Use Markov regime simulation?", default=False):
        config.simulation.method = SimulationMethod.MARKOV_REGIME
        config.simulation.regime.enabled = True
    config.tax.enabled = typer.confirm("Enable simplified German tax model?", default=False)
    output.write_text(config.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"Wrote configuration to [bold]{output}[/bold]")


@app.command()
def version() -> None:
    console.print(json.dumps({"version": __version__}, indent=2))


if __name__ == "__main__":
    app()
