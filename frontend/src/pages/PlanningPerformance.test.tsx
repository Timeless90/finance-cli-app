import "@testing-library/jest-dom/vitest";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { companies, periods, scenarios, WorkspaceContext, type WorkspaceContextValue } from "@/app/context/workspace-context";
import { PerformancePage } from "@/pages/PerformancePage";
import { PlanningPage } from "@/pages/PlanningPage";

function renderWorkspace(page: "planning" | "performance", scenarioId = "local-base") {
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
  const Page = page === "planning" ? PlanningPage : PerformancePage;

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

describe("FE-06 Planning & Performance", () => {
  it("renders versioned planning with statement and drivers", async () => {
    renderWorkspace("planning");

    expect(await screen.findByRole("heading", { name: "Planning" })).toBeInTheDocument();
    expect(screen.getByText("fcst-fy26-p08-base-v4")).toBeInTheDocument();
    expect(screen.getByText("INCOME STATEMENT OUTLOOK // FY26 // P08")).toBeInTheDocument();
    expect(screen.getByText("Volume growth")).toBeInTheDocument();
  });

  it("renders downside performance signals from workspace context", async () => {
    renderWorkspace("performance", "local-downside");

    expect(await screen.findByRole("heading", { name: "Performance" })).toBeInTheDocument();
    expect(screen.getByText("-2.6%")).toBeInTheDocument();
    expect(screen.getByText("-€9.6M")).toBeInTheDocument();
    expect(screen.getByText("AN-031")).toBeInTheDocument();
  });
});
