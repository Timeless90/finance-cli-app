import "@testing-library/jest-dom/vitest";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { companies, periods, scenarios, WorkspaceContext, type WorkspaceContextValue } from "@/app/context/workspace-context";
import { ActionsPage } from "@/pages/ActionsPage";
import { CapitalPage } from "@/pages/CapitalPage";

function renderWorkspace(page: "actions" | "capital", scenarioId = "local-base") {
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
  const Page = page === "actions" ? ActionsPage : CapitalPage;
  return render(
    <QueryClientProvider client={queryClient}>
      <WorkspaceContext.Provider value={context}>
        <MemoryRouter><Page /></MemoryRouter>
      </WorkspaceContext.Provider>
    </QueryClientProvider>,
  );
}

describe("FE-10 Action Steering & Capital Allocation", () => {
  it("renders action lifecycle and realized benefits", async () => {
    renderWorkspace("actions");
    expect(await screen.findByRole("heading", { name: "Action Steering" })).toBeInTheDocument();
    expect(screen.getByText("ACT-042")).toBeInTheDocument();
    expect(screen.getByText("Accelerate price corridor update")).toBeInTheDocument();
    expect(screen.getByText("72%")).toBeInTheDocument();
  });

  it("shows defensive capital constraint breach in downside", async () => {
    renderWorkspace("capital", "local-downside");
    expect(await screen.findByRole("heading", { name: "Capital Allocation" })).toBeInTheDocument();
    expect(screen.getByText("€27.8M")).toBeInTheDocument();
    expect(screen.getByText("-€14.3M")).toBeInTheDocument();
    expect(screen.getAllByText("DEFERRED").length).toBeGreaterThanOrEqual(2);
  });
});
