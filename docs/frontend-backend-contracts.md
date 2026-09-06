# Frontend ↔ Backend Contracts

This document is the living integration boundary between the CFO web client and the FastAPI platform.

## Contract rule

The FastAPI OpenAPI document at `/openapi.json` is the authoritative machine-readable contract. Frontend request/response models are generated from it and are never manually duplicated once a backend endpoint exists.

```text
FastAPI / Pydantic
      |
      v
/openapi.json
      |
      v
OpenAPI export
      |
      v
generated TypeScript paths/components
      |
      v
openapi-fetch adapter
      |
      v
TanStack Query / feature hooks
      |
      v
React UI
```

## Responsibility boundary

**Backend owns** finance calculations, authoritative validation, authorization, workflow state transitions and persisted run/snapshot/model state.

**Frontend owns** presentation, interaction state, loading/empty/error UX, convenience validation, formatting, visualization, navigation and accessibility.

Client-side validation never replaces backend validation.

## FE-01 — Finance 2060 Design System

Backend contract: none.

## FE-02 — Application Shell & Navigation

Company, fiscal period and scenario selectors use the authoritative context APIs in live UAT mode. Mock mode continues to show explicitly local context values.

Current backend contract:

- `GET /api/v1/context/principal`, `/companies`, `/periods`, `/scenarios` and `/resolve` provide authoritative context.
- The UAT reverse proxy replaces browser-supplied `X-User`, `X-Roles`, and `X-Companies` values with a deploy-side test principal.
- Production identity propagation remains an OIDC/Entra release gate; the browser never creates trust headers.

## FE-03 — API Contract & Mock Architecture

### Machine contract

- source: `GET /openapi.json`
- local export: `npm run api:export`
- TypeScript generation: `npm run api:generate`
- full synchronization: `pnpm api:sync`
- runtime transport: `openapi-fetch`
- remote-state orchestration: TanStack Query
- mock transport: MSW

### Bound system contracts

| Purpose | Method | Endpoint | Request | Response | Auth |
| --- | --- | --- | --- | --- | --- |
| API readiness | GET | `/health/ready` | none | `HealthResponse { status, service, environment, version }` | none |
| Platform metadata | GET | `/api/v1/platform` | none | `PlatformResponse { name, api_version, capabilities[] }` | none |

### Context contracts

| Frontend need | Endpoint | Current state |
| --- | --- | --- |
| principal identity and permissions | `GET /api/v1/context/principal` | UAT live |
| accessible companies | `GET /api/v1/context/companies` | UAT live |
| fiscal periods | `GET /api/v1/context/periods` | UAT live |
| scenarios | `GET /api/v1/context/scenarios` | UAT live |
| canonical selection validation | `GET /api/v1/context/resolve` | UAT live |

In live mode the UI labels these values as backend-bound context.

### Authentication boundary

The frontend will not invent production identities or role headers. The existing `X-User`, `X-Roles` and `X-Companies` mechanism is recorded as the current backend contract, but production identity propagation will be integrated only when the authentication architecture is finalized.

## FE-04 — Public Landing Experience

**Backend contract: none.**

The public landing route `/` is intentionally independent from FastAPI and must render when the platform API is unavailable. Finance values shown in product previews are static simulated presentation data and are labelled as such. The only product boundary is navigation into `/app/command-center`; business API calls remain inside authenticated/product workspaces.

## FE-05 — CFO Command Center

Lifecycle state: **LIVE API CONNECTED in UAT; MOCK CONNECTED in isolated frontend mode.**

The executive cockpit requires one authoritative backend read model. It must not reconstruct group-level finance truth in the browser by orchestrating calculation endpoints or combining partially persisted module state.

### Existing backend capabilities relevant to FE-05

- `GET /api/v1/risk/register` can list currently registered enterprise risks.
- `GET /api/v1/actions` can list currently registered management actions.
- `GET /api/v1/planning/forecasts/{version_id}` can read a known forecast version.
- performance and liquidity APIs currently expose calculation-oriented `POST` endpoints rather than persisted executive read models.
- `GET /api/v1/command-center/overview` returns a published company / period / scenario scoped CFO overview.

