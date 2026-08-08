import "@testing-library/jest-dom/vitest";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { companies, periods, scenarios, WorkspaceContext, type WorkspaceContextValue } from "@/app/context/workspace-context";
import { RiskPage } from "@/pages/RiskPage";

function renderRisk(scenarioId = "local-base") {
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
          <RiskPage />
        </MemoryRouter>
      </WorkspaceContext.Provider>
    </QueryClientProvider>,
  );
}

describe("FE-08 Risk Command Center", () => {
  it("renders the enterprise risk portfolio and model boundaries", async () => {
    renderRisk();

    expect(await screen.findByRole("heading", { name: "Risk Command Center" })).toBeInTheDocument();
    expect(screen.getByText("€19.8M")).toBeInTheDocument();
    expect(screen.getByText("Energy cost escalation")).toBeInTheDocument();
    expect(screen.getAllByText("MODEL CONTRACT PENDING")).toHaveLength(2);
    expect(screen.getByText("LATE-CYCLE / PRESSURE")).toBeInTheDocument();
  });

  it("raises portfolio exposure and risk breaches in downside context", async () => {
    renderRisk("local-downside");

    expect(await screen.findByText("€36.7M")).toBeInTheDocument();
    expect(screen.getByText("Combined downside")).toBeInTheDocument();
    expect(screen.getByText("112%", { exact: false })).toBeInTheDocument();
    expect(screen.getAllByText(/BREACHED/)).toHaveLength(2);
  });
});
