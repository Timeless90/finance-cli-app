export type WorkspaceSelection = {
  companyId: string;
  periodId: string;
  scenarioId: string;
};

export type PlanningScenarioSummary = {
  id: string;
  label: string;
  type: "BASE" | "UPSIDE" | "DOWNSIDE";
  status: "ACTIVE" | "APPROVED" | "DRAFT";
  revenue: string;
  ebitda: string;
  freeCashFlow: string;
  owner: string;
};

export type ForecastSeriesPoint = {
  period: string;
  actual?: number;
  plan: number;
  forecast: number;
  lower: number;
  upper: number;
};

export type StatementRow = {
  id: string;
  label: string;
  level: 0 | 1;
  actual: string;
  plan: string;
  forecast: string;
  variance: string;
  varianceTone: "positive" | "negative" | "neutral";
};

export type PlanningDriver = {
  id: string;
  label: string;
  value: string;
  unit: string;
  delta: string;
  owner: string;
  status: "LOCKED" | "REVIEW" | "OPEN";
};

export type PlanningSnapshot = {
  contractStatus: "MOCK_CONNECTED";
  context: WorkspaceSelection & {
    companyLabel: string;
    periodLabel: string;
    scenarioLabel: string;
    asOf: string;
  };
  scenarios: PlanningScenarioSummary[];
  activeScenario: {
    id: string;
    label: string;
    versionId: string;
    snapshotId: string;
    assumptionSetId: string;
    modelVersion: string;
    status: "APPROVED" | "DRAFT";
  };
  forecast: {
    kpi: "EBITDA";
    unit: "EUR_M";
    horizon: string;
    points: ForecastSeriesPoint[];
    confidence: string;
    mape: string;
    bias: string;
  };
  statement: StatementRow[];
  drivers: PlanningDriver[];
  thresholds: Array<{
    kpi: string;
    target: string;
    warning: string;
    current: string;
    status: "ON_TARGET" | "WARNING" | "BREACH";
  }>;
};

export type KpiNode = {
  id: string;
  label: string;
  value: string;
  variance: string;
  tone: "positive" | "negative" | "neutral";
  parentId?: string;
};

export type VarianceStep = {
  id: string;
  label: string;
  amount: number;
  display: string;
  type: "start" | "positive" | "negative" | "end";
};

export type PerformanceTrendPoint = {
  period: string;
  actual: number;
  plan: number;
  forecast: number;
};

export type PerformanceSnapshot = {
  contractStatus: "MOCK_CONNECTED";
  context: PlanningSnapshot["context"];
  metrics: Array<{
    id: string;
    label: string;
    value: string;
    delta: string;
    deltaTone: "positive" | "negative" | "neutral";
    meta: string;
  }>;
  kpiTree: KpiNode[];
  varianceBridge: {
    kpi: "EBITDA";
    comparison: "ACTUAL_VS_PLAN";
    baseline: string;
    actual: string;
    explained: string;
    unexplained: string;
    fullyExplained: boolean;
    steps: VarianceStep[];
  };
  trend: {
    kpi: "EBITDA_MARGIN";
    unit: "PERCENT";
    points: PerformanceTrendPoint[];
  };
  anomalies: Array<{
    id: string;
    period: string;
    kpi: string;
    observation: string;
    severity: "HIGH" | "MEDIUM" | "LOW";
    status: "OPEN" | "REVIEWED";
  }>;
  commentary: Array<{
    id: string;
    kpi: string;
    variance: string;
    threshold: string;
    status: "REQUIRED" | "COMPLETE" | "NOT_REQUIRED";
    owner: string;
  }>;
};
