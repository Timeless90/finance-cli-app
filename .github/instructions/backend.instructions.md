---
description: Backend conventions for this repository.
applyTo: "backend/**/*.py,backend/pyproject.toml"
---


# Backend
Use Python 3.13, uv, FastAPI, Pydantic Settings, Ruff and Pyright with the existing project configuration.
Keep vertical slices: feature/router -> service -> repository -> database. Shared infrastructure belongs in app/shared.
Keep existing Psycopg/SQLite/in-memory adapters. Shared application ports and composition remain under app/shared.
Type public functions and important business logic. Keep authorization and authoritative validation on the backend.
Use structured, redacted logs and existing OpenTelemetry instrumentation; never print secrets.
Use local backend/.venv via normal discovery, not hard-coded personal interpreter paths.
Run the backend Make targets; do not replace the project toolchain with a new formatter/type checker.
