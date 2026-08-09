# Phase 2 — Production Backend Integration

## Scope

This phase is backend-only. Its purpose is to close the integration contracts identified while
building the client workspaces without moving finance calculations, model execution, governance
or orchestration into the frontend.

The sequence is deliberately integration-first:

| Priority | Backend epic | Outcome | Status |
| --- | --- | --- | --- |
| P1 | BE-01 Company / Period / Scenario Context APIs | Authoritative selectable workspace context and principal/RBAC read contract | Complete |
| P1 | BE-02 Workspace Read Models | Backend-produced, query-oriented projections for CFO workspaces | Complete |
| P2 | BE-03 Risk & Market-Risk Model Runs | Reproducible persisted risk execution contracts | Complete |
| P2 | BE-04 Action & Capital Runs | Versioned decision, action and capital-allocation runs | In review |
| P3 | BE-05 Reporting Orchestration | Governed report jobs, artefacts, approvals and publication | Planned |
| P3 | BE-06 Microsoft Foundry Copilot Orchestration | Governed context assembly, routing, tool execution and lineage | Planned |
| P4 | BE-07 Production Integration Hardening | Idempotency, concurrency, caching, observability and resilience | Planned |

## BE-01 — Context APIs

### Contracts

```text
GET /api/v1/context/principal
GET /api/v1/context/companies
GET /api/v1/context/periods?company_id=...
GET /api/v1/context/scenarios?company_id=...&period_id=...
GET /api/v1/context/resolve?company_id=...&period_id=...&scenario_id=...
```

Company and period availability come from governed finance data snapshots. Company authorization
uses the existing RBAC `Principal.company_scopes`. Scenario codes and governed scenario versions
are projected through one stateless selector contract.

## BE-02 — Workspace Read Models

Published backend projections now cover the Command Center plus Planning, Performance,
Profitability, Liquidity, Risk, Market Risk, Actions, Capital Allocation and Reporting. Every
projection is resolved against the canonical Company / Period / Scenario context and carries
version, freshness, assurance and source-snapshot lineage. Missing authoritative projections fail
closed with `404`; the client does not manufacture finance values.

## BE-03 — Risk & Market-Risk Model Runs

Persisted model-run contracts wrap existing risk engines with backend-owned execution status and
lineage:

```text
POST /api/v1/risk/model-runs
GET  /api/v1/risk/model-runs/{run_id}
POST /api/v1/market-risk/model-runs
GET  /api/v1/market-risk/model-runs/{run_id}
```

Enterprise Risk aggregation and Market Risk VaR/ES, GARCH-t, regime HMM, EVT, copula and VaR
backtesting remain backend-owned and reproducible against the selected context and source
snapshots.

## BE-04 — Action & Capital Runs

BE-04 turns the existing Action Management and Capital Allocation engines into governed,
persisted decision runs. Existing synchronous calculation endpoints remain backward compatible.

### Action run contracts

```text
POST /api/v1/actions/runs
GET  /api/v1/actions/runs?company_id=...&period_id=...&scenario_id=...
GET  /api/v1/actions/runs/{run_id}
POST /api/v1/actions/runs/{run_id}/validate
POST /api/v1/actions/runs/{run_id}/approve
POST /api/v1/actions/runs/{run_id}/reject
```

Supported Action run types:

- `simulation` — expected EBITDA, cash and covenant effects from registered management actions;
- `prioritization` — backend-owned action portfolio ranking;
- `benefit_tracking` — realized-versus-planned benefit measurement.

### Capital run contracts

```text
POST /api/v1/capital/runs
GET  /api/v1/capital/runs?company_id=...&period_id=...&scenario_id=...
GET  /api/v1/capital/runs/{run_id}
POST /api/v1/capital/runs/{run_id}/validate
POST /api/v1/capital/runs/{run_id}/approve
POST /api/v1/capital/runs/{run_id}/reject
```

Supported Capital run types:

- `project_valuation` — NPV/IRR/ROIC/payback evaluation;
- `monte_carlo_npv` — reproducible stochastic project valuation;
- `portfolio_allocation` — constrained project portfolio optimization;
- `funding_scenario` — funding/refinancing and covenant-headroom evaluation.

Every decision run carries an immutable run ID, canonical Company / Period / Scenario context,
backend-derived source snapshot IDs, explicit upstream run IDs, engine version, execution
lifecycle, creator/timestamps and a separate governance lifecycle:

```text
execution:  pending -> running -> succeeded | failed
governance: draft -> validated -> approved | rejected
```

Creation requires `CREATE_RUN`; validation requires `VALIDATE_RUN`; approval/rejection requires
`APPROVE_RUN`. Company scope is enforced for reads and transitions. Failed runs are retained and
cannot be validated or approved.

## BE-05 — Reporting Orchestration

Reporting moves from direct rendering calls to a governed asynchronous lifecycle:

```text
report request -> background job -> governed report run -> artefact -> approval -> publication
```

PDF/PPTX artefacts retain source context, lineage, publication state and references to approved
workspace/model/decision runs.

## BE-06 — Microsoft Foundry Copilot Orchestration

The Finance Copilot consumes a governed context assembler rather than arbitrary backend state. The
orchestration layer owns approved read-model/run context assembly, model routing, Foundry tool
invocation, grounding/citations, fallback handling, token/cost telemetry and complete interaction
lineage.

## BE-07 — Production Integration Hardening

Cross-cutting hardening includes idempotency keys, optimistic concurrency/version checks,
pagination/filtering, rate limiting, correlation IDs, structured logs, metrics/traces,
retry/circuit-breaker behavior for Azure/Foundry dependencies, read-model caching and systematic
RBAC/company-scope tests.

## Definition of Done for Phase 2

A client can select a company, period and scenario, load governed workspace projections, start and
retrieve risk/capital/action runs, generate governed reports and invoke the Finance Copilot against
the same approved backend context without knowing internal service topology or recomputing
authoritative finance/model outputs.
