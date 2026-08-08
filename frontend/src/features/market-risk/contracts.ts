export type WorkspaceSelection = {
  companyId: string;
  periodId: string;
  scenarioId: string;
};

export type ModelLifecycle = "MODEL_CONTRACT_PENDING";

export type MarketRiskAsset = {
  id: string;
  label: string;
  assetClass: "FX" | "COMMODITY" | "EQUITY" | "RATE";
  exposure: string;
  spot: string;
  dailyVol: string;
  annualizedVol: string;
  var95: string;
  es95: string;
  beta: string;
  status: "NORMAL" | "WATCH" | "STRESS";
};

export type TimePoint = {
  index: number;
  observed: number;
  fitted: number;
  upper: number;
  lower: number;
};

export type MarketRiskSnapshot = {
  contractStatus: "MOCK_CONNECTED";
  modelLifecycle: ModelLifecycle;
  context: WorkspaceSelection & {
    companyLabel: string;
    periodLabel: string;
    scenarioLabel: string;
    asOf: string;
  };
  assets: MarketRiskAsset[];
  selectedAssetId: string;
  garch: {
    model: "GARCH(1,1)-t";
    runId: string;
    convergence: "CONVERGED";
    logLikelihood: string;
    aic: string;
    bic: string;
    persistence: string;
    unconditionalVol: string;
    parameters: Array<{
      name: string;
      estimate: string;
      stdError: string;
      tStat: string;
      pValue: string;
    }>;
    volatility: TimePoint[];
    residuals: Array<{ index: number; value: number }>;
    qq: Array<{ theoretical: number; observed: number }>;
  };
  regimes: {
    model: "2-STATE MARKOV SWITCHING";
    runId: string;
    currentState: "LOW VOL" | "HIGH VOL";
    confidence: string;
    states: Array<{
      id: string;
      label: string;
      probability: number;
      mean: string;
      volatility: string;
    }>;
    probabilities: Array<{ index: number; low: number; high: number }>;
    transitionMatrix: number[][];
  };
  marginals: Array<{
    assetId: string;
    family: string;
    location: string;
    scale: string;
    dof: string;
    aic: string;
    ksPValue: string;
  }>;
  dependency: {
    model: "t-COPULA";
    runId: string;
    dof: string;
    logLikelihood: string;
    tailDependence: string;
    labels: string[];
    matrix: number[][];
    edges: Array<{
      source: string;
      target: string;
      correlation: number;
      tailDependence: number;
    }>;
  };
  simulation: {
    runId: string;
    paths: string;
    horizon: "252D";
    seed: string;
    var95: string;
    es95: string;
    fan: Array<{
      horizon: number;
      p05: number;
      p25: number;
      p50: number;
      p75: number;
      p95: number;
    }>;
  };
  backtest: {
    window: string;
    observations: number;
    varExceptions: number;
    expectedExceptions: string;
    kupiecPValue: string;
    christoffersenPValue: string;
    trafficLight: "GREEN" | "YELLOW" | "RED";
    breaches: Array<{
      date: string;
      return: string;
      varLimit: string;
      severity: string;
      documented: boolean;
      note: string;
    }>;
  };
  modelComparison: Array<{
    id: string;
    model: string;
    aic: string;
    bic: string;
    outOfSampleLoss: string;
    varCoverage: string;
    tailFit: string;
    status: "CANDIDATE" | "CHAMPION" | "REJECTED";
  }>;
  thresholds: Array<{
    id: string;
    metric: string;
    warning: string;
    breach: string;
    current: string;
    status: "NORMAL" | "WARNING" | "BREACH";
    documentation: string;
  }>;
};
