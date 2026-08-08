import type { ActionCapitalSnapshot, WorkspaceSelection } from "./contracts";

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

const baseActions: ActionCapitalSnapshot["actions"] = {
  metrics: [
    { id: "impact", label: "EXPECTED EBITDA IMPACT", value: "+€14.8M", delta: "+€2.1M vs prior gate", deltaTone: "positive", meta: "approved + executing" },
    { id: "cash", label: "EXPECTED CASH IMPACT", value: "+€18.3M", delta: "+€3.4M vs prior gate", deltaTone: "positive", meta: "12-month effect" },
    { id: "realization", label: "BENEFIT REALIZATION", value: "72%", delta: "+6pp vs P07", deltaTone: "positive", meta: "realized / expected YTD" },
    { id: "atrisk", label: "VALUE AT RISK", value: "€4.6M", delta: "3 actions at risk", deltaTone: "negative", meta: "execution confidence overlay" },
  ],
  queue: [
    { id: "ACT-042", title: "Accelerate price corridor update", source: "Performance / DACH", owner: "Commercial Finance", sponsor: "CCO", due: "P09 W2", status: "IN_EXECUTION", priority: "P0", confidence: "84%", expectedEbitda: "+€2.8M", expectedCash: "+€2.2M", realizedEbitda: "+€1.7M", realizedCash: "+€1.3M", realizationPct: "61%", riskReduction: "€0.9M", evidence: "Pricing wave 2 approved", nextGate: "P09 W1 review" },
    { id: "ACT-036", title: "Extend energy hedge ladder", source: "Risk R-017", owner: "Treasury", sponsor: "CFO", due: "P09 W1", status: "AT_RISK", priority: "P0", confidence: "71%", expectedEbitda: "+€1.6M", expectedCash: "+€1.4M", realizedEbitda: "+€0.4M", realizedCash: "+€0.3M", realizationPct: "25%", riskReduction: "€2.1M", evidence: "Counterparty capacity pending", nextGate: "CFO approval" },
    { id: "ACT-051", title: "Reduce slow-moving inventory", source: "Liquidity / DIO", owner: "Supply Chain", sponsor: "COO", due: "P10 W1", status: "IN_EXECUTION", priority: "P1", confidence: "79%", expectedEbitda: "+€0.7M", expectedCash: "+€3.4M", realizedEbitda: "+€0.2M", realizedCash: "+€1.6M", realizationPct: "47%", riskReduction: "€0.6M", evidence: "SKU disposal list locked", nextGate: "Weekly WC review" },
    { id: "ACT-058", title: "Freeze discretionary spend pool", source: "Planning / Downside", owner: "Group FP&A", sponsor: "CFO", due: "P09 W1", status: "APPROVED", priority: "P0", confidence: "91%", expectedEbitda: "+€3.1M", expectedCash: "+€3.1M", realizedEbitda: "€0.0M", realizedCash: "€0.0M", realizationPct: "0%", riskReduction: "€1.3M", evidence: "Budget owners notified", nextGate: "Execution launch" },
    { id: "ACT-061", title: "Supplier dual-source qualification", source: "Risk R-031", owner: "Procurement", sponsor: "COO", due: "P11 W2", status: "PROPOSED", priority: "P1", confidence: "66%", expectedEbitda: "+€0.5M", expectedCash: "+€0.1M", realizedEbitda: "€0.0M", realizedCash: "€0.0M", realizationPct: "0%", riskReduction: "€1.9M", evidence: "Business case drafted", nextGate: "Risk committee" },
    { id: "ACT-029", title: "Service contract repricing", source: "Profitability / Services", owner: "Service Finance", sponsor: "CCO", due: "P08 W4", status: "COMPLETED", priority: "P2", confidence: "96%", expectedEbitda: "+€1.2M", expectedCash: "+€0.9M", realizedEbitda: "+€1.3M", realizedCash: "+€1.0M", realizationPct: "108%", riskReduction: "€0.2M", evidence: "Contracts live", nextGate: "Benefits closeout" },
  ],
  benefitTrend: [
    { period: "P03", expected: 1.1, realized: 0.7 }, { period: "P04", expected: 2.0, realized: 1.3 },
    { period: "P05", expected: 3.2, realized: 2.1 }, { period: "P06", expected: 5.0, realized: 3.6 },
    { period: "P07", expected: 7.3, realized: 5.1 }, { period: "P08", expected: 9.4, realized: 6.8 },
    { period: "P09", expected: 11.8, realized: 8.6 }, { period: "P10", expected: 14.8, realized: 10.7 },
  ],
  statusMix: [
    { status: "PROPOSED", count: 4 }, { status: "APPROVED", count: 3 }, { status: "IN_EXECUTION", count: 8 }, { status: "AT_RISK", count: 3 }, { status: "COMPLETED", count: 12 },
  ],
  dependencies: [
    { actionId: "ACT-042", dependsOn: "ACT-036", type: "ENABLING" },
    { actionId: "ACT-051", dependsOn: "ACT-058", type: "BLOCKING" },
    { actionId: "ACT-061", dependsOn: "ACT-036", type: "ENABLING" },
  ],
};

