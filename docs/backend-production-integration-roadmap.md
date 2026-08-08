# Phase 2 — Production Backend Integration

## Scope

This phase is backend-only. Its purpose is to close the integration contracts identified while
building the client workspaces without moving finance calculations, model execution, governance
or orchestration into the frontend.

The sequence is deliberately integration-first:

| Priority | Backend epic | Outcome | Status |
| --- | --- | --- | --- |
| P1 | BE-01 Company / Period / Scenario Context APIs | Authoritative selectable workspace context and principal/RBAC read contract | In progress |
| P1 | BE-02 Workspace Read Models | Backend-produced, query-oriented projections for CFO workspaces | Foundation in progress |
| P2 | BE-03 Risk & Market-Risk Model Runs | Reproducible persisted risk execution contracts | Planned |
| P2 | BE-04 Action & Capital Runs | Versioned decision, action and capital-allocation runs | Planned |
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

The implementation reuses existing backend sources:

- company and period availability are projected from governed finance data snapshots;
- company authorization is enforced by the existing RBAC `Principal.company_scopes`;
- finance-data scenario codes and latest governed `ScenarioVersion` records are exposed through
  one selector contract;
- the resolved context is stateless and explicit. There is no process-global "current company"
  or "current scenario".

No finance values are calculated in these context APIs.

## BE-02 — Workspace Read Models

The first projection contract is:

```text
GET /api/v1/command-center/overview
    ?company_id=...
    &period_id=...
    &scenario_id=...
```

A Command Center response is a **published backend projection**, not an on-demand browser
calculation. The read-model service stores a versioned snapshot containing:

- canonical workspace context;
- as-of timestamp;
- metrics;
- forecast summary;
- liquidity summary;
- risk summary;
- variance drivers;
- actions;
- management briefing;
- assurance / lineage metadata;
- source snapshot IDs.

If no authoritative projection exists for the requested context, the API returns `404`. It does
not manufacture placeholder finance values.

The same repository/service pattern will be extended to:

```text
GET /api/v1/planning/workspace
GET /api/v1/performance/workspace
GET /api/v1/profitability/workspace
GET /api/v1/liquidity/workspace
GET /api/v1/risk/workspace
GET /api/v1/market-risk/workspace
GET /api/v1/actions/workspace
GET /api/v1/capital/workspace
GET /api/v1/reports/workspace
```

## BE-03 — Risk & Market-Risk Model Runs

Next, synchronous model utilities will be wrapped in persisted run contracts with common metadata:

- `run_id`;
- company / period / scenario context;
- source snapshot IDs;
- model family and version;
- parameters and random seed;
- status and validation state;
- created-by / created-at;
- lineage and result references.

Risk aggregation, volatility/GARCH, regime, dependency/copula, simulation and backtest execution
remain backend-owned.

## BE-04 — Action & Capital Runs

Action simulation, portfolio prioritization, project valuation, Monte Carlo NPV, portfolio
optimization and funding scenarios will become versioned decision runs linked to the exact
forecast, risk and covenant state used for the decision.

## BE-05 — Reporting Orchestration

Reporting will move from direct rendering calls to:

```text
report request -> background job -> governed report run -> artefact -> approval -> publication
```

PDF/PPTX artefacts will retain source context, lineage and publication state.

## BE-06 — Microsoft Foundry Copilot Orchestration

The Finance Copilot will consume a governed context assembler rather than querying arbitrary
backend state. The orchestration layer will own:

- approved workspace/read-model context assembly;
- model routing;
- Foundry tool invocation;
- grounding/citation metadata;
- fallback handling;
- token/cost telemetry;
- complete interaction and run lineage.

## BE-07 — Production Integration Hardening

Cross-cutting hardening includes:

- idempotency keys;
- optimistic concurrency/version checks;
- pagination and filtering;
- rate limiting;
- correlation IDs and structured logs;
- metrics and traces;
- retry/circuit-breaker behavior for Azure/Foundry dependencies;
- read-model caching;
- systematic RBAC and company-scope tests.

## Definition of Done for Phase 2

A client can select a company, period and scenario, load governed workspace projections, start and
retrieve risk/capital/action runs, generate governed reports and invoke the Finance Copilot against
the same approved backend context without knowing internal service topology or recomputing
authoritative finance/model outputs.
