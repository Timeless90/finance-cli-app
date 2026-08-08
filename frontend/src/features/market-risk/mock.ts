import type { MarketRiskSnapshot, WorkspaceSelection } from "./contracts";

const companyLabels: Record<string, string> = {
  "local-holding": "AURELIA HOLDING",
  "local-eu": "EUROPE DIVISION",
};

const periodLabels: Record<string, string> = {
  "local-fy26-p08": "FY26 // P08",
  "local-fy26-p07": "FY26 // P07",
};

const scenarioLabels: Record<string, string> = {
  "local-base": "BASE",
  "local-upside": "UPSIDE",
  "local-downside": "DOWNSIDE",
};

const volatility: MarketRiskSnapshot["garch"]["volatility"] = [
  { index: 1, observed: 0.74, fitted: 0.78, lower: 0.58, upper: 0.98 },
  { index: 2, observed: 0.81, fitted: 0.80, lower: 0.60, upper: 1.00 },
  { index: 3, observed: 0.96, fitted: 0.86, lower: 0.64, upper: 1.08 },
  { index: 4, observed: 1.22, fitted: 1.04, lower: 0.78, upper: 1.30 },
  { index: 5, observed: 1.46, fitted: 1.28, lower: 0.96, upper: 1.60 },
  { index: 6, observed: 1.18, fitted: 1.25, lower: 0.94, upper: 1.56 },
  { index: 7, observed: 0.98, fitted: 1.14, lower: 0.86, upper: 1.43 },
  { index: 8, observed: 0.87, fitted: 1.02, lower: 0.77, upper: 1.28 },
  { index: 9, observed: 0.91, fitted: 0.97, lower: 0.73, upper: 1.21 },
  { index: 10, observed: 1.04, fitted: 1.00, lower: 0.75, upper: 1.25 },
  { index: 11, observed: 1.31, fitted: 1.14, lower: 0.86, upper: 1.43 },
  { index: 12, observed: 1.62, fitted: 1.39, lower: 1.04, upper: 1.74 },
  { index: 13, observed: 1.38, fitted: 1.38, lower: 1.04, upper: 1.73 },
  { index: 14, observed: 1.11, fitted: 1.26, lower: 0.95, upper: 1.58 },
  { index: 15, observed: 0.94, fitted: 1.12, lower: 0.84, upper: 1.40 },
  { index: 16, observed: 0.86, fitted: 1.01, lower: 0.76, upper: 1.26 },
  { index: 17, observed: 0.90, fitted: 0.96, lower: 0.72, upper: 1.20 },
  { index: 18, observed: 1.08, fitted: 1.01, lower: 0.76, upper: 1.27 },
  { index: 19, observed: 1.34, fitted: 1.16, lower: 0.87, upper: 1.45 },
  { index: 20, observed: 1.19, fitted: 1.20, lower: 0.90, upper: 1.50 },
];

const residuals: MarketRiskSnapshot["garch"]["residuals"] = [
  { index: 1, value: -0.42 }, { index: 2, value: 0.18 }, { index: 3, value: 0.94 }, { index: 4, value: -1.34 },
  { index: 5, value: 1.72 }, { index: 6, value: -0.66 }, { index: 7, value: 0.31 }, { index: 8, value: -0.18 },
  { index: 9, value: 0.47 }, { index: 10, value: -0.88 }, { index: 11, value: 1.14 }, { index: 12, value: -2.08 },
  { index: 13, value: 1.38 }, { index: 14, value: -0.52 }, { index: 15, value: 0.21 }, { index: 16, value: -0.33 },
  { index: 17, value: 0.58 }, { index: 18, value: -1.02 }, { index: 19, value: 1.56 }, { index: 20, value: -0.74 },
];