The Command Center uses an adapter over generated OpenAPI types in live mode. It does not calculate or reconstruct finance values; unpublished contexts display an explicit error state rather than fixtures.

### Required aggregate read contract

Recommended endpoint:

`GET /api/v1/command-center/overview`

Recommended query parameters:

| Parameter | Required | Purpose |
| --- | --- | --- |
| `company_id` | yes | authoritative company scope |
| `period_id` | yes | reporting / forecast cut-off |
| `scenario_id` | yes | active scenario/version context |

Recommended response shape:

```text
CommandCenterSnapshot
  context
    company_id / company_label
    period_id / period_label
    scenario_id / scenario_label
    currency
    as_of
  metrics[]
    id / label / value / delta / status
  forecast
    title / unit / points[]
  liquidity
    cash / runway / minimum_headroom / covenant_headroom / status
  risk
    score / expected_loss / tail_loss / appetite_usage / top_risks[]
  variance_drivers[]
  actions[]
  briefing
    headline / summary / decisions[]
  assurance
    data_freshness / coverage / model_status / lineage_status
```

The authoritative API should return already-governed values and source/run identifiers where applicable. The frontend may scale chart coordinates and format display values, but it must not recompute EBITDA, cash, risk exposure, scenario probabilities or action benefit values.

### Current FE-05 temporary contract

`frontend/src/features/command-center/contracts.ts` is a **provisional mock-only interface**, not a replacement for OpenAPI. Once the backend endpoint is implemented, the temporary type must be deleted and the feature adapter must map the generated OpenAPI response into the view model.

The application visibly labels the command center as `MOCK CONNECTED` and keeps the global selectors labelled `LOCAL CONTEXT` so simulated values cannot be confused with backend-produced finance output.

## FE-06 — Planning & Performance Workspace

Lifecycle state: **LIVE API CONNECTED in UAT/live; MOCK CONNECTED only in explicit frontend isolation mode.**

FE-06 implements the Planning and Performance workspaces while preserving the calculation boundary. Published, company/period/scenario-scoped workspace projections are loaded through the generated FastAPI contract; the frontend maps values for presentation but does not derive financial results.

### Existing planning calculation contracts

| Method | Endpoint | Current use |
| --- | --- | --- |
| POST | `/api/v1/planning/forecasts` | create a rolling forecast from complete driver inputs |
| GET | `/api/v1/planning/forecasts/{version_id}` | retrieve one forecast when the version ID is already known |
| POST | `/api/v1/planning/probabilistic` | generate a probabilistic forecast from deterministic values and residual history |
| POST | `/api/v1/planning/backtests` | evaluate forecast observations |
| POST | `/api/v1/planning/thresholds/evaluate` | evaluate one KPI against target/warning thresholds |

The create/evaluate endpoints require authoritative source inputs. The frontend must not synthesize those inputs from displayed values merely to make a dashboard appear live.

### Existing performance calculation contracts

| Method | Endpoint | Current use |
| --- | --- | --- |
| POST | `/api/v1/performance/kpi-tree/evaluate` | evaluate a KPI from supplied leaf values |
| POST | `/api/v1/performance/variance-bridges` | build a variance bridge from supplied version values and contributions |
| POST | `/api/v1/performance/forecast-accuracy` | summarize supplied forecast/actual observations |
| POST | `/api/v1/performance/anomalies` | detect anomalies in supplied observations |
| POST | `/api/v1/performance/commentary/requirements` | evaluate commentary materiality/requirements |

These are domain engines, not workspace query APIs. The normal workspace views instead load the published read models below; fixtures are retained only for explicit mock mode and frontend tests.

### Published Planning read contract

Recommended minimum API surface:

- `GET /api/v1/planning/workspace?company_id=...&period_id=...&scenario_id=...`

The planning workspace response should provide:

