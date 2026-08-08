import type { ReportingCopilotSnapshot, WorkspaceSelection } from "./contracts";

const companies: Record<string, string> = {
  "local-holding": "AURELIA HOLDING",
  "local-eu": "EUROPE DIVISION",
};
const periods: Record<string, string> = {
  "local-fy26-p08": "FY26 // P08",
  "local-fy26-p07": "FY26 // P07",
};
const scenarios: Record<string, string> = {
  "local-base": "BASE",
  "local-upside": "UPSIDE",
  "local-downside": "DOWNSIDE",
};

function context(selection: WorkspaceSelection): ReportingCopilotSnapshot["context"] {
  return {
    ...selection,
    companyLabel: companies[selection.companyId] ?? selection.companyId,
    periodLabel: periods[selection.periodId] ?? selection.periodId,
    scenarioLabel: scenarios[selection.scenarioId] ?? selection.scenarioId,
    asOf: "2026-08-08T06:15:00+02:00",
  };
}

const reporting: ReportingCopilotSnapshot["reporting"] = {
  activeReport: {
    id: "RPT-FY26-P08-BOARD",
    title: "CFO Board Performance & Risk Report",
    template: "Board Pack // Finance 2060 v3",
    reportingDate: "2026-08-31",
    status: "REVIEW",
    currentVersionId: "RPT-FY26-P08-BOARD-v6",
    reviewer: "Group Controlling",
    approver: "CFO",
    completeness: "91%",
    sourceCoverage: "96%",
    unresolvedFindings: 3,
  },
  sections: [
    { id: "SEC-01", title: "Executive Summary", purpose: "Decision-focused CFO overview", owner: "Group FP&A", status: "REVIEWED", sourceCount: 8, wordCount: 420, materiality: "HIGH" },
    { id: "SEC-02", title: "Performance & Outlook", purpose: "Actual, plan, forecast and key drivers", owner: "Group Controlling", status: "APPROVED", sourceCount: 11, wordCount: 780, materiality: "HIGH" },
    { id: "SEC-03", title: "Liquidity & Capital", purpose: "Cash, covenant, debt and allocation state", owner: "Treasury", status: "REVIEWED", sourceCount: 7, wordCount: 540, materiality: "HIGH" },
    { id: "SEC-04", title: "Risk & Uncertainty", purpose: "Enterprise risk, tail metrics and mitigations", owner: "Risk Management", status: "GENERATED", sourceCount: 9, wordCount: 630, materiality: "HIGH" },
    { id: "SEC-05", title: "Management Actions", purpose: "Owned actions and value realization", owner: "CFO Office", status: "GENERATED", sourceCount: 6, wordCount: 390, materiality: "MEDIUM" },
    { id: "SEC-06", title: "Lagebericht Risk Narrative", purpose: "Auditable risk narrative draft", owner: "Group Accounting", status: "GENERATED", sourceCount: 12, wordCount: 910, materiality: "HIGH" },
  ],
  versions: [
    { id: "RPT-FY26-P08-BOARD-v6", label: "v6 // Review candidate", createdAt: "08 Aug 2026 06:12", createdBy: "Reporting Service", status: "REVIEW", sourceSnapshotIds: ["snap-fin-p08-v4", "snap-risk-p08-v3", "snap-liq-p08-v5"], modelRunIds: ["narrative-run-882", "risk-run-417"], checksum: "sha256:7d31…bb9a" },
    { id: "RPT-FY26-P08-BOARD-v5", label: "v5 // Risk refresh", createdAt: "07 Aug 2026 17:44", createdBy: "Reporting Service", status: "DRAFT", sourceSnapshotIds: ["snap-fin-p08-v4", "snap-risk-p08-v2"], modelRunIds: ["narrative-run-861"], checksum: "sha256:a04f…9c12" },
    { id: "RPT-FY26-P08-BOARD-v4", label: "v4 // Controller baseline", createdAt: "06 Aug 2026 14:08", createdBy: "Group Controlling", status: "APPROVED", sourceSnapshotIds: ["snap-fin-p08-v3", "snap-risk-p08-v2"], modelRunIds: [], checksum: "sha256:d81e…31f0" },
  ],
  sourcePack: [
    { id: "SRC-FIN", type: "FINANCE SNAPSHOT", label: "P08 Actual / Forecast Snapshot", status: "VALIDATED", asOf: "08 Aug 2026 06:00", owner: "Group Controlling" },
    { id: "SRC-RISK", type: "RISK RUN", label: "Enterprise Risk Aggregation", status: "VALIDATED", asOf: "08 Aug 2026 05:51", owner: "Risk Management" },
    { id: "SRC-LIQ", type: "LIQUIDITY SNAPSHOT", label: "13-Week Cash & Covenant", status: "VALIDATED", asOf: "08 Aug 2026 05:46", owner: "Treasury" },
    { id: "SRC-ACT", type: "ACTION REGISTER", label: "Management Action Steering", status: "VALIDATED", asOf: "08 Aug 2026 05:39", owner: "CFO Office" },
    { id: "SRC-CAP", type: "CAPITAL RUN", label: "Balanced Allocation Run", status: "STALE", asOf: "07 Aug 2026 16:30", owner: "Investment Committee" },
  ],
  exportTargets: [
    { id: "EXP-PDF", label: "Board Pack PDF", format: "PDF", status: "READY", note: "Review watermark applied" },
    { id: "EXP-PPT", label: "Executive Slides", format: "PPTX", status: "READY", note: "Finance 2060 theme" },
    { id: "EXP-DOC", label: "Lagebericht Draft", format: "DOCX", status: "READY", note: "Risk section only" },
    { id: "EXP-XLS", label: "Evidence Appendix", format: "XLSX", status: "BLOCKED", note: "Capital source pack stale" },
  ],
  narrativePreview: [
    { id: "NAR-01", heading: "Executive Summary", content: "FY26 P08 remains above base-plan EBITDA, but downside exposure has increased through energy, DACH volume and liquidity sensitivity. Management response is concentrated on pricing, working capital and discretionary-spend controls.", citations: ["SRC-FIN", "SRC-RISK", "SRC-ACT"], status: "REVIEWED" },
    { id: "NAR-02", heading: "Risk & Uncertainty", content: "Portfolio risk remains within group appetite in the base case, while the downside scenario materially increases P95 loss and covenant pressure. Energy and demand risks are the dominant correlated drivers.", citations: ["SRC-RISK", "SRC-LIQ"], status: "GENERATED" },
  ],
  findings: [
    { id: "F-021", severity: "HIGH", section: "Liquidity & Capital", finding: "Capital allocation source is older than the active liquidity snapshot.", owner: "Investment Committee", status: "OPEN" },
    { id: "F-024", severity: "MEDIUM", section: "Risk & Uncertainty", finding: "Risk narrative references a mitigation awaiting final evidence upload.", owner: "Risk Management", status: "OPEN" },
    { id: "F-026", severity: "LOW", section: "Executive Summary", finding: "Decision wording requires CFO sign-off before publication.", owner: "CFO Office", status: "OPEN" },
  ],
};

