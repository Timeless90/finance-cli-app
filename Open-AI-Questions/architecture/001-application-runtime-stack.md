# OAQ-001 — Application runtime and deployment architecture

## Status

Resolved — accepted on 2026-08-06.

## Binding target architecture

- **Cloud platform:** Microsoft Azure
- **Backend:** Python with FastAPI
- **Containerization:** Docker
- **Web frontend:** JavaScript

## Architectural consequences

### Backend

FastAPI is the primary product API and application backend. The existing quantitative Python code remains in the same technology ecosystem and is integrated through explicit application ports and service boundaries.

The initial deployment may run the API and quantitative execution in one deployable unit where this reduces complexity. Long-running simulations must still be isolated behind job interfaces so they can later move to dedicated workers without changing domain contracts.

### Web frontend

The web application uses JavaScript. Framework and build-tool selection remain implementation details unless a later product requirement makes them material.

The frontend consumes versioned REST endpoints and must not contain finance calculation logic. Statistical calculations, validations, permissions and reporting rules remain authoritative in the Python backend.

### Azure deployment direction

The target deployment uses Azure-native services where they provide clear operational value. Expected building blocks include:

- Azure Container Registry for Docker images
- Azure Container Apps or Azure App Service for initial application hosting
- Azure Database for PostgreSQL for relational persistence
- Azure Blob Storage for uploaded data, report artifacts and immutable snapshots
- Azure Key Vault for secrets and credentials
- Azure Monitor and Application Insights for logs, metrics and tracing
- Microsoft Entra ID for enterprise identity and access management

The exact choice between Azure Container Apps, App Service and AKS will be made based on workload complexity. AKS is not required for the first product release.

### Repository and service boundaries

The repository remains Python-first. The planned top-level boundaries are:

```text
src/
├── cfo_platform/       # enterprise domain and application services
└── finance_cli/        # existing portfolio CLI and quantitative capabilities

web/                    # JavaScript web application
infra/                  # Docker and Azure deployment definitions
```

The `cfo_platform` domain layer must remain independent of FastAPI, Azure SDKs, database libraries and frontend technology.

## Decision impact on Epic 01

The following Epic 01 work is now unblocked:

1. FastAPI application factory and versioned API routes.
2. Dependency-injection composition root.
3. Transport DTOs separated from domain entities.
4. Docker development and production images.
5. Azure-ready health, readiness and observability endpoints.
6. JavaScript web application scaffold after the backend contract is stable.

## Superseded options

The previously considered Node.js product API plus Python quant-service split is no longer the target architecture. Node.js is not required for backend services.
