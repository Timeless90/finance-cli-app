---
name: database-migration
description: Review and verify an existing PostgreSQL/SQLite schema change with explicit protection of data and environments.
---


1. Identify schema intent, affected queries/contracts, migration dependencies and data risk.
2. Ask about ambiguous data transformation or destructive operations before generating the affected migration.
3. Generate with the existing approved workflow and inspect every operation; autogeneration is a draft, not proof of safety.
4. Evaluate locking, nullability, index creation, backfill, transaction boundaries and compatibility with the current application version.
5. Test against an explicitly disposable test database after approval. Never infer that a connection string points to a safe environment.
6. Verify upgrade and rollback strategy; a downgrade that destroys data is not a safe rollback plan.
7. Add tests/docs and report exactly which environment and migration revisions were verified, without exposing connection secrets.

This project retains its existing persistence adapters and has no Alembic chain. Use their schema definitions and explicit SQL changes; do not introduce SQLAlchemy/Alembic as an incidental step. `make backend-migration-check` checks table presence, not full schema drift.
