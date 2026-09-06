---
description: Database conventions for this repository.
applyTo: "backend/**/models.py,backend/**/repository.py,backend/**/migrations/**,backend/**/alembic/**"
---


# Database changes
PostgreSQL is the default; other services are opt-in. Retain existing repository contracts and parameterized Psycopg queries.
Use the existing schema initialization in the PostgreSQL adapters; this project deliberately retains SQLite/PostgreSQL adapters and has no Alembic migration chain. Review autogeneration for dropped columns, type changes, constraints, indexes and data backfills.
State explicitly whether a migration is additive, breaking or destructive. Ask before data-affecting migrations and use an isolated disposable test database for verification.
Do not run production/destructive migration commands autonomously. Keep API/Pydantic/OpenAPI compatibility in view.
