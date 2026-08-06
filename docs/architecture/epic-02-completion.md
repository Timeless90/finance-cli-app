# Epic 02 Completion — Finance Data Foundation

## Status

Implementation complete pending CI validation.

## Delivered capabilities

### E1-F1 — CSV and Excel ingestion

- Canonical finance-record contract for company, account, period, scenario, value, currency and dimensions.
- UTF-8 CSV ingestion with configurable source-column mappings.
- XLSX/XLSM ingestion using the same canonical parser and optional sheet selection.
- Explicit source-row metadata for data-quality evidence.

### E1-F2 — Finance semantic model

- Versioned account mappings.
- Canonical account and metric references.
- Configurable sign normalization.
- KPI definitions and aggregation metadata.
- Explicit detection of unmapped source accounts.

### E1-F3 — Data quality framework

- Blocking and non-blocking findings.
- Empty-dataset, completeness, duplicate, period and currency validation.
- Allowed-currency and required-dimension policies.
- Deterministic data-quality score and run-eligibility decision.

### E1-F4 — Reconciliation engine

- Reference-total and trial-balance-style rules.
- Account, company, period and scenario filters.
- Absolute tolerance handling.
- Passed, warning and failed statuses.
- Account-period aggregation evidence.

### E1-F5 — Data snapshotting

- Canonical serialization independent of source row order.
- SHA-256 content-addressed snapshot identity.
- Immutable repository contract with collision protection.
- Snapshot creation only after quality, mapping and reconciliation gates pass.

### Data API

- `POST /api/v1/data/imports` for governed CSV and Excel imports.
- Data-quality and reconciliation evidence in the response.
- Run-eligibility and immutable snapshot references.
- `GET /api/v1/data/snapshots/{snapshot_id}` for snapshot metadata.

## Acceptance-criteria matrix

| Criterion | Evidence |
|---|---|
| Critical data errors block forecast-ready datasets | `FinanceDataWorkflow.run_eligible` and no snapshot creation |
| Every eligible run can reference a concrete snapshot | `DataSnapshotRepository`, snapshot API |
| Identical canonical data produce identical hashes | order-independent snapshot regression test |
| General-ledger totals reconcile to references | `FinanceReconciliationService` and tolerance tests |
| CSV and Excel use one canonical data contract | `_CanonicalRowParser` shared by both importers |
| Unmapped accounts are visible and blocking | `SemanticMappingResult.unmapped_accounts` |
| Data APIs are versioned and contract-tested | `/api/v1/data/*` API tests |

## Architectural boundaries

```text
CSV / Excel
    |
Canonical Importers
    |
Semantic Mapping
    |
Data Quality + Reconciliation
    |
Immutable Snapshot Factory
    |
Snapshot Repository Port
    |
FastAPI Data Resources / Model Runs
```

The in-memory snapshot repository is the local-development adapter. Epic 03 may replace it with PostgreSQL metadata and Azure Blob Storage without changing the workflow or repository contracts.

## Deferred by design

The following concerns are assigned to later roadmap epics:

- durable PostgreSQL and Azure Blob snapshot persistence — Epic 03
- RBAC and entity-level data permissions — Epic 03
- interactive browser-based mapping assistant — web delivery after API stabilization
- ERP-specific connectors and scheduled ingestion — later integration roadmap
- consolidation and intercompany elimination logic — integrated planning and reporting epics
