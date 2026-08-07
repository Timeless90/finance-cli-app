# Epic 03 Completion — Governance, Run Store & Audit Trail

## Scope

Epic 03 establishes product-wide governance for model runs, scenarios, assumptions, model versions, approvals, audit events and role-based access.

## Delivered capabilities

### E2-F1 Versioned Run Store

- Run lineage stores model ID/version, code version, snapshot ID, parameter hash and random seed.
- Lifecycle states: draft, validated, approved and retired.
- Approved and retired runs are immutable.
- Output payloads are content-hashed.
- In-memory and durable SQLite reference repositories are available behind the same ports.

### E2-F2 Scenario & Assumption Store

- Base, upside, downside and stress scenario types.
- Versioned assumptions with owner, unit and source metadata.
- Clone, compare and independent approval workflows.
- Scenario content hashes provide integrity evidence.

### E2-F3 Model Registry

- Model ID, semantic version, owner, description and limitations.
- Development, validated, approved, deprecated and retired lifecycle states.
- Validation runs are mandatory before approval.
- Model owners cannot self-approve.

### E2-F4 Immutable Audit Trail

- Append-only audit events for run creation, validation, approval and retirement.
- Actor, timestamp, correlation ID, reason and before/after hashes.
- Durable SQLite audit repository with aggregate lookup.

### E2-F5 Role-Based Access Control

- Roles: CFO, FP&A, Risk, Treasury, Controller, Reviewer and Admin.
- Explicit permissions for data, runs, scenarios, models, audit and access management.
- Optional company scopes restrict access by legal entity.
- API enforcement uses identity, role and scope headers as a development contract; production identity will be supplied by Microsoft Entra ID.

## API contracts

- `POST /api/v1/governance/runs`
- `POST /api/v1/governance/runs/{run_id}/validate`
- `POST /api/v1/governance/runs/{run_id}/approve`
- `POST /api/v1/governance/runs/{run_id}/retire`
- `GET /api/v1/governance/runs/{run_id}/lineage`
- `POST /api/v1/governance/scenarios`
- `POST /api/v1/governance/models`

## Acceptance evidence

| Acceptance criterion | Evidence |
|---|---|
| Identical snapshot, code, configuration and seed are reproducible | deterministic `RunLineage.parameters_hash`; explicit snapshot, code and seed fields; regression tests |
| Every published number has complete lineage | run lineage endpoint returns model, code, snapshot, parameter hash and seed |
| Approved runs cannot be overwritten | repository immutability guard and lifecycle tests |
| Changes are auditable | append-only events include actor, time, reason, correlation ID and before/after hashes |
| Approval segregation is enforced | preparer/approver and model-owner/reviewer checks |
| Entity access is scoped | RBAC company-scope enforcement tests |
| Governance survives process restart | SQLite repository re-instantiation test |

## Azure production mapping

The implementation uses ports so deployment adapters can be replaced without changing domain logic:

- Azure Database for PostgreSQL: governed runs, scenarios, model registry and indexed audit metadata.
- Azure Blob Storage with immutable/versioned containers: large run outputs, reports and evidence packages.
- Microsoft Entra ID: authenticated principals, application roles and group claims.
- Azure Key Vault: connection strings and signing secrets.
- Application Insights: request correlation and operational telemetry.

The SQLite adapter is the durable reference implementation for local and CI execution. PostgreSQL/Azure adapters must preserve identical repository and immutability contracts.

## Definition of Done

- Domain contracts are framework-independent.
- API routes are versioned and protected by explicit permissions.
- Approved artifacts are immutable.
- Audit records are append-only.
- Tests cover lifecycle, segregation, persistence, RBAC and API lineage.
- No unresolved product decision blocks Epic 04.
