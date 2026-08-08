import type {
  PerformanceSnapshot,
  PlanningSnapshot,
  WorkspaceSelection,
} from "./contracts";

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

function context(selection: WorkspaceSelection): PlanningSnapshot["context"] {
  return {
    ...selection,
    companyLabel: companies[selection.companyId] ?? selection.companyId,
    periodLabel: periods[selection.periodId] ?? selection.periodId,
    scenarioLabel: scenarios[selection.scenarioId] ?? selection.scenarioId,
    asOf: "2026-08-08T06:15:00+02:00",
  };
}

const scenarioCards: PlanningSnapshot["scenarios"] = [
  {
    id: "local-base",
    label: "Operating Base",
    type: "BASE",
    status: "ACTIVE",
    revenue: "€486.3M",
    ebitda: "€82.4M",
    freeCashFlow: "€41.7M",
    owner: "Group FP&A",
  },
  {
    id: "local-upside",
    label: "Commercial Upside",
    type: "UPSIDE",
    status: "APPROVED",
    revenue: "€503.8M",
    ebitda: "€89.6M",
    freeCashFlow: "€49.9M",
    owner: "Group FP&A",
  },
  {
    id: "local-downside",
    label: "Margin Defense",
    type: "DOWNSIDE",
    status: "APPROVED",
    revenue: "€451.7M",
    ebitda: "€68.9M",
    freeCashFlow: "€24.3M",
    owner: "Group FP&A",
  },
];

const planningPresets: Record<
  string,
  Pick<PlanningSnapshot, "activeScenario" | "forecast" | "statement" | "drivers" | "thresholds">
