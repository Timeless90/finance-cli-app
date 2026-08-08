# Finance CLI App / CFO Platform

A Python-based finance platform evolving from a statistically grounded ETF Monte Carlo CLI into a modular CFO Command Center for planning, forecasting, performance management, profitability, liquidity, enterprise risk, treasury risk, capital allocation, governed reporting and AI-assisted finance interpretation.

The repository currently contains two product surfaces:

1. **CFO Platform** — a FastAPI-based enterprise finance application layer.
2. **Finance CLI** — the original quantitative toolkit for ETF calibration, Monte Carlo simulation, diagnostics, backtesting, stress analysis and long-term investment planning.

> **Frontend status:** the CFO backend and APIs are implemented, but there is currently **no production frontend application** in the repository. A dedicated CFO web client remains a planned product layer.

## Current product status

The current `main` branch contains the implementation through **Roadmap E12 — Capital Allocation & Funding**. The repository uses implementation labels `Epic 01` through `Epic 13`; these are offset by one from the roadmap because the roadmap starts at `E0`.

| Implementation | Roadmap | Module | Status |
|---|---|---|---|
| Epic 01 | E0 | Product Architecture & Domain Separation | Complete |
| Epic 02 | E1 | Finance Data Foundation | Complete |
| Epic 03 | E2 | Governance, Run Store & Audit Trail | Complete |
| Epic 04 | E3 | Integrated Planning & Rolling Forecast | Complete |
| Epic 05 | E4 | Financial Performance Management | Complete |
| Epic 06 | E5 | Cost & Profitability Management | Complete |
| Epic 07 | E6 | Cash, Liquidity & Covenant Control | Complete |
| Epic 08 | E7 | Enterprise Risk Management | Complete |
| Epic 09 | E8 | Action & Decision Management | Complete |
| Epic 10 | E9 | Reporting Factory | Complete |
| Epic 11 | E10 | LLM Finance Copilot / Microsoft Foundry | Complete |
| Epic 12 | E11 | Market & Treasury Risk | Complete |
| Epic 13 | E12 | Capital Allocation & Funding | Complete |
| — | E13 | Enterprise Hardening & Scale | Next roadmap epic |

The current platform therefore covers the full roadmap through **Phase 4 — Advanced Finance**. The next roadmap step is **E13 — Enterprise Hardening & Scale**.

## Current architecture

```text
Planned CFO Web Client
        |
        v
Python / FastAPI API
        |
        +-----------------------------------------------+
        |                                               |
        v                                               v
CFO Domain & Application Layer                    Quant / Simulation Layer
        |                                               |
        +-----------------------+-----------------------+
                                |
                                v
                     Governance / Audit / Repositories
                                |
                                v
                  Azure-oriented Production Target
```

Current stack:

- **Backend:** Python 3.11/3.12 + FastAPI
- **API:** versioned REST endpoints under `/api/v1`
- **Quant:** NumPy/SciPy-based deterministic and probabilistic analytics
- **Reporting:** JSON, CSV, XLSX, PDF and PPTX generation
- **AI:** Microsoft Foundry-compatible multi-model Finance Copilot using OpenAI-compatible `/openai/v1` APIs
- **Governance:** run lineage, approvals, audit events, model registry, RBAC and company scopes
- **Packaging:** Docker
- **Persistence:** repository abstractions with local/in-memory and SQLite reference adapters
- **Frontend:** not implemented yet
- **Cloud direction:** Microsoft Azure

## CFO Platform capability map

### Foundation, data and governance

The platform provides:

- framework-independent finance domain contracts
- FastAPI application factory and composition root
- OpenAPI, liveness and readiness endpoints
- background job execution contracts
- CSV and Excel ingestion
- source-to-canonical field mapping
- semantic finance records and account mappings
- data-quality scoring and reconciliation
- immutable content-addressed data snapshots
- governed model runs and scenarios
- model registry and lifecycle
- preparer/reviewer segregation
- append-only audit events
- role-based and company-scoped access control

Representative API areas:

```text
/api/v1/data/...
/api/v1/governance/...
/api/v1/jobs/...
```

### Integrated Planning & Rolling Forecast

Capabilities include:

- driver-based revenue planning
- workforce, cost, capex, tax and working-capital drivers
- integrated P&L, balance sheet and cash flow
- 12-, 18- and 24-month rolling forecasts
- Student-t probabilistic forecasts
- moving-block bootstrap
- optional regime overlays
- P10/P50/P90 bands
- deterministic seeds
- rolling-origin backtesting
- MAE, WAPE, bias, coverage and log-score metrics
- threshold and shortfall evaluation

