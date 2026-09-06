# CFO Command Center

Finance planning, forecasting, reporting and quantitative risk platform: FastAPI,
React and the `finance-cli` quantitative CLI. The development structure follows
VSCodeProfileRepo template 1.0.0; existing financial behavior and persistence
adapters are retained.

## Work planning

[Finance CLI App Project](https://github.com/users/Timeless90/projects/2) owns the
backlog, priorities and delivery status. Tim prioritizes and authorizes work;
[the project workflow](docs/development/github-project-workflow.md) defines issue
intake, status transitions and completion evidence.

## Start development

```sh
mise trust
mise install
mise exec -- make install
mise exec -- make dev
```

Docker Desktop must be running. Open http://127.0.0.1:5173; API documentation is
at http://127.0.0.1:8000/docs. PostgreSQL listens on 127.0.0.1:15432. The new
`finance-cli-app` Compose project owns its own persistent database volume.
The database starts empty; local users and mock/UAT contexts are explicitly
labelled development fixtures. Use `make dev-mock` for frontend-only previews
or `make e2e-live` for isolated UAT browser tests. UAT does not seed the normal
development database.

`make dev` supplies the local PostgreSQL URL, import directory and local identity
gateway explicitly. Existing root `.env.local` files and old databases are not
loaded or changed. Export `CFO_*` variables to customize runtime configuration;
Python callers may explicitly pass `_env_file=...` to `ApiSettings`. No real
credentials are required for local development. Cloud-model settings remain
optional and use the existing CFO environment variables.

## Daily commands

| Command | Purpose |
|---|---|
| `make install` | Install locked Python/pnpm dependencies, generate API client and install Chromium |
| `make dev` | Start PostgreSQL, API and frontend with the local role gateway |
| `make check` | Formatting, lint, Pyright/TypeScript, tests, 80% coverage, API drift and config checks |
| `make format` | Format Python and frontend code |
| `make frontend-build` | Build the frontend |
| `make e2e` | Mock browser navigation and accessibility checks |
| `make e2e-live` | Browser tests against an isolated seeded API |
| `make api-generate` | Export OpenAPI and generate Orval models/operations |
| `make cli ARGS="--help"` | Run the retained quantitative CLI |
| `make dev-full` | Development with optional telemetry services |
| `make containers-up` | Build/run the local API and frontend containers |
| `make backend-migrate` | Initialize existing adapter schemas in the new local PostgreSQL database |
| `make backend-migration-check` | Check the existing persistence schema |
| `make acceptance` | Full local quality, browser, container and telemetry verification |

Prefix commands with `mise exec --` unless mise is activated in your shell. Stop
native servers before browser acceptance or container startup: they share ports.
`make infra-down`, `make containers-down` and `make observability-down` stop
services while keeping data volumes. Grafana uses port 3000 when enabled.

## Structure and contracts

- `backend/app/`: feature routers and schemas, financial services, existing
  PostgreSQL/SQLite/in-memory repositories; shared configuration, domain ports,
  composition and telemetry under `app/shared/`.
- `backend/finance_cli/`: installed quantitative CLI; package entrypoints remain
  `finance-cli` and `cfo-api`.
- `backend/tests/`: backend and CLI regression tests.
- `frontend/src/app/`, `features/`, `shared/`: TanStack Router shell, financial
  workspaces and common UI/API code. Storybook remains available with
  `pnpm --dir frontend storybook`.
- `backend/openapi.json` → Orval → `frontend/src/generated/`: versioned contract,
  model types, fetch/query operations and generated path dispatch. Never edit
  generated files manually. Feature adapters retain their scoped query keys.
- `.vscode/`, `.codex/`, `.devcontainer/`, `.github/`: editor, agent, container and
  CI configuration. No profile installation, authentication or cloud deployment
  happens automatically.

The existing `/api/v1` routes and health endpoints remain available. New internal
Python imports use `app`; the relocation map is in `docs/migration-module-map.json`.
Existing persistence formats remain compatible. There is deliberately no
SQLAlchemy/Alembic rewrite or old-data import in this migration.

See [migration and validation](docs/template-migration.md),
[frontend/backend contracts](docs/frontend-backend-contracts.md),
[MCP setup](docs/mcp-setup.md), and the
[historical application guide](docs/pre-migration-README.md) for domain background.
