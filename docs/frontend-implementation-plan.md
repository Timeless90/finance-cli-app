# CFO Frontend Implementation Plan

## Scope

This roadmap covers only the JavaScript/TypeScript web client for `finance-cli-app`. Backend implementation remains outside frontend scope. Frontend delivery is designed to proceed in parallel with backend work through OpenAPI contracts, adapters and mock handlers.

## Product direction

The web client is a **Future 2060 CFO Command Center**: a dark, technical, retro-futuristic finance interface using carbon surfaces, burnt-orange signal colors, selective mint/green analytical states, strong typographic hierarchy, thin tactical frames and dense but controlled data visualization.

## Target stack

- React + TypeScript
- Vite
- React Router
- Tailwind CSS v4
- shadcn/ui + Radix UI
- TanStack Query
- Zustand for limited local UI state
- React Hook Form + Zod
- TanStack Table
- Recharts + Apache ECharts
- Motion
- OpenAPI-generated TypeScript API contracts
- MSW for API mocks
- Vitest + Testing Library
- Playwright
- Storybook

## Delivery principles

1. No authoritative finance calculation is implemented in the browser.
2. Backend contracts are generated from OpenAPI rather than copied manually.
3. Feature code consumes a frontend API adapter, not generated clients directly.
4. Every domain screen can run against realistic mock data before live API integration.
5. The Finance 2060 design language is implemented through tokens and reusable components, not hard-coded page styling.
6. Critical views include loading, empty, error and authorization states.
7. Accessibility, keyboard usage, reduced motion and visual regression are product requirements.

## Epics

| Epic | Name | Primary outcome |
|---|---|---|
| FE-00 | Frontend Foundation | Buildable, testable and independently deployable React application |
| FE-01 | Finance 2060 Design System | Tokens, primitives, finance components and visualization grammar |
| FE-02 | Application Shell & Navigation | CFO workspace frame, routing and global context |
| FE-03 | API Contract & Mock Architecture | OpenAPI client, adapters, TanStack Query and MSW |
| FE-04 | Public Landing Experience | Product landing page based on the approved visual direction |
| FE-05 | CFO Command Center | Executive cross-module cockpit |
| FE-06 | Planning & Performance Workspace | Planning, scenarios, statements, KPI and variance analysis |
| FE-07 | Profitability & Liquidity Workspace | Profitability, cash, working capital, debt and covenants |
| FE-08 | Enterprise & Treasury Risk Command | Enterprise risk, market risk and advanced risk visualizations |
| FE-09 | Actions & Capital Allocation | Action steering, project valuation and capital allocation |
| FE-10 | Reporting & Finance Copilot | Reporting factory and grounded AI interaction surfaces |
| FE-11 | Data & Governance Console | Data quality, snapshots, runs, models, approvals and lineage |
| FE-12 | Enterprise UX Hardening | Auth integration, RBAC UX, accessibility, security and observability |

## Initial execution sequence

1. FE-00 Frontend Foundation
2. FE-01 Finance 2060 Design System core
3. FE-04 Public Landing Experience
4. FE-02 Application Shell & Navigation
5. FE-03 API Contract & Mock Architecture
6. FE-05 CFO Command Center
7. FE-06 through FE-11 domain workspaces
8. FE-12 hardening continuously and as a final release gate

## Feature lifecycle

Each feature moves through three explicit states:

`DESIGN -> MOCK CONNECTED -> LIVE API CONNECTED`

This prevents frontend delivery from blocking on backend timing while preserving API contract discipline.

## Definition of Done

A frontend feature is complete when applicable checks pass:

- TypeScript strict mode
- ESLint with zero warnings
- component/unit tests
- responsive layout
- loading, empty and error states
- accessibility and keyboard behavior
- mock API coverage
- live API adapter when contract exists
- design tokens only for product styling
- no duplicated backend finance logic
- visual regression coverage for critical screens
