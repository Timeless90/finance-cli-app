import "@testing-library/jest-dom/vitest";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { companies, periods, scenarios, WorkspaceContext, type WorkspaceContextValue } from "@/app/context/workspace-context";
import { LiquidityPage } from "@/pages/LiquidityPage";
import { ProfitabilityPage } from "@/pages/ProfitabilityPage";

function renderWorkspace(page: "profitability" | "liquidity", scenarioId = "local-base") {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const context: WorkspaceContextValue = {
    companies,
    periods,
    scenarios,
    companyId: "local-holding",
    periodId: "local-fy26-p08",
    scenarioId,
    setCompanyId: () => undefined,
    setPeriodId: () => undefined,
    setScenarioId: () => undefined,
  };
  const Page = page === "profitability" ? ProfitabilityPage : LiquidityPage;

  return render(
    <QueryClientProvider client={queryClient}>
      <WorkspaceContext.Provider value={context}>
        <MemoryRouter>
          <Page />
        </MemoryRouter>
      </WorkspaceContext.Provider>
    </QueryClientProvider>,
  );
}

describe("FE-07 Profitability & Liquidity", () => {
  it("renders reconciled profitability and segment economics", async () => {
    renderWorkspace("profitability");

    expect(await screen.findByRole("heading", { name: "Profitability" })).toBeInTheDocument();
    expect(screen.getByText("alloc-fy26-p08-v6")).toBeInTheDocument();
    expect(screen.getByText("Premium Systems")).toBeInTheDocument();
    expect(screen.getByText("99.98%")).toBeInTheDocument();
  });

  it("renders downside liquidity breaches from scenario context", async () => {
    renderWorkspace("liquidity", "local-downside");

    expect(await screen.findByRole("heading", { name: "Liquidity" })).toBeInTheDocument();
    expect(screen.getAllByText("€24.6M")).toHaveLength(3);
    expect(screen.getByText("78d")).toBeInTheDocument();
    expect(screen.getByText(/Emergency liquidity plan/i)).toBeInTheDocument();
  });
});
