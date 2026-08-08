export type WorkspaceNavItem = {
  code: string;
  label: string;
  path: string;
  description: string;
  group: "steer" | "decide" | "system";
};

export const workspaceNavigation: WorkspaceNavItem[] = [
  {
    code: "01",
    label: "Command Center",
    path: "/app/command-center",
    description: "Executive finance, liquidity, risk and action overview.",
    group: "steer",
  },
  {
    code: "02",
    label: "Planning",
    path: "/app/planning",
    description: "Integrated planning, rolling forecast and scenarios.",
    group: "steer",
  },
  {
    code: "03",
    label: "Performance",
    path: "/app/performance",
    description: "KPI steering, variance analysis and forecast accuracy.",
    group: "steer",
  },
  {
    code: "04",
    label: "Profitability",
    path: "/app/profitability",
    description: "Margin, contribution and profitability analysis.",
    group: "steer",
  },
  {
    code: "05",
    label: "Liquidity",
    path: "/app/liquidity",
    description: "Cash, working capital, debt and covenant control.",
    group: "steer",
  },
  {
    code: "06",
    label: "Enterprise Risk",
    path: "/app/risk",
    description: "Risk register, aggregation, appetite and Risk-to-Plan.",
    group: "decide",
  },
  {
    code: "07",
    label: "Treasury Risk",
    path: "/app/market-risk",
    description: "Market exposure, VaR, stress and hedge analytics.",
    group: "decide",
  },
  {
    code: "08",
    label: "Actions",
    path: "/app/actions",
    description: "Management actions, ownership and benefit tracking.",
    group: "decide",
  },
  {
    code: "09",
    label: "Capital",
    path: "/app/capital",
    description: "Capital allocation, project valuation and funding.",
    group: "decide",
  },
  {
    code: "10",
    label: "Reporting",
    path: "/app/reports",
    description: "Governed management, board and external reporting.",
    group: "decide",
  },
  {
    code: "11",
    label: "Finance Copilot",
    path: "/app/copilot",
    description: "Grounded AI interpretation across finance workloads.",
    group: "decide",
  },
  {
    code: "12",
    label: "Data",
    path: "/app/data",
    description: "Imports, mappings, snapshots and data quality.",
    group: "system",
  },
  {
    code: "13",
    label: "Governance",
    path: "/app/governance",
    description: "Runs, scenarios, models, approvals and lineage.",
    group: "system",
  },
];

export function getWorkspaceByPath(pathname: string) {
  return workspaceNavigation.find((item) => pathname === item.path);
}
