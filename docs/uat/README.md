# Production User Acceptance Testing

This directory is the version-controlled acceptance package for the CFO Platform and CFO Command
Center. It covers the current product and the complete planned production application. A case being
listed does not mean its capability is production-ready: `release_scope`, `readiness`, and `blocker`
must be read together.

## Package contents

- `frontend-uat.csv` defines business-facing functional, visual, responsive, accessibility, and
  frontend/backend contract acceptance.
- `developer-data-flow-acceptance.csv` defines human review of authorization, processing,
  persistence, lineage, audit, API responses, artifacts, and recovery.
- `execution-log.csv` is the append-only history of case executions and reviews.
- `evidence/README.md` defines evidence naming, redaction, metadata, and retention.

The acceptance catalogues are stable specifications. Do not write run results into them or change a
case's meaning after execution. Add a new case ID when acceptance behavior materially changes, and
set superseded cases to `retired`.

## CSV rules

All files use UTF-8 and RFC 4180 comma-separated values with one header row. Quote fields containing
commas, quotes, or line breaks. Ordered steps within a field are separated by semicolons so one test
case remains one physical CSV row. Case IDs are immutable and globally unique:

- Frontend cases: `FE-UAT-###`
- Developer data-flow cases: `DEV-DATA-###`

Allowed catalogue values:

| Field | Allowed values |
| --- | --- |
| `release_scope` | `current`, `production_target`, `deferred` |
| `readiness` | `ready`, `planned_blocked`, `deferred`, `retired` |
| `priority` | `critical`, `high`, `medium`, `low` |

Allowed execution results are `not_run`, `passed`, `failed`, `blocked`, and `skipped`. The run log
must contain one row per execution. Never edit or delete historical execution rows; append a new row
for a re-test. Every `case_id` in the run log must resolve to exactly one catalogue case.

## Scope interpretation

- `current/ready` means the documented behavior can be executed against the current application.
- `current/planned_blocked` means a visible surface exists but cannot satisfy the acceptance case
  without a named dependency.
- `production_target/planned_blocked` defines required release behavior whose blocker remains open.
- `deferred/deferred` preserves an agreed future capability without including it in the current
  release exit decision.
- `retired` preserves traceability for a case that must no longer be executed.

Mock fixtures, local context selectors, in-memory repositories, trusted identity headers, and
thread-backed jobs are not production evidence. Cases using them must say so. `MOCK CONNECTED` and
`LOCAL CONTEXT` labels may disappear only when the corresponding authoritative backend contracts
are bound and verified.

## Test environments

Use synthetic or formally approved anonymized finance data. Record the environment and immutable
build identifier in every execution row.

| Environment | Purpose | Permitted evidence |
| --- | --- | --- |
| `local-mock` | Current UI behavior with MSW or local fixtures | Screenshots, accessibility output, browser logs |
| `local-integrated` | Frontend and FastAPI integration | Redacted API payloads, logs, local database checks |
| `staging` | Production-like UAT and resilience review | Full evidence set using approved non-production data |
| `production-smoke` | Explicitly approved post-release checks only | Redacted operational evidence; no destructive tests |

## Entry criteria

1. The build and commit SHA are recorded and deployable in the selected environment.
2. Required synthetic datasets and personas are identified and approved.
3. OpenAPI synchronization is current for integrated frontend cases.
4. Required dependencies are healthy, or the case is recorded as `blocked` with the blocker.
5. Known defects, feature flags, browser versions, viewport, timezone, and locale are recorded.
6. Testers can capture evidence without exposing credentials or production finance data.

## Execution

1. Select cases whose `release_scope` and `readiness` match the release decision being assessed.
2. Execute the written preconditions and steps without silently substituting mock data for live data.
3. Compare functional, visual, accessibility, authorization, persistence, and lineage outcomes with
   every applicable expected field.
4. Store evidence according to `evidence/README.md` and append one execution-log row.
5. Record a defect reference for every `failed` result and a blocker explanation for every `blocked`
   result. A skipped critical or high-priority case requires reviewer approval in `notes`.
6. Re-test by appending another execution row with a new `run_id`; preserve the original result.

## Exit criteria

A production release can be accepted only when:

- all in-scope critical and high-priority cases are passed;
- no failed case remains without an approved release disposition;
- blocked cases are outside the approved release scope or have an explicit risk acceptance;
- numerical and finance outputs are approved by the finance/data owner;
- identity, role, and company isolation are approved by security;
- persistence, migration, backup, and restore evidence is approved by the DBA;
- resilience and observability evidence is approved by operations;
- the business owner signs off frontend behavior and the engineering owner signs off data flows.

`planned_blocked` and `deferred` catalogue rows cannot be counted as passed merely because the
current application displays a placeholder or mock representation.

## Roles and sign-off

| Role | Acceptance responsibility |
| --- | --- |
| Business owner | Journey completeness, wording, visual hierarchy, usability, release acceptance |
| Finance/data owner | Numerical meaning, reconciliations, source authority, model and run context |
| Engineering owner | Contract correctness, processing, persistence, lineage, failure behavior |
| Security reviewer | Authentication, authorization, segregation of duties, tenant isolation |
| DBA | Migrations, transactions, durability, backup, restore, retention |
| Operations reviewer | Jobs, retries, readiness, logs, metrics, traces, recovery |
| Accessibility reviewer | Keyboard operation, semantics, focus, contrast, zoom, reduced motion |

## Defects and change control

Defects must reference the case ID and execution `run_id`, describe expected versus actual behavior,
identify the affected build, and link to redacted evidence. Changes to a catalogue row require review
by its `owner`. Never weaken expected behavior to make an existing failure pass. If product intent
changes, retire the old case and create a new immutable case ID.

## Authoritative references

- `docs/frontend-backend-contracts.md` defines the current integration boundary and mock gaps.
- `docs/backend-production-integration-roadmap.md` defines BE-01 through BE-07 target contracts.
- `docs/cfo-product-implementation-roadmap.md` defines planned product scope.
- `frontend/src/app/router.tsx` and `frontend/src/app/navigation.ts` define current routes.
- `/openapi.json` and generated frontend API types define the machine-readable API contract.

The backend remains authoritative for finance calculations, validation, authorization, workflows,
persistence, and governed state. Frontend acceptance verifies presentation and interaction; it must
not validate a browser-side recreation of backend finance logic.
