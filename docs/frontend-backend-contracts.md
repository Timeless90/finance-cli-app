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

No live business API calls. Company, fiscal period and scenario selectors remain clearly labelled local context values and must not be submitted to authoritative finance APIs.

Current backend observation:

- `POST /api/v1/governance/scenarios` exists for scenario creation.
- no scenario list/read endpoint currently exists for the global selector.
- governed endpoints currently receive principal context via `X-User`, `X-Roles`, `X-Companies` and optional `X-Correlation-Id` headers.

## FE-03 — API Contract & Mock Architecture

### Machine contract

- source: `GET /openapi.json`
- local export: `npm run api:export`
- TypeScript generation: `npm run api:generate`
- full synchronization: `npm run api:sync`
- runtime transport: `openapi-fetch`
- remote-state orchestration: TanStack Query
- mock transport: MSW

### Bound system contracts

| Purpose | Method | Endpoint | Request | Response | Auth |
| --- | --- | --- | --- | --- | --- |
| API readiness | GET | `/health/ready` | none | `HealthResponse { status, service, environment, version }` | none |
| Platform metadata | GET | `/api/v1/platform` | none | `PlatformResponse { name, api_version, capabilities[] }` | none |

### Context contracts still missing

| Frontend need | Current state | Backend gap |
| --- | --- | --- |
| accessible companies | local-only | read endpoint for user/company scopes |
| fiscal periods | local-only | read endpoint for available reporting periods |
| scenarios | create endpoint only | list/read scenario endpoint |
| principal identity/roles | headers required by governed routes | authoritative identity/RBAC read contract for the web client |

Until these read contracts exist, the UI continues to label global selectors as `LOCAL CONTEXT`.

### Authentication boundary

The frontend will not invent production identities or role headers. The existing `X-User`, `X-Roles` and `X-Companies` mechanism is recorded as the current backend contract, but production identity propagation will be integrated only when the authentication architecture is finalized.

## FE-04 — Public Landing Experience

**Backend contract: none.**

The public landing route `/` is intentionally independent from FastAPI and must render when the platform API is unavailable. Finance values shown in product previews are static simulated presentation data and are labelled as such. The only product boundary is navigation into `/app/command-center`; business API calls remain inside authenticated/product workspaces.

## FE-05 — CFO Command Center

Lifecycle state: **MOCK CONNECTED**.

The executive cockpit requires one authoritative backend read model. It must not reconstruct group-level finance truth in the browser by orchestrating calculation endpoints or combining partially persisted module state.

### Existing backend capabilities relevant to FE-05

- `GET /api/v1/risk/register` can list currently registered enterprise risks.
- `GET /api/v1/actions` can list currently registered management actions.
- `GET /api/v1/planning/forecasts/{version_id}` can read a known forecast version.
- performance and liquidity APIs currently expose calculation-oriented `POST` endpoints rather than persisted executive read models.
- no backend endpoint currently returns a company / period / scenario scoped CFO overview.

These endpoints are useful for their domain workspaces but are insufficient as the authoritative source of an executive cockpit. The frontend therefore uses a typed, explicitly labelled fixture for FE-05 until the aggregate read contract exists.

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

Lifecycle state: **MOCK CONNECTED**.

FE-06 implements the Planning and Performance workspaces while preserving the calculation boundary. The backend already exposes useful calculation services, but the web application is still missing persisted, company/period/scenario-scoped read models for normal workspace loading.

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

These are domain engines, not workspace query APIs. FE-06 therefore uses explicit fixtures for statement values, KPI states, variance explanations, anomaly signals and commentary queues until persisted results can be queried.

### Required Planning read contracts

Recommended minimum API surface:

- `GET /api/v1/planning/scenarios?company_id=...&period_id=...`
- `GET /api/v1/planning/forecasts?company_id=...&period_id=...&scenario_id=...`
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

### Required Performance read contracts

Recommended minimum API surface:

- `GET /api/v1/performance/workspace?company_id=...&period_id=...&scenario_id=...`
- optionally drill-down endpoints such as `GET /api/v1/performance/variance-bridges/{bridge_id}` and `GET /api/v1/performance/anomalies?company_id=...&period_id=...` when persisted identifiers exist.

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

### Current FE-06 temporary contract

`frontend/src/features/planning-performance/contracts.ts` is a provisional mock-only view-model contract. It must be replaced by adapters over OpenAPI-generated response types as the recommended read endpoints become available. The workspaces visibly display `MOCK CONNECTED`, and global Company / Period / Scenario values remain local context until FE-02 context gaps are resolved.