```text
PlanningWorkspaceSnapshot
  context
  scenarios[]
  active_forecast
    version_id
    snapshot_id
    assumption_set_id
    model_version
    status
  forecast_series[]
    period / actual / plan / forecast / lower / upper
  financial_statement[]
    line_item / actual / plan / forecast / variance
  drivers[]
    driver_id / value / unit / owner / status
  thresholds[]
  forecast_assurance
    confidence / backtest_metrics / bias
```

### Published Performance read contract

- `GET /api/v1/performance/workspace?company_id=...&period_id=...&scenario_id=...`

Optional drill-down endpoints such as `GET /api/v1/performance/variance-bridges/{bridge_id}` and `GET /api/v1/performance/anomalies?...` can be added when persisted identifiers are available.

The performance workspace response should provide:

```text
PerformanceWorkspaceSnapshot
  context
  metrics[]
  kpi_tree[]
  variance_bridge
    baseline / comparison / total / explained / unexplained / contributions[]
  trend[]
  anomalies[]
  commentary_requirements[]
  source_snapshot_ids[]
```

All returned financial values must be backend-produced or persisted domain outputs. The frontend may format numbers and scale visual coordinates, but it must not calculate income statement lines, KPI formulas, variance contributions, accuracy statistics or anomalies.

### FE-06 client contract

`frontend/src/features/planning-performance/query.ts` adapts generated `PlanningWorkspaceResponse` and `PerformanceWorkspaceResponse` types into display view models. It shows `LIVE API CONNECTED` for backend projections. Company, period and scenario options are loaded from the FE-02 context endpoints; a missing projection is surfaced as an empty/error state, never as a fixture fallback.

## FE-07 — Profitability & Liquidity Workspace

Lifecycle state: **LIVE API CONNECTED in UAT/live; MOCK CONNECTED only in explicit frontend isolation mode.**

FE-07 implements product/segment/customer profitability plus liquidity, working capital, debt, covenant and stress-control workspaces without moving backend finance calculations into the browser.

### Existing profitability calculation contracts

| Method | Endpoint | Current use |
| --- | --- | --- |
| POST | `/api/v1/profitability/summary` | summarize supplied profitability records or group them by one dimension |
| POST | `/api/v1/profitability/allocations` | allocate one supplied cost pool using supplied drivers |
| POST | `/api/v1/profitability/activity-based-costing` | calculate ABC rates and target costs from supplied activity pools/consumption |
| POST | `/api/v1/profitability/reconcile` | reconcile supplied expected and actual values |
| POST | `/api/v1/profitability/sensitivity` | evaluate margin sensitivity from supplied revenue/cost assumptions |
| POST | `/api/v1/profitability/margin-at-risk` | calculate margin-at-risk from supplied scenario probabilities and margins |

These endpoints are analytical engines. The normal workspace view reads the published workspace projection; it does not reconstruct profitability records, allocations or margin-at-risk scenarios from displayed numbers merely to invoke these services.

### Existing liquidity calculation contracts

| Method | Endpoint | Current use |
| --- | --- | --- |
| POST | `/api/v1/liquidity/cash-forecast/13-week` | calculate cash positions from supplied weekly flows |
| POST | `/api/v1/liquidity/cash-forecast/monthly` | calculate monthly liquidity positions from supplied period flows |
| POST | `/api/v1/liquidity/working-capital` | calculate working-capital position from supplied revenue/COGS/DSO/DPO/DIO |
| POST | `/api/v1/liquidity/debt-schedules` | calculate a debt schedule from one supplied instrument |
| POST | `/api/v1/liquidity/covenants/evaluate` | evaluate a supplied covenant and optional simulations |
| POST | `/api/v1/liquidity/stress-tests` | apply one supplied liquidity stress scenario |
| POST | `/api/v1/liquidity/cash-forecast/accuracy` | summarize supplied cash forecast observations |

Again, these are calculation contracts. The normal workspace view reads the published workspace projection rather than supplying synthetic source inputs.

### Published Profitability read contract

- `GET /api/v1/profitability/workspace?company_id=...&period_id=...&scenario_id=...`

Recommended workspace response:

