# Finance CLI App / CFO Platform

A Python-based finance platform evolving from a statistically grounded ETF Monte Carlo CLI into an enterprise-oriented CFO command center for planning, forecasting, performance management, profitability, liquidity, governance, and risk.

The repository currently contains two complementary product surfaces:

1. **CFO Platform** — a FastAPI-based application layer for enterprise finance workflows.
2. **Finance CLI** — the original quantitative toolkit for ETF calibration, Monte Carlo simulation, diagnostics, backtesting, stress analysis, and long-term investment planning.

## Current product status

The current `main` branch contains the completed implementation through **Epic 07**.

| Epic | Module | Status |
|---|---|---|
| 01 | Product Architecture & Domain Foundation | Complete |
| 02 | Finance Data Foundation | Complete |
| 03 | Governance, Run Store & Audit Trail | Complete |
| 04 | Integrated Planning & Rolling Forecast | Complete |
| 05 | Financial Performance Management | Complete |
| 06 | Cost & Profitability Management | Complete |
| 07 | Cash, Liquidity & Covenant Control | Complete |
| 08 | Enterprise Risk Management | Next |

The long-term product goal is a modular **CFO Command Center** that combines governed finance data, integrated planning, probabilistic forecasting, performance steering, liquidity control, risk analytics, reporting, and AI-assisted interpretation.

## Target architecture

```text
JavaScript Web Client
        |
        v
Python / FastAPI API
        |
        +-------------------------------+
        |                               |
        v                               v
CFO Domain & Application Layer     Quant / Simulation Layer
        |                               |
        +---------------+---------------+
                        |
                        v
                Persistence / Audit
                        |
                        v
                     Azure
```

Target stack:

- **Cloud:** Microsoft Azure
- **Backend:** Python 3.11/3.12 + FastAPI
- **Packaging:** Docker
- **Web:** JavaScript
- **Persistence:** repository abstractions with development adapters today and Azure/PostgreSQL-oriented production adapters planned
- **Observability:** Azure-compatible liveness/readiness contracts
- **Governance:** immutable lineage, approvals, audit events, model registry and scoped access control

## CFO Platform modules

### Epic 01 — Product Architecture & Domain Foundation

Provides the application foundation and clean separation between domain, API, application services, quantitative models, and infrastructure.

Key capabilities:

- framework-independent CFO domain model
- company, account, period, scenario and metric contracts
- model execution ports and model registry
- FastAPI application factory and composition root
- versioned API routes
- OpenAPI support
- liveness and readiness endpoints
- CORS support for the future JavaScript frontend
- non-blocking jobs with status, progress, cancellation and retry/resume contracts
- Docker production image

### Epic 02 — Finance Data Foundation

Provides controlled finance-data ingestion and the canonical semantic foundation used by downstream modules.

Key capabilities:

- CSV and Excel ingestion
- source-column mapping
- canonical finance records
- semantic account mappings
- sign normalization
- KPI metadata
- unmapped-account detection
- data-quality scoring and blocking findings
- reconciliation rules and tolerances
- immutable SHA-256 content-addressed snapshots
- governed import workflow

Representative endpoints:

```text
POST /api/v1/data/imports
GET  /api/v1/data/snapshots/{snapshot_id}
```

### Epic 03 — Governance, Run Store & Audit Trail

Introduces auditability, approvals, lineage and controlled model usage.

Key capabilities:

- run lineage including model, code, snapshot, parameters and random seed
- Draft -> Validated -> Approved -> Retired lifecycle
- preparer/reviewer segregation
- immutable approved runs
- append-only audit events
- before/after hashes, actor, reason and correlation ID
- governed scenarios and assumptions
- model registry and lifecycle
- RBAC for CFO, FP&A, Risk, Treasury, Controller, Reviewer and Admin roles
- company-level access scopes
- durable SQLite reference repositories for local development and CI

Representative endpoints:

```text
POST /api/v1/governance/runs
POST /api/v1/governance/runs/{run_id}/validate
POST /api/v1/governance/runs/{run_id}/approve
POST /api/v1/governance/runs/{run_id}/retire
GET  /api/v1/governance/runs/{run_id}/lineage
POST /api/v1/governance/scenarios
POST /api/v1/governance/models
```

### Epic 04 — Integrated Planning & Rolling Forecast

Implements driver-based corporate planning and probabilistic rolling forecasts.

Key capabilities:

