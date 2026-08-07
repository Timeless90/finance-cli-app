# Epic 06 Completion — Cost & Profitability Management

## Scope

Epic 06 implements the cost- and profitability-management layer defined by the CFO product roadmap. It provides contribution-margin accounting, dimensional profitability analysis, versioned cost allocation, optional activity-based costing, reconciliation to financial references, price/cost sensitivity analysis and probability-weighted margin-at-risk.

## Delivered capabilities

### Contribution margin and profitability

- Contribution Margin I from revenue less variable cost.
- Contribution Margin II after direct fixed cost.
- Operating margin after allocated cost.
- Margin percentage with zero-revenue handling.
- Aggregation and drilldown by product, customer, channel, cost center and profit center.
- Snapshot and version lineage retained in summaries.

### Cost allocation

- Direct, driver-based and activity-based allocation methods.
- Allocation-version ID on every allocation result.
- Source snapshot lineage on every allocated amount.
- Driver value and driver total stored for reproducibility.
- Exact reconciliation of allocated cost to source cost pool.

### Activity-Based Costing

- Activity-specific cost pools and rates.
- Target-specific activity consumption.
- Deterministic allocation of activity costs to products, customers or other targets.
- Exact source-to-target reconciliation.

### Financial reconciliation

- Explicit reconciliation service for profitability output versus GuV or cost-accounting reference values.
- Difference and reconciliation status returned as first-class output.

### Sensitivity analysis

- Price sensitivity.
- Volume sensitivity.
- Variable-cost sensitivity.
- Fixed-cost sensitivity.
- Combined stressed revenue, cost and operating-margin output.

### Margin-at-Risk

- Probability-weighted margin distribution.
- Expected margin.
- Confidence-level threshold margin.
- Margin-at-Risk relative to expected margin.
- Probability of falling below a management target margin.

### API

- `POST /api/v1/profitability/summary`
- `POST /api/v1/profitability/allocations`
- `POST /api/v1/profitability/activity-based-costing`
- `POST /api/v1/profitability/reconcile`
- `POST /api/v1/profitability/sensitivity`
- `POST /api/v1/profitability/margin-at-risk`

## Acceptance criteria evidence

| Criterion | Evidence |
|---|---|
| Profitability values reconcile with P&L and cost accounting | `ProfitabilityReconciliationService` returns an exact difference and reconciled flag; acceptance tests verify zero-difference reconciliation. |
| Cost allocations are versioned | Every `CostAllocation` stores `allocation_version_id`; ABC results also carry the allocation version. |
| Cost allocations are traceable | Every driver-based allocation stores the immutable source snapshot ID, driver value and driver total. |
| Allocated costs reconcile to source pools | `CostAllocationService` rejects non-reconciled allocation runs and ABC reports the exact source-versus-allocated difference. |
| Profitability is available by relevant management dimensions | `ProfitabilityService.group_by` supports product, customer, channel, cost center and profit center. |
| Price and cost sensitivities are measurable | `MarginSensitivityService` calculates stressed revenue, stressed cost and margin change. |
| Margin risk is quantified | `MarginAtRiskService` calculates expected margin, tail threshold, Margin-at-Risk and target-shortfall probability. |
| API contracts are versioned and tested | Routes are registered below `/api/v1/profitability`; acceptance tests exercise allocation and Margin-at-Risk endpoints. |

## Test coverage

`tests/test_epic06_profitability.py` covers:

- Contribution Margin I, Contribution Margin II and operating margin.
- Product-level profitability drilldown.
- Versioned and traceable driver-based cost allocation.
- Exact allocation reconciliation.
- Activity-Based Costing and activity-rate allocation.
- Profitability reconciliation to a financial reference.
- Combined price, volume and cost sensitivities.
- Probability-weighted Margin-at-Risk and shortfall probability.
- FastAPI contracts.

## Dependency and merge strategy

The branch is stacked on `feature/epic-05-financial-performance-management`. After Epic 05 is merged, this pull request can be retargeted to `main` without changing the Epic 06 implementation diff.
