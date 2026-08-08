export type WorkspaceSelection = {
  companyId: string;
  periodId: string;
  scenarioId: string;
};

export type SteeringTone = "positive" | "warning" | "negative" | "neutral";

export type ManagementAction = {
  id: string;
  title: string;
  source: string;
  owner: string;
  sponsor: string;
  due: string;
  status: "PROPOSED" | "APPROVED" | "IN_EXECUTION" | "AT_RISK" | "COMPLETED";
  priority: "P0" | "P1" | "P2";
  confidence: string;
  expectedEbitda: string;
  expectedCash: string;
  realizedEbitda: string;
  realizedCash: string;
  realizationPct: string;
  riskReduction: string;
  evidence: string;
  nextGate: string;
};

export type CapitalCandidate = {
  id: string;
  name: string;
  category: string;
  sponsor: string;
  capitalRequired: string;
  npv: string;
  irr: string;
  payback: string;
  riskAdjustedScore: number;
  strategicFit: number;
  liquidityImpact: string;
  downsideLoss: string;
  status: "PROPOSED" | "SCREENED" | "APPROVED" | "DEFERRED" | "REJECTED";
};

export type ActionCapitalSnapshot = {
  contractStatus: "MOCK_CONNECTED";
  context: WorkspaceSelection & {
    companyLabel: string;
    periodLabel: string;
    scenarioLabel: string;
    asOf: string;
  };
  actions: {
    metrics: Array<{
      id: string;
      label: string;
      value: string;
      delta: string;
      deltaTone: SteeringTone;
      meta: string;
    }>;
    queue: ManagementAction[];
    benefitTrend: Array<{
      period: string;
      expected: number;
      realized: number;
    }>;
    statusMix: Array<{
      status: ManagementAction["status"];
      count: number;
    }>;
    dependencies: Array<{
      actionId: string;
      dependsOn: string;
      type: "BLOCKING" | "ENABLING";
    }>;
  };
  capital: {
    budget: string;
    committed: string;
    approved: string;
    unallocated: string;
    liquidityReserve: string;
    expectedPortfolioNpv: string;
    downsideCapitalAtRisk: string;
    candidates: CapitalCandidate[];
    frontier: Array<{
      id: string;
      label: string;
      risk: number;
      return: number;
      selected: boolean;
    }>;
    constraints: Array<{
      id: string;
      label: string;
      limit: string;
      used: string;
      headroom: string;
      status: "PASS" | "WATCH" | "BREACH";
    }>;
    allocation: Array<{
      category: string;
      amount: string;
      share: number;
      expectedNpv: string;
    }>;
    approvals: Array<{
      id: string;
      candidateId: string;
      gate: string;
      owner: string;
      status: "PENDING" | "APPROVED" | "REJECTED";
      due: string;
    }>;
  };
};
