# Epic 08 — Enterprise Risk Management Completion Evidence

## Scope

Epic 08 implements roadmap E7 as the repository's eighth delivery epic. It connects qualitative risk ownership with quantitative loss modelling, portfolio aggregation, risk appetite, controls, plan impacts, and reporting.

## Delivered capabilities

### Risk Register

- Risk ID, title, cause, event, owner, category, and horizon.
- Gross and net risk descriptions.
- Control catalogue per risk including owner, effectiveness, annual cost, and status.
- Explicit double-count groups for overlap detection.

### Risk Quantification

- Bernoulli occurrence probability and Poisson annual frequency models.
- Empirical severity distributions.
- Lognormal severity distributions.
- Pareto severity distributions with finite-mean validation (`shape > 1`).
- User-supplied discrete/custom loss distributions.
- Expected gross loss calculation.
- Gross-to-residual mitigation bridge with separately reported avoided loss and control cost.

### Risk Aggregation

- Reproducible Monte Carlo aggregation with deterministic seed.
- Linear correlation matrix as the baseline dependence model.
- Validation of matrix dimensions, diagonal, bounds, symmetry, and positive semidefiniteness.
- Correlated occurrence/frequency and severity drivers via Gaussian latent variables.
- Portfolio mean, P50, P90, P95, P99, and Expected Shortfall at 95%.
- Risk-level gross/net mean, P95, contribution share, and mitigation effect.
- Copula modelling explicitly deferred until sufficient data quality and governance maturity.

### Risk Appetite & Limits

- Category, KPI, and risk-capacity limit scopes.
- Maximum exposure, warning utilization, headroom, and explicit healthy/warning/breached status.

### Controls & Mitigation

- Multiplicative residual-risk factors for active controls.
- Control costs are kept separate from residual loss.
- Planned, ineffective, and retired controls do not reduce simulated residual loss.

### Risk-to-Plan Integration

- Explicit mapping into income statement, balance sheet, or cash-flow metrics.
- Period-specific loss factors.
- Deterministic impact keys.
- Duplicate impact keys are rejected to prevent plan-side double counting.

### Risk Reporting

- Top-risk ranking.
- Risk heatmap with probability and impact bands.
- Portfolio loss distribution and tail metrics.
- Total simulated mitigation effect.
- Methodology disclosures including correlation assumptions and the deliberate deferral of copulas.

## API surface

- `POST /api/v1/risk/register`
- `GET /api/v1/risk/register`
- `GET /api/v1/risk/register/{risk_id}`
- `POST /api/v1/risk/quantification/expected-loss`
- `POST /api/v1/risk/aggregation`
- `POST /api/v1/risk/limits/evaluate`
- `POST /api/v1/risk/plan/integrate`
- `POST /api/v1/risk/reports`

## Acceptance criteria evidence

### Einzelrisiken sind bis zur Gesamtverteilung nachvollziehbar

Evidence:

- Every aggregate run receives an ordered tuple of risk records and an explicit correlation matrix.
- Portfolio results include `RiskContribution` entries keyed by `risk_id`.
- Contribution outputs separate gross mean, residual mean, P95 residual loss, expected-loss share, and mitigation effect.
- Aggregation is reproducible with the same risk definitions, correlation matrix, path count, and seed.

Tests:

- `test_monte_carlo_aggregation_is_reproducible_and_traceable`
- `test_reporting_contains_top_risks_heatmap_methodology_and_mitigation`

### Doppelzählungs- und Korrelationsprüfungen sind dokumentiert

Evidence:

- Shared `double_count_group` values are rejected before aggregation.
- Correlation matrices must match the risk count, contain unit diagonals, remain within [-1, 1], be symmetric, and be positive semidefinite.
- Plan integration rejects duplicate impact keys.
- The reporting methodology explicitly states the dependence model and copula deferral.

Tests:

- `test_correlation_and_double_counting_controls_are_enforced`
- `test_risk_to_plan_integration_blocks_duplicate_impact_keys`

### Maßnahmenwirkung ist separat ausweisbar

Evidence:

- `RiskMitigationResult` exposes gross loss, residual loss, avoided loss, residual factor, and annual control cost independently.
- Portfolio contributions expose `mitigation_effect` per risk.
- Risk reports aggregate the mitigation effect without netting it against control cost.

Tests:

- `test_risk_register_and_expected_loss_separate_gross_and_net`
- `test_reporting_contains_top_risks_heatmap_methodology_and_mitigation`

## Statistical design decisions

1. Linear correlation is the baseline because it is transparent, governable, and testable with limited enterprise loss data.
2. Correlation matrices are PSD-validated before simulation; invalid dependence structures fail fast.
3. Bernoulli and Poisson frequency are explicit alternatives rather than silently mixing probability and frequency assumptions.
4. Pareto shape must exceed one so the expected severity used in management reporting is finite.
5. Monte Carlo outputs are scenario distributions, not point forecasts or guarantees.
6. Copulas are intentionally not introduced in this epic; they require stronger empirical dependence evidence and additional model-governance controls.

## Out of scope / future hardening

- Copula dependence models.
- Bayesian parameter uncertainty.
- Extreme-value threshold fitting and tail diagnostics beyond the existing Pareto option.
- Persistent enterprise risk repository and approval lifecycle beyond the current in-memory application adapter.
- Regulatory report templates; these are delivered through the later Reporting Factory epic.

## Definition of Done

- Domain services implemented and wired through the application composition root.
- Versioned FastAPI endpoints registered.
- Acceptance tests cover register, quantification, aggregation, limits, plan integration, reporting, reproducibility, and overlap checks.
- Ruff and pytest must pass under the repository CI matrix before the pull request is considered complete.
