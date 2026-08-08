import { Navigate, createBrowserRouter } from "react-router-dom";

import { App } from "@/app/App";
import { AppShell } from "@/components/layout";
import { CommandCenterPage } from "@/pages/CommandCenterPage";
import { LiquidityPage } from "@/pages/LiquidityPage";
import { PerformancePage } from "@/pages/PerformancePage";
import { PlanningPage } from "@/pages/PlanningPage";
import { ProfitabilityPage } from "@/pages/ProfitabilityPage";
import { RiskPage } from "@/pages/RiskPage";
import { WorkspacePlaceholder } from "@/pages/WorkspacePlaceholder";

const workspaceRoutes = [
  "market-risk",
  "actions",
  "capital",
  "reports",
  "copilot",
  "data",
  "governance",
].map((path) => ({ path, element: <WorkspacePlaceholder /> }));

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    path: "/app",
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate replace to="command-center" /> },
      { path: "command-center", element: <CommandCenterPage /> },
      { path: "planning", element: <PlanningPage /> },
      { path: "performance", element: <PerformancePage /> },
      { path: "profitability", element: <ProfitabilityPage /> },
      { path: "liquidity", element: <LiquidityPage /> },
      { path: "risk", element: <RiskPage /> },
      ...workspaceRoutes,
    ],
  },
]);