const baseCapital: ActionCapitalSnapshot["capital"] = {
  budget: "€96.0M",
  committed: "€58.4M",
  approved: "€18.6M",
  unallocated: "€19.0M",
  liquidityReserve: "€12.0M",
  expectedPortfolioNpv: "€74.8M",
  downsideCapitalAtRisk: "€16.2M",
  candidates: [
    { id: "INV-104", name: "Digital pricing platform", category: "Digital", sponsor: "CCO", capitalRequired: "€8.4M", npv: "€19.6M", irr: "31%", payback: "2.1y", riskAdjustedScore: 86, strategicFit: 92, liquidityImpact: "-€5.1M Y1", downsideLoss: "€3.2M", status: "APPROVED" },
    { id: "INV-118", name: "Energy efficiency retrofit", category: "Operations", sponsor: "COO", capitalRequired: "€12.7M", npv: "€17.2M", irr: "22%", payback: "3.4y", riskAdjustedScore: 82, strategicFit: 88, liquidityImpact: "-€8.8M Y1", downsideLoss: "€2.6M", status: "SCREENED" },
    { id: "INV-126", name: "Benelux capacity expansion", category: "Growth", sponsor: "CCO", capitalRequired: "€21.0M", npv: "€28.4M", irr: "24%", payback: "3.7y", riskAdjustedScore: 75, strategicFit: 90, liquidityImpact: "-€14.5M Y1", downsideLoss: "€8.9M", status: "SCREENED" },
    { id: "INV-131", name: "Cyber resilience uplift", category: "Resilience", sponsor: "CIO", capitalRequired: "€6.8M", npv: "€8.1M", irr: "18%", payback: "4.2y", riskAdjustedScore: 79, strategicFit: 84, liquidityImpact: "-€4.9M Y1", downsideLoss: "€1.7M", status: "APPROVED" },
    { id: "INV-139", name: "Legacy portfolio automation", category: "Productivity", sponsor: "COO", capitalRequired: "€9.6M", npv: "€7.4M", irr: "14%", payback: "5.1y", riskAdjustedScore: 58, strategicFit: 61, liquidityImpact: "-€6.1M Y1", downsideLoss: "€4.8M", status: "DEFERRED" },
    { id: "INV-145", name: "Service acquisition option", category: "M&A", sponsor: "CEO", capitalRequired: "€32.0M", npv: "€31.5M", irr: "19%", payback: "4.8y", riskAdjustedScore: 63, strategicFit: 78, liquidityImpact: "-€24.0M close", downsideLoss: "€14.2M", status: "PROPOSED" },
  ],
  frontier: [
    { id: "P1", label: "Liquidity first", risk: 18, return: 42, selected: false },
    { id: "P2", label: "Balanced", risk: 31, return: 67, selected: true },
    { id: "P3", label: "Growth tilt", risk: 47, return: 81, selected: false },
    { id: "P4", label: "Maximum NPV", risk: 66, return: 92, selected: false },
  ],
  constraints: [
    { id: "CAP-BUD", label: "Annual capital budget", limit: "€96.0M", used: "€77.0M", headroom: "€19.0M", status: "PASS" },
    { id: "CAP-LIQ", label: "Minimum liquidity reserve", limit: ">= €12.0M", used: "€14.2M", headroom: "€2.2M", status: "WATCH" },
    { id: "CAP-LEV", label: "Net leverage ceiling", limit: "<= 2.75x", used: "2.42x", headroom: "0.33x", status: "PASS" },
    { id: "CAP-GRO", label: "Growth concentration", limit: "<= 45%", used: "38%", headroom: "7pp", status: "PASS" },
  ],
  allocation: [
    { category: "Growth", amount: "€29.4M", share: 38, expectedNpv: "€39.6M" },
    { category: "Resilience", amount: "€18.2M", share: 24, expectedNpv: "€14.7M" },
    { category: "Digital", amount: "€16.8M", share: 22, expectedNpv: "€26.3M" },
    { category: "Productivity", amount: "€12.6M", share: 16, expectedNpv: "€9.8M" },
  ],
  approvals: [
    { id: "APR-221", candidateId: "INV-118", gate: "Investment Committee", owner: "CFO", status: "PENDING", due: "P09 W1" },
    { id: "APR-224", candidateId: "INV-126", gate: "Executive Board", owner: "CEO", status: "PENDING", due: "P09 W2" },
    { id: "APR-209", candidateId: "INV-104", gate: "Investment Committee", owner: "CFO", status: "APPROVED", due: "P08 W3" },
    { id: "APR-213", candidateId: "INV-131", gate: "Risk Committee", owner: "CRO", status: "APPROVED", due: "P08 W4" },
  ],
};