```text
ProfitabilityWorkspaceSnapshot
  context
  metrics[]
  segments[]
    dimensions / revenue / contribution_margin / ebitda / allocated_cost / margin_at_risk
  margin_waterfall[]
  profitability_matrix[]
  sensitivity_summary[]
  allocation_assurance
    allocation_version_id / snapshot_id / method
    source_cost / allocated_cost / reconciliation_difference / reconciled
```

### Published Liquidity read contract

- `GET /api/v1/liquidity/workspace?company_id=...&period_id=...&scenario_id=...`

Recommended workspace response:

```text
LiquidityWorkspaceSnapshot
  context
  metrics[]
  cash_forecast
    positions[] / minimum_liquidity / minimum_headroom / accuracy
  working_capital[]
  debt[]
  covenants[]
  stresses[]
  source_snapshot_ids[]
```

All cash positions, working-capital balances, debt schedules, covenant states, stress outcomes, allocations and margin-at-risk values must come from backend-produced or persisted domain outputs. Frontend visualization may scale coordinates and format currency/ratios only.

### FE-07 client contract

`frontend/src/features/profitability-liquidity/query.ts` adapts generated `ProfitabilityWorkspaceResponse` and `LiquidityWorkspaceResponse` types into display view models. It shows `LIVE API CONNECTED` for backend projections. A missing publication or inaccessible company is rendered as its corresponding API state; it never falls back to fixture finance values.

## FE-08 — Enterprise Risk Command

Lifecycle state: **LIVE API CONNECTED in UAT/live; MOCK CONNECTED only in explicit frontend isolation mode.**

`GET /api/v1/risk/workspace?company_id=...&period_id=...&scenario_id=...` is the published workspace contract. It supplies the portfolio, percentile curve, risk register, appetite view, correlation matrix, scenario, controls, and UAT-published regime/EVT diagnostics. The frontend maps the generated `RiskWorkspaceResponse` only for display and renders an explicit API state for an unavailable projection; it never calculates or replaces risk data in the browser.

BE-03 model execution uses `POST` and `GET /api/v1/risk/model-runs`. Every UAT run carries its input context, seed, source snapshot IDs, projection version, status, result or controlled error. The local UAT repository is process-scoped; durable workers and persisted runs remain a production-release requirement.

## Enterprise & Market Risk — Release 3

Lifecycle state: **LIVE API CONNECTED in UAT/live; MOCK CONNECTED only in explicit frontend isolation mode.**

`GET /api/v1/market-risk/workspace?company_id=...&period_id=...&scenario_id=...` supplies published assets, the selected run diagnostics and threshold states. The adapter maps GARCH, regime, copula, Monte-Carlo, backtest and champion/challenger read-model data for display only; it does not invoke quantitative algorithms or construct loss inputs in the browser.

BE-03 provides `POST` and `GET /api/v1/market-risk/model-runs` for governed execution and polling. UAT validates a historical VaR/ES run with source snapshot and context lineage. The process-scoped UAT repository is not a production persistence guarantee.

## FE-09 — Actions & Capital Allocation

Lifecycle state: **LIVE API CONNECTED for published read models in UAT/live; MOCK CONNECTED only in explicit frontend isolation mode.**

`GET /api/v1/actions/workspace?company_id=...&period_id=...&scenario_id=...` supplies the published action-steering metrics, action queue, benefit series and dependencies. `GET /api/v1/capital/workspace?company_id=...&period_id=...&scenario_id=...` supplies the portfolio envelope, investment candidates, constraints, allocation, frontier and approval read-model data. The frontend maps the generated OpenAPI types only for presentation; it does not calculate NPV, ranking, liquidity headroom or financial outcomes in the browser.

Missing publications and inaccessible companies display the corresponding 404/403 API state and never fall back to fixture values in live mode.

