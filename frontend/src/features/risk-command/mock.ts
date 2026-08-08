import type { RiskCommandSnapshot, WorkspaceSelection } from "./contracts";

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

const baseRisks: RiskCommandSnapshot["risks"] = [
  { id: "R-017", title: "Energy cost escalation", category: "Market", owner: "COO", probability: 0.62, impact: 0.78, expectedLoss: "€2.9M", p95Loss: "€8.4M", residualLoss: "€2.1M", mitigationEffect: "€0.8M", appetiteUsage: "74%", status: "WARNING", trend: "UP" },
  { id: "R-009", title: "DACH volume softness", category: "Strategic", owner: "CCO", probability: 0.54, impact: 0.72, expectedLoss: "€2.1M", p95Loss: "€6.5M", residualLoss: "€1.8M", mitigationEffect: "€0.3M", appetiteUsage: "67%", status: "WARNING", trend: "STABLE" },
  { id: "R-024", title: "FX translation pressure", category: "Financial", owner: "Treasury", probability: 0.46, impact: 0.55, expectedLoss: "€1.2M", p95Loss: "€3.8M", residualLoss: "€0.9M", mitigationEffect: "€0.3M", appetiteUsage: "48%", status: "HEALTHY", trend: "DOWN" },
  { id: "R-031", title: "Supplier concentration", category: "Operational", owner: "Procurement", probability: 0.31, impact: 0.76, expectedLoss: "€1.0M", p95Loss: "€5.1M", residualLoss: "€0.8M", mitigationEffect: "€0.2M", appetiteUsage: "52%", status: "HEALTHY", trend: "STABLE" },
  { id: "R-038", title: "Cyber service disruption", category: "Cyber", owner: "CIO", probability: 0.18, impact: 0.92, expectedLoss: "€0.8M", p95Loss: "€7.6M", residualLoss: "€0.6M", mitigationEffect: "€0.2M", appetiteUsage: "61%", status: "WARNING", trend: "UP" },
  { id: "R-044", title: "Liquidity refinancing spread", category: "Liquidity", owner: "CFO", probability: 0.24, impact: 0.66, expectedLoss: "€0.7M", p95Loss: "€2.9M", residualLoss: "€0.5M", mitigationEffect: "€0.2M", appetiteUsage: "43%", status: "HEALTHY", trend: "STABLE" },
];

const categories: RiskCommandSnapshot["categories"] = [
  { id: "strategic", label: "Strategic", grossExposure: 72, residualExposure: 58, appetite: 62, tone: "warning" },
  { id: "market", label: "Market", grossExposure: 84, residualExposure: 71, appetite: 60, tone: "negative" },
  { id: "financial", label: "Financial", grossExposure: 51, residualExposure: 39, appetite: 58, tone: "positive" },
  { id: "operational", label: "Operational", grossExposure: 63, residualExposure: 49, appetite: 60, tone: "positive" },
  { id: "cyber", label: "Cyber", grossExposure: 78, residualExposure: 61, appetite: 55, tone: "warning" },
  { id: "liquidity", label: "Liquidity", grossExposure: 47, residualExposure: 35, appetite: 55, tone: "positive" },
];

const distribution: RiskCommandSnapshot["portfolio"]["distribution"] = [
  { percentile: 5, loss: 0.8 }, { percentile: 10, loss: 1.2 }, { percentile: 20, loss: 2.0 }, { percentile: 30, loss: 2.8 },
  { percentile: 40, loss: 3.7 }, { percentile: 50, loss: 4.6 }, { percentile: 60, loss: 5.5 }, { percentile: 70, loss: 6.7 },
  { percentile: 80, loss: 8.2 }, { percentile: 90, loss: 11.7 }, { percentile: 95, loss: 15.4 }, { percentile: 97.5, loss: 18.8 },
  { percentile: 99, loss: 23.6 }, { percentile: 99.5, loss: 27.9 },
];