> = {
  "local-base": {
    activeScenario: {
      id: "local-base",
      label: "Operating Base",
      versionId: "fcst-fy26-p08-base-v4",
      snapshotId: "snap-fy26-p08-t1",
      assumptionSetId: "asm-fy26-p08-base-v3",
      modelVersion: "planning-core-2.4.1",
      status: "APPROVED",
    },
    forecast: {
      kpi: "EBITDA",
      unit: "EUR_M",
      horizon: "P09-P12",
      confidence: "82%",
      mape: "4.6%",
      bias: "+0.8%",
      points: [
        { period: "P03", actual: 11.8, plan: 11.5, forecast: 11.8, lower: 11.8, upper: 11.8 },
        { period: "P04", actual: 12.6, plan: 12.2, forecast: 12.6, lower: 12.6, upper: 12.6 },
        { period: "P05", actual: 13.4, plan: 13.0, forecast: 13.4, lower: 13.4, upper: 13.4 },
        { period: "P06", actual: 14.1, plan: 13.8, forecast: 14.1, lower: 14.1, upper: 14.1 },
        { period: "P07", actual: 14.7, plan: 14.4, forecast: 14.7, lower: 14.7, upper: 14.7 },
        { period: "P08", actual: 15.2, plan: 14.9, forecast: 15.2, lower: 15.2, upper: 15.2 },
        { period: "P09", plan: 15.3, forecast: 15.8, lower: 14.9, upper: 16.5 },
        { period: "P10", plan: 15.8, forecast: 16.4, lower: 14.6, upper: 17.6 },
        { period: "P11", plan: 16.2, forecast: 17.1, lower: 14.2, upper: 18.7 },
        { period: "P12", plan: 16.6, forecast: 18.0, lower: 13.8, upper: 20.1 },
      ],
    },
    statement: [
      { id: "rev", label: "Revenue", level: 0, actual: "€322.6M", plan: "€316.1M", forecast: "€486.3M", variance: "+€6.5M", varianceTone: "positive" },
      { id: "cogs", label: "Cost of goods sold", level: 1, actual: "-€207.8M", plan: "-€205.4M", forecast: "-€312.5M", variance: "-€2.4M", varianceTone: "negative" },
      { id: "gp", label: "Gross profit", level: 0, actual: "€114.8M", plan: "€110.7M", forecast: "€173.8M", variance: "+€4.1M", varianceTone: "positive" },
      { id: "opex", label: "Operating expenses", level: 1, actual: "-€61.7M", plan: "-€60.9M", forecast: "-€91.4M", variance: "-€0.8M", varianceTone: "negative" },
      { id: "ebitda", label: "EBITDA", level: 0, actual: "€53.1M", plan: "€49.8M", forecast: "€82.4M", variance: "+€3.3M", varianceTone: "positive" },
      { id: "da", label: "D&A", level: 1, actual: "-€14.2M", plan: "-€14.0M", forecast: "-€21.5M", variance: "-€0.2M", varianceTone: "negative" },
      { id: "ebit", label: "EBIT", level: 0, actual: "€38.9M", plan: "€35.8M", forecast: "€60.9M", variance: "+€3.1M", varianceTone: "positive" },
      { id: "ni", label: "Net income", level: 0, actual: "€24.7M", plan: "€22.8M", forecast: "€38.4M", variance: "+€1.9M", varianceTone: "positive" },
    ],
    drivers: [
      { id: "volume", label: "Volume growth", value: "+3.7", unit: "%", delta: "+0.9pp", owner: "Commercial Finance", status: "LOCKED" },
      { id: "price", label: "Price / mix", value: "+2.1", unit: "%", delta: "+0.4pp", owner: "Commercial Finance", status: "LOCKED" },
      { id: "dso", label: "DSO", value: "48", unit: "days", delta: "+3d", owner: "Working Capital", status: "REVIEW" },
      { id: "inventory", label: "Inventory days", value: "63", unit: "days", delta: "+5d", owner: "Supply Chain", status: "REVIEW" },
      { id: "capex", label: "Capex envelope", value: "31.2", unit: "€M", delta: "+€1.4M", owner: "Investment Control", status: "OPEN" },
      { id: "energy", label: "Energy index", value: "112", unit: "idx", delta: "+8pts", owner: "Procurement", status: "REVIEW" },
    ],
    thresholds: [
      { kpi: "EBITDA margin", target: ">= 16.5%", warning: "< 15.5%", current: "16.9%", status: "ON_TARGET" },
      { kpi: "Free cash flow", target: ">= €40M", warning: "< €32M", current: "€41.7M", status: "ON_TARGET" },
      { kpi: "DSO", target: "<= 45d", warning: "> 50d", current: "48d", status: "WARNING" },
    ],
  },
  "local-upside": {
    activeScenario: {
      id: "local-upside",
      label: "Commercial Upside",
      versionId: "fcst-fy26-p08-upside-v2",
      snapshotId: "snap-fy26-p08-t1",
      assumptionSetId: "asm-fy26-p08-upside-v2",
      modelVersion: "planning-core-2.4.1",
      status: "APPROVED",
    },
    forecast: {
      kpi: "EBITDA", unit: "EUR_M", horizon: "P09-P12", confidence: "76%", mape: "5.1%", bias: "+1.4%",
      points: [
        { period: "P03", actual: 11.8, plan: 11.5, forecast: 11.8, lower: 11.8, upper: 11.8 },
        { period: "P04", actual: 12.6, plan: 12.2, forecast: 12.6, lower: 12.6, upper: 12.6 },
        { period: "P05", actual: 13.4, plan: 13.0, forecast: 13.4, lower: 13.4, upper: 13.4 },
        { period: "P06", actual: 14.1, plan: 13.8, forecast: 14.1, lower: 14.1, upper: 14.1 },
        { period: "P07", actual: 14.7, plan: 14.4, forecast: 14.7, lower: 14.7, upper: 14.7 },
        { period: "P08", actual: 15.2, plan: 14.9, forecast: 15.2, lower: 15.2, upper: 15.2 },
        { period: "P09", plan: 15.3, forecast: 16.5, lower: 15.3, upper: 17.4 },
        { period: "P10", plan: 15.8, forecast: 17.6, lower: 15.5, upper: 18.9 },
        { period: "P11", plan: 16.2, forecast: 18.7, lower: 15.8, upper: 20.4 },
        { period: "P12", plan: 16.6, forecast: 20.1, lower: 16.0, upper: 22.5 },
      ],
    },
    statement: [
      { id: "rev", label: "Revenue", level: 0, actual: "€322.6M", plan: "€316.1M", forecast: "€503.8M", variance: "+€6.5M", varianceTone: "positive" },
      { id: "gp", label: "Gross profit", level: 0, actual: "€114.8M", plan: "€110.7M", forecast: "€182.1M", variance: "+€4.1M", varianceTone: "positive" },
      { id: "ebitda", label: "EBITDA", level: 0, actual: "€53.1M", plan: "€49.8M", forecast: "€89.6M", variance: "+€3.3M", varianceTone: "positive" },
      { id: "ni", label: "Net income", level: 0, actual: "€24.7M", plan: "€22.8M", forecast: "€43.9M", variance: "+€1.9M", varianceTone: "positive" },
    ],
    drivers: [
      { id: "volume", label: "Volume growth", value: "+5.9", unit: "%", delta: "+3.1pp", owner: "Commercial Finance", status: "LOCKED" },
      { id: "price", label: "Price / mix", value: "+2.8", unit: "%", delta: "+1.1pp", owner: "Commercial Finance", status: "LOCKED" },
      { id: "dso", label: "DSO", value: "45", unit: "days", delta: "0d", owner: "Working Capital", status: "LOCKED" },
      { id: "capex", label: "Capex envelope", value: "34.0", unit: "€M", delta: "+€4.2M", owner: "Investment Control", status: "OPEN" },
    ],
    thresholds: [
      { kpi: "EBITDA margin", target: ">= 16.5%", warning: "< 15.5%", current: "17.8%", status: "ON_TARGET" },
      { kpi: "Free cash flow", target: ">= €40M", warning: "< €32M", current: "€49.9M", status: "ON_TARGET" },
      { kpi: "DSO", target: "<= 45d", warning: "> 50d", current: "45d", status: "ON_TARGET" },
    ],
  },
  "local-downside": {
    activeScenario: {
      id: "local-downside",
      label: "Margin Defense",
      versionId: "fcst-fy26-p08-downside-v3",
      snapshotId: "snap-fy26-p08-t1",
      assumptionSetId: "asm-fy26-p08-downside-v3",
      modelVersion: "planning-core-2.4.1",
      status: "APPROVED",
    },
    forecast: {
      kpi: "EBITDA", unit: "EUR_M", horizon: "P09-P12", confidence: "71%", mape: "6.3%", bias: "-2.2%",
      points: [
        { period: "P03", actual: 11.8, plan: 11.5, forecast: 11.8, lower: 11.8, upper: 11.8 },
        { period: "P04", actual: 12.6, plan: 12.2, forecast: 12.6, lower: 12.6, upper: 12.6 },
        { period: "P05", actual: 13.4, plan: 13.0, forecast: 13.4, lower: 13.4, upper: 13.4 },
        { period: "P06", actual: 14.1, plan: 13.8, forecast: 14.1, lower: 14.1, upper: 14.1 },
        { period: "P07", actual: 14.7, plan: 14.4, forecast: 14.7, lower: 14.7, upper: 14.7 },
        { period: "P08", actual: 15.2, plan: 14.9, forecast: 15.2, lower: 15.2, upper: 15.2 },
        { period: "P09", plan: 15.3, forecast: 14.9, lower: 13.7, upper: 15.8 },
        { period: "P10", plan: 15.8, forecast: 14.6, lower: 12.8, upper: 15.8 },
        { period: "P11", plan: 16.2, forecast: 14.2, lower: 11.9, upper: 15.7 },
        { period: "P12", plan: 16.6, forecast: 13.8, lower: 10.9, upper: 15.5 },
      ],
    },
    statement: [
      { id: "rev", label: "Revenue", level: 0, actual: "€322.6M", plan: "€316.1M", forecast: "€451.7M", variance: "+€6.5M", varianceTone: "positive" },
      { id: "gp", label: "Gross profit", level: 0, actual: "€114.8M", plan: "€110.7M", forecast: "€151.2M", variance: "+€4.1M", varianceTone: "positive" },
      { id: "ebitda", label: "EBITDA", level: 0, actual: "€53.1M", plan: "€49.8M", forecast: "€68.9M", variance: "+€3.3M", varianceTone: "positive" },
      { id: "ni", label: "Net income", level: 0, actual: "€24.7M", plan: "€22.8M", forecast: "€27.1M", variance: "+€1.9M", varianceTone: "positive" },
    ],
    drivers: [
      { id: "volume", label: "Volume growth", value: "-1.8", unit: "%", delta: "-4.6pp", owner: "Commercial Finance", status: "REVIEW" },
      { id: "price", label: "Price / mix", value: "+1.2", unit: "%", delta: "-0.5pp", owner: "Commercial Finance", status: "REVIEW" },
      { id: "dso", label: "DSO", value: "56", unit: "days", delta: "+11d", owner: "Working Capital", status: "REVIEW" },
      { id: "inventory", label: "Inventory days", value: "71", unit: "days", delta: "+13d", owner: "Supply Chain", status: "REVIEW" },
      { id: "capex", label: "Capex envelope", value: "22.4", unit: "€M", delta: "-€7.4M", owner: "Investment Control", status: "OPEN" },
    ],
    thresholds: [
      { kpi: "EBITDA margin", target: ">= 16.5%", warning: "< 15.5%", current: "15.3%", status: "BREACH" },
      { kpi: "Free cash flow", target: ">= €40M", warning: "< €32M", current: "€24.3M", status: "BREACH" },
      { kpi: "DSO", target: "<= 45d", warning: "> 50d", current: "56d", status: "BREACH" },
    ],
  },
};

