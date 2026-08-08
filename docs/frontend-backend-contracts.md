# Frontend ↔ Backend Contracts

This document is the living integration boundary between the CFO web client and the FastAPI platform.

## Contract rule

The FastAPI OpenAPI document at `/openapi.json` is the authoritative machine-readable contract. Frontend request/response models are generated from it and are never manually duplicated.

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