function context(selection: WorkspaceSelection): ActionCapitalSnapshot["context"] {
  return {
    ...selection,
    companyLabel: companies[selection.companyId] ?? selection.companyId,
    periodLabel: periods[selection.periodId] ?? selection.periodId,
    scenarioLabel: scenarios[selection.scenarioId] ?? selection.scenarioId,
    asOf: "2026-08-08T06:15:00+02:00",
  };
}

export function getMockActionCapitalSnapshot(selection: WorkspaceSelection): ActionCapitalSnapshot {
  if (selection.scenarioId === "local-downside") {
    return {
      contractStatus: "MOCK_CONNECTED",
      context: context(selection),
      actions: {
        ...baseActions,
        metrics: [
          { id: "impact", label: "EXPECTED EBITDA IMPACT", value: "+€18.9M", delta: "+€6.2M protection", deltaTone: "positive", meta: "defensive portfolio" },
          { id: "cash", label: "EXPECTED CASH IMPACT", value: "+€26.4M", delta: "+€11.5M protection", deltaTone: "positive", meta: "liquidity actions" },
          { id: "realization", label: "BENEFIT REALIZATION", value: "58%", delta: "-8pp vs base", deltaTone: "negative", meta: "execution pressure" },
          { id: "atrisk", label: "VALUE AT RISK", value: "€9.8M", delta: "6 actions at risk", deltaTone: "negative", meta: "confidence overlay" },
        ],
        queue: baseActions.queue.map((action) => action.id === "ACT-036" || action.id === "ACT-051" ? { ...action, status: "AT_RISK" as const, confidence: action.id === "ACT-036" ? "54%" : "61%" } : action),
      },
      capital: {
        ...baseCapital,
        unallocated: "€9.0M",
        liquidityReserve: "€20.0M",
        expectedPortfolioNpv: "€61.7M",
        downsideCapitalAtRisk: "€27.8M",
        constraints: baseCapital.constraints.map((constraint) => constraint.id === "CAP-LIQ" ? { ...constraint, limit: ">= €20.0M", used: "€5.7M", headroom: "-€14.3M", status: "BREACH" as const } : constraint),
        candidates: baseCapital.candidates.map((candidate) => candidate.id === "INV-126" || candidate.id === "INV-145" ? { ...candidate, status: "DEFERRED" as const } : candidate),
      },
    };
  }

  return { contractStatus: "MOCK_CONNECTED", context: context(selection), actions: baseActions, capital: baseCapital };
}
