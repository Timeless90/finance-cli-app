---
description: Infrastructure conventions for this repository.
applyTo: "infrastructure/**,compose*.yml,**/Dockerfile"
---


# Infrastructure
Terraform is the chosen IaC tool, but remote-state standardization is deferred. Do not introduce a state backend as a side effect of development work.
Azure operations remain CLI/IaC/pipeline-first; no mandatory Azure UI extensions.
The base Compose stack is small; optional observability uses separate files/profiles and explicit Make targets.
Infrastructure/cloud writes, deployments and data-changing migrations require approval. Never run terraform destroy autonomously.
Even terraform plan can access credentials, state and providers; treat it as potentially sensitive, not a guaranteed read-only local operation.
Do not print state, plans or outputs that could contain secrets into model context.
