# Epic 01 Completion — Product Architecture & Domain Separation

## Status

Implementation complete pending successful CI validation.

## Delivered capabilities

### E0-F1 — Modularized quantitative core

- Framework-independent `QuantModel` contract with explicit input and output objects.
- Versioned `QuantModelRegistry` for model discovery and execution.
- Adapter exposing the existing ETF portfolio simulation through the generic contract.
- Regression test comparing adapter results with the existing simulation functions for identical seed and parameters.
- CLI, enterprise domain, API, orchestration, infrastructure and quantitative code remain separate packages.

### E0-F2 — Enterprise domain model

- Companies, accounts, organizational dimensions, scenarios, versions and fiscal periods.
- Monetary and metric value objects with validation.
- Metric observations carry company, account, scenario, period, currency, unit, source and dimensions.

### E0-F3 — API foundation

- FastAPI application factory and composition root.
- OpenAPI schema and environment-based settings.
- Versioned `/api/v1/forecast`, `/api/v1/risk` and `/api/v1/data` foundations.
- Azure-compatible liveness and readiness endpoints.
- CORS preparation for the JavaScript web client.
- HTTP validation models and job resource contracts.

### E0-F4 — Background job execution

- Non-blocking thread-backed local job execution.
- Unique job and run identifiers.
- Status, progress, attempt, error and run references.
- Cancellation and resume/retry contracts.
- Reproducible requests with snapshot ID, model version, parameters and random seed.
- API endpoints for submission, retrieval, cancellation and resume.

## Acceptance-criteria matrix

| Criterion | Evidence |
|---|---|
| Existing simulations execute through new interfaces | `LegacyPortfolioSimulationModel` |
| Identical results are protected by regression tests | `test_legacy_adapter_matches_existing_simulation` |
| Generic models require no portfolio domain object | `QuantModelInput`, `EchoForecastModel` |
| Example enterprise can be represented | `cfo_platform.domain` tests and entities |
| Every metric carries dimensional context | `MetricObservation` domain model |
| Forecast, risk and data APIs are versioned | `/api/v1/forecast`, `/api/v1/risk`, `/api/v1/data` |
| API schema is automatically tested | `tests/test_api.py`, `tests/test_epic01_foundation.py` |
| Long-running work does not execute on request workers | `InMemoryJobManager` executor boundary |
| Jobs have status, progress, cancel and resume | Job API and `JobRecord` |
| Runs are reproducibly identified | snapshot, model version, parameters, seed, UUID |

## Architectural boundaries

```text
JavaScript Web Client
        |
FastAPI HTTP Adapters
        |
Application Services and Ports
        |
Quant Model Registry / Enterprise Domain
        |
Infrastructure Adapters
```

The local in-memory repository and thread executor are development adapters. Later epics may replace them with Azure PostgreSQL, Blob Storage and a durable Azure job service without changing the domain or application contracts.

## Deferred by design

The following items belong to subsequent roadmap epics and are not gaps in Epic 01:

- persistent PostgreSQL run storage and immutable audit trail — Epic 03
- production Azure queue and worker deployment — infrastructure evolution with Epic 03
- authentication and role-based access control — Epic 03
- finance data ingestion and reconciliation — Epic 02
- business planning calculations — Epic 04
