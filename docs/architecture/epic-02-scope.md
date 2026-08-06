# Epic 02 — Finance Data Foundation

## Objective

Provide trusted, harmonized and immutable finance data for forecasting, risk and reporting.

## Delivery slices

### Slice 1 — Canonical import contracts

- Typed tabular finance records for company, account, period, scenario, value, currency and dimensions.
- CSV and Excel readers with explicit source metadata.
- Mapping from source columns to canonical fields.

### Slice 2 — Data quality

- Blocking and non-blocking validation findings.
- Completeness, uniqueness, type, period, currency and dimensional checks.
- Dataset-level quality score and run eligibility decision.

### Slice 3 — Reconciliation

- Trial-balance and reference-total checks.
- Account- and period-level variance evidence.
- Blocking reconciliation thresholds.

### Slice 4 — Immutable snapshots

- Content-addressed snapshot IDs.
- Canonical serialization and SHA-256 integrity hashes.
- Snapshot reference as mandatory model-run input.

### Slice 5 — Data API

- Import, validate, reconcile and snapshot endpoints under `/api/v1/data`.
- Consistent validation and error responses.

## Epic acceptance criteria

- Critical quality findings block forecast execution.
- Every model run can reference one immutable data snapshot.
- Repeated imports of identical canonical data produce the same snapshot hash.
- General-ledger totals reconcile against defined references within configured tolerances.
