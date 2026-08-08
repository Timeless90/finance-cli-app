import type {
  LiquiditySnapshot,
  ProfitabilitySnapshot,
  WorkspaceContextSnapshot,
  WorkspaceSelection,
} from "./contracts";

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

function context(selection: WorkspaceSelection): WorkspaceContextSnapshot {
  return {
    ...selection,
    companyLabel: companyLabels[selection.companyId] ?? selection.companyId,
    periodLabel: periodLabels[selection.periodId] ?? selection.periodId,
    scenarioLabel: scenarioLabels[selection.scenarioId] ?? selection.scenarioId,
    asOf: "2026-08-08T06:15:00+02:00",
  };
}

const profitabilityBase: Omit<ProfitabilitySnapshot, "context" | "contractStatus"> = {
  metrics: [
    { id: "cm", label: "CONTRIBUTION MARGIN", value: "€144.6M", delta: "+€5.2M vs plan", deltaTone: "positive", meta: "29.7% of revenue" },
    { id: "ebitda", label: "EBITDA AFTER ALLOCATION", value: "€82.4M", delta: "+€3.9M vs plan", deltaTone: "positive", meta: "allocation v6" },
    { id: "mar", label: "MARGIN AT RISK", value: "€12.8M", delta: "+€1.6M exposure", deltaTone: "negative", meta: "95% confidence" },
    { id: "recon", label: "COST RECONCILIATION", value: "99.98%", delta: "€0.04M open", deltaTone: "neutral", meta: "ABC + driver allocation" },
  ],
  segments: [
    { id: "premium", label: "Premium Systems", revenue: "€168.2M", contributionMargin: "€61.7M", contributionMarginPct: "36.7%", ebitda: "€38.4M", allocatedCost: "€12.9M", marginAtRisk: "€3.1M", status: "STRONG" },
    { id: "core", label: "Core Products", revenue: "€214.6M", contributionMargin: "€58.5M", contributionMarginPct: "27.3%", ebitda: "€31.2M", allocatedCost: "€18.8M", marginAtRisk: "€5.4M", status: "STRONG" },
    { id: "services", label: "Services", revenue: "€71.9M", contributionMargin: "€18.6M", contributionMarginPct: "25.9%", ebitda: "€10.7M", allocatedCost: "€5.2M", marginAtRisk: "€2.6M", status: "WATCH" },
    { id: "legacy", label: "Legacy Portfolio", revenue: "€31.6M", contributionMargin: "€5.8M", contributionMarginPct: "18.4%", ebitda: "€2.1M", allocatedCost: "€3.4M", marginAtRisk: "€1.7M", status: "CRITICAL" },
  ],
  waterfall: [
    { id: "revenue", label: "REVENUE", amount: 486.3, display: "€486.3M", type: "start" },
    { id: "variable", label: "VARIABLE COST", amount: -265.4, display: "-€265.4M", type: "negative" },
    { id: "cm", label: "CONTRIBUTION", amount: 220.9, display: "€220.9M", type: "positive" },
    { id: "direct", label: "DIRECT FIXED", amount: -76.3, display: "-€76.3M", type: "negative" },
    { id: "allocated", label: "ALLOCATED", amount: -62.2, display: "-€62.2M", type: "negative" },
    { id: "ebitda", label: "EBITDA", amount: 82.4, display: "€82.4M", type: "end" },
  ],
  matrix: [
    { id: "m1", product: "PX-900", customer: "Strategic A", channel: "Direct", revenue: "€42.8M", marginPct: "41.2%", marginAtRisk: "€0.8M", status: "STRONG" },
    { id: "m2", product: "PX-700", customer: "Strategic B", channel: "Direct", revenue: "€35.1M", marginPct: "34.8%", marginAtRisk: "€1.1M", status: "STRONG" },
    { id: "m3", product: "CX-400", customer: "Key Accounts", channel: "Partner", revenue: "€61.5M", marginPct: "26.1%", marginAtRisk: "€2.9M", status: "WATCH" },
    { id: "m4", product: "LX-100", customer: "Long Tail", channel: "Distributor", revenue: "€24.9M", marginPct: "15.7%", marginAtRisk: "€2.2M", status: "CRITICAL" },
  ],
  sensitivities: [
    { lever: "Price", movement: "+1.0%", ebitdaImpact: "+€4.9M", marginImpact: "+1.0pp", tone: "positive" },
    { lever: "Volume", movement: "+2.0%", ebitdaImpact: "+€2.8M", marginImpact: "+0.4pp", tone: "positive" },
    { lever: "Variable cost", movement: "+1.0%", ebitdaImpact: "-€2.7M", marginImpact: "-0.6pp", tone: "negative" },
    { lever: "Fixed cost", movement: "+2.0%", ebitdaImpact: "-€1.5M", marginImpact: "-0.3pp", tone: "negative" },
  ],
  allocation: {
    versionId: "alloc-fy26-p08-v6",
    snapshotId: "snap-fy26-p08-t1",
    method: "DRIVER + ABC",
    sourceCost: "€62.24M",
    allocatedCost: "€62.20M",
    reconciliationDifference: "€0.04M",
    reconciled: true,
  },
};

