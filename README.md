# Finance CLI App

Production-ready Python CLI for ETF calibration, Monte Carlo simulation, risk analysis, and long-term investment planning.

## Features

- Statistical calibration from historical ETF price data
- Monthly simple and logarithmic return calculation
- Normal and Student-t Monte Carlo simulation
- Historical bootstrap and moving-block bootstrap
- Monthly savings contributions with configurable timing
- Inflation and external fee handling
- Percentile analysis, shortfall probability, VaR, and Expected Shortfall
- Per-path risk metrics: Sharpe, Sortino, Omega, max drawdown, Ulcer Index
- Simplified German terminal-gain tax model
- Distribution goodness-of-fit diagnostics and rolling-origin coverage backtest
- Deterministic sensitivity grid across return and inflation assumptions
- Percentile path chart export
- CSV and JSON result exports
- Reproducible simulations through deterministic random seeds
- Interactive configuration wizard

## Requirements

- Python 3.11 or 3.12
- Git

## Installation

Clone the repository and create an isolated Python environment:

```bash
git clone https://github.com/Timeless90/finance-cli-app.git
cd finance-cli-app

python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the application and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Verify the installation:

```bash
finance-cli version
```

## Quickstart without historical data

Generate an example configuration:

```bash
finance-cli config example --output config.json
```

Run the simulation:

```bash
finance-cli simulate --config config.json
```

Without historical data, the application uses the configured long-term return assumption and a fallback annual volatility of 15%. Bootstrap methods require historical data.

Use the interactive wizard to create a configuration by answering prompts:

```bash
finance-cli wizard --output config.json
```

## Configuration example

The following example models a current portfolio value of EUR 34,932.42, a monthly contribution of EUR 1,200, and a 30-year Student-t simulation with 10,000 paths:

```json
{
  "data": {
    "csv_path": null,
    "date_column": "date",
    "price_column": "price",
    "returns_are_net_of_fund_fees": true
  },
  "calibration": {
    "lookback_years": 10,
    "assumed_annual_return": 0.06,
    "mean_shrinkage_months": 60.0,
    "volatility_shrinkage_months": 36.0
  },
  "portfolio": {
    "initial_value": 34932.42,
    "monthly_contribution": 1200.0,
    "contribution_timing": "month_end",
    "annual_inflation": 0.02,
    "annual_external_fee": 0.0
  },
  "simulation": {
    "method": "student_t",
    "years": 30,
    "paths": 10000,
    "seed": 20260804,
    "block_length_months": 3,
    "student_t_degrees_of_freedom": null
  },
  "risk": {
    "annual_risk_free_rate": 0.02,
    "annual_omega_threshold": 0.0,
    "confidence_level": 0.95
  },
  "diagnostics": {
    "enabled": true,
    "rolling_training_months": 60,
    "interval_coverage": 0.90,
    "monte_carlo_samples": 999
  },
  "tax": {
    "enabled": false,
    "partial_exemption": 0.30,
    "saver_allowance": 1000.0,
    "capital_gains_tax_rate": 0.25,
    "solidarity_surcharge_rate": 0.055,
    "church_tax_rate": 0.0
  },
  "output": {
    "directory": "runs/latest",
    "export_charts": true
  }
}
```

Percentages are entered as decimal values. For example, `0.06` means 6% and `0.02` means 2%.

## Using historical ETF data

Provide a CSV file with at least one date column and one adjusted-price or total-return price column.

Example `data/etf-prices.csv`:

```csv
date,price
2021-01-29,72.15
2021-02-26,74.03
2021-03-31,77.18
2021-04-30,79.44
2021-05-31,78.92
2021-06-30,81.37
```

Update the `data` section in the configuration:

```json
{
  "data": {
    "csv_path": "data/etf-prices.csv",
    "date_column": "date",
    "price_column": "price",
    "returns_are_net_of_fund_fees": true
  }
}
```

The application sorts the observations, aggregates them to month-end prices, and calculates monthly simple and logarithmic returns.

For ETF analysis, use adjusted prices or total-return data whenever possible. Unadjusted prices can omit distributions and materially understate historical performance.

## Simulation methods

Set `simulation.method` to one of the following values:

| Method | Value | Historical data required | Description |
|---|---|---:|---|
| Normal | `normal` | No | Parametric normal log-return model |
| Student-t | `student_t` | No | Parametric heavy-tail model |
| Historical bootstrap | `historical_bootstrap` | Yes | Resamples individual historical monthly returns |
| Block bootstrap | `block_bootstrap` | Yes | Resamples consecutive return blocks to retain short-term dependence |

Example for moving-block bootstrap:

```json
{
  "simulation": {
    "method": "block_bootstrap",
    "years": 30,
    "paths": 25000,
    "seed": 20260804,
    "block_length_months": 6,
    "student_t_degrees_of_freedom": null
  }
}
```

## Additional commands

### diagnose

Compare how well the normal and Student-t distributions fit historical returns:

```bash
finance-cli diagnose --config config.json
```

Requires `data.csv_path` to be set. Prints a goodness-of-fit table to the terminal.

### backtest

Run a rolling-origin interval coverage backtest on historical returns:

```bash
finance-cli backtest --config config.json
```

Requires `data.csv_path` to be set. Uses the `diagnostics.rolling_training_months` and `diagnostics.interval_coverage` settings to evaluate whether the model's prediction intervals are well-calibrated.

### sensitivity

Compute a deterministic sensitivity grid across a range of annual return and inflation assumptions:

```bash
finance-cli sensitivity --config config.json
```

Writes `sensitivity-grid.csv` to the output directory and prints the results to the terminal.

## Tax configuration

The application includes a simplified German terminal-gain tax model. It is disabled by default. Set `tax.enabled` to `true` to activate it:

```json
{
  "tax": {
    "enabled": true,
    "partial_exemption": 0.30,
    "saver_allowance": 1000.0,
    "capital_gains_tax_rate": 0.25,
    "solidarity_surcharge_rate": 0.055,
    "church_tax_rate": 0.0
  }
}
```

The model applies a partial exemption (`partial_exemption`) to gross gains, subtracts the saver's allowance, and then applies capital gains tax plus solidarity surcharge and optional church tax. The result is saved to `tax-summary.json` and covers terminal gains only; interim taxation is not modelled.

## Risk configuration

Risk metrics are computed across all simulated paths and saved to `risk-summary.csv`. Configure the reference rates used:

```json
{
  "risk": {
    "annual_risk_free_rate": 0.02,
    "annual_omega_threshold": 0.0,
    "confidence_level": 0.95
  }
}
```

Computed metrics include annual return, annual volatility, Sharpe ratio, Sortino ratio, Omega ratio, maximum drawdown, Ulcer Index, Value-at-Risk, and Expected Shortfall.

## CLI commands

Use `finance-cli --help` to list all commands:

- `simulate --config <path>`: run calibration + simulation and write output files
- `diagnose --config <path>`: print distribution goodness-of-fit diagnostics (historical data required)
- `backtest --config <path>`: print rolling-origin coverage backtest results (historical data required)
- `sensitivity --config <path>`: run deterministic return/inflation sensitivity grid
- `wizard --output <path>`: interactive config wizard
- `config example --output <path>`: write example JSON config (default: `config.example.json`)
- `version`: print CLI version



A successful run prints a horizon summary similar to this:

```text
                     ETF Simulation Summary
