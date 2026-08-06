# OAQ-001 — Application runtime and monorepo boundary

## Status

Open

## Context

The accepted product roadmap names FastAPI as the API foundation and the existing quantitative engine is implemented in Python. Earlier stack preferences also point to a TypeScript/JavaScript monorepo with Next.js, Node.js, PostgreSQL, Python for quantitative and AI workloads, Docker and AWS.

Before implementing E0-F3, we need a deliberate boundary between the product API and the Python model-execution service.

## Options

### Option A — Python API first

- FastAPI hosts the application API and invokes the Python quant layer in-process initially.
- Next.js is added as the web client.
- Background execution is split out later.

**Advantages**

- Lowest migration risk.
- Direct reuse of the current typed Python code.
- Fastest path to the first CFO-domain endpoints.

**Disadvantages**

- Does not use Node.js as the primary product backend.
- A later service split may require API orchestration changes.

### Option B — Node.js product API plus Python quant service

- A TypeScript API owns product workflows, identity and persistence.
- A Python service owns simulation, statistics and AI/data workloads.
- Services communicate through versioned contracts and asynchronous jobs.

**Advantages**

- Aligns with the previously preferred TypeScript product stack.
- Strong separation between product workflows and numerical execution.
- Natural long-term service boundary.

**Disadvantages**

- Higher initial complexity.
- Requires distributed tracing, contract testing and local orchestration earlier.

### Option C — Python platform backend only

- FastAPI remains the sole backend technology.
- TypeScript is used only for the Next.js frontend.

**Advantages**

- Simplest operational model.
- Strongest continuity with the existing repository.

**Disadvantages**

- Deviates most from the prior Node.js backend preference.

## Recommendation

Adopt **Option B** for the target architecture, but deliver it incrementally:

1. Complete domain separation and generic Python model ports first.
2. Define transport-neutral contracts.
3. Add the TypeScript product API and PostgreSQL persistence.
4. Expose the Python engine as an internal model-execution service.

This preserves delivery speed while avoiding a long-term in-process coupling between enterprise workflows and computational models.

## Decision requested

Confirm whether Option B is the binding target architecture before E0-F3 begins.
