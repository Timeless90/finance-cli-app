import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  redirect,
} from '@tanstack/react-router';
import { App } from '@/app/App';
import { AppShell } from '@/app/layout';
import { ActionsPage } from '@/features/action-capital/ActionsPage';
import { CapitalPage } from '@/features/action-capital/CapitalPage';
import { CommandCenterPage } from '@/features/command-center/CommandCenterPage';
import { CopilotPage } from '@/features/reporting-copilot/CopilotPage';
import { DataGovernancePage } from '@/features/data-governance/DataGovernancePage';
import { LiquidityPage } from '@/features/profitability-liquidity/LiquidityPage';
import { MarketRiskPage } from '@/features/market-risk/MarketRiskPage';
import { PerformancePage } from '@/features/planning-performance/PerformancePage';
import { PlanningPage } from '@/features/planning-performance/PlanningPage';
import { ProfitabilityPage } from '@/features/profitability-liquidity/ProfitabilityPage';
import { RiskPage } from '@/features/risk-command/RiskPage';
import { ReportsPage } from '@/features/reporting-copilot/ReportsPage';
const rootRoute = createRootRoute({ component: Outlet });
const landingRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: App,
});
const appRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/app',
  component: AppShell,
});
const indexRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/',
  beforeLoad: () => {
    throw redirect({ to: '/app/command-center' });
  },
});
const children = [
  createRoute({
    getParentRoute: () => appRoute,
    path: 'command-center',
    component: CommandCenterPage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'planning',
    component: PlanningPage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'performance',
    component: PerformancePage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'profitability',
    component: ProfitabilityPage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'liquidity',
    component: LiquidityPage,
  }),
  createRoute({ getParentRoute: () => appRoute, path: 'risk', component: RiskPage }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'market-risk',
    component: MarketRiskPage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'actions',
    component: ActionsPage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'capital',
    component: CapitalPage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'reports',
    component: ReportsPage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'copilot',
    component: CopilotPage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'data',
    component: DataGovernancePage,
  }),
  createRoute({
    getParentRoute: () => appRoute,
    path: 'governance',
    component: DataGovernancePage,
  }),
];
export const router = createRouter({
  routeTree: rootRoute.addChildren([
    landingRoute,
    appRoute.addChildren([indexRoute, ...children]),
  ]),
});
