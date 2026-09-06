# Migration to the VSCodeProfileRepo structure

The existing finance-cli-app working tree was migrated in place on 2026-09-06.
The source is the local VSCodeProfileRepo template 1.0.0, including its uncommitted
configuration. No branch, commit, push or remote change was performed.

## Preserved working state

The pre-migration working tree (including untracked source/configuration files) and
Git status were archived beside this repository in
`finance-cli-app-migration-backup-20260906-152930/`. Its archive and SHA-256 manifest
are access-restricted. The original Git directory/history remains in place.
Existing local credentials, `.local` data, UAT evidence, mock-data and deployment
material were retained. Build caches and old virtual environments were not moved
into the new runtime.

The original baseline passed 134 backend tests (84% statement coverage) and 21
frontend tests. New checks also enforce branch coverage; percentages therefore
cannot be compared directly to the previous baseline.

## Resulting development model

- Python application and tests are under `backend/`; FastAPI feature routers and
  request/response schemas are separated. Financial services retain their domain
  names, application ports and composition. Existing persistence adapters remain
  the implementation of the repository layer.
- The quantitative CLI remains an installed package with `finance-cli` and
  `cfo-api` entrypoints. Internal CFO imports now use `app`; the module mapping
  is recorded in `migration-module-map.json`.
- Frontend pages and domain components belong to `features/`; shell/routing to
  `app/`; general components, API transport, styles and test support to `shared/`.
  TanStack Router preserves the previous application URLs.
- OpenAPI → Orval owns generated models, fetch/query operations and a generated
  dispatch adapter. Existing scoped feature queries use that adapter, retaining
  errors, abort signals, lineage and idempotency headers. Generated output is
  versioned; the former openapi-fetch/openapi-typescript pipeline was removed.
- mise controls Python 3.13, Node 24, uv and pnpm. Backend uses Ruff and Pyright;
  frontend uses ESLint, Prettier, Vitest and Playwright. Make is the shared command
  interface for local development, VS Code and CI.
- The Dev Container has separate Linux Python/node dependency volumes and the
  required Chromium libraries. It does not replace native macOS dependencies.
- Codex/Copilot MCP definitions reference environment variables and interactive
  inputs. Personal credentials and profile installations were not copied.

## Database and behavior compatibility

The original and migrated contracts were compared after dereferencing schema
references: all 125 API paths retain their request/response contracts and endpoint
metadata. Internal schema component names can change with Python module locations;
consumers receive regenerated types. See `api-migration-validation.json`.

A separate Compose project, `finance-cli-app`, owns the new PostgreSQL and import
volumes. The development database is empty. Native development explicitly chooses
this database and `.local/migrated/imports`. Old database URLs and root `.env.local`
are not automatically loaded. Existing `CFO_*` variables remain supported;
Python callers can opt into an env file through `ApiSettings(_env_file=...)`.

Unit tests force isolated in-memory defaults. `make e2e-live` creates a unique
PostgreSQL test database and removes only that database after testing. UAT uses the
existing explicit Echo gateway, without an external model account. The ordinary
development environment is not seeded. Empty contexts are labelled and empty
selectors are disabled; `make dev-mock` provides the existing simulated UI preview.

There is no SQLAlchemy/Alembic migration. `make backend-migrate` initializes the
existing adapter schemas; `make backend-migration-check` only checks table presence.
It does not claim to detect arbitrary schema drift. A pre-existing PostgreSQL
integer/boolean mismatch in the governed-run immutable flag was corrected without
changing the table format, and is covered by a real PostgreSQL regression test.

## Validation and operation

The machine-readable full acceptance result is `.local/acceptance.json`. The
checked-in `migration-validation.json` records the handover verification summary.
The complete acceptance covers quality and coverage, PostgreSQL, mock browser
navigation, automated accessibility, live financial workflows, Docker builds,
frontend proxy, Grafana, Prometheus, traces and correlated Loki logs.

The Dev Container was separately installed and checked with backend/frontend
lint/type checks, frontend build and Chromium smoke/accessibility tests. Native
`make dev` was also started against the empty database and visually inspected.
Storybook builds successfully.

The pinned template Python release is 3.13.15; the native installed interpreter
reported 3.13.1. The supported major/minor line is 3.13; this is not an assertion
that native and container patch versions are identical. Existing dependency
warnings remain visible. Authenticated external MCP connections, GitHub-hosted
CI, Windows/WSL and cloud deployment were not exercised. Automated accessibility
checks do not replace a manual accessibility audit.

To continue, open the repository root and run `mise exec -- make dev`. Run only
one normal app mode at a time (native or Docker) because ports 5173/8000 are shared.
Browser tests use their own ports. Telemetry remains optional via `make dev-full`.
Stop targets retain data volumes; no prune or old-data reset is performed.
