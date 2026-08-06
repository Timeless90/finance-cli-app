# Epic 01 — Product Architecture and Domain Foundation

## Objective

Transform the existing quantitative finance CLI into a reusable model-execution component inside a modular CFO platform without breaking existing ETF simulations.

## Delivery slices

### Slice 1 — Domain and application boundaries

- Introduce a new `cfo_platform` package.
- Define enterprise finance value objects and entities without infrastructure dependencies.
- Define application ports for models, run persistence and job execution.
- Keep `finance_cli` operational as the existing quantitative adapter.
- Add architecture tests that prevent the domain layer from importing infrastructure or UI packages.

### Slice 2 — Quant adapter

- Wrap existing simulation and risk functions behind generic model-execution ports.
- Introduce regression fixtures proving unchanged seeded outputs.
- Move orchestration out of CLI command functions.

### Slice 3 — API foundation

- Add a versioned HTTP API after the runtime-stack decision in `Open-AI-Questions` is resolved.
- Define unified validation, error and asynchronous job-status schemas.

### Slice 4 — Background execution

- Introduce durable jobs with cancellation, progress and deterministic replay.
- Keep model execution independent from the selected queue technology.

## Architectural rules

1. `cfo_platform.domain` contains no framework, persistence, API or data-science imports.
2. `cfo_platform.application` may depend on the domain and application ports only.
3. Infrastructure implements ports; it does not define finance semantics.
4. Existing `finance_cli` modules remain backward compatible during migration.
5. Decimal-based monetary values are used in enterprise-domain objects.
6. Every model run must eventually reference model version, input snapshot, configuration and random seed.

## Definition of Done for Slice 1

- Enterprise finance entities can represent a sample company, dimensions, periods, scenarios and metric observations.
- Model execution is expressed through typed protocols rather than CLI-specific functions.
- Unit tests cover validation and serialization-relevant behavior.
- Architecture tests enforce dependency direction.
- Open design decisions are recorded under `Open-AI-Questions/`.
