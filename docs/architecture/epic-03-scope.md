# Epic 03 — Governance, Run Store & Audit Trail

## Objective

Provide product-wide reproducibility, approvals, immutable lineage and access governance for forecast, risk, backtest and reporting workflows.

## Delivery slices

### Slice 1 — Versioned run governance

- Persist model ID and version, code version, data snapshot, parameters, random seed and outputs.
- Lifecycle states: draft, validated, approved and retired.
- Approved runs are immutable and may only be superseded by a new run.

### Slice 2 — Scenario and assumption governance

- Versioned scenarios and assumption sets.
- Clone, compare, submit, approve and retire workflows.
- Explicit owner and rationale for every material assumption.

### Slice 3 — Model registry

- Model identity, version, owner, validation state, limitations and lifecycle.
- Links to validation evidence, backtests and approved use cases.

### Slice 4 — Immutable audit trail

- Append-only events for data, assumptions, models, runs, reports and access decisions.
- Actor, timestamp, correlation ID, reason and before/after hashes.

### Slice 5 — Role-based access control

- Roles for CFO, FP&A, Risk, Treasury, Controller, Reviewer and Admin.
- Scope restrictions by company and organizational unit.
- Approval separation between preparer and reviewer.

## Epic acceptance criteria

- Identical snapshot, model version, parameters and seed reproduce identical results.
- Every approved output exposes complete lineage.
- Approved records cannot be overwritten or deleted through application services.
- Every governance mutation creates one immutable audit event.
- Unauthorized company or organizational-unit access is rejected.