const profitabilityDownside: Omit<ProfitabilitySnapshot, "context" | "contractStatus"> = {
  ...profitabilityBase,
  metrics: [
    { id: "cm", label: "CONTRIBUTION MARGIN", value: "€121.4M", delta: "-€18.0M vs plan", deltaTone: "negative", meta: "26.9% of revenue" },
    { id: "ebitda", label: "EBITDA AFTER ALLOCATION", value: "€68.9M", delta: "-€9.6M vs plan", deltaTone: "negative", meta: "margin defense scenario" },
    { id: "mar", label: "MARGIN AT RISK", value: "€24.7M", delta: "+€13.5M exposure", deltaTone: "negative", meta: "95% confidence" },
    { id: "recon", label: "COST RECONCILIATION", value: "99.98%", delta: "€0.04M open", deltaTone: "neutral", meta: "ABC + driver allocation" },
  ],
  segments: profitabilityBase.segments.map((segment) =>
    segment.id === "legacy"
      ? { ...segment, contributionMarginPct: "11.8%", ebitda: "-€0.9M", marginAtRisk: "€4.1M", status: "CRITICAL" }
      : segment.id === "services"
        ? { ...segment, contributionMarginPct: "20.2%", ebitda: "€6.8M", marginAtRisk: "€5.3M", status: "CRITICAL" }
        : { ...segment, marginAtRisk: segment.id === "premium" ? "€6.4M" : "€8.9M", status: "WATCH" },
  ),
  sensitivities: [
    { lever: "Price recovery", movement: "+1.5%", ebitdaImpact: "+€6.8M", marginImpact: "+1.5pp", tone: "positive" },
    { lever: "Volume loss", movement: "-3.0%", ebitdaImpact: "-€5.4M", marginImpact: "-0.8pp", tone: "negative" },
    { lever: "Energy", movement: "+8.0%", ebitdaImpact: "-€3.6M", marginImpact: "-0.8pp", tone: "negative" },
    { lever: "Fixed cost action", movement: "-4.0%", ebitdaImpact: "+€3.0M", marginImpact: "+0.7pp", tone: "positive" },
  ],
};

const liquidityBase: Omit<LiquiditySnapshot, "context" | "contractStatus"> = {
  metrics: [
    { id: "cash", label: "CLOSING CASH", value: "€36.8M", delta: "+€2.4M vs plan", deltaTone: "positive", meta: "13-week forecast" },
    { id: "headroom", label: "MIN LIQUIDITY HEADROOM", value: "€14.2M", delta: "+€1.7M vs plan", deltaTone: "positive", meta: "lowest weekly point" },
    { id: "wc", label: "NET WORKING CAPITAL", value: "€74.6M", delta: "+€6.1M cash tied", deltaTone: "negative", meta: "DSO/DIO pressure" },
    { id: "covenant", label: "COVENANT HEADROOM", value: "38%", delta: "+7pp vs warning", deltaTone: "positive", meta: "minimum projected" },
  ],
  cashForecast: {
    horizon: "13_WEEK",
    minimumLiquidity: "€20.0M",
    minimumHeadroom: "€14.2M",
    forecastAccuracy: "92.4%",
    points: Array.from({ length: 13 }, (_, index) => {
      const week = index + 1;
      const opening = 31.5 + index * 0.4;
      const inflow = 14.5 + ((index * 7) % 5) * 0.7;
      const outflow = 13.8 + ((index * 5) % 4) * 0.8;
      const closing = opening + inflow - outflow;
      return { period: `W${String(week).padStart(2, "0")}`, opening, inflow, outflow, closing, minimum: 20 };
    }),
  },
  workingCapital: [
    { id: "dso", label: "DSO", current: "48d", target: "45d", cashImpact: "-€3.9M", status: "WATCH" },
    { id: "dio", label: "DIO", current: "63d", target: "58d", cashImpact: "-€4.8M", status: "WATCH" },
    { id: "dpo", label: "DPO", current: "51d", target: "50d", cashImpact: "+€0.9M", status: "ON_TARGET" },
    { id: "ccc", label: "CASH CONVERSION CYCLE", current: "60d", target: "53d", cashImpact: "-€7.8M", status: "WATCH" },
  ],
  debt: [
    { id: "RCF-01", instrument: "Revolving Credit Facility", principal: "€18.0M", rate: "3.85%", maturity: "FY29 P06", committedLimit: "€50.0M", headroom: "€32.0M", status: "NORMAL" },
    { id: "TL-02", instrument: "Term Loan B", principal: "€74.0M", rate: "4.20%", maturity: "FY30 P03", committedLimit: "€74.0M", headroom: "€0.0M", status: "NORMAL" },
    { id: "NOTE-01", instrument: "Private Placement", principal: "€40.0M", rate: "3.55%", maturity: "FY28 P11", committedLimit: "€40.0M", headroom: "€0.0M", status: "WATCH" },
  ],
  covenants: [
    { id: "COV-LEV", metric: "Net leverage", actual: "2.18x", threshold: "<= 3.50x", headroom: "1.32x", projectedMinimum: "0.74x", status: "PASS" },
    { id: "COV-ICR", metric: "Interest cover", actual: "6.4x", threshold: ">= 3.0x", headroom: "3.4x", projectedMinimum: "4.7x", status: "PASS" },
    { id: "COV-LIQ", metric: "Minimum liquidity", actual: "€36.8M", threshold: ">= €20.0M", headroom: "€16.8M", projectedMinimum: "€34.2M", status: "PASS" },
  ],
  stresses: [
    { id: "S-BASE", name: "Baseline", closingCash: "€36.8M", headroom: "€16.8M", breach: false, mitigation: "None" },
    { id: "S-REV", name: "Revenue -10% + DSO delay", closingCash: "€24.9M", headroom: "€4.9M", breach: false, mitigation: "Collections sprint" },
    { id: "S-REFI", name: "Refinancing shock", closingCash: "€21.7M", headroom: "€1.7M", breach: false, mitigation: "RCF draw + capex gate" },
    { id: "S-COMB", name: "Combined downside", closingCash: "€17.6M", headroom: "-€2.4M", breach: true, mitigation: "Spend gate + RCF + WC actions" },
  ],
};