const qq: MarketRiskSnapshot["garch"]["qq"] = [
  { theoretical: -2.3, observed: -2.62 }, { theoretical: -1.8, observed: -1.96 }, { theoretical: -1.4, observed: -1.45 },
  { theoretical: -1.0, observed: -1.02 }, { theoretical: -0.6, observed: -0.59 }, { theoretical: -0.2, observed: -0.18 },
  { theoretical: 0.2, observed: 0.19 }, { theoretical: 0.6, observed: 0.61 }, { theoretical: 1.0, observed: 1.04 },
  { theoretical: 1.4, observed: 1.51 }, { theoretical: 1.8, observed: 2.02 }, { theoretical: 2.3, observed: 2.78 },
];

const regimeProbabilities: MarketRiskSnapshot["regimes"]["probabilities"] = [
  { index: 1, low: 0.86, high: 0.14 }, { index: 2, low: 0.84, high: 0.16 }, { index: 3, low: 0.77, high: 0.23 },
  { index: 4, low: 0.48, high: 0.52 }, { index: 5, low: 0.21, high: 0.79 }, { index: 6, low: 0.28, high: 0.72 },
  { index: 7, low: 0.54, high: 0.46 }, { index: 8, low: 0.71, high: 0.29 }, { index: 9, low: 0.80, high: 0.20 },
  { index: 10, low: 0.74, high: 0.26 }, { index: 11, low: 0.43, high: 0.57 }, { index: 12, low: 0.16, high: 0.84 },
  { index: 13, low: 0.23, high: 0.77 }, { index: 14, low: 0.46, high: 0.54 }, { index: 15, low: 0.68, high: 0.32 },
  { index: 16, low: 0.82, high: 0.18 }, { index: 17, low: 0.79, high: 0.21 }, { index: 18, low: 0.61, high: 0.39 },
  { index: 19, low: 0.34, high: 0.66 }, { index: 20, low: 0.41, high: 0.59 },
];

const fan: MarketRiskSnapshot["simulation"]["fan"] = [
  { horizon: 0, p05: 100, p25: 100, p50: 100, p75: 100, p95: 100 },
  { horizon: 21, p05: 93, p25: 97, p50: 100, p75: 103, p95: 108 },
  { horizon: 42, p05: 89, p25: 95, p50: 100, p75: 106, p95: 113 },
  { horizon: 63, p05: 85, p25: 93, p50: 101, p75: 109, p95: 119 },
  { horizon: 84, p05: 82, p25: 92, p50: 101, p75: 111, p95: 124 },
  { horizon: 126, p05: 76, p25: 89, p50: 102, p75: 116, p95: 134 },
  { horizon: 168, p05: 71, p25: 87, p50: 103, p75: 120, p95: 143 },
  { horizon: 210, p05: 67, p25: 85, p50: 104, p75: 124, p95: 151 },
  { horizon: 252, p05: 63, p25: 83, p50: 105, p75: 129, p95: 160 },
];

