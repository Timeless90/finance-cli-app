# Epic 04 — Integrated Planning & Rolling Forecast

## Goal

Deliver an integrated, driver-based planning engine for income statement, balance sheet and cash flow, with governed rolling forecast versions and probabilistic overlays.

## Features

### E3-F1 Driver-Based Revenue Planning

- volume, price and mix drivers
- backlog and pipeline conversion
- segment, product and region dimensions

### E3-F2 Cost & Workforce Planning

- variable and fixed operating cost drivers
- headcount, salary, hires and leavers
- material, energy, logistics and other costs

### E3-F3 Integrated Statements

- income statement, balance sheet and cash flow linkage
- working-capital and capital-expenditure logic
- balance-sheet control and cash reconciliation

### E3-F4 Rolling Forecast Workflow

- 12-, 18- and 24-month horizons
- monthly close refresh
- immutable version references and governance integration

### E3-F5 Probabilistic Forecast Overlay

- Student-t baseline
- moving-block bootstrap for temporal dependence
- Markov-regime model only when validated out of sample
- P10/P50/P90 for EBITDA, EBIT, cash flow and goals

### E3-F6 Forecast Backtesting

- rolling-origin evaluation
- MAE, WAPE, bias, interval coverage and log score
- no future leakage

### E3-F7 Goal & Threshold Engine

- KPI targets and warning thresholds
- shortfall probabilities
- cash and covenant-compatible thresholds

## Acceptance Criteria

- Income statement, balance sheet and cash flow reconcile mathematically.
- Forecast results contain deterministic and probabilistic outputs.
- Rolling-origin backtests use only information available at each origin.
- Forecast intervals are validated against historical coverage.
- Every forecast references governed scenario, assumptions, model version and data snapshot.

## Initial implementation slice

The first slice establishes framework-independent planning contracts and deterministic integrated-statement calculations. API workflows, probabilistic overlays, backtesting and governance integration follow as separate vertical slices on the same branch.