const liquidityDownside: Omit<LiquiditySnapshot, "context" | "contractStatus"> = {
  ...liquidityBase,
  metrics: [
    { id: "cash", label: "CLOSING CASH", value: "€24.6M", delta: "-€9.8M vs plan", deltaTone: "negative", meta: "13-week forecast" },
    { id: "headroom", label: "MIN LIQUIDITY HEADROOM", value: "€5.7M", delta: "-€6.8M vs plan", deltaTone: "negative", meta: "lowest weekly point" },
    { id: "wc", label: "NET WORKING CAPITAL", value: "€88.3M", delta: "+€19.8M cash tied", deltaTone: "negative", meta: "collections + inventory" },
    { id: "covenant", label: "COVENANT HEADROOM", value: "19%", delta: "-12pp vs warning", deltaTone: "negative", meta: "minimum projected" },
  ],
  cashForecast: {
    ...liquidityBase.cashForecast,
    minimumHeadroom: "€5.7M",
    forecastAccuracy: "86.1%",
    points: liquidityBase.cashForecast.points.map((point, index) => ({
      ...point,
      closing: point.closing - index * 0.95,
      inflow: point.inflow - 1.3,
      outflow: point.outflow + 0.6,
    })),
  },
  workingCapital: [
    { id: "dso", label: "DSO", current: "56d", target: "45d", cashImpact: "-€14.2M", status: "BREACH" },
    { id: "dio", label: "DIO", current: "71d", target: "58d", cashImpact: "-€12.1M", status: "BREACH" },
    { id: "dpo", label: "DPO", current: "49d", target: "50d", cashImpact: "-€0.9M", status: "WATCH" },
    { id: "ccc", label: "CASH CONVERSION CYCLE", current: "78d", target: "53d", cashImpact: "-€27.2M", status: "BREACH" },
  ],
  covenants: [
    { id: "COV-LEV", metric: "Net leverage", actual: "2.88x", threshold: "<= 3.50x", headroom: "0.62x", projectedMinimum: "0.18x", status: "WATCH" },
    { id: "COV-ICR", metric: "Interest cover", actual: "4.1x", threshold: ">= 3.0x", headroom: "1.1x", projectedMinimum: "3.2x", status: "WATCH" },
    { id: "COV-LIQ", metric: "Minimum liquidity", actual: "€24.6M", threshold: ">= €20.0M", headroom: "€4.6M", projectedMinimum: "€25.7M", status: "WATCH" },
  ],
  stresses: [
    { id: "S-BASE", name: "Downside baseline", closingCash: "€24.6M", headroom: "€4.6M", breach: false, mitigation: "Weekly cash governance" },
    { id: "S-REV", name: "Revenue -10% + DSO delay", closingCash: "€15.8M", headroom: "-€4.2M", breach: true, mitigation: "RCF + collections sprint" },
    { id: "S-REFI", name: "Refinancing shock", closingCash: "€13.1M", headroom: "-€6.9M", breach: true, mitigation: "RCF + capex freeze" },
    { id: "S-COMB", name: "Combined downside", closingCash: "€7.4M", headroom: "-€12.6M", breach: true, mitigation: "Emergency liquidity plan" },
  ],
};

export function getMockProfitabilitySnapshot(selection: WorkspaceSelection): ProfitabilitySnapshot {
  const preset = selection.scenarioId === "local-downside" ? profitabilityDownside : profitabilityBase;
  return { contractStatus: "MOCK_CONNECTED", context: context(selection), ...preset };
}

export function getMockLiquiditySnapshot(selection: WorkspaceSelection): LiquiditySnapshot {
  const preset = selection.scenarioId === "local-downside" ? liquidityDownside : liquidityBase;
  return { contractStatus: "MOCK_CONNECTED", context: context(selection), ...preset };
}
