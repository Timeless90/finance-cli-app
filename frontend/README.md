# CFO Command Center Frontend

Dedicated web client for the CFO Platform. The frontend is intentionally isolated from the Python backend and consumes the versioned FastAPI contracts under `/api/v1`.

## Requirements

- Node.js 22+
- npm 10+

## Local development

```bash
cd frontend
npm install
npm run dev
```

The Vite development server runs on `http://localhost:3000` and proxies `/api` and `/health` to the local FastAPI service on `http://127.0.0.1:8000`.

## Quality gates

```bash
npm run lint
npm run typecheck
npm run test
npm run build
npm run build:storybook
npm run test:e2e
```

## Architecture rule

Finance calculations remain server-side. The web client renders and orchestrates backend results; it must not duplicate authoritative finance, risk or simulation logic in the browser.