BE-04 command runs are now exposed as UAT contracts. `POST /api/v1/actions/runs` starts server-owned action simulation or prioritization, and `POST /api/v1/actions/runs/benefit-tracking` summarizes published benefit baselines/actuals; all use Action IDs rather than browser finance values. `POST /api/v1/capital/runs/valuation`, `/monte-carlo-npv`, `/allocation`, and `/funding` run server-owned candidate and funding inputs selected by business ID. Every create request requires `Idempotency-Key`, context, source snapshot IDs, projection version and model version. `GET /api/v1/decision-runs/{run_id}` plus `POST .../validate`, `.../approve`, and `.../reject` implement the lifecycle; `GET .../events` provides audit history. Validation, approval and rejection are role-gated and a preparer cannot approve or reject their own run.

The Actions and Capital screens can start every published BE-04 UAT run type, show server result/lineage, immediately refresh a context-scoped review queue, and enable Validate/Approve/Reject only when the backend principal advertises the required permission. The server still enforces every transition and segregation-of-duties rule. Full production persistence, queue workers, real identity and durable action/capital master-data repositories remain Release 7 work.

## FE-10 — Reporting Studio

Lifecycle state: **LIVE API CONNECTED in UAT/live; MOCK CONNECTED only in explicit frontend isolation mode.**

`GET /api/v1/reporting/workspace?company_id=...&period_id=...&scenario_id=...` supplies the published report, sections, versions, source pack, findings and export targets. The Reporting Studio maps this generated contract for display only and treats a missing projection as an API no-data state.

BE-05 adds the governed report-run contract: `POST /api/v1/reporting/runs`, `GET /api/v1/reporting/runs`, `GET /api/v1/reporting/runs/{report_id}`, and `POST .../review`, `.../approve`, `.../publish`. A creation binds company, period, scenario, projection version and existing snapshot IDs. The reporting factory rejects values from unapproved runs and material narratives without sources; the workflow requires an authorized reviewer, rejects self-approval, and keeps the approved artifact immutable. Existing `GET /api/v1/reporting/reports/{report_id}/export/{format}` remains the artifact exporter.

## FE-11 — Data & Governance

Lifecycle state: **LIVE API CONNECTED in UAT/live.**

`GET /api/v1/data-governance/workspace?company_id=...&period_id=...&scenario_id=...` is the published read contract for source snapshots, data-quality findings, governed runs, model versions, approvals and lineage. `/app/data` and `/app/governance` intentionally render this backend projection rather than fake approval data. Ingestion commands remain under `/api/v1/data/imports`; durable storage, asynchronous export jobs and production identity remain Release 7 work.

## FE-10 — Governed Finance Copilot

Lifecycle state: **LIVE API CONNECTED for context/session binding in UAT; a successful answer additionally requires the configured Foundry UAT deployment.**

The browser uses `POST /api/v1/copilot/sessions` with only module/workload and the selected company, period and scenario, followed by `POST /api/v1/copilot/sessions/{session_id}/messages`. It never supplies a principal, identity header, source fact, citation, tool permission or model deployment. The backend resolves the principal from the gateway, checks company scope, assembles facts from the published reporting projection, applies prompt-injection and grounding rules, routes through the configured deployment, and records interaction lineage in the backend service.

The former direct `/api/v1/copilot/respond` request is retired with `410 Gone`; it cannot be used to inject browser-provided facts or principal data. A missing Foundry configuration returns a controlled `503` without revealing source content. Local UAT therefore proves session scope, source assembly and safe failure; it does not claim a successful Foundry-model response until the UAT deployment is configured.

## Release 7 — Local hardening completed, production infrastructure pending

All API responses now receive a request correlation ID (`X-Request-ID`) and basic browser hardening headers. `CFO_RATE_LIMIT_REQUESTS_PER_MINUTE` enables a process-local limiter for `/api` traffic and returns a controlled `429` with `Retry-After`; the frontend maps that status to a retryable busy state. This is deliberately a local/UAT guardrail, not a substitute for a distributed gateway limiter.

Production completion still requires Entra JWT validation, PostgreSQL and migration execution, Blob artifacts, a distributed queue/rate limiter, Key Vault-managed configuration, Azure Monitor and recovery/load/security evidence.
