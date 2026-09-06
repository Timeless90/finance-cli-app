# CFO Command Center frontend

Node 24 and pnpm 10, React/Vite/TypeScript, TanStack Router/Query and Orval.
Use `mise exec -- make install` and `mise exec -- make dev` at the repository root.
The frontend runs on port 5173; the local gateway forwards `/api` and `/health`.

From this directory: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`,
`pnpm build:storybook`, `pnpm api:sync`. Use root `make e2e` / `make e2e-live`
for browser tests with the correct mock/live environment.

API source: `../backend/openapi.json`. Generated Orval output: `src/generated/`.
The shared API adapter preserves scoped feature query keys, errors, abort signals
and idempotency headers while dispatching through generated operations.
The browser never supplies trusted identity claims: the explicitly enabled local
gateway attaches development identities. MSW mock mode remains clearly labelled.

Unit tests live with features and shared code; browser tests live in `e2e/`.
Global coverage requires 80% statements, branches, functions and lines.
