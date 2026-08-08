export type WorkspaceSelection = {
  companyId: string;
  periodId: string;
  scenarioId: string;
};

export type RiskTone = "positive" | "warning" | "negative" | "neutral";

export type EnterpriseRisk = {
  id: string;
  title: string;
  category: string;
  owner: string;
  probability: number;
  impact: number;
  expectedLoss: string;
  p95Loss: string;
  residualLoss: string;
  mitigationEffect: string;
  appetiteUsage: string;
  status: "HEALTHY" | "WARNING" | "BREACHED";
  trend: "UP" | "DOWN" | "STABLE";
};

export type PortfolioPoint = {
  percentile: number;
  loss: number;
};

export type RiskCommandSnapshot = {
  contractStatus: "MOCK_CONNECTED";
  context: WorkspaceSelection & {
    companyLabel: string;
    periodLabel: string;
    scenarioLabel: string;
    asOf: string;
  };
  portfolio: {
    meanGrossLoss: string;
    meanNetLoss: string;
    p50NetLoss: string;
    p95NetLoss: string;
    p99NetLoss: string;
    expectedShortfall95: string;
    appetiteUsage: string;
    paths: string;
    seed: string;
    distribution: PortfolioPoint[];
  };
  risks: EnterpriseRisk[];
  categories: Array<{
    id: string;
    label: string;
    grossExposure: number;
    residualExposure: number;
    appetite: number;
    tone: RiskTone;
  }>;
  radar: Array<{
    dimension: string;
    exposure: number;
    appetite: number;
  }>;
  correlation: {
    labels: string[];
    matrix: number[][];
  };
  regimes: {
    lifecycle: "MODEL_CONTRACT_PENDING";
    currentState: string;
    stateConfidence: string;
    states: Array<{ id: string; label: string; probability: number; expectedLossMultiplier: string }>;
    transitionMatrix: number[][];
  };
  tail: {
    lifecycle: "MODEL_CONTRACT_PENDING";
    threshold: string;
    shape: string;
    scale: string;
    expectedShortfall: string;
    qq: Array<{ theoretical: number; observed: number }>;
  };
  scenario: {
    name: string;
    description: string;
    earningsAtRisk: string;
    cashAtRisk: string;
    probability: string;
    topDrivers: string[];
  };
  controls: Array<{
    id: string;
    riskId: string;
    name: string;
    owner: string;
    effectiveness: string;
    annualCost: string;
    avoidedLoss: string;
    status: "ACTIVE" | "PLANNED" | "INEFFECTIVE";
  }>;
};
