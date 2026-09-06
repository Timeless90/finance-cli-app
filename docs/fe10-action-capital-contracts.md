# FE-09 — Action Steering & Capital Allocation Backend Contracts

## Lifecycle

Frontend lifecycle: **LIVE API CONNECTED for published read models in UAT/live; MOCK CONNECTED only in explicit frontend isolation mode.**

The published company/period/scenario Action Steering and Capital Allocation read models are bound through generated OpenAPI types. The browser must not calculate benefit realization, capital rankings, NPV/IRR, constrained allocations or approval outcomes. BE-04's governed mutation lifecycle remains outstanding.

## Action Steering

### Existing boundary

`GET /api/v1/actions` remains available for the action register where applicable. FE-09 uses the published workspace projection for source-signal lineage, expected-value baselines, realized benefits, evidence, decision gates and dependencies in one read model.

### Recommended endpoint

`GET /api/v1/actions/workspace?company_id=...&period_id=...&scenario_id=...`

Recommended response:

```text
ActionSteeringSnapshot
  context
  lineage
    source_snapshot_ids[]
    action_register_version
  metrics
  actions[]
    action_id
    title
    source_type
    source_id
    owner
    sponsor
    due_at
    priority
    status
    confidence
    expected_ebitda
    expected_cash
    realized_ebitda
    realized_cash
    realization_pct
    risk_reduction
    evidence[]
    next_gate
  benefit_series[]
  dependencies[]
  assurance
```

Recommended lifecycle mutations should use explicit state transitions rather than arbitrary field replacement, for example:

- `POST /api/v1/actions/{action_id}/approve`
- `POST /api/v1/actions/{action_id}/start`
- `POST /api/v1/actions/{action_id}/complete`
- `POST /api/v1/actions/{action_id}/benefits`
- `POST /api/v1/actions/{action_id}/evidence`

Every transition should preserve principal, timestamp, previous/new state, rationale and correlation ID.

## Benefit realization

Expected and realized benefits must be backend-owned and traceable to an approved baseline. Recommended model:

```text
ActionBenefitBaseline
  baseline_id
  action_id
  metric
    EBITDA | CASH | COST | REVENUE | RISK_REDUCTION
  expected_value
  currency
  start_period
  end_period
  confidence
  source_snapshot_ids[]
  approved_by
  approved_at

ActionBenefitRealization
  realization_id
  baseline_id
  period_id
  realized_value
  evidence_ids[]
  validation_status
```

The frontend may display realization percentages but should receive either the percentage or both validated numerator/denominator values from the backend.

## Capital Allocation

### Recommended read model

`GET /api/v1/capital/workspace?company_id=...&period_id=...&scenario_id=...`

Recommended response:

```text
CapitalAllocationSnapshot
  context
  portfolio
    budget
    committed
    approved
    unallocated
    liquidity_reserve
    expected_portfolio_npv
    downside_capital_at_risk
  candidates[]
    candidate_id
    name
    category
    sponsor
    capital_required
    npv
    irr
    payback
    risk_adjusted_score
    strategic_fit
    liquidity_impact
    downside_loss
    status
  constraints[]
  allocation[]
  frontier_points[]
  approvals[]
  selected_allocation_run_id
  lineage
```

## Capital candidate evaluation runs

Candidate economics should be versioned outputs, not client-side formulas.

Recommended API:

- `POST /api/v1/capital/candidates`
- `GET /api/v1/capital/candidates/{candidate_id}`
- `POST /api/v1/capital/evaluations`
- `GET /api/v1/capital/evaluations/{run_id}`

Recommended evaluation output:

```text
CapitalEvaluationRun
  run_id
  candidate_id
  model_version
  source_snapshot_ids[]
  assumptions_version
  cash_flow_version
  npv
  irr
  payback
  risk_adjusted_npv
  downside_loss
  liquidity_metrics
  strategic_fit
  validation_status
```

## Constrained allocation runs

Recommended API:

- `POST /api/v1/capital/allocation-runs`
- `GET /api/v1/capital/allocation-runs/{run_id}`
- `GET /api/v1/capital/allocation-runs?company_id=...&period_id=...&scenario_id=...`

Recommended run metadata/result:

```text
CapitalAllocationRun
  run_id
  model_version
  candidate_evaluation_run_ids[]
  scenario_id
  objective
    MAX_NPV | MAX_RISK_ADJUSTED_NPV | LIQUIDITY_FIRST | BALANCED
  constraints[]
    constraint_id
    metric
    limit
    source
  selected_candidates[]
  allocations[]
  expected_portfolio_npv
  downside_capital_at_risk
  liquidity_headroom
  frontier_points[]
  solver_status
  validation_status
  created_by
  created_at
```

No optimization or project ranking should be implemented in React.

## Approval governance

Recommended approval endpoints:

- `GET /api/v1/capital/approvals?...`
- `POST /api/v1/capital/candidates/{candidate_id}/submit`
- `POST /api/v1/capital/approvals/{approval_id}/approve`
- `POST /api/v1/capital/approvals/{approval_id}/reject`

Approval records should preserve gate, owner/role, decision, rationale, evidence, allocation-run reference and immutable timestamp.

## Frontend replacement rule

`frontend/src/features/action-capital/contracts.ts` is a display view-model contract. The OpenAPI-backed read models are mapped through thin adapters; the remaining replacement rule applies to BE-04 command workflows:

1. generate response types through FE-03 OpenAPI sync;
2. map generated types through thin feature adapters;
3. delete duplicated authoritative fields from frontend contracts;
4. retain only display-specific types;
5. keep `LIVE API CONNECTED` for published read models and add mutation states only when governed commands are bound.
