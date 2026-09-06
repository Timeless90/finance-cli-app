---
description: Testing conventions for this repository.
applyTo: "backend/tests/**/*.py,frontend/**/*.test.{ts,tsx},frontend/e2e/**,frontend/playwright.config.*"
---


# Testing
Use Pytest in backend, Vitest/React Testing Library for frontend units/components and Playwright for E2E.
No automatic continuous test execution on workspace open. Watch/UI modes start explicitly.
Prefer existing Make targets for suite runs; use native Test Explorer for a targeted test/debug session.
Global backend and frontend coverage targets are at least 80 percent. Also use diff coverage in CI; the exact changed-line threshold must be documented separately, not invented here.
Do not enforce global coverage thresholds on a single test. Exclude genuinely generated/build code consistently, not difficult business logic.
Use retain-on-failure traces and only-on-failure screenshots. Traces may contain credentials or personal data; keep them local/access-controlled and never commit them.
Do not auto-update snapshots to silence a failure. Report commands, environment, passed/failed/not-run status and limitations.
