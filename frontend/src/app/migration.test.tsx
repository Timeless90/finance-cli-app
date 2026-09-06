import { afterEach, describe, expect, it } from 'vitest';
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import {
  createMemoryHistory,
  createRouter,
  RouterProvider,
} from '@tanstack/react-router';
import { http, HttpResponse } from 'msw';
import { server } from '@/shared/test/server';
import fixtures from '@/shared/test/fixtures/uat.json';
import { router as applicationRouter } from './router';

afterEach(cleanup);
function mount(path: string, empty = false, denied = false) {
  server.use(
    http.get('http://localhost/*', ({ request }) => {
      if (denied && new URL(request.url).pathname === '/api/v1/context/principal')
        return HttpResponse.json({ detail: 'forbidden' }, { status: 403 });
      if (empty && new URL(request.url).pathname === '/api/v1/context/companies')
        return HttpResponse.json([]);
      const value = fixtures[new URL(request.url).pathname as keyof typeof fixtures];
      return value
        ? HttpResponse.json(value)
        : HttpResponse.json({ detail: 'missing' }, { status: 404 });
    }),
  );
  const router = createRouter({
    routeTree: applicationRouter.routeTree,
    history: createMemoryHistory({ initialEntries: [path] }),
    defaultPendingMinMs: 0,
  });
  render(<RouterProvider router={router} />);
  return router;
}
describe('Migrated route tree and scoped shell', () => {
  it.each([
    'command-center',
    'planning',
    'performance',
    'profitability',
    'liquidity',
    'risk',
    'market-risk',
    'actions',
    'capital',
    'reports',
    'copilot',
    'data',
    'governance',
  ])('opens /app/%s directly', async (path) => {
    const router = mount('/app/' + path);
    await screen.findByRole('navigation', { name: 'Primary application navigation' });
    await waitFor(() => expect(screen.getByLabelText('COMPANY')).not.toBeDisabled());
    expect(router.state.location.pathname).toBe('/app/' + path);
  });
  it('redirects the workspace root and navigates without losing context', async () => {
    const router = mount('/app');
    await waitFor(() =>
      expect(router.state.location.pathname).toBe('/app/command-center'),
    );
    await waitFor(() => expect(screen.getByLabelText('COMPANY')).not.toBeDisabled());
    fireEvent.change(screen.getByLabelText('COMPANY'), { target: { value: 'EUROPE' } });
    expect(localStorage.getItem('cfo-context-company')).toBe('EUROPE');
    await waitFor(() =>
      expect(
        screen.getByLabelText('PERIOD').querySelector('option[value="2026-08"]'),
      ).not.toBeNull(),
    );
    fireEvent.change(screen.getByLabelText('PERIOD'), { target: { value: '2026-08' } });
    await waitFor(() =>
      expect(
        screen.getByLabelText('SCENARIO').querySelector('option[value="downside"]'),
      ).not.toBeNull(),
    );
    fireEvent.change(screen.getByLabelText('SCENARIO'), {
      target: { value: 'downside' },
    });
    expect(localStorage.getItem('cfo-context-period')).toBe('2026-08');
    expect(localStorage.getItem('cfo-context-scenario')).toBe('downside');
    await act(() => router.navigate({ to: '/app/reports' }));
    expect(router.state.location.pathname).toBe('/app/reports');
  });
});

it('renders a fresh database without stale company selection or perpetual loading', async () => {
  localStorage.setItem('cfo-context-company', 'OLD-COMPANY');
  mount('/app/command-center', true);
  expect(await screen.findByText('NO PUBLISHED COMPANY DATA')).toBeInTheDocument();
  expect(screen.getByLabelText('COMPANY')).toBeDisabled();
  expect(screen.getByLabelText('COMPANY').querySelectorAll('option')).toHaveLength(0);
});

it('keeps an unauthorized workspace in an explicit error state', async () => {
  mount('/app/command-center', false, true);
  expect(
    await screen.findByText('CONTEXT UNAVAILABLE', {}, { timeout: 4000 }),
  ).toBeInTheDocument();
  expect(screen.getByLabelText('COMPANY')).toBeDisabled();
});