const copilotBase: ReportingCopilotSnapshot["copilot"] = {
  sessionId: "copilot-session-fy26-p08-0017",
  groundingMode: "VALIDATED_SOURCES_ONLY",
  contextSources: [
    { id: "SRC-FIN", label: "Finance Snapshot", type: "SNAPSHOT", enabled: true, status: "VALIDATED" },
    { id: "SRC-RISK", label: "Enterprise Risk Run", type: "MODEL_RUN", enabled: true, status: "VALIDATED" },
    { id: "SRC-LIQ", label: "Liquidity Snapshot", type: "SNAPSHOT", enabled: true, status: "VALIDATED" },
    { id: "SRC-ACT", label: "Action Register", type: "ACTION", enabled: true, status: "VALIDATED" },
    { id: "SRC-CAP", label: "Capital Allocation", type: "MODEL_RUN", enabled: false, status: "STALE" },
  ],
  routes: [
    { id: "route-explain", workload: "Finance explanation", modelLabel: "Finance Reasoning", deployment: "finance-reasoning-primary", reasoning: "HIGH", groundingRequired: true, status: "ACTIVE" },
    { id: "route-narrative", workload: "Report narrative", modelLabel: "Narrative Drafting", deployment: "finance-narrative-default", reasoning: "MEDIUM", groundingRequired: true, status: "ACTIVE" },
    { id: "route-risk", workload: "Risk synthesis", modelLabel: "Risk Reasoning", deployment: "risk-reasoning-primary", reasoning: "HIGH", groundingRequired: true, status: "ACTIVE" },
    { id: "route-fast", workload: "Classification / extraction", modelLabel: "Fast Utility", deployment: "finance-fast-default", reasoning: "LOW", groundingRequired: true, status: "FALLBACK" },
  ],
  messages: [
    { id: "MSG-01", role: "USER", content: "What changed since P07 and what requires a CFO decision?", createdAt: "08:14", citations: [] },
    { id: "MSG-02", role: "ASSISTANT", content: "Three changes are decision-relevant: EBITDA remains above base plan but downside sensitivity widened; 13-week liquidity headroom is still positive in base but materially tighter in downside; and two high-priority actions depend on Treasury and working-capital execution. The immediate CFO decisions are hedge extension, discretionary-spend gating and whether to defer growth capital until the liquidity source pack is refreshed.", createdAt: "08:14", confidence: "91%", routeId: "route-explain", modelLabel: "Finance Reasoning", requiresApproval: false, citations: [
      { id: "CIT-01", label: "P08 Finance Snapshot", sourceType: "SNAPSHOT", sourceId: "snap-fin-p08-v4", excerpt: "EBITDA outlook and variance drivers", verified: true },
      { id: "CIT-02", label: "13-Week Liquidity", sourceType: "SNAPSHOT", sourceId: "snap-liq-p08-v5", excerpt: "Base and downside liquidity headroom", verified: true },
      { id: "CIT-03", label: "Action Register", sourceType: "ACTION", sourceId: "action-register-p08-v8", excerpt: "Treasury and working-capital action status", verified: true },
    ] },
  ],
  suggestedPrompts: [
    "Explain the P08 EBITDA variance and cite every driver.",
    "Which actions protect cash fastest in the downside scenario?",
    "Draft the board risk paragraph using validated sources only.",
    "Which capital candidates should be deferred if liquidity reserve is raised?",
  ],
  proposedActions: [
    { id: "PA-01", title: "Approve energy hedge extension", sourceInsight: "Energy risk remains the largest market exposure.", estimatedImpact: "€2.1M risk reduction", confidence: "84%", status: "APPROVAL_REQUIRED" },
    { id: "PA-02", title: "Refresh capital allocation run", sourceInsight: "Capital source pack is stale relative to liquidity snapshot.", estimatedImpact: "Decision quality / liquidity protection", confidence: "96%", status: "PROPOSED" },
  ],
  guardrails: [
    { id: "GR-01", label: "Validated sources only", status: "ENFORCED", detail: "Assistant may not use stale/disabled finance sources for numeric claims." },
    { id: "GR-02", label: "Citation required", status: "ENFORCED", detail: "Material numeric and decision claims require source IDs." },
    { id: "GR-03", label: "No autonomous write", status: "ENFORCED", detail: "Actions, reports and approvals require explicit user confirmation and backend authorization." },
    { id: "GR-04", label: "Model routing audit", status: "PENDING", detail: "Backend must persist route, deployment, reasoning profile and fallback chain per response." },
  ],
};

