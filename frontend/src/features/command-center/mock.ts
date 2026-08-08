import type { CommandCenterContext, CommandCenterSnapshot } from "./contracts";

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

const baseSnapshot: Omit<CommandCenterSnapshot, "context"> = {
  contractStatus: "MOCK_CONNECTED",
  source: "frontend-fixture",
  metrics: [
    {
      id: "revenue",
      label: "REVENUE",
      value: "€486.3M",
      delta: "+4.8% vs plan",
      deltaTone: "positive",
      meta: "FY26 rolling outlook",
    },
    {
      id: "ebitda",
      label: "EBITDA",
      value: "€82.4M",
      delta: "+€3.9M vs plan",
      deltaTone: "positive",
      meta: "16.9% margin",
    },
    {
      id: "fcf",
      label: "FREE CASH FLOW",
      value: "€41.7M",
      delta: "-€2.1M vs plan",
      deltaTone: "negative",
      meta: "working capital drag",
    },
    {
      id: "risk",
      label: "RISK-ADJUSTED EBITDA",
      value: "€75.8M",
      delta: "€6.6M expected loss",
      deltaTone: "negative",
      meta: "enterprise risk overlay",
    },
  ],
  forecast: {
    title: "EBITDA trajectory",
    subtitle: "Actual + scenario corridor // €M",
    points: [
      { period: "P03", actual: 11.8, base: 11.8, upside: 11.8, downside: 11.8 },
      { period: "P04", actual: 12.6, base: 12.6, upside: 12.6, downside: 12.6 },
      { period: "P05", actual: 13.4, base: 13.4, upside: 13.4, downside: 13.4 },
      { period: "P06", actual: 14.1, base: 14.1, upside: 14.1, downside: 14.1 },
      { period: "P07", actual: 14.7, base: 14.7, upside: 14.7, downside: 14.7 },
      { period: "P08", actual: 15.2, base: 15.2, upside: 15.2, downside: 15.2 },
      { period: "P09", base: 15.8, upside: 16.5, downside: 14.9 },
      { period: "P10", base: 16.4, upside: 17.6, downside: 14.6 },
      { period: "P11", base: 17.1, upside: 18.7, downside: 14.2 },
      { period: "P12", base: 18.0, upside: 20.1, downside: 13.8 },
    ],
  },
  liquidity: {
    cash: "€36.8M",
    runway: "17.4 months",
    minimumHeadroom: "€14.2M",
    covenantHeadroom: "38%",
    tone: "positive",
  },
  risk: {
    score: "42 / 100",
    expectedLoss: "€6.6M",
    tailLoss: "€18.9M",
    appetiteUsage: "61%",
    signals: [
      {
        id: "R-017",
        title: "Energy cost escalation",
        owner: "COO",
        exposure: "€5.8M",
        severity: "HIGH",
        trend: "UP",
      },
      {
        id: "R-009",
        title: "DACH volume softness",
        owner: "CCO",
        exposure: "€4.1M",
        severity: "HIGH",
        trend: "STABLE",
      },
      {
        id: "R-024",
        title: "FX translation pressure",
        owner: "Treasury",
        exposure: "€2.7M",
        severity: "MEDIUM",
        trend: "DOWN",
      },
    ],
  },
  varianceDrivers: [
    { label: "Volume", amount: "+€5.6M", share: "46%", tone: "positive" },
    { label: "Price / mix", amount: "+€3.1M", share: "25%", tone: "positive" },
    { label: "Energy", amount: "-€2.4M", share: "20%", tone: "negative" },
    { label: "Personnel", amount: "-€1.1M", share: "9%", tone: "negative" },
  ],
  actions: [
    {
      id: "ACT-042",
      title: "Accelerate price corridor update",
      owner: "Commercial Finance",
      due: "P09 W2",
      status: "ON TRACK",
      impact: "+€2.8M EBITDA",
      confidence: "84%",
    },
    {
      id: "ACT-036",
      title: "Energy hedge extension",
      owner: "Treasury",
      due: "P09 W1",
      status: "AT RISK",
      impact: "€1.6M downside protected",
      confidence: "71%",
    },
    {
      id: "ACT-051",
      title: "Reduce slow-moving inventory",
      owner: "Supply Chain",
      due: "P10 W1",
      status: "ON TRACK",
      impact: "+€3.4M cash",
      confidence: "79%",
    },
  ],
  briefing: {
    headline: "Growth remains ahead of plan, but cash conversion needs intervention.",
    summary:
      "Volume and price/mix are supporting EBITDA above plan. Energy exposure and slower inventory rotation are consuming part of the upside and reducing free cash flow conversion. Liquidity remains above internal thresholds.",
    decisions: [
      "Approve the P09 price corridor update for DACH and Benelux.",
      "Extend energy hedge coverage before the next procurement window.",
      "Escalate inventory reduction plan to weekly working-capital review.",
    ],
  },
  assurance: {
    dataFreshness: "T-1 / 06:15 CET",
    coverage: "98.7%",
    modelStatus: "VALIDATED",
    lineageStatus: "TRACEABLE",
  },
};

