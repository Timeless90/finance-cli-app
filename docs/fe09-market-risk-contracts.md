# FE-09 — Market Risk Lab Backend Contracts

## Lifecycle

Frontend lifecycle: **MOCK CONNECTED / MODEL CONTRACT PENDING**.

The Market Risk Lab is a diagnostic and model-governance surface. It must never estimate GARCH parameters, classify regimes, fit copulas, generate production Monte Carlo paths, or execute risk backtests in browser JavaScript.

## Existing repository capability

The repository already contains useful Python foundations in the Finance CLI:

- `finance_cli.models`: log-return parameter estimation (`mu_log`, `sigma_log`, arithmetic mean) and parameter validation;
- `finance_cli.simulation`: deterministic-seed IID-normal Monte Carlo for the investment/DCA use case plus tax-aware liquidation paths;
- `finance_cli.risk`: drawdown, Sharpe, Sortino, Omega, Ulcer Index, historical/normal VaR and Expected Shortfall;
- `finance_cli.diagnostics`: walk-forward forecast diagnostics, historical/normal VaR/CVaR, PIT, autocorrelation checks, Jensen-Shannon/Wasserstein metrics, POT threshold estimation and bootstrap comparison utilities.

These functions are valuable analytical building blocks, but they are not exposed as a governed FastAPI Market Risk service. No production GARCH, Markov/regime-switching, copula or market-risk model-run contract was found in the current API surface.

## Required service architecture

FE-09 should consume versioned **model runs** rather than ad-hoc synchronous calculation payloads. Each model run must be reproducible and auditable.

Recommended common run metadata:

```text
ModelRunMetadata
  run_id
  model_family
  model_version
  company_id
  period_id
  scenario_id
  asset_ids[]
  source_snapshot_ids[]
  training_window
  evaluation_window
  parameters
  random_seed
  status
    DRAFT | VALIDATED | APPROVED | SUPERSEDED | FAILED
  validation_status
  created_at
  created_by
```

## Gap 1 — Market Risk workspace read model

Recommended endpoint:

`GET /api/v1/market-risk/workspace`

Query parameters:

- `company_id`
- `period_id`
- `scenario_id`
- optional `asset_id`
- optional model-run selectors

Recommended response:

```text
MarketRiskWorkspaceSnapshot
  context
  lineage
  assets[]
    asset_id
    label
    asset_class
    exposure
    spot
    daily_volatility
    annualized_volatility
    var_95
    expected_shortfall_95
    beta
    status
  selected_runs
    volatility_run_id
    regime_run_id
    dependency_run_id
    simulation_run_id
    backtest_run_id
  threshold_states[]
```

## Gap 2 — Volatility / GARCH runs

Recommended API:

- `POST /api/v1/market-risk/models/volatility/runs`
- `GET /api/v1/market-risk/models/volatility/runs/{run_id}`
- `GET /api/v1/market-risk/models/volatility/runs?asset_id=...`

Recommended result:

```text
VolatilityModelRun
  metadata
  specification
    family
    innovation_distribution
    mean_specification
  parameters[]
    name / estimate / standard_error / t_stat / p_value
  fitted_volatility[]
  standardized_residuals[]
  qq_points[]
  diagnostics
    convergence
    log_likelihood
    aic
    bic
    persistence
    unconditional_volatility
    residual_autocorrelation
    squared_residual_autocorrelation
```

Candidate specifications may include EWMA, GARCH(1,1)-Normal, GARCH(1,1)-Student-t and later EGARCH/GJR-GARCH where justified by validation evidence.

## Gap 3 — Regime / Markov runs

Recommended API:

- `POST /api/v1/market-risk/models/regime/runs`
- `GET /api/v1/market-risk/models/regime/runs/{run_id}`

Result requirements:

```text
MarketRegimeRun
  metadata
  specification
  states[]
    state_id / label / mean / volatility
  filtered_probabilities[]
  smoothed_probabilities[]
  current_state
  current_state_probability
  transition_matrix[][]
  diagnostics
    convergence
    log_likelihood
    aic
    bic
    state_separation
```

FE-09 must display state probabilities and transitions only; regime inference remains backend-owned.

## Gap 4 — Marginal distribution fitting

Recommended API:

- `POST /api/v1/market-risk/models/marginal/runs`
- `GET /api/v1/market-risk/models/marginal/runs/{run_id}`

The response should include candidate family, estimated parameters, AIC/BIC, goodness-of-fit tests, PIT diagnostics and QQ data. Marginal fits must be versioned because they feed dependency/copula estimation.

## Gap 5 — Dependency / copula runs

Recommended API:

- `POST /api/v1/market-risk/models/dependency/runs`
- `GET /api/v1/market-risk/models/dependency/runs/{run_id}`

Recommended result:

```text
MarketDependencyRun
  metadata
  marginal_run_ids[]
  family
    correlation | gaussian_copula | t_copula
  variables[]
  correlation_matrix[][]
  copula_parameters
  tail_dependence
  log_likelihood
  aic
  bic
  fit_diagnostics
```

The frontend must never estimate correlation/copula parameters from visible chart data.

## Gap 6 — Monte Carlo market simulation runs

Recommended API:

- `POST /api/v1/market-risk/simulation/runs`
- `GET /api/v1/market-risk/simulation/runs/{run_id}`

Required configuration/result metadata:

```text
MarketSimulationRun
  metadata
  volatility_run_ids[]
  regime_run_id
  dependency_run_id
  horizon_days
  path_count
  random_seed
  fan_quantiles[]
  portfolio_var
  portfolio_expected_shortfall
  marginal_contributions[]
  threshold_breach_probabilities[]
```

Raw path matrices should not normally be returned to the browser. The API should return downsampled chart series or quantile surfaces appropriate for UI consumption.

## Gap 7 — Backtest and model-comparison runs

Recommended endpoints:

- `POST /api/v1/market-risk/backtests`
- `GET /api/v1/market-risk/backtests/{run_id}`
- `POST /api/v1/market-risk/model-comparisons`
- `GET /api/v1/market-risk/model-comparisons/{run_id}`

Backtest result should include:

- observation count;
- VaR exception count and expected exception count;
- Kupiec unconditional-coverage result;
- Christoffersen independence/conditional-coverage result;
- traffic-light status;
- dated exception records with documentation state;
- forecast-loss metrics for volatility models.

Model comparison should include AIC/BIC where comparable, out-of-sample loss, VaR coverage, tail fit, stability diagnostics and explicit champion/challenger governance status.

## Gap 8 — Threshold breach documentation

Recommended read/write contracts:

- `GET /api/v1/market-risk/thresholds?company_id=...&asset_id=...`
- `GET /api/v1/market-risk/breaches?company_id=...&period_id=...`
- `PATCH /api/v1/market-risk/breaches/{breach_id}` for governed owner commentary/status transitions.

A breach record should preserve metric, threshold/version, observed value, source model run, timestamp, owner, commentary, approval state and linked mitigation/action IDs.

## Frontend replacement rule

`frontend/src/features/market-risk/contracts.ts` is a temporary mock/view-model schema. When these backend contracts are implemented:

1. generate TypeScript types from FastAPI OpenAPI;
2. build thin adapters from generated responses to presentation models;
3. delete duplicated authoritative finance/model fields from the frontend contract;
4. keep only display-specific types such as chart-coordinate helpers;
5. remove `MODEL CONTRACT PENDING` only after validated backend runs are actually bound.
