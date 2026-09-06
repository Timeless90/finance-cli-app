---
description: Frontend conventions for this repository.
applyTo: "frontend/**/*.{ts,tsx,js,jsx,css}"
---


# Frontend
Use React/Vite/TypeScript/pnpm, ESLint and Prettier. Keep code feature-oriented under src/features, app wiring under src/app and domain-independent code under src/shared.
Server state: TanStack Query. Shared client/UI state only where needed: Zustand. Forms: React Hook Form + Zod. Component-local state stays local.
Routing: TanStack Router. Consume the Orval-generated fetch/query client; do not duplicate API entities in client state or hand-edit generated files.
UI: Tailwind, shadcn/ui, semantic tokens, own UI layer. Reuse existing components before consulting 21st. Check external component license, dependencies, compatibility and accessibility before adoption.
Only general-purpose components belong in shared/ui; domain-specific blocks remain within features. Prepare for a future versioned design-system package without building that separate project now.
WCAG 2.2 AA is the target. Automated scans alone do not prove conformance. Test keyboard, focus, contrast and relevant screen-reader semantics.
Verify affected UI flows with Playwright, plus applicable unit/component tests and type/lint checks.