const base: Omit<RiskCommandSnapshot, "context" | "contractStatus"> = {
  portfolio: {
    meanGrossLoss: "€9.4M", meanNetLoss: "€6.7M", p50NetLoss: "€4.6M", p95NetLoss: "€15.4M", p99NetLoss: "€23.6M", expectedShortfall95: "€19.8M", appetiteUsage: "61%", paths: "10,000", seed: "42", distribution,
  },
  risks: baseRisks,
  categories,
  radar: categories.map((item) => ({ dimension: item.label, exposure: item.residualExposure, appetite: item.appetite })),
  correlation: {
    labels: ["Energy", "Volume", "FX", "Supplier", "Cyber", "Liquidity"],
    matrix: [
      [1, 0.28, 0.34, 0.12, 0.05, 0.18],
      [0.28, 1, 0.22, 0.31, 0.04, 0.29],
      [0.34, 0.22, 1, 0.08, 0.02, 0.41],
      [0.12, 0.31, 0.08, 1, 0.09, 0.16],
      [0.05, 0.04, 0.02, 0.09, 1, 0.11],
      [0.18, 0.29, 0.41, 0.16, 0.11, 1],
    ],
  },
  regimes: {
    lifecycle: "MODEL_CONTRACT_PENDING",
    currentState: "LATE-CYCLE / PRESSURE",
    stateConfidence: "68%",
    states: [
      { id: "S1", label: "Expansion", probability: 0.12, expectedLossMultiplier: "0.72x" },
      { id: "S2", label: "Normal", probability: 0.36, expectedLossMultiplier: "1.00x" },
      { id: "S3", label: "Pressure", probability: 0.38, expectedLossMultiplier: "1.42x" },
      { id: "S4", label: "Stress", probability: 0.14, expectedLossMultiplier: "2.35x" },
    ],
    transitionMatrix: [
      [0.68, 0.25, 0.06, 0.01],
      [0.14, 0.62, 0.21, 0.03],
      [0.03, 0.22, 0.61, 0.14],
      [0.01, 0.08, 0.31, 0.60],
    ],
  },
  tail: {
    lifecycle: "MODEL_CONTRACT_PENDING",
    threshold: "€11.7M / P90",
    shape: "ξ = 0.21",
    scale: "β = €4.8M",
    expectedShortfall: "€19.8M",
    qq: [
      { theoretical: 0.5, observed: 0.6 }, { theoretical: 1.1, observed: 1.0 }, { theoretical: 1.8, observed: 1.9 },
      { theoretical: 2.7, observed: 2.6 }, { theoretical: 3.9, observed: 4.2 }, { theoretical: 5.4, observed: 5.9 },
      { theoretical: 7.2, observed: 8.0 }, { theoretical: 9.6, observed: 11.1 }, { theoretical: 12.8, observed: 15.4 },
    ],
  },
  scenario: {
    name: "Energy + demand compression",
    description: "Simultaneous energy escalation, DACH volume softness and FX translation pressure.",
    earningsAtRisk: "€13.8M EBITDA",
    cashAtRisk: "€10.6M FCF",
    probability: "17%",
    topDrivers: ["Energy +14%", "DACH volume -6%", "EUR/USD -5%"],
  },
  controls: [
    { id: "CTL-17-A", riskId: "R-017", name: "Energy hedge ladder", owner: "Treasury", effectiveness: "38%", annualCost: "€0.42M", avoidedLoss: "€0.8M", status: "ACTIVE" },
    { id: "CTL-09-A", riskId: "R-009", name: "Pricing and demand trigger", owner: "Commercial Finance", effectiveness: "17%", annualCost: "€0.08M", avoidedLoss: "€0.3M", status: "ACTIVE" },
    { id: "CTL-38-A", riskId: "R-038", name: "Resilience failover", owner: "CIO", effectiveness: "29%", annualCost: "€0.31M", avoidedLoss: "€0.2M", status: "ACTIVE" },
    { id: "CTL-31-B", riskId: "R-031", name: "Dual-source qualification", owner: "Procurement", effectiveness: "24%", annualCost: "€0.16M", avoidedLoss: "€0.2M", status: "PLANNED" },
  ],
};

function context(selection: WorkspaceSelection): RiskCommandSnapshot["context"] {
  return {
    ...selection,
    companyLabel: companyLabels[selection.companyId] ?? selection.companyId,
    periodLabel: periodLabels[selection.periodId] ?? selection.periodId,
    scenarioLabel: scenarioLabels[selection.scenarioId] ?? selection.scenarioId,
    asOf: "2026-08-08T06:15:00+02:00",
  };
}

export function getMockRiskCommandSnapshot(selection: WorkspaceSelection): RiskCommandSnapshot {
  if (selection.scenarioId === "local-downside") {
    return {
      contractStatus: "MOCK_CONNECTED",
      context: context(selection),
      ...base,
      portfolio: { ...base.portfolio, meanNetLoss: "€11.7M", p50NetLoss: "€8.9M", p95NetLoss: "€28.6M", p99NetLoss: "€43.9M", expectedShortfall95: "€36.7M", appetiteUsage: "88%" },
      risks: base.risks.map((risk) => ({ ...risk, probability: Math.min(0.95, risk.probability + 0.12), appetiteUsage: risk.id === "R-017" ? "112%" : risk.id === "R-009" ? "104%" : risk.appetiteUsage, status: risk.id === "R-017" || risk.id === "R-009" ? "BREACHED" : risk.status })),
      scenario: { ...base.scenario, name: "Combined downside", earningsAtRisk: "€24.9M EBITDA", cashAtRisk: "€22.1M FCF", probability: "29%" },
    };
  }
  if (selection.scenarioId === "local-upside") {
    return {
      contractStatus: "MOCK_CONNECTED",
      context: context(selection),
      ...base,
      portfolio: { ...base.portfolio, meanNetLoss: "€5.1M", p50NetLoss: "€3.5M", p95NetLoss: "€11.9M", p99NetLoss: "€18.2M", expectedShortfall95: "€15.6M", appetiteUsage: "49%" },
      scenario: { ...base.scenario, name: "Protected upside", earningsAtRisk: "€9.1M EBITDA", cashAtRisk: "€6.8M FCF", probability: "11%" },
    };
  }
  return { contractStatus: "MOCK_CONNECTED", context: context(selection), ...base };
}
