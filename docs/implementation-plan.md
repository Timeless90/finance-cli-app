# Implementation Plan

## MVP

1. Typed JSON configuration with Pydantic.
2. Historical CSV ingestion and monthly total-return preparation.
3. Statistical calibration with shrinkage of the expected return.
4. Normal and Student-t Monte Carlo.
5. Historical and moving-block bootstrap.
6. Monthly contribution engine with start/end timing.
7. Inflation-adjusted outputs.
8. Horizon summaries and path percentiles.
9. Reproducible run manifests.
10. Unit tests and GitHub Actions.

## Phase 2

- Rolling-origin backtests and coverage diagnostics.
- Goodness-of-fit comparison using AIC/BIC and Monte Carlo GOF tests.
- Drawdown, Sharpe, Sortino, Omega, Ulcer Index, VaR, and Expected Shortfall.
- Stress scenarios and parameter sensitivity grids.
- German simplified tax policy.
- Interactive wizard and chart export.

## Advanced

- GARCH and regime-switching models.
- Extreme-value tail overlays.
- Multi-asset portfolios, rebalancing, and copulas.
- Parallel path generation with independent RNG streams.
