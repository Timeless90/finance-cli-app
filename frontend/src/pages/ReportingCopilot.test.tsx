import "@testing-library/jest-dom/vitest";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { companies, periods, scenarios, WorkspaceContext, type WorkspaceContextValue } from "@/app/context/workspace-context";
import { CopilotPage } from "@/pages/CopilotPage";
import { ReportsPage } from "@/pages/ReportsPage";

function renderWorkspace(page: "reports" | "copilot", scenarioId = "local-base") {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const context: WorkspaceContextValue = { companies, periods, scenarios, companyId: "local-holding", periodId: "local-fy26-p08", scenarioId, setCompanyId: () => undefined, setPeriodId: () => undefined, setScenarioId: () => undefined };
  const Page = page === "reports" ? ReportsPage : CopilotPage;
  return render(<QueryClientProvider client={queryClient}><WorkspaceContext.Provider value={context}><MemoryRouter><Page /></MemoryRouter></WorkspaceContext.Provider></QueryClientProvider>);
}

describe("FE-11 Reporting Studio & Financial Copilot", () => {
  it("renders versioned reporting with lineage and findings", async () => {
    renderWorkspace("reports");
    expect(await screen.findByRole("heading", { name: "Reporting Studio" })).toBeInTheDocument();
    expect(screen.getByText("RPT-FY26-P08-BOARD-v6")).toBeInTheDocument();
    expect(screen.getByText("SRC-CAP")).toBeInTheDocument();
    expect(screen.getByText(/Capital allocation source is older/i)).toBeInTheDocument();
  });

  it("renders grounded downside copilot with model route and citations", async () => {
    renderWorkspace("copilot", "local-downside");
    expect(await screen.findByRole("heading", { name: "Financial Copilot" })).toBeInTheDocument();
    expect(screen.getByText(/downside scenario requires immediate CFO intervention/i)).toBeInTheDocument();
    expect(screen.getByText("route-explain", { exact: true })).toBeInTheDocument();
    expect(screen.getByText("CIT-01", { exact: false })).toBeInTheDocument();
    expect(screen.getAllByText(/COPILOT CONTRACT PENDING/).length).toBeGreaterThanOrEqual(1);
  });
});
