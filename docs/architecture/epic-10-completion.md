# Epic 10 Completion — Reporting Factory

## Scope

Epic 10 implements roadmap E9 — Reporting Factory.

Delivered capabilities:

- versioned report templates,
- Management Pack,
- Board Risk Pack,
- Forecast Report,
- Lagebericht Draft,
- Audit Evidence Pack,
- immutable content hashing,
- run- and snapshot-lineage validation,
- human approval for external artifacts,
- export to JSON, CSV, Excel, PDF and PowerPoint,
- versioned FastAPI reporting endpoints.

## Architecture

The reporting layer consumes already-calculated and approved finance values. It does not calculate forecast, risk, liquidity or performance metrics itself.

Each `ReportValue` must carry:

- source snapshot ID,
- source run ID,
- source run approval status.

Each material narrative statement must carry explicit source references.

The report content hash is deterministic for identical template versions and report content. Generated report IDs and timestamps are intentionally excluded from the content hash.

## Built-in templates

### Management Pack

Required sections:

- KPI,
- performance,
- forecast,
- cash.

Risk and action sections can be added without changing the template contract once those upstream modules are merged.

### Board Risk Pack

Required sections:

- top risks,
- risk capacity,
- stress,
- limits.

### Forecast Report

Required sections:

- assumptions,
- distribution,
- targets,
- model quality.

### Lagebericht Draft

Required sections:

- economic report,
- forecast,
- opportunities,
- risks.

This template is classified as external. Export is blocked until explicit human approval is recorded.

### Audit Evidence Pack

Required sections:

- lineage,
- approvals,
- models,
- assumptions,
- hashes.

## Export formats

The export service generates:

- JSON for machine-readable downstream workflows,
- CSV for flat finance extracts,
- XLSX using `openpyxl`,
- PDF using `reportlab`,
- PPTX using `python-pptx`.

ESEF/XBRL tagging remains a later roadmap extension.

## API

The reporting surface is available under `/api/v1/reporting`:

- `GET /templates`
- `POST /reports`
- `GET /reports/{report_id}`
- `POST /reports/{report_id}/approve`
- `GET /reports/{report_id}/export/{format}`

Supported export format path values are `json`, `csv`, `xlsx`, `pdf` and `pptx`.

## Acceptance Criteria Evidence

### Report numbers equal approved runs

`ReportingFactory.generate` rejects every report value that does not contain source lineage or references a run whose status is not `approved`.

Acceptance tests verify that approved Decimal values are passed through unchanged and unapproved run values are rejected.

### Every material statement has lineage

`ReportingFactory.generate` rejects narrative statements with an empty `source_refs` collection.

Acceptance tests explicitly validate this condition.

### External reports require human approval

Templates classify reports as internal or external.

`ReportExporter` rejects every export attempt for an external draft report. `ReportingFactory.approve` records approver and UTC approval timestamp before external export is allowed.

Acceptance tests verify that the Lagebericht PDF export is blocked before approval and succeeds after approval.

### Export coverage

Acceptance tests validate generated signatures/content for all roadmap formats:

- JSON,
- CSV,
- XLSX,
- PDF,
- PPTX.

## Upstream integration strategy

Epic 10 is intentionally implemented on `main` without a compile-time dependency on the still-open Epic 08 and Epic 09 branches.

Risk and action results enter reports as governed `ReportSection` values with explicit run/snapshot lineage. Once those upstream PRs are merged, adapters can construct these sections directly from their domain services without changing the reporting contracts.

## Deferred enterprise concerns

The following concerns remain later enterprise hardening items rather than Epic 10 acceptance requirements:

- durable report artifact storage in Azure Blob Storage,
- PostgreSQL persistence for report metadata,
- qualified electronic approvals/signatures,
- ESEF/XBRL taxonomy mapping,
- pixel-perfect corporate design systems,
- asynchronous rendering for very large packs.
