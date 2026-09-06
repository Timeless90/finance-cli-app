---
description: Documentation conventions for this repository.
applyTo: "README.md,docs/**/*.md"
---


# Documentation
Keep README as entry point, and details in docs/architecture, docs/adr, docs/development, docs/testing, docs/deployment and docs/security.
For each meaningful feature, update affected documentation or explain why no documentation content changes.
Document important architecture decisions as ADRs with context, decision, alternatives, consequences and status. Supersede rather than rewrite history.
Use Mermaid for small flows and sequences; Draw.io sources for larger architectures with optional exported SVG.
Do not create meaningless documentation churn. Do not include secrets, raw sensitive trace data or unsupported claims of test success.
