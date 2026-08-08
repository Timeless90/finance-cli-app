# Frontend ↔ Backend Contracts

This document is the living integration boundary between the CFO web client and the FastAPI platform.

## Contract rule

The backend OpenAPI document at `/openapi.json` is the authoritative machine-readable API contract. The frontend must not manually duplicate backend request/response models. Generated TypeScript contracts are wrapped by frontend adapters before feature code consumes them.

```text
FastAPI / Pydantic
      |
      v
/openapi.json
      |
      v
generated TypeScript client
      |
      v
frontend API adapter
      |
      v
TanStack Query / feature hooks
      |
      v
React UI
```

## Responsibility boundary

**Backend owns**

- finance calculations and business rules
- risk, forecast, valuation and simulation results
- authorization decisions
- workflow state transitions
- persisted run/snapshot/model state
- authoritative validation

**Frontend owns**

- presentation and interaction state
- loading, empty and error UX
- input forms and client-side convenience validation
- formatting and visualization of backend results
- navigation and feature composition
- accessibility and responsive behavior

Client-side validation never replaces backend validation.

## Per-epic contract format

Every frontend epic documents endpoint/method, request, response, errors, frontend consumption and any backend prerequisite or gap.

## FE-01 — Finance 2060 Design System

**Backend contract:** none.

The design system contains tokens, primitives and finance presentation components only. It renders and tests without FastAPI.

## FE-02 — Application Shell & Navigation

**Live backend contract:** none yet.

FE-02 owns route composition and a global UI context for company, fiscal period and scenario. Until FE-03 binds these selectors to authoritative APIs, all selector values use `local-*` identifiers and the UI explicitly marks them as `LOCAL CONTEXT`.

### Current local presentation contract

```text
companyId  : string   // local-* only in FE-02
periodId   : string   // local-* only in FE-02
scenarioId : string   // local-* only in FE-02
```

These are presentation values only. They must not be submitted to authoritative finance endpoints.

### Existing backend facts relevant to FE-02

The current governance API accepts identity/scope through request headers on protected governance operations:

```text
X-User
X-Roles
X-Companies
X-Correlation-Id   // where applicable
```

The current governance router exposes `POST /api/v1/governance/scenarios` to create a scenario, but no GET/list scenario endpoint is currently available for populating a global scenario selector.

### Backend read contracts required before live global context

FE-03 must inspect the authoritative OpenAPI document before naming or requesting new endpoints. Functionally the frontend will need read contracts that provide:

- companies the signed-in principal may access,
- selectable fiscal/reporting periods,
- existing scenarios with stable scenario IDs and display names,
- eventually authenticated principal/role/scope information.

If equivalent endpoints already exist when FE-03 runs, they will be consumed. If not, they will be documented as backend gaps rather than implemented by the frontend.

## FE-03 — API Contract & Mock Architecture

This epic introduces the first technical integration contract:

- source: `GET /openapi.json`
- generated TypeScript contracts are treated as build artifacts
- generated code is never edited manually
- feature code accesses APIs through frontend adapters
- MSW fixtures reproduce the same request/response shapes for parallel development

Concrete endpoint matrices are added as each product workspace is connected.
