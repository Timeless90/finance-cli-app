---
name: api-contract-change
description: Safely update a FastAPI OpenAPI contract and regenerate the versioned Orval TypeScript client.
---


1. Identify changed endpoints/schemas and backward-compatibility consequences. Obtain a decision for breaking changes.
2. Update source schemas/routers and backend tests; never begin by patching generated TypeScript.
3. Use the existing OpenAPI export and make api-generate workflow. If it is missing, propose it rather than inventing an implicit network export.
4. Inspect generated output for intended contract differences only. The generated client is versioned in Git.
5. Update consumers using the generated fetch/query functions; run type checks, affected frontend/backend tests and relevant Playwright flows.
6. Run make api-check and the configured final gate. An unchanged generator output is not sufficient proof of runtime correctness.
7. Document compatibility and test evidence. Preserve generated-code notices and avoid manual changes to generated files.
