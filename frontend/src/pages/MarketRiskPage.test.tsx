import "@testing-library/jest-dom/vitest";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { companies, periods, scenarios, WorkspaceContext, type WorkspaceContextValue } from "@/app/context/workspace-context";
import { MarketRiskPage } from "@/pages/MarketRiskPage";

function renderLab(scenarioId = "local-base") {
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

  return render(
    <QueryClientProvider client={queryClient}>
      <WorkspaceContext.Provider value={context}>
        <MemoryRouter>
          <MarketRiskPage />
        </MemoryRouter>
      </WorkspaceContext.Provider>
    </QueryClientProvider>,
  );
}

describe("FE-09 Market Risk Lab", () => {
  it("renders model diagnostics and explicit pending contracts", async () => {
    renderLab();

    expect(await screen.findByRole("heading", { name: "Market Risk Lab" })).toBeInTheDocument();
    expect(screen.getByText("garch-brent-fy26-p08-v1")).toBeInTheDocument();
    expect(screen.getByText("GARCH(1,1)-t", { exact: true })).toBeInTheDocument();
    expect(screen.getByText("Regime GARCH-t")).toBeInTheDocument();
    expect(screen.getByText("ACTION REQUIRED")).toBeInTheDocument();
    expect(screen.getAllByText(/MODEL CONTRACT PENDING/).length).toBeGreaterThanOrEqual(4);
  });

  it("escalates volatility and simulation risk in downside context", async () => {
    renderLab("local-downside");

    expect(await screen.findAllByText("42.8%", { exact: true })).toHaveLength(2);
    expect(screen.getByText("€8.9M", { exact: true })).toBeInTheDocument();
    expect(screen.getByText("€12.7M", { exact: true })).toBeInTheDocument();
    expect(screen.getAllByText("82%", { exact: true })).toHaveLength(2);
    expect(screen.getByText("YELLOW", { exact: true })).toBeInTheDocument();
  });
});
