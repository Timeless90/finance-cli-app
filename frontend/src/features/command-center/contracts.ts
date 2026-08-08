export type SignalTone = "positive" | "negative" | "warning" | "neutral";

export type CommandCenterContext = {
  companyId: string;
  periodId: string;
  scenarioId: string;
};

export type ExecutiveMetric = {
  id: string;
  label: string;
  value: string;
  delta: string;
  deltaTone: "positive" | "negative" | "neutral";
  meta: string;
};

export type ForecastPoint = {
  period: string;
  actual?: number;
  base: number;
  upside: number;
  downside: number;
};

export type VarianceDriver = {
  label: string;
  amount: string;
  share: string;
  tone: SignalTone;
};

export type RiskSignal = {
  id: string;
  title: string;
  owner: string;
  exposure: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  trend: "UP" | "DOWN" | "STABLE";
};

export type ManagementAction = {
  id: string;
  title: string;
  owner: string;
  due: string;
  status: "ON TRACK" | "AT RISK" | "BLOCKED";
  impact: string;
  confidence: string;
};

export type CommandCenterSnapshot = {
  contractStatus: "MOCK_CONNECTED";
  source: "frontend-fixture";
  context: CommandCenterContext & {
    companyLabel: string;
    periodLabel: string;
    scenarioLabel: string;
    currency: "EUR";
    asOf: string;
  };
  metrics: ExecutiveMetric[];
  forecast: {
    title: string;
    subtitle: string;
    points: ForecastPoint[];
  };
  liquidity: {
    cash: string;
    runway: string;
    minimumHeadroom: string;
    covenantHeadroom: string;
    tone: SignalTone;
  };
  risk: {
    score: string;
    expectedLoss: string;
    tailLoss: string;
    appetiteUsage: string;
    signals: RiskSignal[];
  };
  varianceDrivers: VarianceDriver[];
  actions: ManagementAction[];
  briefing: {
    headline: string;
    summary: string;
    decisions: string[];
  };
  assurance: {
    dataFreshness: string;
    coverage: string;
    modelStatus: string;
    lineageStatus: string;
  };
};