API prefix:

```text
/api/v1/planning/...
```

### Financial Performance Management

Capabilities include:

- KPI trees and management metrics
- Plan vs Actual, Forecast vs Actual and Forecast vs Forecast bridges
- Price-Volume-Mix decomposition
- exact variance reconciliation
- forecast-accuracy analysis
- robust anomaly detection
- management commentary requirements

API prefix:

```text
/api/v1/performance/...
```

### Cost & Profitability Management

Capabilities include:

- CM1, CM2 and operating-margin analysis
- profitability by product, customer, channel, cost center and profit center
- driver-based cost allocation
- Activity-Based Costing
- profitability reconciliation
- price, volume, variable-cost and fixed-cost sensitivities
- Margin-at-Risk and target-shortfall probability

API prefix:

```text
/api/v1/profitability/...
```

### Cash, Liquidity & Covenant Control

Capabilities include:

- 13-week direct cash forecasting
- monthly liquidity forecasting
- DSO, DPO and DIO working-capital modelling
- debt schedules, interest and amortization
- leverage and interest-cover covenant evaluation
- covenant headroom and breach probability
- liquidity stress testing
- mitigation and funding-option effects
- cash forecast accuracy

API prefix:

```text
/api/v1/liquidity/...
```

### Enterprise Risk Management

Capabilities include:

- enterprise risk register
- financial and operational risk taxonomy
- probability/impact modelling
- Monte Carlo risk aggregation
- dependency handling
- risk appetite and limits
- controls and mitigation measures
- residual risk
- Risk-to-Plan integration
- EBITDA, cash and covenant risk contribution
- stress and reverse-stress concepts
- management and board risk reporting

API prefix:

```text
/api/v1/risk/...
```

### Action & Decision Management

Capabilities include:

- governed action catalogue
- action simulation
- financial-impact evaluation
- action portfolio prioritization
- review and approval support
- benefit tracking
- linkage between identified finance/risk issues and management responses

API prefix:

```text
/api/v1/actions/...
```

### Reporting Factory

Capabilities include:

- Management Pack
- Board Risk Pack
- Forecast Report
- Lagebericht draft
- Audit Evidence Pack
- report templates and run/data lineage
- human-approval controls
- JSON, CSV, XLSX, PDF and PPTX exporters

API prefix:

```text
/api/v1/reporting/...
```

### Microsoft Foundry Multi-Model Finance Copilot

The Finance Copilot is prepared for Microsoft Foundry and supports routing different finance workloads to different model deployments.

Routing is resolved by **finance module × workload**, rather than by one global model. Example deployment aliases include:

- `finance-fast`
- `finance-reasoning`
- `finance-drafting`
- `model-router`

Supported workload categories include:

- management summaries
- variance explanation
- risk explanation
- action recommendations
- report drafting
- general finance Q&A

Governance and grounding controls include:

- approved facts only
- company-scoped retrieval
- prompt-injection checks
- source references
- numeric-grounding validation
- explicit data-gap and model-limit requirements
- interaction audit records
- no autonomous approval, booking or transaction execution

Configuration is environment-driven through variables including:

```text
CFO_FOUNDRY_ENDPOINT
CFO_FOUNDRY_AUTH_MODE
CFO_FOUNDRY_API_KEY
CFO_FOUNDRY_ROUTES_JSON
```

Representative endpoints:

```text
GET  /api/v1/copilot/routes
GET  /api/v1/copilot/routes/resolve
POST /api/v1/copilot/respond
```

See `docs/architecture/microsoft-foundry-multi-model.md` for the current routing and deployment guidance.

### Market & Treasury Risk

Capabilities include:

- FX, rates, commodity and funding exposure aggregation
- sensitivity analysis
- historical and Student-t VaR / Expected Shortfall
- Student-t GARCH(1,1)
- two-state Gaussian HMM regime overlay
- EVT peaks-over-threshold / GPD tail overlay
- Gaussian vs Student-t copula comparison
- hedge-ratio and variance-reduction analysis
- Kupiec and Christoffersen VaR backtests

Advanced models are activation-gated and are not enabled merely because a fit converges. GARCH, regime and EVT overlays must demonstrate diagnostic value before they are treated as preferred models.

Representative endpoints:

