# FE-11 — Reporting Studio & Financial Copilot Backend Contracts

## Lifecycle

Frontend lifecycle: **MOCK CONNECTED / COPILOT CONTRACT PENDING**.

Reporting, narrative generation, grounding, citations, model routing, exports and business writes remain backend-owned. The browser must never generate authoritative finance narratives, call Foundry deployments directly, manufacture citations or execute autonomous approvals/actions.

## Existing reusable backend capabilities

The platform already contains domain reporting capabilities, including risk reporting operations for risk maps, scenarios, board summaries, Lagebericht-oriented output and risk narratives. FE-11 should compose validated domain outputs through a governed reporting service rather than rebuilding reporting logic in React.

## Reporting Studio read model

Recommended endpoint:

`GET /api/v1/reporting/workspace?company_id=...&period_id=...&scenario_id=...&report_id=...`

Recommended response:

```text
ReportingWorkspaceSnapshot
  context
  active_report
    report_id
    template_id
    reporting_date
    status
    current_version_id
    reviewer
    approver
    completeness
    source_coverage
  sections[]
  versions[]
  source_pack[]
  findings[]
  export_targets[]
  lineage
```

## Report generation and versioning

Recommended endpoints:

- `POST /api/v1/reporting/reports`
- `GET /api/v1/reporting/reports/{report_id}`
- `POST /api/v1/reporting/reports/{report_id}/versions`
- `GET /api/v1/reporting/reports/{report_id}/versions/{version_id}`
- `POST /api/v1/reporting/reports/{report_id}/submit-review`
- `POST /api/v1/reporting/reports/{report_id}/approve`
- `POST /api/v1/reporting/reports/{report_id}/publish`

Every immutable report version should retain:

```text
ReportVersion
  version_id
  report_id
  template_version
  section_payloads[]
  source_snapshot_ids[]
  source_model_run_ids[]
  narrative_run_ids[]
  generated_at
  generated_by
  review_state
  approval_state
  checksum
```

Published reports should never mutate in place.

## Narrative generation

Recommended run contract:

- `POST /api/v1/reporting/narrative-runs`
- `GET /api/v1/reporting/narrative-runs/{run_id}`

A narrative run must receive validated source IDs rather than free-form client-supplied finance facts. Recommended response:

```text
NarrativeRun
  run_id
  workload
  route_id
  deployment_id
  model_version
  prompt_template_version
  source_ids[]
  generated_sections[]
    section_id
    text
    citations[]
  confidence
  validation_findings[]
  status
  created_at
```

Numeric/material claims should be source-addressable and verifiable.

## Export service

Recommended endpoint:

`POST /api/v1/reporting/exports`

Input should reference an approved/versioned report, not raw browser HTML. Export targets may include PDF, PPTX, DOCX and XLSX/evidence appendices. The service should persist artifact ID, report version, format, template version, checksum, generated timestamp and download authorization metadata.

## Financial Copilot orchestration

Recommended API:

- `POST /api/v1/copilot/sessions`
- `GET /api/v1/copilot/sessions/{session_id}`
- `POST /api/v1/copilot/sessions/{session_id}/messages`

Message request:

```text
CopilotMessageRequest
  text
  company_id
  period_id
  scenario_id
  enabled_source_ids[]
  conversation_version
```

Response:

```text
CopilotMessageResponse
  message_id
  text
  route
    route_id
    workload
    deployment_id
    model_version
    reasoning_profile
    fallback_used
  citations[]
    citation_id
    source_type
    source_id
    excerpt_reference
    verified
  confidence
  proposed_tools[]
  proposed_actions[]
  requires_approval
  audit_id
```

## Microsoft Foundry model routing

The frontend should not select a raw model/deployment for production calls. A backend model router should select deployments per workload and policy, supporting different models for finance explanation, report narrative, risk synthesis, classification/extraction and future workloads.

Recommended routing metadata to persist per response:

- `route_id`;
- workload classification;
- deployment/model version;
- reasoning profile;
- grounding policy;
- fallback chain and whether fallback was used;
- token/cost telemetry where permitted;
- latency;
- policy/guardrail result.

This preserves multi-model flexibility without coupling UI code to one Foundry deployment.

## Grounding and citation rules

Copilot must enforce:

1. validated sources only for material numeric claims;
2. source ID/citation on every material finance or decision claim;
3. stale-source rejection or explicit warning;
4. no model-generated numbers where an authoritative backend value exists;
5. deterministic source pack attached to the response audit record;
6. no hidden source substitution during retries/fallbacks.

## Tool/write governance

Copilot may propose actions, report updates or approvals, but writes must use explicit governed tools and require user confirmation plus backend authorization. Recommended pattern:

```text
CopilotToolProposal
  proposal_id
  tool_name
  arguments_preview
  source_message_id
  expected_effect
  authorization_requirement
  approval_status
```

Only a subsequent confirmed mutation may execute the write. This applies to management actions, report publication, capital approvals and similar business-state changes.

## Frontend replacement rule

`frontend/src/features/reporting-copilot/contracts.ts` is a temporary view-model contract. When backend contracts are implemented, OpenAPI-generated response types become authoritative and the frontend retains only presentation-specific adapters/types. `MOCK CONNECTED` and `COPILOT CONTRACT PENDING` are removed only after real reporting and orchestration services are bound.
