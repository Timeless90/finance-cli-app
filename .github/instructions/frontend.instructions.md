---
name: "CFO Command Center Frontend"
description: "Use when adding or modifying CFO Command Center React components, pages, features, API clients, mocks, styles, tests, or Storybook stories in frontend/."
applyTo: "frontend/src/**/*.ts, frontend/src/**/*.tsx, frontend/src/**/*.css, frontend/tests/**/*.ts, frontend/tests/**/*.tsx, frontend/.storybook/**/*.ts"
---

# CFO Command Center Frontend

## Structure

- Put domain types, fixtures, and data hooks together in `src/features/<feature>/contracts.ts`, `mock.ts`, and `query.ts`.
- Put reusable primitives in `src/components/ui/`, finance-specific presentation in `src/components/finance/`, and shell/navigation components in `src/components/layout/` or `src/app/`.
- Keep pages focused on route composition. Move reusable presentation or data concerns to the appropriate shared component or feature module.

## Design And Accessibility

- Extend `src/design-system/tokens.css` before introducing a new color, spacing, radius, type, or transition value. Reference the CSS custom property from Tailwind utilities rather than hardcoding visual values.
- Use `cn()` for conditional Tailwind classes. Use `class-variance-authority` and the existing `Button` primitive when a control has shared variants; retain its visible keyboard-focus treatment.
- Prefer semantic HTML. Icon-only controls need an accessible name; meaningful visualizations need an accessible text alternative; decorative visuals must be hidden from assistive technology.
- Design data-driven states deliberately: loading, empty, error, and mock/local-context labels are part of the interface, not optional placeholders.

## Data And Contracts

- The backend remains the source of truth for financial calculations, validation, workflow state, and persisted data. The frontend renders, formats, and orchestrates results; it does not recreate finance, risk, or simulation logic.
- For feature data, expose a typed async getter and a `useQuery` hook. Include every context dimension that changes the result in the query key, such as company, period, and scenario.
- Keep mock fixtures typed and local to the feature. Preserve explicit mock status when no authoritative read endpoint exists; do not fabricate production identities, headers, or read models.
- Treat `src/api/generated/schema.d.ts` as generated output. Never edit it manually; run `npm run api:sync` after changing a consumed FastAPI route or Pydantic request/response model.
- Keep browser MSW handlers aligned with the generated API contract. Unit tests must not make live HTTP requests; the shared setup intentionally fails on unhandled requests.

## Tests And Stories

- Colocate unit tests with the component or page they cover. Use Testing Library queries by role, label, or visible text so assertions reflect accessible user behavior.
- Add or update a Storybook story for a reusable UI or finance component when its variants or visual states change. Keep stories isolated from live API dependencies.

## Validation

- Run the narrow affected Vitest file first, then `npm run lint`, `npm run typecheck`, and `npm run test` from `frontend/`.
- Run `npm run build` for any frontend change. Also run `npm run test:e2e` for changed user flows and `npm run build:storybook` when Storybook configuration or stories change.
- Follow [frontend/README.md](../../frontend/README.md) for setup and full quality gates. Consult [docs/frontend-backend-contracts.md](../../docs/frontend-backend-contracts.md) before changing an integration boundary.