- revenue planning using volume, price, conversion and mix
- workforce planning
- fixed and variable cost planning
- capex, depreciation and tax logic
- DSO/DPO/inventory-day working-capital drivers
- integrated income statement, balance sheet and cash flow
- exact multi-period balance-sheet reconciliation
- 12-, 18- and 24-month rolling forecast horizons
- monthly-close refresh and predecessor lineage
- Student-t probabilistic forecast overlay
- moving-block bootstrap
- optional Markov-regime forecast mode
- P10/P50/P90 bands
- deterministic seeds
- rolling-origin backtesting
- MAE, WAPE, bias, coverage and probabilistic log score
- threshold and target-breach evaluation

Representative endpoints:

```text
POST /api/v1/planning/forecasts
GET  /api/v1/planning/forecasts/{version_id}
POST /api/v1/planning/probabilistic
POST /api/v1/planning/backtests
POST /api/v1/planning/thresholds/evaluate
```

### Epic 05 — Financial Performance Management

Adds management-performance steering on top of actuals, plans and forecasts.

Key capabilities:

- hierarchical KPI tree
- EBITDA, EBIT, NOPAT, operating cash flow and free cash flow
- entity, segment, product and cost-center drilldowns
- Plan vs Actual, Forecast vs Actual and Forecast vs Forecast bridges
- Price-Volume-Mix decomposition
- exact variance reconciliation
- source-snapshot lineage
- forecast-accuracy analysis by KPI, business unit, horizon and model
- robust MAD-based anomaly detection
- materiality-based management commentary requirements
- commentary ownership and linked actions

Representative endpoints:

```text
POST /api/v1/performance/kpi-tree/evaluate
POST /api/v1/performance/variance-bridges
POST /api/v1/performance/forecast-accuracy
POST /api/v1/performance/anomalies
POST /api/v1/performance/commentary/requirements
```

### Epic 06 — Cost & Profitability Management

Adds unit-economic and profitability steering.

Key capabilities:

- CM1, CM2 and operating margin
- profitability by product, customer, channel, cost center and profit center
- versioned driver-based cost allocations
- exact source-to-target allocation reconciliation
- Activity-Based Costing
- P&L / cost-accounting reconciliation
- price, volume, variable-cost and fixed-cost sensitivity analysis
- probability-weighted Margin-at-Risk
- target-shortfall probability

Representative endpoints live under:

```text
/api/v1/profitability/...
```

### Epic 07 — Cash, Liquidity & Covenant Control

Adds treasury-oriented cash visibility and covenant management.

Key capabilities:

- direct 13-week cash forecast
- weekly bank-opening and closing-cash reconciliation
- 12- to 24-month monthly liquidity forecast
- minimum-liquidity headroom and funding-gap calculation
- DSO/DPO/DIO working-capital model
- instrument-level debt schedules
- interest, amortization and maturity handling
- leverage-ratio and interest-cover covenant engine
- minimum and maximum covenant directions
- covenant headroom
- simulated breach probability
- liquidity stress testing for revenue, collections, costs and refinancing
- mitigation and funding-option impacts
- cash-forecast accuracy by horizon

Representative endpoints:

```text
POST /api/v1/liquidity/cash-forecast/13-week
POST /api/v1/liquidity/cash-forecast/monthly
POST /api/v1/liquidity/working-capital
POST /api/v1/liquidity/debt-schedules
POST /api/v1/liquidity/covenants/evaluate
POST /api/v1/liquidity/stress-tests
POST /api/v1/liquidity/cash-forecast/accuracy
```

## Next module: Enterprise Risk Management

Epic 08 is the next planned module. Its intended scope includes:

- enterprise risk register
- financial and operational risk taxonomy
- probability and impact distributions
- Monte Carlo risk aggregation
- correlation/dependency handling
- risk appetite and limits
- controls and mitigation measures
- residual risk
- Risk-to-Plan integration
- risk contribution to EBITDA, cash and covenant outcomes
- stress scenarios and reverse stress tests
- management and board risk reporting

See `docs/cfo-product-implementation-roadmap.md` for the complete multi-epic roadmap.

## Running the CFO Platform API

### Requirements

- Python 3.11 or 3.12
- Git

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/Timeless90/finance-cli-app.git
cd finance-cli-app

python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install application and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Run the FastAPI application:

```bash
uvicorn cfo_platform.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

Useful endpoints:

```text
GET /health/live
GET /health/ready
GET /api/v1/platform
GET /docs
GET /openapi.json
```

The interactive OpenAPI UI is available at `/docs` when the application is running.

## Docker

Build the production container:

```bash
docker build -t finance-cfo-platform .
```

Run it locally:

```bash
docker run --rm -p 8000:8000 finance-cfo-platform
```

The container exposes health contracts intended to remain compatible with Azure deployment patterns.

## Development and validation

Run linting, type checks and tests:

```bash
ruff check .
mypy src
pytest
```

Run the CI-equivalent test suite with coverage:

```bash
pytest --cov=finance_cli --cov-report=term-missing
```

GitHub Actions validates the repository against Python 3.11 and Python 3.12.

## Architecture and completion evidence

Each completed enterprise epic includes explicit acceptance evidence under `docs/architecture/`:

```text
docs/architecture/
├── epic-01-completion.md
├── epic-02-completion.md
├── epic-03-completion.md
├── epic-04-completion.md
├── epic-05-completion.md
├── epic-06-completion.md
└── epic-07-completion.md
```

Open product or architecture decisions that require human input are recorded under:

```text
Open-AI-Questions/
```

## Finance CLI / Quant Toolkit

The original ETF-focused CLI remains part of the repository and serves as a reusable quantitative research and simulation toolkit.

### Core CLI capabilities

- historical ETF price ingestion
- monthly simple and logarithmic returns
- statistical calibration
- Normal and Student-t Monte Carlo simulation
- historical bootstrap
- moving-block bootstrap
- regime-switching simulation
- monthly savings contributions
- inflation and fee handling
- percentile analysis
- shortfall probability
- Sharpe, Sortino and Omega ratios
- maximum drawdown and Ulcer Index
- Value-at-Risk and Expected Shortfall
- distribution diagnostics
- rolling-origin coverage backtesting
- deterministic sensitivity analysis
- simplified German terminal-gain tax logic
- chart, CSV and JSON exports
- deterministic random seeds
- interactive configuration wizard

### CLI quickstart

Verify the installation:

```bash
finance-cli version
```

Generate an example configuration:

```bash
finance-cli config example --output config.json
```

Run a simulation:

```bash
finance-cli simulate --config config.json
```

Create a configuration interactively:

```bash
finance-cli wizard --output config.json
```

### CLI commands

```text
finance-cli simulate --config <path>
finance-cli diagnose --config <path>
finance-cli backtest --config <path>
finance-cli sensitivity --config <path>
finance-cli wizard --output <path>
finance-cli config example --output <path>
finance-cli version
```

### Historical ETF data

Provide a CSV with a date and adjusted-price or total-return column, for example:

```csv
date,price
2021-01-29,72.15
2021-02-26,74.03
2021-03-31,77.18
2021-04-30,79.44
```

For ETF analysis, adjusted prices or total-return data are recommended because unadjusted prices can omit distributions and materially understate historical performance.

### Simulation methods

| Method | Historical data required | Purpose |
|---|---:|---|
| Normal | No | Parametric Gaussian log-return model |
| Student-t | No | Heavy-tail parametric model |
| Historical bootstrap | Yes | Independent resampling of historical returns |
| Moving-block bootstrap | Yes | Retains short-term temporal dependence |
| Markov regime | Yes | Regime-dependent return dynamics |

Monte Carlo outputs are distributions of scenarios, not guarantees or deterministic predictions.

## Repository direction

The project is intentionally moving from a single-purpose simulation CLI toward a modular enterprise finance platform. The quantitative CLI is retained because many of its statistical components — calibration, bootstrapping, Monte Carlo simulation, regime modelling, stress analysis and reproducible RNG handling — are directly reusable inside the CFO Platform.

The strategic product direction is therefore:

```text
Quantitative Engine
       +
Finance Domain Model
       +
Governance & Audit
       +
Planning / Performance / Liquidity / Risk
       +
FastAPI Platform
       +
JavaScript CFO Dashboard
       +
AI-assisted interpretation and reporting
```

## Additional documentation

- [CFO product implementation roadmap](docs/cfo-product-implementation-roadmap.md)
- [Implementation plan](docs/implementation-plan.md)
- [Simulation methodology](docs/simulation-methodology.md)
- [Epic 01 completion](docs/architecture/epic-01-completion.md)
- [Epic 02 completion](docs/architecture/epic-02-completion.md)
- [Epic 03 completion](docs/architecture/epic-03-completion.md)
- [Epic 04 completion](docs/architecture/epic-04-completion.md)
- [Epic 05 completion](docs/architecture/epic-05-completion.md)
- [Epic 06 completion](docs/architecture/epic-06-completion.md)
- [Epic 07 completion](docs/architecture/epic-07-completion.md)

## Disclaimer

This software is intended for analytical, planning and educational purposes. It does not constitute financial, tax, investment, legal, accounting or audit advice. Simulated and forecast outcomes depend on assumptions, model choices, data quality and scenario design and should be reviewed by appropriately qualified users before being used for material business decisions.
