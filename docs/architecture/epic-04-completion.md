# Epic 04 Completion — Integrated Planning & Rolling Forecast

## Scope

Epic 04 implements an integrated deterministic and probabilistic planning workflow for income statement, balance sheet and cash flow forecasting.

## Delivered features

### E3-F1 Driver-Based Revenue Planning

- volume, price, conversion and mix drivers
- multiple revenue-driver lines per period
- deterministic revenue aggregation

### E3-F2 Cost & Workforce Planning

- workforce opening FTE, hires and leavers
- salary and payroll-oncost calculation
- variable, fixed, personnel and depreciation costs

### E3-F3 Integrated Statements

- EBITDA, EBIT, tax and net income
- accounts receivable, inventory and accounts payable
- operating, investing and financing cash flow
- closing cash and equity
- mathematical balance-sheet reconciliation
- multi-period opening/closing balance roll-forward

### E3-F4 Rolling Forecast Workflow

- explicit 12-, 18- and 24-month horizons
- immutable version identifiers
- mandatory snapshot, scenario, assumption-set and model-version references
- predecessor lineage between forecast versions
- monthly-close refresh with horizon extension

### E3-F5 Probabilistic Forecast Overlay

- Student-t residual simulation as the robust default
- moving-block bootstrap for temporally dependent residuals
- explicit Markov-regime option for advanced use
- deterministic seeding and reproducible P10/P50/P90 bands

### E3-F6 Forecast Backtesting

- rolling-origin observation contracts
- MAE, WAPE and bias
- interval coverage and Gaussian log score
- explicit future-leakage guard

### E3-F7 Goal & Threshold Engine

- minimum and maximum targets
- warning and breach status
- simulated shortfall or exceedance probability

## API contracts

- `POST /api/v1/planning/forecasts`
- `GET /api/v1/planning/forecasts/{version_id}`
- `POST /api/v1/planning/probabilistic`
- `POST /api/v1/planning/backtests`
- `POST /api/v1/planning/thresholds/evaluate`

## Acceptance criteria evidence

| Acceptance criterion | Evidence |
|---|---|
| Income statement, balance sheet and cash flow are mathematically integrated | `IntegratedPlanningEngine`, reconciliation tests |
| Forecasts contain deterministic and probabilistic results | rolling forecast and probabilistic engines |
| No future leakage in backtests | `assert_no_future_leakage` and regression test |
| Forecast bands can be validated against historical coverage | coverage and log-score metrics |
| Forecasts are linked to governed data and assumptions | mandatory snapshot, scenario, assumption and model references |
| Monthly-close refresh preserves lineage | predecessor version and refresh test |
| Long-running simulation logic remains reproducible | deterministic seed and equality regression test |

## Deliberate boundaries

- Legal-entity consolidation and intercompany elimination remain outside this epic.
- Detailed debt schedules and covenant formulas belong to the liquidity epic.
- Markov-regime forecasting is exposed only as an advanced option; production selection must be supported by out-of-sample evidence.
- The current rolling forecast repository is an in-memory application adapter. Durable enterprise persistence follows the existing repository-port architecture.

## Quality gates

The branch is expected to pass:

```bash
ruff check .
mypy src/finance_cli src/cfo_platform
pytest
```

The pull request remains in draft until repository CI confirms these gates.