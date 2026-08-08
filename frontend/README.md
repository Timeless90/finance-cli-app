# CFO Command Center Frontend

Dedicated web client for the CFO Platform. The frontend is intentionally isolated from backend implementation code and consumes the FastAPI OpenAPI contract.

## Requirements

- Node.js 22+
- npm 10+
- Python 3.11+ with the repository installed (`pip install -e .`) when synchronizing API contracts

## Local development

```bash
pip install -e .
cd frontend
npm install
npm run api:sync
npm run dev
```

The Vite development server runs on `http://localhost:3000` and proxies `/api` and `/health` to the local FastAPI service on `http://127.0.0.1:8000`.

## API contract workflow

`npm run api:sync` exports the authoritative schema from `cfo_platform.api.main:app` and generates TypeScript types from it. Generated files are build artifacts and must never be edited by hand.

```text
FastAPI / Pydantic
      -> /openapi.json
      -> exported OpenAPI schema
      -> generated TypeScript paths/components
      -> openapi-fetch adapter
      -> TanStack Query
      -> React UI
```

Run `npm run api:sync` whenever backend routes or Pydantic request/response models change.

## Mock mode

For frontend-only work, initialize the MSW browser worker once and opt into mock mode:

```bash
npm run mock:init
VITE_API_MODE=mock npm run dev
```

MSW fixtures must conform to the generated backend contract. Unhandled requests bypass the browser worker so missing fixtures remain visible during integration.

## Quality gates

```bash
npm run api:sync
npm run lint
npm run typecheck
npm run test
npm run build
npm run build:storybook
npm run test:e2e
```

## Architecture rule

Finance calculations remain server-side. The web client renders and orchestrates backend results; it must not duplicate authoritative finance, risk or simulation logic in the browser.
