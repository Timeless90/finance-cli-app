import '@testing-library/jest-dom/vitest';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from '@/shared/test/router';
import { describe, expect, it } from 'vitest';

import {
  companies,
  periods,
  scenarios,
  WorkspaceContext,
  type WorkspaceContextValue,
} from '@/app/context/workspace-context';
import { CopilotPage } from '@/features/reporting-copilot/CopilotPage';
import { ReportsPage } from '@/features/reporting-copilot/ReportsPage';

function renderWorkspace(page: 'reports' | 'copilot', scenarioId = 'local-base') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const context: WorkspaceContextValue = {
    companies,
    periods,
    scenarios,
    companyId: 'local-holding',
    periodId: 'local-fy26-p08',
    scenarioId,
    setCompanyId: () => undefined,
    setPeriodId: () => undefined,
    setScenarioId: () => undefined,
  };
  const Page = page === 'reports' ? ReportsPage : CopilotPage;
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

describe('FE-11 Reporting Studio & Financial Copilot', () => {
  it('renders versioned reporting with lineage and findings', async () => {
    renderWorkspace('reports');
    expect(
      await screen.findByRole('heading', { name: 'Reporting Studio' }),
    ).toBeInTheDocument();
    expect(screen.getByText('RPT-FY26-P08-BOARD-v6')).toBeInTheDocument();
    expect(screen.getByText('SRC-CAP')).toBeInTheDocument();
    expect(screen.getByText(/Capital allocation source is older/i)).toBeInTheDocument();
  });

  it('renders the secure session boundary without browser-provided facts', async () => {
    renderWorkspace('copilot', 'local-downside');
    expect(
      await screen.findByRole('heading', { name: 'Financial Copilot' }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: 'START SECURE SESSION' }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/browser never sends a principal, source facts/i),
    ).toBeInTheDocument();
    expect(screen.getByLabelText('QUESTION')).toBeInTheDocument();
  });
});
