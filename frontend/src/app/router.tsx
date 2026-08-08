import { Navigate, createBrowserRouter } from "react-router-dom";

import { App } from "@/app/App";
import { AppShell } from "@/components/layout";
import { WorkspacePlaceholder } from "@/pages/WorkspacePlaceholder";

const workspaceRoutes = [
  "command-center",
  "planning",
  "performance",
  "profitability",
  "liquidity",
  "risk",
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
      ...workspaceRoutes,
    ],
  },
]);
