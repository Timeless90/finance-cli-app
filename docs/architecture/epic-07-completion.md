# Epic 07 Completion — Cash, Liquidity & Covenant Control

## Scope

Epic 07 implements the liquidity-control layer defined by the CFO product roadmap. It combines short-term cash planning, monthly liquidity forecasting, working-capital mechanics, debt scheduling, covenant monitoring, stress testing and forecast-accuracy diagnostics.

## Delivered capabilities

### 13-week cash forecast

- Direct weekly cash planning for bank opening balance, AR collections, AP payments, payroll, taxes, capex, financing and other cash flows.
- Exact week-to-week bank reconciliation: each opening cash balance must equal the prior closing balance.
- Explicit inflow, outflow, net cash flow and closing cash outputs.

### Monthly liquidity forecast

- 12- to 24-month liquidity horizon.
- Opening-to-closing cash roll-forward.
- Minimum-liquidity headroom and funding-gap calculation.
- Designed to consume operating, investing and financing cash flows from the integrated planning layer.

### Working-capital model

- DSO, DPO and DIO based receivables, payables and inventory calculation.
- Net-working-capital output.
- Deterministic probabilistic-payment helper for scenario shock series.

### Debt schedule

- Instrument-level principal schedule.
- Monthly interest, amortization, maturity and remaining principal.
- Contract metadata for committed limits and maturity handling.

### Covenant engine

- Net-debt / EBITDA leverage ratio.
- EBIT / net-interest coverage ratio.
- Minimum and maximum covenant directions.
- Headroom, current breach status and simulated breach probability.
- Contract examples included in tests.

### Liquidity stress testing

- Revenue decline.
- Collection delay.
- Cost increase.
- Refinancing shock.
- Mitigation and funding options.
- Stressed cash and funding-gap output.

### Cash forecast accuracy

- MAE and bias by forecast horizon.
- Deterministic grouping to support operational liquidity forecast monitoring.

### API

- `POST /api/v1/liquidity/cash-forecast/13-week`
- `POST /api/v1/liquidity/cash-forecast/monthly`
- `POST /api/v1/liquidity/working-capital`
- `POST /api/v1/liquidity/debt-schedules`
- `POST /api/v1/liquidity/covenants/evaluate`
- `POST /api/v1/liquidity/stress-tests`
- `POST /api/v1/liquidity/cash-forecast/accuracy`

## Acceptance criteria evidence

| Criterion | Evidence |
|---|---|
| Bank and cash values reconcile | `ThirteenWeekCashForecast` and `MonthlyLiquidityForecast` reject any opening balance that differs from the prior period closing balance. |
| Covenant formulas are tested against contract examples | Epic tests validate 3.0x leverage and 4.0x interest-cover examples and minimum/maximum threshold directions. |
| Cash forecast accuracy is measured by horizon | `CashForecastAccuracyService` reports MAE and bias for each horizon. |
| Minimum liquidity and funding gaps are visible | Monthly forecasts and stress tests expose headroom and funding gap explicitly. |
| Liquidity stress factors are separately traceable | Stress scenario fields isolate revenue, collection, cost, refinancing and mitigation effects. |
| API contracts are versioned and tested | All routes are registered under `/api/v1/liquidity`; acceptance tests exercise covenant and working-capital endpoints. |

## Test coverage

`tests/test_epic07_liquidity.py` covers:

- 13-week bank/cash reconciliation.
- Monthly headroom and funding-gap calculations.
- DSO/DPO/DIO formulas.
- Debt interest and maturity schedules.
- Leverage and interest-cover contract examples.
- Simulated covenant-breach probability.
- Liquidity stress and mitigation logic.
- Cash-forecast accuracy by horizon.
- FastAPI contracts.

## Dependency and merge strategy

The branch is stacked on `feature/epic-06-cost-profitability-management`. After Epic 06 is merged, this pull request can be retargeted to `main` without changing the Epic 07 implementation diff.