```text
POST /api/v1/market-risk/exposures/aggregate
POST /api/v1/market-risk/sensitivities
POST /api/v1/market-risk/var-es
POST /api/v1/market-risk/models/garch-t
POST /api/v1/market-risk/models/regime-hmm
POST /api/v1/market-risk/models/evt
POST /api/v1/market-risk/models/copula
POST /api/v1/market-risk/hedges/effectiveness
POST /api/v1/market-risk/backtests/var
```

### Capital Allocation & Funding

Capabilities include:

- project and Capex valuation
- NPV, IRR, ROIC and payback
- reproducible Monte Carlo NPV
- scenario and risk-event overlays
- exact project portfolio optimization
- budget, cash-headroom, leverage and interest-cover constraints
- funding and refinancing scenario evaluation
- proceeds, interest, amortization and debt-service analytics
- post-funding leverage and covenant headroom

Representative endpoints:

```text
POST /api/v1/capital/projects/value
POST /api/v1/capital/projects/monte-carlo
POST /api/v1/capital/portfolio/optimize
POST /api/v1/capital/funding/evaluate
```

## Frontend status

There is currently **no dedicated frontend application** in `main`.

In particular, the repository does not yet contain a production React/Vue/Angular application, frontend package manifest or CFO dashboard shell. FastAPI's Swagger/OpenAPI UI at `/docs` is currently the primary interactive interface for the CFO Platform API.

A future CFO web client should consume the existing API and can be organized around the implemented modules:

```text
Dashboard
Planning
Performance
Profitability
Liquidity
Enterprise Risk
Actions
Reporting
Market & Treasury Risk
Capital Allocation
Finance Copilot
Administration / Governance
```

The backend already exposes CORS support and versioned APIs to support this future client.

## Next roadmap epic: E13 — Enterprise Hardening & Scale

The next roadmap step is the enterprise-scale hardening phase. Its purpose is to turn the current feature-complete backend foundation into a production-ready multi-user platform.

Expected focus areas include:

- production-grade persistence
- tenant and organizational isolation
- authentication and identity integration
- security hardening
- secrets and key management
- operational observability
- resilience and recovery
- workload scaling
- deployment automation
- compliance and audit hardening
- performance/load validation
- enterprise production-readiness

See `docs/cfo-product-implementation-roadmap.md` for the canonical roadmap.

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

Completed enterprise epics include acceptance evidence under `docs/architecture/`.

Key documents include:

```text
docs/architecture/epic-01-completion.md
...
docs/architecture/epic-10-completion.md
docs/architecture/epic-11-completion.md
docs/architecture/epic-12-completion.md
docs/architecture/epic-13-completion.md
docs/architecture/microsoft-foundry-multi-model.md
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

Adjusted prices or total-return data are recommended because unadjusted prices can omit distributions and materially understate historical performance.

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

The repository has moved beyond the original single-purpose simulation CLI into a broad CFO backend platform. The quantitative CLI remains useful because calibration, bootstrapping, Monte Carlo simulation, regime modelling, stress analysis and reproducible RNG handling are reused throughout the enterprise finance modules.

The current strategic direction is:

```text
Quantitative Engine
       +
Finance Domain Model
       +
Governance & Audit
       +
Planning / Performance / Profitability / Liquidity
       +
Enterprise Risk / Treasury Risk / Capital Allocation
       +
Reporting Factory
       +
Microsoft Foundry Finance Copilot
       +
FastAPI Platform
       +
Enterprise Hardening
       +
Future CFO Web Client
```

## Additional documentation

- [CFO product implementation roadmap](docs/cfo-product-implementation-roadmap.md)
- [Implementation plan](docs/implementation-plan.md)
- [Simulation methodology](docs/simulation-methodology.md)
- [Microsoft Foundry multi-model architecture](docs/architecture/microsoft-foundry-multi-model.md)
- [Epic 08 completion](docs/architecture/epic-08-completion.md)
- [Epic 09 completion](docs/architecture/epic-09-completion.md)
- [Epic 10 completion](docs/architecture/epic-10-completion.md)
- [Epic 11 completion](docs/architecture/epic-11-completion.md)
- [Epic 12 completion](docs/architecture/epic-12-completion.md)
- [Epic 13 completion](docs/architecture/epic-13-completion.md)

## Disclaimer

This software is intended for analytical, planning and educational purposes. It does not constitute financial, tax, investment, legal, accounting or audit advice. Simulated and forecast outcomes depend on assumptions, model choices, data quality and scenario design and should be reviewed by appropriately qualified users before being used for material business decisions.
