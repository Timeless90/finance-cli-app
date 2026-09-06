# Backend Implementation Plan

> Aufgaben, Prioritäten und Lieferstatus werden im [GitHub Project](https://github.com/users/Timeless90/projects/2) geführt. Dieses Dokument bleibt fachliche Planungsreferenz; historische Reihenfolgen und Statusangaben können vom lokalen Lieferstand abweichen. Siehe [Arbeitsablauf und Übernahmeabgleich](development/github-project-workflow.md).
## Phase 2 – Production Backend Integration

## 1. Zielbild

Das Backend soll von einer Sammlung funktionaler Finance-Engines zu einer produktionsfähigen, integrierten CFO-Plattform weiterentwickelt werden.

Die bestehenden Finance-Module bleiben die fachliche Berechnungsschicht. Phase 2 ergänzt darüber eine konsistente Integrations- und Orchestrierungsschicht.

Zielzustand:

```text
Frontend / External Clients
            │
            ▼
┌──────────────────────────────┐
│        FastAPI API Layer     │
│                              │
│ Context APIs                 │
│ Workspace Read APIs          │
│ Run APIs                     │
│ Reporting APIs               │
│ Copilot APIs                 │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Application / Orchestration  │
│                              │
│ Context Resolution           │
│ Run Lifecycle                │
│ Workflow Orchestration       │
│ Approval / Governance        │
│ Read Model Projection        │
│ AI Context Assembly          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Finance Domain Engines       │
│                              │
│ Planning                     │
│ Performance                  │
│ Profitability                │
│ Liquidity                    │
│ Enterprise Risk              │
│ Market Risk                  │
│ Actions                      │
│ Capital Allocation           │
│ Reporting                    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Persistence / Infrastructure │
│                              │
│ Run Repository               │
│ Snapshot Repository          │
│ Read Model Repository        │
│ Audit Repository             │
│ Artifact Storage             │
│ Azure / Foundry Integration  │
└──────────────────────────────┘
```

Grundprinzip:

**Der Client orchestriert keine Finance-Logik.**

Das Frontend darf:

- Inputs erfassen
- Backend-Runs starten
- Status pollen bzw. Events empfangen
- Read Models darstellen
- filtern und sortieren
- Drill-downs aufrufen

Das Frontend darf nicht:

- KPIs selbst neu berechnen
- NPV oder IRR berechnen
- Risk-Metriken berechnen
- Portfoliooptimierung durchführen
- Liquidity Forecasts erzeugen
- Report-Inhalte fachlich aggregieren
- AI-Kontext selbst zusammensetzen

---

# 2. Einheitlicher Backend Contract

Jeder relevante Finance-Workflow basiert auf einem gemeinsamen fachlichen Context:

```text
company_id
period_id
scenario_id
```

Optional:

```text
snapshot_id
projection_version
model_version
run_id
currency
```

Jeder persistierte Backend-Run erhält mindestens:

```text
run_id
domain
run_type
status

input_context
input_payload

source_snapshot_ids
model_version
projection_version

result
error

created_by
created_at
started_at
completed_at

validation_status
validated_by
validated_at

approval_status
approved_by
approved_at

lineage
```

Gemeinsamer Lifecycle:

```text
pending
   │
   ▼
running
   │
   ├──────────────► failed
   │
   ▼
succeeded
   │
   ▼
validated
   │
   ├──────────────► rejected
   │
   ▼
approved
```

Nicht jeder technische Run benötigt Approval.

Decision-, Reporting- und publikationsrelevante Runs dagegen schon.

---

# 3. Gemeinsame HTTP-Semantik

## 200

Ressource erfolgreich gelesen oder Workflow synchron abgeschlossen.

## 201

Persistierte Ressource erstellt.

## 202

Asynchroner Run angenommen.

## 400

Ungültiger Request oder fachlich inkonsistente Parameter.

## 403

User besitzt keine Berechtigung oder Company liegt außerhalb des Scopes.

## 404

Context, Run, Snapshot oder Projection existiert nicht.

## 409

Ungültiger Lifecycle-Übergang, Versionskonflikt oder Idempotency-Konflikt.

## 422

Schema-/Validation-Fehler.

## 503

Externer Dienst wie Microsoft Foundry temporär nicht verfügbar.

---

# 4. Roadmap

Phase 2 besteht aus sieben Backend-Epics:

```text
BE-01 Context APIs
        ↓
BE-02 Workspace Read Models
        ↓
BE-03 Risk & Market Risk Runs
        ↓
BE-04 Action & Capital Runs
        ↓
BE-05 Reporting Orchestration
        ↓
BE-06 Microsoft Foundry Copilot Orchestration
        ↓
BE-07 Production Integration Hardening
```

BE-01, BE-02 und BE-03 sind bereits umgesetzt.

Der nächste Entwicklungsschritt ist BE-04.

---

# 5. BE-01 – Company / Period / Scenario Context APIs

## Status

Completed.

## Ziel

Ein einheitlicher fachlicher Kontext für sämtliche Finance-Module.

## Contracts

```text
GET /api/v1/context/principal

GET /api/v1/context/companies

GET /api/v1/context/periods
    ?company_id=

GET /api/v1/context/scenarios
    ?company_id=
    &period_id=

GET /api/v1/context/resolve
    ?company_id=
    &period_id=
    &scenario_id=
```

## Backend Responsibilities

- RBAC prüfen
- Company Scope prüfen
- Period validieren
- Scenario validieren
- Currency bestimmen
- zugrunde liegende Snapshots identifizieren
- stateless Context erzeugen

## Definition of Done

- kein globaler „current company“-State
- jeder Request explizit context-aware
- 403 bei Company Scope violation
- 404 bei ungültigem Period-/Scenario-Context
- Integration Tests vorhanden

---

# 6. BE-02 – Workspace Read Models

## Status

Completed.

## Ziel

Das Frontend soll Finance-Dashboards nicht aus vielen granularen Endpunkten zusammensetzen müssen.

Backend liefert fertige query-orientierte Projections.

## Contracts

```text
GET /api/v1/planning/workspace

GET /api/v1/performance/workspace

GET /api/v1/profitability/workspace

GET /api/v1/liquidity/workspace

GET /api/v1/risk/workspace

GET /api/v1/market-risk/workspace

GET /api/v1/actions/workspace

GET /api/v1/capital/workspace

GET /api/v1/reporting/workspace
```

Immer mit:

```text
company_id
period_id
scenario_id
```

## Response Metadata

```text
context
as_of
projection_version
source_snapshot_ids
lineage
assurance
```

## Prinzip

Read Models berechnen keine neue Fachlogik.

Sie projizieren ausschließlich Ergebnisse bestehender Backend-Services und persistierter Runs.

---

# 7. BE-03 – Risk & Market-Risk Model Runs

## Status

Completed.

## Ziel

Risk-Berechnungen werden persistierte und reproduzierbare Model Runs.

## Enterprise Risk

```text
POST /api/v1/risk/model-runs

GET /api/v1/risk/model-runs/{run_id}
```

Aktuell:

```text
aggregation
```

## Market Risk

```text
POST /api/v1/market-risk/model-runs

GET /api/v1/market-risk/model-runs/{run_id}
```

Model Types:

```text
var_es
garch_t
regime_hmm
evt
copula
var_backtest
```

## Run Metadata

```text
run_id
status
input_context
input_payload
source_snapshot_ids
projection_version
result
error
timestamps
```

## Reproduzierbarkeit

Monte-Carlo-basierte Modelle speichern zusätzlich:

```text
seed
paths
model parameters
model version
```

---

# 8. BE-04 – Action & Capital Runs

## Status

Next / Implementation.

## Ziel

Management Actions und Capital Allocation werden zu versionierten Decision Runs.

Das ist entscheidend, weil ein späteres Management- oder Board-Reporting nachvollziehen können muss:

> Welche Entscheidung wurde auf Grundlage welcher Daten, welcher Annahmen und welcher Finance-Runs getroffen?

---

## 8.1 Action Runs

### Contract

```text
POST /api/v1/actions/runs

GET /api/v1/actions/runs/{run_id}

POST /api/v1/actions/runs/{run_id}/validate

POST /api/v1/actions/runs/{run_id}/approve

POST /api/v1/actions/runs/{run_id}/reject
```

### Run Types

```text
simulation
prioritization
benefit_tracking
```

### Simulation Input

```text
company_id
period_id
scenario_id

action_ids[]
```

Backend liest die Actions aus dem Catalogue.

Keine vollständigen Action-Objekte vom Frontend.

### Output

```text
selected_action_ids

total_cost

expected_ebitda_effect
expected_cash_effect

covenant_effects

period_impacts[]
```

---

## 8.2 Action Prioritization

Input:

```text
action_ids[]
```

Output:

```text
action_id
score
expected_benefit
cost
benefit_cost_ratio
```

Persistiert als Run.

Damit kann später nachvollzogen werden, warum bestimmte Maßnahmen priorisiert wurden.

---

## 8.3 Benefit Tracking Run

Input:

```text
observations[]
```

Backend verknüpft Observations mit bestehenden Actions.

Output:

```text
planned_amount
realized_amount
variance
realization_ratio
```

---

# 9. Capital Decision Runs

## Contracts

```text
POST /api/v1/capital/runs

GET /api/v1/capital/runs/{run_id}

POST /api/v1/capital/runs/{run_id}/validate

POST /api/v1/capital/runs/{run_id}/approve

POST /api/v1/capital/runs/{run_id}/reject
```

## Run Types

```text
project_valuation
project_monte_carlo
portfolio_optimization
funding_scenario
```

---

## 9.1 Project Valuation

Input:

```text
company_id
period_id
scenario_id

project
discount_rate
```

Output:

```text
npv
irr
roic
payback_years
```

---

## 9.2 Monte-Carlo NPV

Input:

```text
project
discount_rate

paths
seed

cash_flow_volatility

risk_event_probability
risk_event_impact

scenario_multiplier
```

Output:

```text
mean_npv

p10
p50
p90

probability_negative_npv

paths
seed
```

---

## 9.3 Portfolio Optimization

Input:

```text
projects[]

risk_adjusted_npvs

budget

opening_cash_headroom
minimum_cash_headroom

base_leverage
maximum_leverage

base_interest_cover
minimum_interest_cover

strategic_weight
```

Output:

```text
selected_project_ids

total_investment
total_risk_adjusted_npv

ending_cash_headroom
ending_leverage
ending_interest_cover

constraints_satisfied
```

---

## 9.4 Funding Scenario

Input:

```text
funding_option

base_debt
base_ebitda
base_interest_expense

maximum_leverage
```

Output:

```text
gross_proceeds
net_proceeds

annual_interest
annual_principal
annual_debt_service

leverage_after
interest_cover_after

covenant_headroom
```

---

# 10. Decision Run Governance

BE-04 erweitert den bisherigen technischen Lifecycle.

Ein Decision Run bekommt zusätzlich:

```text
validation_status
approval_status
```

Beispiel:

```text
calculation succeeded
        │
        ▼
awaiting_validation
        │
        ▼
validated
        │
        ▼
awaiting_approval
        │
        ▼
approved
```

Reject:

```text
validated
   │
   ▼
rejected
```

---

# 11. Berechtigungen

Bereits bestehende Permissions werden verwendet:

```text
CREATE_RUN
VALIDATE_RUN
APPROVE_RUN
```

Beispielsweise:

CFO:

```text
CREATE_RUN
APPROVE_RUN
```

FP&A:

```text
CREATE_RUN
VALIDATE_RUN
```

Risk:

```text
CREATE_RUN
VALIDATE_RUN
```

Controller:

```text
CREATE_RUN
VALIDATE_RUN
```

Reviewer:

```text
APPROVE_RUN
```

Admin:

```text
all
```

---

# 12. Idempotency für Decision Runs

Bereits in BE-04 vorbereiten:

```text
Idempotency-Key
```

Der gleiche Request mit identischem Key erzeugt nicht mehrere Runs.

Persistierter Fingerprint:

```text
user_id
company_id
run_type
request_hash
idempotency_key
```

Vollständige produktive Umsetzung folgt spätestens in BE-07.

---

# 13. BE-05 – Reporting Orchestration

## Ziel

Reporting wird von synchroner Dateierzeugung zu einem governeden Workflow.

## Contract

```text
POST /api/v1/reporting/runs

GET /api/v1/reporting/runs/{run_id}

GET /api/v1/reporting/runs/{run_id}/artifacts

POST /api/v1/reporting/runs/{run_id}/validate

POST /api/v1/reporting/runs/{run_id}/approve

POST /api/v1/reporting/runs/{run_id}/publish
```

---

## Reporting Lifecycle

```text
Report Request
      │
      ▼
Context Resolution
      │
      ▼
Read Model Assembly
      │
      ▼
Report Composition
      │
      ▼
Artifact Generation
      │
      ├── PDF
      ├── PPTX
      └── structured JSON
      │
      ▼
Validation
      │
      ▼
Approval
      │
      ▼
Publication
```

---

# 14. Report Lineage

Jeder Report muss referenzieren:

```text
company_id
period_id
scenario_id

workspace_projection_versions

risk_run_ids
market_risk_run_ids

action_run_ids
capital_run_ids

report_template_version

generated_at
generated_by
```

Damit ist jede Zahl später nachvollziehbar.

---

# 15. Artifact Storage

Für Production:

Azure Blob Storage.

Interface:

```text
ArtifactRepository

save()
get()
list()
delete()
```

Metadata:

```text
artifact_id
report_run_id

content_type
filename

blob_uri

checksum
created_at
```

---

# 16. BE-06 – Microsoft Foundry Copilot Orchestration

## Ziel

Das LLM wird keine direkte Datenbank-Suchmaschine.

Es bekommt kontrollierten Finance-Kontext.

---

# 17. Copilot Request Contract

```text
POST /api/v1/copilot/runs

GET /api/v1/copilot/runs/{run_id}
```

Input:

```text
company_id
period_id
scenario_id

workload
question

optional:
workspace_modules[]
run_ids[]
```

---

# 18. Governed Context Assembly

```text
User Question
      │
      ▼
RBAC
      │
      ▼
Company Context
      │
      ▼
Workspace Read Models
      │
      ▼
Approved Finance Runs
      │
      ▼
Approved Reports
      │
      ▼
Context Package
      │
      ▼
Microsoft Foundry
```

---

# 19. Model Routing

Weiterverwendung der bestehenden Architektur:

```text
module × workload
```

Beispiel:

```text
Performance Explanation
    → finance-fast

Risk Explanation
    → finance-reasoning

Board Report Draft
    → finance-drafting

Generic CFO QA
    → model-router
```

---

# 20. Copilot Run Metadata

Persistieren:

```text
run_id

company_id
period_id
scenario_id

workload

route_id
deployment

prompt_version

source_read_models
source_run_ids
source_report_ids

token_usage
estimated_cost

latency

response

citations

fallback_used

created_by
created_at
```

---

# 21. AI Financial Guardrails

Das Modell darf erklären.

Das Modell darf keine Finance-Zahl erfinden.

Zahlen müssen auf:

```text
Workspace Read Model
Finance Run
Report Artifact
```

zurückführbar sein.

Wenn eine neue Zahl erscheint:

```text
response rejected
```

oder als unverified markiert.

---

# 22. BE-07 – Production Integration Hardening

Das letzte Phase-2-Epic macht sämtliche bisherigen Backend-Slices produktionsfähig.

---

# 23. Persistence

InMemory-Repositories werden durch Production Adapter ergänzt.

Ziel:

```text
Repository Interface
        │
        ├── InMemory
        │
        ├── SQLite
        │
        └── Azure SQL / PostgreSQL
```

Betroffene Daten:

```text
contexts
snapshots

workspace projections

model runs
decision runs

audit events

reports
artifacts

copilot runs
```

---

# 24. Database Design

Kernobjekte:

```text
companies

periods
scenarios

data_snapshots

workspace_projections

finance_runs

finance_run_inputs

finance_run_results

finance_run_sources

decision_approvals

reports

report_artifacts

copilot_runs

audit_events
```

---

# 25. Optimistic Concurrency

Versionierte Ressourcen:

```text
version
updated_at
```

Write Requests optional:

```text
If-Match
```

Bei Konflikt:

```text
409 Conflict
```

---

# 26. Idempotency

Für POST-Operationen:

```text
Idempotency-Key
```

Backend speichert:

```text
key
request_hash
response_reference
expires_at
```

---

# 27. Pagination

Alle Listen-Endpunkte:

```text
?limit=50
&cursor=
```

Response:

```text
items
next_cursor
has_more
```

Keine Offset-Pagination für große produktive Tabellen.

---

# 28. Observability

Jeder Request:

```text
request_id
correlation_id
user_id
company_id
run_id
```

Structured JSON Logs.

---

# 29. Metrics

Mindestens:

```text
http_request_duration

run_execution_duration

run_failure_count

report_generation_duration

foundry_latency

foundry_token_usage

foundry_error_rate

projection_generation_duration
```

---

# 30. Distributed Tracing

OpenTelemetry.

Targets:

```text
FastAPI

Run Execution

Database

Azure Blob Storage

Microsoft Foundry
```

---

# 31. Resilience

Externe Calls erhalten:

```text
timeouts
retry policy
exponential backoff
circuit breaker
```

Besonders:

```text
Microsoft Foundry

Azure Blob Storage

Azure SQL
```

---

# 32. Rate Limiting

Unterschiedliche Limits für:

```text
Read APIs
Finance Runs
Monte Carlo Runs
Reporting
Copilot
```

LLM- und Monte-Carlo-Calls benötigen niedrigere Limits als Read APIs.

---

# 33. Security Hardening

Produktionsauthentifizierung:

```text
Microsoft Entra ID
```

Nicht vertrauen auf Client Header wie:

```text
X-User
X-Roles
X-Companies
```

Diese bleiben Development/Test Adapter.

Production:

```text
JWT
  │
  ▼
Entra Claims
  │
  ▼
Principal
  │
  ▼
RBAC
```

---

# 34. Multi-Tenant Isolation

Jede DB-Abfrage muss Company Scope beinhalten.

Verboten:

```text
repository.get(run_id)
```

ohne nachfolgende Scope-Prüfung.

Bevorzugt:

```text
repository.get(
    run_id,
    allowed_company_ids
)
```

Fail closed.

---

# 35. Audit Trail

Audit Events für:

```text
run_created

run_started
run_failed
run_succeeded

run_validated
run_approved
run_rejected

report_generated
report_published

copilot_called

configuration_changed
```

Event:

```text
event_id

user_id
company_id

entity_type
entity_id

event_type

timestamp

metadata
```

---

# 36. Azure Production Architecture

Zielarchitektur:

```text
Azure Front Door
      │
      ▼
Azure App Service / Container Apps
      │
      ▼
FastAPI Docker Container
      │
      ├── Azure SQL / PostgreSQL
      │
      ├── Azure Blob Storage
      │
      ├── Azure Key Vault
      │
      ├── Azure Monitor
      │
      └── Microsoft Foundry
```

---

# 37. Containerisierung

Backend bleibt Docker-first.

Production Container:

```text
python
fastapi
uvicorn/gunicorn
```

Health Checks:

```text
/health/live

/health/ready
```

Readiness prüft später:

```text
database
blob storage
foundry optional
```

---

# 38. CI/CD

GitHub Actions:

```text
Ruff

pytest Python 3.11

pytest Python 3.12

OpenAPI contract generation

Docker build

security scan

dependency scan
```

Später:

```text
Azure deployment
migration validation
smoke tests
```

---

# 39. Database Migrations

Einführung von:

```text
Alembic
```

Regel:

```text
Schemaänderung
   │
   ▼
Migration
   │
   ▼
Migration Test
   │
   ▼
Deployment
```

Keine automatischen ORM-Schemaänderungen in Production.

---

# 40. Testing Strategy

## Unit Tests

Finance Engines isoliert.

## Application Tests

Orchestratoren mit InMemory-Repositories.

## API Tests

FastAPI TestClient.

## Contract Tests

OpenAPI Schema.

## Repository Contract Tests

Jeder Persistence Adapter muss dieselben Repository-Tests bestehen.

## Integration Tests

Azure-compatible Services.

## Security Tests

Company isolation.

## Regression Tests

Finance-Referenzwerte.

---

# 41. Statistical Regression Tests

Für relevante Modelle werden feste Seeds und Referenzbereiche verwendet.

Beispiele:

```text
Monte Carlo

VaR

Expected Shortfall

GARCH

HMM

EVT

Copulas

Monte Carlo NPV
```

Tests prüfen nicht nur „läuft“.

Sie prüfen statistisch plausible Eigenschaften.

---

# 42. Definition of Done pro Backend Epic

Ein Backend-Epic ist erst abgeschlossen, wenn:

```text
Domain Logic integriert

API Contract vorhanden

RBAC vorhanden

Company Context vorhanden

Persistence definiert

Lineage vorhanden

Audit Events vorhanden

OpenAPI aktualisiert

Unit Tests grün

API Tests grün

Python 3.11 grün

Python 3.12 grün

keine Frontend-Business-Logic notwendig
```

---

# 43. Reihenfolge ab aktuellem Stand

Aktueller Fortschritt:

```text
BE-01 Context APIs                  ✅

BE-02 Workspace Read Models         ✅

BE-03 Risk / Market-Risk Runs       ✅

BE-04 Action / Capital Runs         ← NOW

BE-05 Reporting Orchestration

BE-06 Foundry Copilot Orchestration

BE-07 Production Hardening
```

---

# 44. Konkrete BE-04 Implementierungsreihenfolge

## Step 1

Run-Domain aus BE-03 generalisieren.

Neue Domains:

```text
ACTION

CAPITAL
```

## Step 2

Run Types ergänzen:

```text
Action:

simulation

prioritization

benefit_tracking
```

```text
Capital:

project_valuation

project_monte_carlo

portfolio_optimization

funding_scenario
```

## Step 3

Action Dispatcher implementieren.

Bestehende Services verwenden.

## Step 4

Capital Dispatcher implementieren.

Bestehende Services verwenden.

## Step 5

Decision Governance ergänzen.

```text
validate

approve

reject
```

## Step 6

RBAC mit bestehenden Permissions integrieren.

## Step 7

REST Contracts implementieren.

## Step 8

Snapshot-/Context-Lineage übernehmen.

## Step 9

OpenAPI Contract Tests.

## Step 10

Integration Tests.

## Step 11

Roadmap-Status aktualisieren.

## Step 12

PR öffnen und CI validieren.

---

# 45. Erwarteter BE-04 Pull Request

Branch:

```text
feature/be-04-action-capital-runs
```

Expected files ungefähr:

```text
backend/app/model_runs/finance_model_runs.py

backend/app/decision_runs.py
oder Erweiterung finance_model_runs.py

backend/app/model_runs/router.py

backend/app/shared/composition.py

backend/app/factory.py

tests/test_be04_action_capital_runs.py

docs/backend-production-integration-roadmap.md
```

Keine Änderungen in:

```text
frontend/
```

---

# 46. Ziel nach Phase 2

Wenn BE-07 abgeschlossen ist, kann ein Client:

```text
Company auswählen

Period auswählen

Scenario auswählen

Workspace laden

Risk Run starten

Market Risk Run starten

Action Simulation starten

Capital Allocation starten

Decision validieren

Decision freigeben

Report erzeugen

Report freigeben

Copilot auf denselben Kontext anwenden
```

und jeder Schritt ist:

```text
persistiert

reproduzierbar

versioniert

company-scoped

auditierbar

lineage-aware

API-first
```

Das ist der Punkt, an dem aus den heutigen Finance Engines eine tatsächlich produktionsfähige CFO-Plattform wird.