export function getMockReportingCopilotSnapshot(selection: WorkspaceSelection): ReportingCopilotSnapshot {
  const downside = selection.scenarioId === "local-downside";
  return {
    contractStatus: "MOCK_CONNECTED",
    copilotLifecycle: "COPILOT_CONTRACT_PENDING",
    context: context(selection),
    reporting: downside ? {
      ...reporting,
      activeReport: { ...reporting.activeReport, completeness: "87%", sourceCoverage: "92%", unresolvedFindings: 5 },
      findings: [
        ...reporting.findings,
        { id: "F-031", severity: "HIGH", section: "Executive Summary", finding: "Downside liquidity breach requires explicit going-concern mitigation wording before publication.", owner: "CFO Office", status: "OPEN" },
        { id: "F-034", severity: "HIGH", section: "Risk & Uncertainty", finding: "Downside P95 loss and covenant sensitivity require refreshed risk narrative.", owner: "Risk Management", status: "OPEN" },
      ],
    } : reporting,
    copilot: downside ? {
      ...copilotBase,
      messages: [
        copilotBase.messages[0]!,
        { ...copilotBase.messages[1]!, id: "MSG-02-D", content: "The downside scenario requires immediate CFO intervention. Liquidity headroom falls below the protected reserve, market-risk volatility breaches the defined threshold and the action portfolio shows lower realization confidence. Recommended decisions are to approve the hedge extension, activate the discretionary-spend gate, intensify collections and defer liquidity-intensive growth capital until a refreshed capital run confirms headroom.", confidence: "94%", citations: copilotBase.messages[1]!.citations },
      ],
    } : copilotBase,
  };
}
