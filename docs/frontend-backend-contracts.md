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

Every frontend epic will document:

1. endpoint and HTTP method,
2. request contract,
3. response contract,
4. relevant HTTP/business errors,
5. how the frontend consumes the response,
6. backend prerequisite or open dependency.

## FE-01 — Finance 2060 Design System

**Backend contract:** none.

The design system contains tokens, primitives and finance presentation components only. It must render and be testable without the FastAPI service.

## FE-03 — API Contract & Mock Architecture

This epic introduces the first technical integration contract:

- source: `GET /openapi.json`
- generated TypeScript contracts are treated as build artifacts
- generated code is never edited manually
- feature code accesses APIs through frontend adapters
- MSW fixtures reproduce the same request/response shapes for parallel development

Concrete endpoint matrices are added as each product workspace is connected.
