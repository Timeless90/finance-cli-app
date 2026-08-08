export type WorkspaceSelection = {
  companyId: string;
  periodId: string;
  scenarioId: string;
};

export type WorkspaceContextSnapshot = WorkspaceSelection & {
  companyLabel: string;
  periodLabel: string;
  scenarioLabel: string;
  asOf: string;
};

export type ProfitabilitySegment = {
  id: string;
  label: string;
  revenue: string;
  contributionMargin: string;
  contributionMarginPct: string;
  ebitda: string;
  allocatedCost: string;
  marginAtRisk: string;
  status: "STRONG" | "WATCH" | "CRITICAL";
};

export type ProfitabilitySnapshot = {
  contractStatus: "MOCK_CONNECTED";
  context: WorkspaceContextSnapshot;
  metrics: Array<{
    id: string;
    label: string;
    value: string;
    delta: string;
    deltaTone: "positive" | "negative" | "neutral";
    meta: string;
  }>;
  segments: ProfitabilitySegment[];
  waterfall: Array<{
    id: string;
    label: string;
    amount: number;
    display: string;
    type: "start" | "positive" | "negative" | "end";
  }>;
  matrix: Array<{
    id: string;
    product: string;
    customer: string;
    channel: string;
    revenue: string;
    marginPct: string;
    marginAtRisk: string;
    status: "STRONG" | "WATCH" | "CRITICAL";
  }>;
  sensitivities: Array<{
    lever: string;
    movement: string;
    ebitdaImpact: string;
    marginImpact: string;
    tone: "positive" | "negative";
  }>;
  allocation: {
    versionId: string;
    snapshotId: string;
    method: string;
    sourceCost: string;
    allocatedCost: string;
    reconciliationDifference: string;
    reconciled: boolean;
  };
};

export type CashPoint = {
  period: string;
  opening: number;
  inflow: number;
  outflow: number;
  closing: number;
  minimum: number;
};

export type LiquiditySnapshot = {
  contractStatus: "MOCK_CONNECTED";
  context: WorkspaceContextSnapshot;
  metrics: Array<{
    id: string;
    label: string;
    value: string;
    delta: string;
    deltaTone: "positive" | "negative" | "neutral";
    meta: string;
  }>;
  cashForecast: {
    horizon: "13_WEEK";
    points: CashPoint[];
    minimumLiquidity: string;
    minimumHeadroom: string;
    forecastAccuracy: string;
  };
  workingCapital: Array<{
    id: string;
    label: string;
    current: string;
    target: string;
    cashImpact: string;
    status: "ON_TARGET" | "WATCH" | "BREACH";
  }>;
  debt: Array<{
    id: string;
    instrument: string;
    principal: string;
    rate: string;
    maturity: string;
    committedLimit: string;
    headroom: string;
    status: "NORMAL" | "WATCH";
  }>;
  covenants: Array<{
    id: string;
    metric: string;
    actual: string;
    threshold: string;
    headroom: string;
    projectedMinimum: string;
    status: "PASS" | "WATCH" | "BREACH";
  }>;
  stresses: Array<{
    id: string;
    name: string;
    closingCash: string;
    headroom: string;
    breach: boolean;
    mitigation: string;
  }>;
};