const base: Omit<MarketRiskSnapshot, "context" | "contractStatus" | "modelLifecycle"> = {
  assets: [
    { id: "eurusd", label: "EUR/USD", assetClass: "FX", exposure: "€42.0M", spot: "1.148", dailyVol: "0.74%", annualizedVol: "11.8%", var95: "€0.52M", es95: "€0.71M", beta: "0.18", status: "NORMAL" },
    { id: "brent", label: "Brent Crude", assetClass: "COMMODITY", exposure: "€28.5M", spot: "$82.4", dailyVol: "1.92%", annualizedVol: "30.5%", var95: "€0.91M", es95: "€1.24M", beta: "0.41", status: "WATCH" },
    { id: "stoxx", label: "STOXX Europe 600", assetClass: "EQUITY", exposure: "€18.0M", spot: "528.7", dailyVol: "1.08%", annualizedVol: "17.1%", var95: "€0.32M", es95: "€0.44M", beta: "0.76", status: "NORMAL" },
    { id: "eur5y", label: "EUR 5Y Swap", assetClass: "RATE", exposure: "€65.0M", spot: "2.31%", dailyVol: "0.31%", annualizedVol: "4.9%", var95: "€0.34M", es95: "€0.47M", beta: "0.27", status: "NORMAL" },
  ],
  selectedAssetId: "brent",
  garch: {
    model: "GARCH(1,1)-t",
    runId: "garch-brent-fy26-p08-v1",
    convergence: "CONVERGED",
    logLikelihood: "-1,842.6",
    aic: "3,695.2",
    bic: "3,721.8",
    persistence: "0.964",
    unconditionalVol: "29.8%",
    parameters: [
      { name: "ω", estimate: "0.000012", stdError: "0.000004", tStat: "3.00", pValue: "0.003" },
      { name: "α₁", estimate: "0.081", stdError: "0.018", tStat: "4.50", pValue: "<0.001" },
      { name: "β₁", estimate: "0.883", stdError: "0.024", tStat: "36.79", pValue: "<0.001" },
      { name: "ν", estimate: "6.42", stdError: "0.71", tStat: "9.04", pValue: "<0.001" },
    ],
    volatility,
    residuals,
    qq,
  },
  regimes: {
    model: "2-STATE MARKOV SWITCHING",
    runId: "regime-brent-fy26-p08-v1",
    currentState: "HIGH VOL",
    confidence: "59%",
    states: [
      { id: "S1", label: "LOW VOL", probability: 0.41, mean: "+0.03%", volatility: "18.2%" },
      { id: "S2", label: "HIGH VOL", probability: 0.59, mean: "-0.06%", volatility: "38.7%" },
    ],
    probabilities: regimeProbabilities,
    transitionMatrix: [[0.94, 0.06], [0.11, 0.89]],
  },
  marginals: [
    { assetId: "eurusd", family: "Student-t", location: "0.01%", scale: "0.71%", dof: "7.8", aic: "-9,842", ksPValue: "0.31" },
    { assetId: "brent", family: "Student-t", location: "-0.02%", scale: "1.76%", dof: "6.4", aic: "-7,216", ksPValue: "0.22" },
    { assetId: "stoxx", family: "Skew-t", location: "0.03%", scale: "1.02%", dof: "8.9", aic: "-8,117", ksPValue: "0.18" },
    { assetId: "eur5y", family: "Normal", location: "0.00%", scale: "0.30%", dof: "—", aic: "-11,405", ksPValue: "0.44" },
  ],
  dependency: {
    model: "t-COPULA",
    runId: "copula-fy26-p08-v1",
    dof: "5.9",
    logLikelihood: "2,184.7",
    tailDependence: "0.21",
    labels: ["EUR/USD", "Brent", "STOXX", "EUR 5Y"],
    matrix: [
      [1, -0.18, 0.34, 0.29],
      [-0.18, 1, -0.27, 0.12],
      [0.34, -0.27, 1, 0.41],
      [0.29, 0.12, 0.41, 1],
    ],
    edges: [
      { source: "EUR/USD", target: "STOXX", correlation: 0.34, tailDependence: 0.16 },
      { source: "EUR/USD", target: "EUR 5Y", correlation: 0.29, tailDependence: 0.12 },
      { source: "Brent", target: "STOXX", correlation: -0.27, tailDependence: 0.19 },
      { source: "STOXX", target: "EUR 5Y", correlation: 0.41, tailDependence: 0.21 },
    ],
  },
  simulation: {
    runId: "mc-market-fy26-p08-v1",
    paths: "50,000",
    horizon: "252D",
    seed: "20260808",
    var95: "€4.8M",
    es95: "€6.7M",
    fan,
  },
  backtest: {
    window: "500D",
    observations: 500,
    varExceptions: 21,
    expectedExceptions: "25.0",
    kupiecPValue: "0.39",
    christoffersenPValue: "0.28",
    trafficLight: "GREEN",
    breaches: [
      { date: "2026-03-18", return: "-4.7%", varLimit: "-3.8%", severity: "1.24x", documented: true, note: "Energy supply headline shock" },
      { date: "2026-05-04", return: "-4.1%", varLimit: "-3.5%", severity: "1.17x", documented: true, note: "Macro repricing event" },
      { date: "2026-07-21", return: "-5.2%", varLimit: "-4.0%", severity: "1.30x", documented: false, note: "Documentation required" },
    ],
  },
  modelComparison: [
    { id: "M1", model: "Normal EWMA", aic: "3,921", bic: "3,936", outOfSampleLoss: "1.00", varCoverage: "91.8%", tailFit: "WEAK", status: "REJECTED" },
    { id: "M2", model: "GARCH(1,1)-N", aic: "3,742", bic: "3,763", outOfSampleLoss: "0.86", varCoverage: "94.2%", tailFit: "FAIR", status: "CANDIDATE" },
    { id: "M3", model: "GARCH(1,1)-t", aic: "3,695", bic: "3,722", outOfSampleLoss: "0.79", varCoverage: "95.8%", tailFit: "GOOD", status: "CHAMPION" },
    { id: "M4", model: "Regime GARCH-t", aic: "3,681", bic: "3,728", outOfSampleLoss: "0.77", varCoverage: "95.4%", tailFit: "GOOD", status: "CANDIDATE" },
  ],
  thresholds: [
    { id: "TH-VOL", metric: "Annualized volatility", warning: "> 32%", breach: "> 40%", current: "30.5%", status: "NORMAL", documentation: "No action required" },
    { id: "TH-VAR", metric: "1D VaR 95", warning: "> €0.85M", breach: "> €1.10M", current: "€0.91M", status: "WARNING", documentation: "Review hedge ratio in next Treasury meeting" },
    { id: "TH-REG", metric: "High-vol regime probability", warning: "> 55%", breach: "> 75%", current: "59%", status: "WARNING", documentation: "Regime alert recorded; contract pending" },
    { id: "TH-BT", metric: "Undocumented VaR exceptions", warning: "> 0", breach: "> 2", current: "1", status: "WARNING", documentation: "July exception requires owner commentary" },
  ],
};