┏━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Years ┃    Paid in ┃         P5 ┃     Median ┃        P95 ┃ P(< paid in) ┃
┡━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│     1 │    EUR49,332 │    EUR42,151 │    EUR51,906 │    EUR64,159 │        34.1% │
│     5 │   EUR106,932 │    EUR89,078 │   EUR130,655 │   EUR196,594 │        19.7% │
│    15 │   EUR250,932 │   EUR231,594 │   EUR438,112 │   EUR865,544 │         7.6% │
│    30 │   EUR466,932 │   EUR555,969 │ EUR1,410,592 │ EUR3,987,982 │         2.3% │
└───────┴────────────┴────────────┴────────────┴────────────┴──────────────┘
Results written to runs/latest
```

The numbers above are illustrative. Actual values depend on the configuration, historical data, simulation method, and random seed.

## Generated output files

Each simulation writes the following files to the configured `output.directory`:

```text
runs/latest/
├── calibration.json
├── horizon-summary.csv
├── path-percentiles.csv
├── percentile-paths.png
├── risk-summary.csv
├── run-manifest.json
└── tax-summary.json
```

If historical data is provided and diagnostics are enabled, the following additional files are written:

```text
runs/latest/
├── coverage-backtest.csv
└── distribution-fit.csv
```

- `calibration.json`: estimated return-distribution parameters and historical statistics
- `horizon-summary.csv`: selected horizon results including percentiles and shortfall probability
- `path-percentiles.csv`: percentile development for every simulated month
- `percentile-paths.png`: chart of the percentile paths over time (requires `output.export_charts: true`)
- `risk-summary.csv`: per-path risk metrics (Sharpe, Sortino, VaR, Expected Shortfall, and others) summarised across all paths
- `run-manifest.json`: configuration, package version, Python version, seed, and simulation metadata
- `tax-summary.json`: simplified German terminal-gain tax estimate (always written; only meaningful when `tax.enabled: true`)
- `coverage-backtest.csv`: rolling-origin interval coverage backtest results
- `distribution-fit.csv`: goodness-of-fit comparison between normal and Student-t models

## Interpreting the results

- **P5**: only 5% of simulated outcomes finish below this value.
- **Median**: half of the simulated outcomes finish below and half above this value.
- **P95**: only 5% of simulated outcomes finish above this value.
- **P(< paid in)**: estimated probability that the portfolio value is below total contributed capital at the selected horizon.
- **Real values**: values adjusted for the configured inflation assumption and expressed in today's purchasing power.

Monte Carlo results are scenario distributions, not forecasts or guarantees. Results are particularly sensitive to the expected-return assumption, volatility estimate, historical observation window, and treatment of extreme market events.

## Development and validation

Run linting, type checks, and tests:

```bash
ruff check .
mypy src
pytest
```

Run tests with coverage:

```bash
pytest --cov=finance_cli --cov-report=term-missing
```

## Additional documentation

- [Implementation plan](docs/implementation-plan.md)
- [Simulation methodology](docs/simulation-methodology.md)

## Disclaimer

This software is intended for analytical and educational purposes. It does not constitute financial, tax, or investment advice. Historical returns and simulated outcomes do not guarantee future performance.
