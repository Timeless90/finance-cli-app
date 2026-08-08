# UAT Evidence

This directory stores non-sensitive evidence for executions recorded in `../execution-log.csv`.
Repository evidence is optional when an approved immutable evidence system is used instead. The run
log must reference either a repository-relative path or the approved immutable link.

## Naming

Create one directory per execution using:

```text
<run_id>_<case_id>_<yyyy-mm-dd>/
```

Use lowercase ASCII names for files and include the evidence type:

```text
uat-2026-08-001_fe-uat-021_2026-08-08/
  screenshot_desktop-chromium_command-center.png
  api_get-command-center_response.json
  accessibility_axe-command-center.json
  database_projection-check.txt
  trace_correlation-8f21.json
  artifact_board-report.sha256
```

## Required metadata

Evidence must be attributable to the execution log and record, in the artifact itself or a sibling
`metadata.txt` file:

- run ID and case ID;
- UTC capture time;
- environment, build version, and commit SHA;
- tester;
- browser name/version, operating system, viewport, zoom, locale, and timezone for UI evidence;
- request method/path and safe correlation ID for API evidence;
- database/schema migration version for persistence evidence;
- worker/broker version for asynchronous-flow evidence.

## Evidence by review type

### Frontend and visual

Capture the entire relevant viewport and a focused image for any defect. Include desktop, tablet, or
mobile dimensions required by the case. Do not crop away mock/live labels, context selectors, error
messages, freshness, or lineage. For responsive defects, capture the narrowest failing width and one
passing adjacent width. Record reduced-motion and 200-percent zoom settings where applicable.

### Accessibility

Retain automated scan output, keyboard traversal notes, focus screenshots when useful, and the
screen-reader/browser combination used for manual review. Automated scans do not replace keyboard,
focus, semantics, zoom, chart alternatives, or announcement review.

### API and data flow

Capture sanitized request/response bodies, HTTP status, headers relevant to versioning/idempotency,
and correlation ID. Redact authorization headers, cookies, tokens, personal data, and confidential
finance values. Prefer synthetic identifiers that can remain visible end to end.

### Persistence and recovery

Store read-only query output showing identifiers, versions, state, checksums, and timestamps before
and after restart, rollback, backup, or restore. Record the database and migration version. Never
include connection strings, passwords, access tokens, or raw production rows.

### Audit and lineage

Capture ordered events and lineage references sufficient to connect actor, company context, source
snapshot, model/scenario/run version, result or artifact, and approval/publication state. Include hash
verification without exposing protected payloads.

### Jobs and observability

Capture job state transitions, attempt counts, retry/dead-letter outcome, and a correlated trace or
structured-log excerpt. Redact secrets and finance payloads. Metrics evidence should show query/time
range, unit, and environment.

### Generated artifacts

Retain artifact metadata and a SHA-256 checksum. For PDF, PPTX, XLSX, or similar outputs, capture a
representative visual inspection plus machine-readable metadata where available. Do not commit large
binary artifacts when the approved evidence store can retain them immutably.

## Redaction and prohibited content

Never store:

- credentials, tokens, session cookies, private keys, or connection strings;
- unredacted production finance data or customer/person identifiers;
- raw model prompts or responses containing protected data;
- infrastructure secrets, internal hostnames, or exploitable stack traces;
- evidence copied from an environment for which the tester lacks approval.

Redaction must preserve the ability to correlate synthetic IDs across the reviewed flow. Use
consistent placeholders such as `[REDACTED_TOKEN]` and `[REDACTED_FINANCE_VALUE]`; do not blur or
remove the case ID, run ID, state, version, timestamp, checksum, or correlation ID needed for review.

## Retention and review

Evidence follows the release and audit retention policy for the environment. A reviewer confirms
that evidence supports every expected field in the catalogue case and contains no prohibited data.
If evidence is replaced because redaction was inadequate, retain the correction trail in the defect
or evidence system and append a new execution-log row when acceptance is re-executed.
