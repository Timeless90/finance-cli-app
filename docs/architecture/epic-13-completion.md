# Epic 13 — Capital Allocation & Funding

## Scope

Epic 13 implements the roadmap capability E12 — Capital Allocation & Funding.

Delivered capabilities:

- Capex and project valuation with NPV, IRR, ROIC and payback.
- Monte Carlo NPV with reproducible random seeds.
- Scenario and risk-event integration in project cash flows.
- Exact portfolio selection under budget, cash and covenant constraints.
- Funding and refinancing scenario analytics.
- FastAPI workflows under `/api/v1/capital`.

## Acceptance Evidence

### Reference projects return validated NPV / IRR values

`tests/test_capital_allocation.py::test_reference_project_npv_irr_roic_and_payback`
uses the independent reference cash-flow series `[-1000, 600, 600]`.

Expected results:

- NPV at 10%: `41.32231404958668`
- IRR: approximately `13.06623863%`
- ROIC for supplied NOPAT: `16%`
- payback: approximately `1.6667` years

The test asserts the implementation against these reference values.

### Portfolio constraints are always enforced

`CapitalPortfolioOptimizer` enumerates feasible project subsets and rejects every subset that violates any of:

- investment budget,
- minimum cash headroom,
- maximum leverage,
- minimum interest cover.

`test_portfolio_optimizer_never_breaks_constraints` verifies all four constraints on the selected portfolio.
The exact optimizer intentionally caps the candidate set at 22 projects; larger enterprise portfolios should use a dedicated MILP adapter in a later scale-hardening step rather than silently falling back to an approximate answer.

### Cash and covenant effects are integrated

Every project can carry explicit cash-headroom, leverage and interest-cover impacts.
The optimizer evaluates these effects jointly with the investment budget.

Funding scenarios calculate:

- gross and net proceeds,
- interest expense,
- principal amortization,
- debt service,
- post-funding leverage,
- post-funding interest cover,
- leverage covenant headroom.

`test_funding_scenario_integrates_cash_and_covenants` verifies these calculations.

### Monte Carlo results are reproducible

`MonteCarloNpvEngine` uses NumPy's independent `default_rng(seed)` generator. The simulation supports:

- cash-flow volatility,
- scenario multipliers,
- event probability,
- event impact,
- P10/P50/P90,
- probability of negative NPV.

`test_monte_carlo_npv_is_reproducible` confirms identical results for identical model inputs and seeds.

## API Contracts

- `POST /api/v1/capital/projects/value`
- `POST /api/v1/capital/projects/monte-carlo`
- `POST /api/v1/capital/portfolio/optimize`
- `POST /api/v1/capital/funding/evaluate`

## Design Notes

The deterministic valuation service remains separate from probabilistic simulation. Portfolio optimization consumes explicitly supplied risk-adjusted NPVs rather than hiding a risk-adjustment convention inside the optimizer. This keeps valuation policy auditable and allows later integration with Enterprise Risk Management, Market Risk and scenario governance without changing the optimization contract.

The current funding engine is a transparent annualized reference model. More complex instruments such as bullet structures, floating-rate curves, swaps, call schedules and multi-tranche refinancing can be added behind the same domain boundary in later Treasury hardening.
