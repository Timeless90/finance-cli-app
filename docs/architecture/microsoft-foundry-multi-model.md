# Microsoft Foundry Multi-Model Operating Model

## Objective

The CFO platform uses Microsoft Foundry as the AI control plane while keeping finance-domain code independent of any concrete model. Model selection is resolved by **Finance module × AI workload**, so different modules can use different deployments, routing strategies, latency/cost classes, and fallback chains.

The runtime integration targets the stable **OpenAI/v1 Responses API** exposed by Microsoft Foundry. It does not depend on the retiring Azure AI Inference beta SDK.

## Runtime endpoint

Set the Foundry resource or project endpoint. The adapter normalizes it to `/openai/v1/`.

```bash
CFO_FOUNDRY_ENDPOINT=https://<resource-name>.openai.azure.com
CFO_FOUNDRY_AUTH_MODE=entra_id
```

Microsoft Entra ID is the preferred production mode. The runtime uses `DefaultAzureCredential` and obtains a token for `https://ai.azure.com/.default` on every model invocation.

API-key authentication is supported for local or transitional environments:

```bash
CFO_FOUNDRY_AUTH_MODE=api_key
CFO_FOUNDRY_API_KEY=<secret>
```

Never commit the API key. Production deployments should use managed identity / workload identity and Azure RBAC.

## Deployment aliases

Application configuration references **deployment names**, not catalog model IDs. This allows a deployment to be replaced or upgraded without changing finance-domain code.

Recommended deployment aliases:

| Deployment alias | Purpose | Typical characteristics |
| --- | --- | --- |
| `model-router` | General/default routing | Foundry Model Router, balanced profile |
| `finance-fast` | Variance explanations, simple summaries | Low latency / lower cost |
| `finance-reasoning` | Risk, treasury, recommendations | Strong reasoning, higher quality |
| `finance-drafting` | Management/report drafting | Strong long-form language quality |

The concrete model behind each direct deployment is intentionally an infrastructure decision. Foundry's Model Router can also be used as a deployment and can apply its own Quality, Cost, or Balanced routing profile and model subset.

## Module × workload routing

Routing priority is:

1. exact `(module, workload)` route;
2. generic route for the workload;
3. fail if no approved route exists.

Built-in defaults demonstrate the intended topology:

- `performance + explain_variance` → `finance-fast` → fallback `model-router`
- `risk + explain_risk` → `finance-reasoning` → fallback `model-router`
- `treasury + explain_risk` → `finance-reasoning` → fallback `model-router`
- `reporting + report_drafting` → `finance-drafting` → fallback `model-router`
- generic `management_summary` → Foundry `model-router`
- generic `general_qa` → Foundry `model-router`

Production routing is overridden through `CFO_FOUNDRY_ROUTES_JSON`.

Example:

```json
[
  {
    "route_id": "planning-cheap",
    "module": "planning",
    "workload": "general_qa",
    "deployment": "planning-small",
    "strategy": "direct",
    "fallback_deployments": ["model-router"],
    "max_output_tokens": 800
  },
  {
    "route_id": "risk-quality",
    "module": "risk",
    "workload": "explain_risk",
    "deployment": "risk-reasoning",
    "strategy": "direct",
    "fallback_deployments": ["model-router"],
    "max_output_tokens": 1800
  },
  {
    "route_id": "summary-balanced",
    "workload": "management_summary",
    "deployment": "model-router",
    "strategy": "foundry_model_router",
    "fallback_deployments": [],
    "max_output_tokens": 1200
  }
]
```

## Governance rules

The Finance Copilot applies application-side controls in addition to Foundry controls:

- only facts marked `approved=true` are sent to the model;
- company-scoped facts are filtered through existing RBAC before prompt construction;
- the LLM is instructed that approved facts are immutable data and not instructions;
- known prompt-injection patterns are blocked before provider invocation;
- numeric values in the answer are checked against numeric values present in approved facts/source references;
- if the model introduces an ungrounded number, the response is rejected;
- every interaction records user, module, workload, route, selected deployment, prompt, response, and source references;
- the LLM never approves runs, posts bookings, or autonomously releases external reports.

For external reporting, the existing Reporting Factory remains the approval boundary. The Copilot produces drafts; the reporting workflow owns external release.

## Foundry-side controls

For production, configure these controls in Microsoft Foundry/Azure as platform policy rather than application code:

- Azure Policy allow-list for approved model deployments and Model Router subsets;
- data-zone/global deployment choice according to data residency requirements;
- content filters and abuse monitoring appropriate for finance workloads;
- per-deployment quotas and budgets;
- private networking where required;
- managed identity and least-privilege RBAC;
- model-version lifecycle and deprecation process;
- evaluation gates before changing the model behind a stable deployment alias.

## API

The platform exposes:

```text
GET  /api/v1/copilot/routes
GET  /api/v1/copilot/routes/resolve?module=<module>&workload=<workload>
POST /api/v1/copilot/respond
```

`GET /copilot/routes` exposes only deployment-routing metadata. It never returns Foundry endpoint credentials or API keys.

## Deployment-change process

A model change should normally be made in Foundry and/or `CFO_FOUNDRY_ROUTES_JSON`, not in application code:

1. deploy/evaluate a candidate model in Foundry;
2. run workload-specific regression and grounding tests;
3. update a deployment alias or route configuration;
4. canary by module/workload if required;
5. compare quality, latency, token usage and cost;
6. promote or roll back without changing finance-domain code.

This structure supports different models for planning, performance, risk, treasury and reporting while preserving one governed API surface inside the CFO platform.
