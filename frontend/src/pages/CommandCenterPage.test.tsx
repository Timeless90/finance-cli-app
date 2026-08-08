import "@testing-library/jest-dom/vitest";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import {
  companies,
  periods,
  scenarios,
  WorkspaceContext,
  type WorkspaceContextValue,
} from "@/app/context/workspace-context";
import { CommandCenterPage } from "@/pages/CommandCenterPage";

function renderCommandCenter(scenarioId = "local-base") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
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
          <CommandCenterPage />
        </MemoryRouter>
      </WorkspaceContext.Provider>
    </QueryClientProvider>,
  );
}

describe("FE-05 CFO Command Center", () => {
  it("renders the mock-connected executive cockpit", async () => {
    renderCommandCenter();

    expect(await screen.findByRole("heading", { name: "Command Center" })).toBeInTheDocument();
    expect(screen.getByText("MOCK CONNECTED")).toBeInTheDocument();
    expect(screen.getByText("€82.4M")).toBeInTheDocument();
    expect(screen.getByText(/Growth remains ahead of plan/i)).toBeInTheDocument();
  });

  it("switches the executive snapshot with scenario context", async () => {
    renderCommandCenter("local-downside");

    expect(await screen.findByText("€68.9M")).toBeInTheDocument();
    expect(screen.getByText(/Downside scenario requires immediate margin and cash protection/i)).toBeInTheDocument();
    expect(screen.getByText("88%")).toBeInTheDocument();
  });
});