const performancePresets: Record<string, Omit<PerformanceSnapshot, "context" | "contractStatus">> = {
  "local-base": {
    metrics: [
      { id: "rev-growth", label: "REVENUE GROWTH", value: "+5.1%", delta: "+1.3pp vs plan", deltaTone: "positive", meta: "organic / YTD" },
      { id: "ebitda-margin", label: "EBITDA MARGIN", value: "16.5%", delta: "+0.7pp vs plan", deltaTone: "positive", meta: "P08 YTD" },
      { id: "cash-conv", label: "CASH CONVERSION", value: "78.5%", delta: "-4.2pp vs plan", deltaTone: "negative", meta: "EBITDA to FCF" },
      { id: "roe", label: "ROIC", value: "12.8%", delta: "+0.9pp vs plan", deltaTone: "positive", meta: "LTM" },
    ],
    kpiTree: [
      { id: "ebitda", label: "EBITDA", value: "€53.1M", variance: "+€3.3M", tone: "positive" },
      { id: "gross-profit", parentId: "ebitda", label: "Gross Profit", value: "€114.8M", variance: "+€4.1M", tone: "positive" },
      { id: "opex", parentId: "ebitda", label: "OPEX", value: "-€61.7M", variance: "-€0.8M", tone: "negative" },
      { id: "revenue", parentId: "gross-profit", label: "Revenue", value: "€322.6M", variance: "+€6.5M", tone: "positive" },
      { id: "cogs", parentId: "gross-profit", label: "COGS", value: "-€207.8M", variance: "-€2.4M", tone: "negative" },
    ],
    varianceBridge: {
      kpi: "EBITDA", comparison: "ACTUAL_VS_PLAN", baseline: "€49.8M", actual: "€53.1M", explained: "€3.3M", unexplained: "€0.0M", fullyExplained: true,
      steps: [
        { id: "plan", label: "PLAN", amount: 49.8, display: "€49.8M", type: "start" },
        { id: "volume", label: "VOLUME", amount: 5.6, display: "+€5.6M", type: "positive" },
        { id: "price", label: "PRICE / MIX", amount: 3.1, display: "+€3.1M", type: "positive" },
        { id: "energy", label: "ENERGY", amount: -2.4, display: "-€2.4M", type: "negative" },
        { id: "people", label: "PERSONNEL", amount: -1.1, display: "-€1.1M", type: "negative" },
        { id: "other", label: "OTHER", amount: -1.9, display: "-€1.9M", type: "negative" },
        { id: "actual", label: "ACTUAL", amount: 53.1, display: "€53.1M", type: "end" },
      ],
    },
    trend: {
      kpi: "EBITDA_MARGIN", unit: "PERCENT",
      points: [
        { period: "P03", actual: 15.2, plan: 14.9, forecast: 15.1 },
        { period: "P04", actual: 15.5, plan: 15.0, forecast: 15.4 },
        { period: "P05", actual: 15.8, plan: 15.2, forecast: 15.7 },
        { period: "P06", actual: 16.0, plan: 15.4, forecast: 16.0 },
        { period: "P07", actual: 16.3, plan: 15.6, forecast: 16.2 },
        { period: "P08", actual: 16.5, plan: 15.8, forecast: 16.5 },
      ],
    },
    anomalies: [
      { id: "AN-014", period: "P08", kpi: "DSO", observation: "+3.8σ above rolling median", severity: "HIGH", status: "OPEN" },
      { id: "AN-011", period: "P07", kpi: "Energy / unit", observation: "+2.9σ vs normalized corridor", severity: "MEDIUM", status: "REVIEWED" },
    ],
    commentary: [
      { id: "COM-041", kpi: "Free cash flow", variance: "-€2.1M", threshold: "€1.0M", status: "REQUIRED", owner: "Working Capital" },
      { id: "COM-038", kpi: "EBITDA", variance: "+€3.3M", threshold: "€2.0M", status: "COMPLETE", owner: "Group FP&A" },
      { id: "COM-035", kpi: "Revenue", variance: "+€6.5M", threshold: "€5.0M", status: "COMPLETE", owner: "Commercial Finance" },
    ],
  },
  "local-upside": {
    metrics: [
      { id: "rev-growth", label: "REVENUE GROWTH", value: "+8.5%", delta: "+4.7pp vs plan", deltaTone: "positive", meta: "scenario outlook" },
      { id: "ebitda-margin", label: "EBITDA MARGIN", value: "17.8%", delta: "+2.0pp vs plan", deltaTone: "positive", meta: "FY26 outlook" },
      { id: "cash-conv", label: "CASH CONVERSION", value: "83.2%", delta: "+0.5pp vs plan", deltaTone: "positive", meta: "EBITDA to FCF" },
      { id: "roe", label: "ROIC", value: "14.1%", delta: "+2.2pp vs plan", deltaTone: "positive", meta: "scenario outlook" },
    ],
    kpiTree: [
      { id: "ebitda", label: "EBITDA", value: "€89.6M", variance: "+€11.1M", tone: "positive" },
      { id: "gross-profit", parentId: "ebitda", label: "Gross Profit", value: "€182.1M", variance: "+€12.8M", tone: "positive" },
      { id: "opex", parentId: "ebitda", label: "OPEX", value: "-€92.5M", variance: "-€1.7M", tone: "negative" },
      { id: "revenue", parentId: "gross-profit", label: "Revenue", value: "€503.8M", variance: "+€17.5M", tone: "positive" },
    ],
    varianceBridge: {
      kpi: "EBITDA", comparison: "ACTUAL_VS_PLAN", baseline: "€78.5M", actual: "€89.6M", explained: "€11.1M", unexplained: "€0.0M", fullyExplained: true,
      steps: [
        { id: "plan", label: "PLAN", amount: 78.5, display: "€78.5M", type: "start" },
        { id: "volume", label: "VOLUME", amount: 8.4, display: "+€8.4M", type: "positive" },
        { id: "price", label: "PRICE / MIX", amount: 5.0, display: "+€5.0M", type: "positive" },
        { id: "cost", label: "COST", amount: -2.3, display: "-€2.3M", type: "negative" },
        { id: "actual", label: "OUTLOOK", amount: 89.6, display: "€89.6M", type: "end" },
      ],
    },
    trend: { kpi: "EBITDA_MARGIN", unit: "PERCENT", points: [
      { period: "P08", actual: 16.5, plan: 15.8, forecast: 16.5 },
      { period: "P09", actual: 16.5, plan: 15.9, forecast: 16.9 },
      { period: "P10", actual: 16.5, plan: 16.0, forecast: 17.2 },
      { period: "P11", actual: 16.5, plan: 16.1, forecast: 17.5 },
      { period: "P12", actual: 16.5, plan: 16.2, forecast: 17.8 },
    ] },
    anomalies: [
      { id: "AN-021", period: "P09", kpi: "Volume", observation: "+3.2σ above historical growth corridor", severity: "MEDIUM", status: "OPEN" },
    ],
    commentary: [
      { id: "COM-051", kpi: "EBITDA", variance: "+€11.1M", threshold: "€2.0M", status: "REQUIRED", owner: "Group FP&A" },
      { id: "COM-052", kpi: "Revenue", variance: "+€17.5M", threshold: "€5.0M", status: "REQUIRED", owner: "Commercial Finance" },
    ],
  },
  "local-downside": {
    metrics: [
      { id: "rev-growth", label: "REVENUE GROWTH", value: "-2.6%", delta: "-6.4pp vs plan", deltaTone: "negative", meta: "scenario outlook" },
      { id: "ebitda-margin", label: "EBITDA MARGIN", value: "15.3%", delta: "-0.9pp vs plan", deltaTone: "negative", meta: "FY26 outlook" },
      { id: "cash-conv", label: "CASH CONVERSION", value: "58.1%", delta: "-24.6pp vs plan", deltaTone: "negative", meta: "EBITDA to FCF" },
      { id: "roe", label: "ROIC", value: "8.7%", delta: "-3.2pp vs plan", deltaTone: "negative", meta: "scenario outlook" },
    ],
    kpiTree: [
      { id: "ebitda", label: "EBITDA", value: "€68.9M", variance: "-€9.6M", tone: "negative" },
      { id: "gross-profit", parentId: "ebitda", label: "Gross Profit", value: "€151.2M", variance: "-€18.1M", tone: "negative" },
      { id: "opex", parentId: "ebitda", label: "OPEX", value: "-€82.3M", variance: "+€8.5M", tone: "positive" },
      { id: "revenue", parentId: "gross-profit", label: "Revenue", value: "€451.7M", variance: "-€34.6M", tone: "negative" },
    ],
    varianceBridge: {
      kpi: "EBITDA", comparison: "ACTUAL_VS_PLAN", baseline: "€78.5M", actual: "€68.9M", explained: "-€9.6M", unexplained: "€0.0M", fullyExplained: true,
      steps: [
        { id: "plan", label: "PLAN", amount: 78.5, display: "€78.5M", type: "start" },
        { id: "volume", label: "VOLUME", amount: -7.2, display: "-€7.2M", type: "negative" },
        { id: "price", label: "PRICE / MIX", amount: 2.2, display: "+€2.2M", type: "positive" },
        { id: "energy", label: "ENERGY", amount: -3.6, display: "-€3.6M", type: "negative" },
        { id: "other", label: "OTHER", amount: -1.0, display: "-€1.0M", type: "negative" },
        { id: "actual", label: "OUTLOOK", amount: 68.9, display: "€68.9M", type: "end" },
      ],
    },
    trend: { kpi: "EBITDA_MARGIN", unit: "PERCENT", points: [
      { period: "P08", actual: 16.5, plan: 15.8, forecast: 16.5 },
      { period: "P09", actual: 16.5, plan: 15.9, forecast: 15.9 },
      { period: "P10", actual: 16.5, plan: 16.0, forecast: 15.6 },
      { period: "P11", actual: 16.5, plan: 16.1, forecast: 15.4 },
      { period: "P12", actual: 16.5, plan: 16.2, forecast: 15.3 },
    ] },
    anomalies: [
      { id: "AN-031", period: "P09", kpi: "Volume", observation: "-4.1σ below historical demand corridor", severity: "HIGH", status: "OPEN" },
      { id: "AN-032", period: "P09", kpi: "DSO", observation: "+4.5σ above rolling median", severity: "HIGH", status: "OPEN" },
      { id: "AN-033", period: "P10", kpi: "Energy / unit", observation: "+3.7σ above normalized corridor", severity: "HIGH", status: "OPEN" },
    ],
    commentary: [
      { id: "COM-061", kpi: "EBITDA", variance: "-€9.6M", threshold: "€2.0M", status: "REQUIRED", owner: "Group FP&A" },
      { id: "COM-062", kpi: "Free cash flow", variance: "-€19.5M", threshold: "€1.0M", status: "REQUIRED", owner: "Working Capital" },
      { id: "COM-063", kpi: "Revenue", variance: "-€34.6M", threshold: "€5.0M", status: "REQUIRED", owner: "Commercial Finance" },
    ],
  },
};

export function getMockPlanningSnapshot(selection: WorkspaceSelection): PlanningSnapshot {
  const preset = planningPresets[selection.scenarioId] ?? planningPresets["local-base"]!;
  return { contractStatus: "MOCK_CONNECTED", context: context(selection), scenarios: scenarioCards, ...preset };
}

export function getMockPerformanceSnapshot(selection: WorkspaceSelection): PerformanceSnapshot {
  const preset = performancePresets[selection.scenarioId] ?? performancePresets["local-base"]!;
  return { contractStatus: "MOCK_CONNECTED", context: context(selection), ...preset };
}
