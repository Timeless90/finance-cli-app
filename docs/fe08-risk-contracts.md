# FE-08 — Risk Command Center Backend Contracts

## Lifecycle

Frontend lifecycle: **MOCK CONNECTED**.

The Risk Command Center is implemented as an executive risk workspace, but it does not calculate portfolio risk, regime probabilities, EVT parameters, correlations, or mitigation economics in the browser. All finance/risk calculations must remain backend-owned and versioned.

## Existing FastAPI capabilities

The current risk API already provides useful domain operations:

| Method | Endpoint | Capability |
| --- | --- | --- |
| POST | `/api/v1/risk/register` | create a risk register entry |
| GET | `/api/v1/risk/register` | list risk register entries |
| GET | `/api/v1/risk/register/{risk_id}` | read one risk |
| POST | `/api/v1/risk/mitigations` | create/evaluate mitigation state |
| POST | `/api/v1/risk/portfolio/aggregate` | Monte-Carlo portfolio aggregation |
| POST | `/api/v1/risk/portfolio/sensitivity` | portfolio sensitivity analysis |
| POST | `/api/v1/risk/reporting/map` | risk-map reporting output |
| POST | `/api/v1/risk/reporting/scenario` | scenario reporting output |
| POST | `/api/v1/risk/reporting/board-summary` | board-level summary |
| POST | `/api/v1/risk/reporting/lagebericht` | Lagebericht-oriented output |
| POST | `/api/v1/risk/reporting/narrative` | risk narrative generation |
| POST | `/api/v1/risk/expectations/backtest` | expectation/backtest evaluation |
| POST | `/api/v1/risk/register/archive-resolved` | register lifecycle operation |

`POST /api/v1/risk/portfolio/aggregate` already supports an explicit path count, deterministic seed, optional correlation matrix, and returns portfolio statistics including mean gross/net loss, P50/P90/P95/P99 net loss, Expected Shortfall 95 and risk contributions.

## Gap 1 — Scoped Risk Command workspace read model

The current register read endpoint is not sufficient as the authoritative source for the FE-08 workspace because the web client requires one governed company/period/scenario context and consistent run/snapshot lineage across register, aggregation, appetite, controls and scenario results.

### Recommended endpoint

`GET /api/v1/risk/workspace`

Recommended query parameters:

| Parameter | Required | Purpose |
| --- | --- | --- |
| `company_id` | yes | authoritative company scope |
| `period_id` | yes | reporting / risk cut-off |
| `scenario_id` | yes | active scenario context |
| `aggregation_run_id` | no | select an existing validated risk aggregation run |

### Recommended response

```text
RiskWorkspaceSnapshot
  context
    company_id
    company_label
    period_id
    period_label
    scenario_id
    scenario_label
    as_of
  lineage
    source_snapshot_ids[]
    risk_register_version
    aggregation_run_id
    model_version
    generated_at
  portfolio
    mean_gross_loss
    mean_net_loss
    p50_net_loss
    p90_net_loss
    p95_net_loss
    p99_net_loss
    expected_shortfall_95
    appetite_usage
    n_paths
    seed
  percentile_curve[]
    percentile
    loss
  risks[]
    risk_id
    title
    category
    owner
    probability
    impact
    expected_loss
    p95_loss
    residual_loss
    mitigation_effect
    appetite_usage
    status
    trend
  categories[]
  appetite_radar[]
  correlation
    labels[]
    matrix[][]
  scenario
    scenario_run_id
    name
    probability
    earnings_at_risk
    cash_at_risk
    drivers[]
  controls[]
  assurance
    data_quality
    validation_status
    lineage_status
```

The response must use backend-produced/persisted values. The frontend may format values and map them into chart coordinates only.

## Gap 2 — Persisted portfolio aggregation runs

The current aggregation endpoint calculates a result synchronously from supplied risk records. The UI needs reproducible, auditable results that can be reopened without resubmitting reconstructed inputs.

Recommended API surface:

- `POST /api/v1/risk/portfolio/runs`
- `GET /api/v1/risk/portfolio/runs/{run_id}`
- `GET /api/v1/risk/portfolio/runs?company_id=...&period_id=...&scenario_id=...`

Recommended run metadata:

```text
RiskAggregationRun
  run_id
  company_id
  period_id
  scenario_id
  source_snapshot_ids[]
  risk_register_version
  model_version
  n_paths
  seed
  correlation_model
  correlation_matrix_id
  status
  validation_status
  created_at
  created_by
  result
```

## Gap 3 — Regime / Markov model contract

No backend regime-switching or Markov transition model was found in the current risk API implementation. FE-08 therefore renders this panel only as a clearly marked `MODEL CONTRACT PENDING` surface.

Recommended run-based API:

- `POST /api/v1/risk/models/regime/runs`
- `GET /api/v1/risk/models/regime/runs/{run_id}`

Recommended response:

```text
RegimeModelRun
  run_id
  model_version
  training_window
  input_snapshot_ids[]
  states[]
    state_id
    label
    probability
    expected_loss_multiplier
  current_state
  current_state_probability
  transition_matrix[][]
  diagnostics
    convergence_status
    log_likelihood
    aic
    bic
  validation_status
```

The frontend must not estimate transition probabilities or classify regimes itself.

## Gap 4 — Extreme Value Theory contract

No EVT/GPD backend contract was found in the current implementation. FE-08's tail diagnostic is therefore presentation-only fixture data.

Recommended API:

- `POST /api/v1/risk/models/evt/runs`
- `GET /api/v1/risk/models/evt/runs/{run_id}`

Recommended response:

```text
EvtModelRun
  run_id
  model_version
  source_snapshot_ids[]
  threshold
  threshold_quantile
  exceedance_count
  shape_xi
  scale_beta
  return_levels[]
  expected_shortfall
  qq_points[]
    theoretical
    observed
  diagnostics
    goodness_of_fit
    stability_checks
  validation_status
```

## Gap 5 — Dependency / copula model contract

The current portfolio aggregation can consume a correlation matrix, but no versioned dependency-model or copula API was found. A future Market Risk / Enterprise Risk implementation should persist how dependency structures were estimated rather than passing anonymous matrices through the UI.

Recommended API:

- `POST /api/v1/risk/models/dependency/runs`
- `GET /api/v1/risk/models/dependency/runs/{run_id}`

Recommended result metadata:

```text
DependencyModelRun
  run_id
  model_version
  method
    correlation | gaussian_copula | t_copula | other
  source_snapshot_ids[]
  variables[]
  correlation_matrix[][]
  copula_parameters
  tail_dependence
  fit_statistics
  validation_status
```

## Governance requirements

Every advanced risk-model result consumed by the frontend should carry:

- immutable `run_id`;
- `model_version`;
- source snapshot / data lineage identifiers;
- deterministic seed where simulation is used;
- configuration/parameter provenance;
- validation status;
- creation timestamp and principal;
- explicit lifecycle state (`DRAFT`, `VALIDATED`, `APPROVED`, `SUPERSEDED`).

This ensures Risk Command outputs remain reproducible, auditable and suitable for executive reporting rather than becoming opaque dashboard calculations.
