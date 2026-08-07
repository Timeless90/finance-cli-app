# Epic 11 — LLM Finance Copilot / Microsoft Foundry Readiness

## Scope delivered

This implementation establishes the production-facing AI platform boundary for the LLM Finance Copilot with Microsoft Foundry as the model control plane.

Delivered capabilities:

- stable OpenAI/v1 Responses API adapter for Microsoft Foundry;
- Microsoft Entra ID authentication with `DefaultAzureCredential`;
- optional API-key authentication for non-production use;
- model routing by Finance module and AI workload;
- direct deployment routing and Foundry Model Router support;
- per-route fallback deployment chains;
- configurable output-token budgets;
- environment-driven routing table (`CFO_FOUNDRY_ROUTES_JSON`);
- approved-fact-only grounding;
- RBAC/company-scope filtering before prompt construction;
- prompt-injection pre-checks;
- numeric grounding validation to prevent invented finance values;
- AI interaction audit records with user, route, deployment and sources;
- Copilot API route catalog and response endpoint;
- operating documentation for multi-model Foundry deployments.

## Architecture decision

The application never routes by raw provider model ID in finance-domain code. It routes to stable **deployment aliases** such as `finance-fast`, `finance-reasoning`, `finance-drafting`, and `model-router`.

This lets infrastructure teams change the concrete model, model version, capacity type, region, or Foundry Model Router subset without changing the Finance domain or API contract.

Routing resolution order:

1. exact module + workload route;
2. generic workload route;
3. fail closed when no route exists.

## Workload examples

- Performance / Explain Variance → fast deployment;
- Risk / Explain Risk → reasoning deployment;
- Treasury / Explain Risk → reasoning deployment;
- Reporting / Report Drafting → drafting deployment;
- Management Summary and general workloads → Foundry Model Router.

These are configuration defaults, not hard provider dependencies.

## Governance evidence

The Copilot service enforces these invariants before accepting an answer:

1. only approved facts are included;
2. facts outside the principal's company scope are removed;
3. prompts matching known injection patterns are rejected before provider invocation;
4. every financial number in the LLM answer must already be present in approved facts/source references;
5. ungrounded numbers cause the answer to be rejected;
6. source references and selected model deployment are retained in the audit record;
7. the LLM has no capability to approve runs, post accounting entries, or release external reports.

External report approval remains owned by the Reporting Factory from Epic 10.

## Microsoft Foundry compatibility

The implementation intentionally uses Microsoft Foundry's stable `/openai/v1/responses` surface and does not depend on the deprecated Azure AI Inference beta SDK.

Supported endpoint patterns:

- Foundry/Azure OpenAI resource endpoint, normalized to `/openai/v1/`;
- Foundry project endpoint, normalized to `/openai/v1/`.

## Configuration

Required production variables:

```text
CFO_FOUNDRY_ENDPOINT=<Foundry resource or project endpoint>
CFO_FOUNDRY_AUTH_MODE=entra_id
CFO_FOUNDRY_ROUTES_JSON=<JSON routing policy>
```

Optional non-production key authentication:

```text
CFO_FOUNDRY_AUTH_MODE=api_key
CFO_FOUNDRY_API_KEY=<secret>
```

See `docs/architecture/microsoft-foundry-multi-model.md` for the deployment and routing operating model.

## Acceptance tests

`tests/test_epic11_foundry_copilot.py` verifies:

- module-specific model routes override generic workload routes;
- fallback deployments are used when the primary deployment fails;
- unapproved/out-of-scope data is not sent to the model;
- ungrounded model-generated numbers are rejected;
- prompt-injection attempts are stopped before a model call;
- routing can be replaced entirely through environment configuration;
- route metadata can be inspected through the API without Foundry credentials.

## Remaining production provisioning

Application code is Foundry-ready. Azure-side provisioning remains environment-specific and should be performed outside the repository:

- create the Foundry resource/project;
- deploy the selected concrete models and/or Model Router deployments;
- grant the workload identity the required Foundry/Azure AI roles;
- configure model subsets, routing mode, quotas and Azure Policy;
- inject `CFO_FOUNDRY_ENDPOINT` and routing configuration through the deployment platform;
- run workload-specific evaluation before promoting model changes.
