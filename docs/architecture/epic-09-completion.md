# Epic 09 Completion — Action & Decision Management

## Scope

This epic implements roadmap E8 — Action & Decision Management. The module converts analysis outcomes into governed management actions with explicit ownership, timing, costs, expected financial effects, portfolio prioritization, workflow review, escalation, and realized-benefit tracking.

## Delivered capabilities

- Action catalogue with stable action IDs, owner, due period, cost, confidence, description and lifecycle status.
- Time-indexed impacts on EBITDA, cash and named covenants.
- Confidence-weighted action simulation with per-period and aggregate effects.
- Explicit `impact_key` controls that reject double counting across selected actions.
- Deterministic action-portfolio prioritization using benefit/cost efficiency and urgency.
- Controlled status transitions from draft through planned, active, blocked, completed or cancelled.
- Review and escalation logic for blocked and overdue actions.
- Realized-vs-planned benefit tracking with variance and realization ratio.
- Versioned FastAPI contracts wired into the application composition root.

## API surface

- `POST /api/v1/actions/register`
- `GET /api/v1/actions`
- `GET /api/v1/actions/{action_id}`
- `POST /api/v1/actions/simulate`
- `POST /api/v1/actions/portfolio/prioritize`
- `POST /api/v1/actions/{action_id}/status`
- `POST /api/v1/actions/{action_id}/review`
- `POST /api/v1/actions/benefits/track`

## Epic acceptance criteria evidence

### Measures are integrated in time and financially

`ActionSimulationEngine` aggregates confidence-weighted EBITDA, cash and covenant effects by period and at portfolio level. Action cost remains separately visible so gross operational benefit is not silently netted with implementation spend.

Covered by `test_action_simulation_integrates_timing_financials_and_confidence` and the Epic 09 API acceptance test.

### Double counting between measures is detected

Each modeled financial effect carries a stable `impact_key`. Selecting two active measures with the same impact key raises a deterministic validation error before aggregation.

Covered by `test_action_simulation_rejects_duplicate_financial_impacts`.

### Realized effects can be measured against plan

`BenefitTrackingService` aggregates planned and realized observations by action and returns absolute variance plus realized/planned ratio.

Covered by `test_benefit_tracking_measures_realized_vs_planned` and the Epic 09 API acceptance test.

## Additional governance evidence

- Invalid lifecycle transitions are blocked.
- Blocked actions receive critical escalation.
- Overdue, incomplete actions receive warning escalation.
- Portfolio prioritization is deterministic for identical inputs.
- Cancelled actions do not contribute simulated portfolio effects.

## Architectural boundary

Epic 09 starts from the current `main` baseline and does not import the unmerged Epic 08 risk-management branch. Financial and covenant action effects therefore use stable metric contracts rather than a hard dependency on a pending risk module. Once Epic 08 is merged, cross-module adapters can map risk mitigations into the same `ManagementAction` contract without changing this domain model.

## Validation

CI is expected to run the repository-standard quality gates:

- `ruff check .`
- `pytest --cov=finance_cli --cov-report=term-missing`
- Python 3.11
- Python 3.12
