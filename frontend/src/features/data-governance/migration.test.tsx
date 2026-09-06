import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '@/shared/test/server';
import fixtures from '@/shared/test/fixtures/uat.json';
import { WorkspaceContext } from '@/app/context/workspace-context';
import { DataGovernancePage } from './DataGovernancePage';

function setup() {
  const client = new QueryClient({
    defaultOptions: {
      queries: { retry: false, retryDelay: 0 },
      mutations: { retry: false },
    },
  });
  render(
    <QueryClientProvider client={client}>
      <WorkspaceContext.Provider
        value={{
          companies: [],
          periods: [],
          scenarios: [],
          companyId: 'AURELIA',
          periodId: '2026-08',
          scenarioId: 'downside',
          setCompanyId: () => {},
          setPeriodId: () => {},
          setScenarioId: () => {},
        }}
      >
        <DataGovernancePage />
      </WorkspaceContext.Provider>
    </QueryClientProvider>,
  );
}
describe('Data import and planning baseline survive structural migration', () => {
  it('uploads, reviews and publishes a source, then publishes a planning baseline', async () => {
    let imported: Record<string, unknown> | null = null;
    let mapping: Record<string, unknown> | null = null;
    let published = false;
    const accounts = ['4000', '5000', '6000', '1000', '9999'];
    server.use(
      http.get('http://localhost/api/v1/*', ({ request }) => {
        const path = new URL(request.url).pathname;
        if (path.endsWith('/accounts'))
          return HttpResponse.json(
            accounts.map((account) => ({ account, total: '10' })),
          );
        if (path.endsWith('/imports'))
          return HttpResponse.json(imported ? [imported] : []);
        if (path.endsWith('/planning-mappings'))
          return HttpResponse.json(mapping ? [mapping] : []);
        if (path.endsWith('/planning-baselines'))
          return HttpResponse.json(
            published
              ? [
                  {
                    baseline_id: 'B1',
                    forecast_eligible: true,
                    missing_categories: [],
                    values: { revenue: '10' },
                  },
                ]
              : [],
          );
        return HttpResponse.json(fixtures['/api/v1/data-governance/workspace']);
      }),
      http.post('http://localhost/api/v1/*', async ({ request }) => {
        const path = new URL(request.url).pathname;
        if (path.endsWith('/imports')) {
          expect(await request.json()).toMatchObject({
            file_name: 'trial.csv',
            file_type: 'csv',
            column_mapping: { company: 'Entity' },
          });
          imported = {
            import_id: 'I1',
            file_name: 'trial.csv',
            status: 'draft',
            row_count: 5,
            quality_score: 100,
            snapshot_id: 'S1',
          };
          return HttpResponse.json(imported);
        }
        if (path.includes('/imports/I1/')) {
          imported = {
            ...imported,
            status: path.endsWith('review')
              ? 'reviewed'
              : path.endsWith('approve')
                ? 'approved'
                : 'published',
          };
          return HttpResponse.json(imported);
        }
        if (path.endsWith('/planning-mappings')) {
          const input = (await request.json()) as { mappings: unknown[] };
          expect(input.mappings).toHaveLength(5);
          mapping = {
            ...input,
            mapping_set_id: 'M1',
            source_snapshot_id: 'S1',
            version_label: 'Mapping v1',
            status: 'draft',
          };
          return HttpResponse.json(mapping);
        }
        if (path.includes('/planning-mappings/M1/')) {
          mapping = {
            ...mapping,
            status: path.endsWith('review') ? 'reviewed' : 'approved',
          };
          return HttpResponse.json(mapping);
        }
        expect(await request.json()).toMatchObject({
          mapping_set_id: 'M1',
          period_id: '2026-08',
          scenario_id: 'downside',
        });
        published = true;
        return HttpResponse.json({ baseline_id: 'B1' });
      }),
    );
    setup();
    await screen.findByRole('heading', { name: 'Data & Governance' });
    expect(screen.getByRole('button', { name: 'UPLOAD & VALIDATE' })).toBeDisabled();
    const file = new File(['Entity,account\nAURELIA,4000'], 'trial.csv', {
      type: 'text/csv',
    });
    Object.defineProperty(file, 'arrayBuffer', {
      value: async () =>
        new TextEncoder().encode('Entity,account\nAURELIA,4000').buffer,
    });
    fireEvent.change(screen.getByLabelText('SOURCE FILE'), {
      target: { files: [file] },
    });
    fireEvent.change(screen.getByLabelText('COLUMN MAPPING'), {
      target: { value: '{"company":"Entity"}' },
    });
    fireEvent.change(screen.getByLabelText('EXPECTED TOTAL'), {
      target: { value: '0' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'UPLOAD & VALIDATE' }));
    await screen.findByText('trial.csv');
    for (const name of ['REVIEW', 'APPROVE', 'PUBLISH']) {
      await waitFor(() => expect(screen.getByRole('button', { name })).toBeEnabled());
      fireEvent.click(screen.getByRole('button', { name }));
    }
    await waitFor(() =>
      expect(screen.getByRole('option', { name: /trial.csv/ })).toBeInTheDocument(),
    );
    fireEvent.change(screen.getByLabelText('SOURCE IMPORT'), {
      target: { value: 'I1' },
    });
    await screen.findByLabelText('CATEGORY 4000');
    expect(screen.getByLabelText('CATEGORY 5000')).toHaveValue('variable_cost');
    fireEvent.change(screen.getByLabelText('CATEGORY 9999'), {
      target: { value: 'debt' },
    });
    fireEvent.change(screen.getByLabelText('SIGN 9999'), { target: { value: '-1' } });
    fireEvent.click(screen.getByRole('button', { name: 'CREATE MAPPING DRAFT' }));
    for (const name of ['REVIEW MAPPING', 'APPROVE MAPPING', 'PUBLISH BASELINE']) {
      await waitFor(() => expect(screen.getByRole('button', { name })).toBeEnabled());
      fireEvent.click(screen.getByRole('button', { name }));
    }
    await waitFor(() => expect(published).toBe(true));
    fireEvent.change(screen.getByLabelText('LOCAL GATEWAY PROFILE'), {
      target: { value: 'reviewer' },
    });
    expect(localStorage.getItem('cfo-local-actor')).toBe('reviewer');
  });
  it('shows malformed mapping errors before sending any upload', async () => {
    server.use(
      http.get('http://localhost/api/v1/*', ({ request }) =>
        HttpResponse.json(
          new URL(request.url).pathname.endsWith('/workspace') ? {} : [],
        ),
      ),
    );
    setup();
    await screen.findByRole('heading', { name: 'Data & Governance' });
    fireEvent.change(screen.getByLabelText('SOURCE FILE'), {
      target: { files: [new File(['x'], 'test.csv')] },
    });
    fireEvent.change(screen.getByLabelText('COLUMN MAPPING'), {
      target: { value: 'invalid json' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'UPLOAD & VALIDATE' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('JSON');
  });
  it('displays authorization failures instead of a data workspace', async () => {
    server.use(
      http.get('http://localhost/api/v1/*', () =>
        HttpResponse.json({ detail: 'denied' }, { status: 403 }),
      ),
    );
    setup();
    expect(await screen.findByText(/do not have access/i)).toBeInTheDocument();
  });
});

it.each([
  ['REVIEW MAPPING', 'draft'],
  ['APPROVE MAPPING', 'reviewed'],
  ['PUBLISH BASELINE', 'approved'],
])(
  'shows server rejection of %s without advancing the mapping',
  async (button, status) => {
    server.use(
      http.get('http://localhost/api/v1/*', ({ request }) => {
        const path = new URL(request.url).pathname;
        if (path.endsWith('/planning-mappings'))
          return HttpResponse.json([
            {
              mapping_set_id: 'M1',
              source_snapshot_id: 'S1',
              version_label: 'Mapping v1',
              status,
              mappings: [],
            },
          ]);
        if (path.endsWith('/planning-baselines'))
          return HttpResponse.json([
            {
              baseline_id: 'B1',
              forecast_eligible: false,
              missing_categories: ['revenue'],
              values: {},
            },
          ]);
        return HttpResponse.json(path.endsWith('/workspace') ? {} : []);
      }),
      http.post('http://localhost/api/v1/*', () =>
        HttpResponse.json({ detail: 'not authorized' }, { status: 403 }),
      ),
    );
    setup();
    await screen.findByRole('heading', { name: 'Data & Governance' });
    await waitFor(() =>
      expect(screen.getByRole('button', { name: button })).toBeEnabled(),
    );
    fireEvent.click(screen.getByRole('button', { name: button }));
    expect(await screen.findByRole('alert')).toHaveTextContent('do not have access');
    expect(screen.getByText('MISSING revenue')).toBeInTheDocument();
    expect(screen.getByText('Mapping v1')).toBeInTheDocument();
  },
);
