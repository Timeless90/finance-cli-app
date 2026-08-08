export type WorkspaceSelection = {
  companyId: string;
  periodId: string;
  scenarioId: string;
};

export type ReportStatus = "DRAFT" | "REVIEW" | "APPROVED" | "PUBLISHED";
export type CopilotLifecycle = "COPILOT_CONTRACT_PENDING";

export type ReportSection = {
  id: string;
  title: string;
  purpose: string;
  owner: string;
  status: "EMPTY" | "GENERATED" | "REVIEWED" | "APPROVED";
  sourceCount: number;
  wordCount: number;
  materiality: "HIGH" | "MEDIUM" | "LOW";
};

export type ReportVersion = {
  id: string;
  label: string;
  createdAt: string;
  createdBy: string;
  status: ReportStatus;
  sourceSnapshotIds: string[];
  modelRunIds: string[];
  checksum: string;
};

export type GroundedCitation = {
  id: string;
  label: string;
  sourceType: "SNAPSHOT" | "MODEL_RUN" | "RISK" | "ACTION" | "REPORT";
  sourceId: string;
  excerpt: string;
  verified: boolean;
};

export type CopilotMessage = {
  id: string;
  role: "USER" | "ASSISTANT";
  content: string;
  createdAt: string;
  citations: GroundedCitation[];
  confidence?: string;
  routeId?: string;
  modelLabel?: string;
  requiresApproval?: boolean;
};

export type ReportingCopilotSnapshot = {
  contractStatus: "MOCK_CONNECTED";
  copilotLifecycle: CopilotLifecycle;
  context: WorkspaceSelection & {
    companyLabel: string;
    periodLabel: string;
    scenarioLabel: string;
    asOf: string;
  };
  reporting: {
    activeReport: {
      id: string;
      title: string;
      template: string;
      reportingDate: string;
      status: ReportStatus;
      currentVersionId: string;
      reviewer: string;
      approver: string;
      completeness: string;
      sourceCoverage: string;
      unresolvedFindings: number;
    };
    sections: ReportSection[];
    versions: ReportVersion[];
    sourcePack: Array<{
      id: string;
      type: string;
      label: string;
      status: "VALIDATED" | "STALE" | "MISSING";
      asOf: string;
      owner: string;
    }>;
    exportTargets: Array<{
      id: string;
      label: string;
      format: "PDF" | "PPTX" | "DOCX" | "XLSX";
      status: "READY" | "BLOCKED";
      note: string;
    }>;
    narrativePreview: Array<{
      id: string;
      heading: string;
      content: string;
      citations: string[];
      status: "GENERATED" | "REVIEWED";
    }>;
    findings: Array<{
      id: string;
      severity: "HIGH" | "MEDIUM" | "LOW";
      section: string;
      finding: string;
      owner: string;
      status: "OPEN" | "RESOLVED";
    }>;
  };
  copilot: {
    sessionId: string;
    groundingMode: "VALIDATED_SOURCES_ONLY";
    contextSources: Array<{
      id: string;
      label: string;
      type: string;
      enabled: boolean;
      status: "VALIDATED" | "STALE";
    }>;
    routes: Array<{
      id: string;
      workload: string;
      modelLabel: string;
      deployment: string;
      reasoning: string;
      groundingRequired: boolean;
      status: "ACTIVE" | "FALLBACK";
    }>;
    messages: CopilotMessage[];
    suggestedPrompts: string[];
    proposedActions: Array<{
      id: string;
      title: string;
      sourceInsight: string;
      estimatedImpact: string;
      confidence: string;
      status: "PROPOSED" | "APPROVAL_REQUIRED";
    }>;
    guardrails: Array<{
      id: string;
      label: string;
      status: "ENFORCED" | "PENDING";
      detail: string;
    }>;
  };
};