function context(selection: WorkspaceSelection): MarketRiskSnapshot["context"] {
  return {
    ...selection,
    companyLabel: companyLabels[selection.companyId] ?? selection.companyId,
    periodLabel: periodLabels[selection.periodId] ?? selection.periodId,
    scenarioLabel: scenarioLabels[selection.scenarioId] ?? selection.scenarioId,
    asOf: "2026-08-08T06:15:00+02:00",
  };
}

export function getMockMarketRiskSnapshot(selection: WorkspaceSelection): MarketRiskSnapshot {
  if (selection.scenarioId === "local-downside") {
    return {
      contractStatus: "MOCK_CONNECTED",
      modelLifecycle: "MODEL_CONTRACT_PENDING",
      context: context(selection),
      ...base,
      assets: base.assets.map((asset) => asset.id === "brent" ? { ...asset, annualizedVol: "42.8%", var95: "€1.31M", es95: "€1.82M", status: "STRESS" } : asset),
      regimes: { ...base.regimes, currentState: "HIGH VOL", confidence: "82%", states: [{ ...base.regimes.states[0]!, probability: 0.18 }, { ...base.regimes.states[1]!, probability: 0.82 }] },
      simulation: { ...base.simulation, var95: "€8.9M", es95: "€12.7M" },
      backtest: { ...base.backtest, trafficLight: "YELLOW", varExceptions: 31, kupiecPValue: "0.08" },
      thresholds: base.thresholds.map((threshold) => threshold.id === "TH-VOL" ? { ...threshold, current: "42.8%", status: "BREACH" } : threshold.id === "TH-VAR" ? { ...threshold, current: "€1.31M", status: "BREACH" } : threshold),
    };
  }

  return {
    contractStatus: "MOCK_CONNECTED",
    modelLifecycle: "MODEL_CONTRACT_PENDING",
    context: context(selection),
    ...base,
  };
}