const scenarioOverrides: Record<
  string,
  Pick<CommandCenterSnapshot, "metrics" | "liquidity" | "risk" | "briefing">
> = {
  "local-base": {
    metrics: baseSnapshot.metrics,
    liquidity: baseSnapshot.liquidity,
    risk: baseSnapshot.risk,
    briefing: baseSnapshot.briefing,
  },
  "local-upside": {
    metrics: [
      { ...baseSnapshot.metrics[0]!, value: "€503.8M", delta: "+8.5% vs plan" },
      { ...baseSnapshot.metrics[1]!, value: "€89.6M", delta: "+€11.1M vs plan" },
      { ...baseSnapshot.metrics[2]!, value: "€49.9M", delta: "+€6.1M vs plan", deltaTone: "positive" },
      { ...baseSnapshot.metrics[3]!, value: "€84.5M", delta: "€5.1M expected loss" },
    ],
    liquidity: {
      cash: "€44.1M",
      runway: "20.8 months",
      minimumHeadroom: "€21.5M",
      covenantHeadroom: "46%",
      tone: "positive",
    },
    risk: {
      ...baseSnapshot.risk,
      score: "34 / 100",
      expectedLoss: "€5.1M",
      tailLoss: "€15.2M",
      appetiteUsage: "49%",
    },
    briefing: {
      headline: "Upside conversion is credible if commercial execution stays on cadence.",
      summary:
        "Higher volume retention and favorable mix improve EBITDA and free cash flow. Risk appetite usage falls, leaving capacity for selective growth initiatives without weakening the liquidity envelope.",
      decisions: [
        "Protect the current price discipline while selectively funding growth capacity.",
        "Keep energy hedge extension as a protection action rather than an earnings lever.",
        "Prioritize projects with cash payback inside twelve months.",
      ],
    },
  },
  "local-downside": {
    metrics: [
      { ...baseSnapshot.metrics[0]!, value: "€451.7M", delta: "-2.6% vs plan", deltaTone: "negative" },
      { ...baseSnapshot.metrics[1]!, value: "€68.9M", delta: "-€9.6M vs plan", deltaTone: "negative" },
      { ...baseSnapshot.metrics[2]!, value: "€24.3M", delta: "-€19.5M vs plan", deltaTone: "negative" },
      { ...baseSnapshot.metrics[3]!, value: "€57.2M", delta: "€11.7M expected loss", deltaTone: "negative" },
    ],
    liquidity: {
      cash: "€24.6M",
      runway: "11.2 months",
      minimumHeadroom: "€5.7M",
      covenantHeadroom: "19%",
      tone: "warning",
    },
    risk: {
      ...baseSnapshot.risk,
      score: "67 / 100",
      expectedLoss: "€11.7M",
      tailLoss: "€31.4M",
      appetiteUsage: "88%",
    },
    briefing: {
      headline: "Downside scenario requires immediate margin and cash protection.",
      summary:
        "Volume weakness and energy pressure compress EBITDA while inventory and collections reduce liquidity headroom. Risk appetite approaches the warning boundary and management actions should be accelerated.",
      decisions: [
        "Trigger discretionary spend containment for P09 and P10.",
        "Increase weekly cash governance and working-capital escalation.",
        "Re-prioritize the action portfolio toward liquidity protection and margin defense.",
      ],
    },
  },
};

export function getMockCommandCenterSnapshot(context: CommandCenterContext): CommandCenterSnapshot {
  const scenario = scenarioOverrides[context.scenarioId] ?? scenarioOverrides["local-base"]!;

  return {
    ...baseSnapshot,
    ...scenario,
    context: {
      ...context,
      companyLabel: companyLabels[context.companyId] ?? context.companyId,
      periodLabel: periodLabels[context.periodId] ?? context.periodId,
      scenarioLabel: scenarioLabels[context.scenarioId] ?? context.scenarioId,
      currency: "EUR",
      asOf: "2026-08-08T06:15:00+02:00",
    },
  };
}
