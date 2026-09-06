import { afterEach, describe, expect, it, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '@/shared/test/server';
import fixtures from '@/shared/test/fixtures/uat.json';
import { createApiClient } from './client';
import { getCompanies, getPeriods, getPrincipal, getScenarios } from './context';
import { ApiContractError, describeApiError, toApiContractError } from './errors';
import * as decisions from '@/features/action-capital/decision-runs';
import { createManagementPackRun } from '@/features/reporting-copilot/report-runs';
import {
  createCopilotSession,
  sendCopilotMessage,
} from '@/features/reporting-copilot/copilot-session';

const context = {
  companyId: 'AURELIA',
  periodId: '2026-08',
  scenarioId: 'downside',
  sourceSnapshotIds: ['uat-snapshot-v1'],
  projectionVersion: 1,
};
afterEach(() => vi.unstubAllEnvs());

describe('Orval transport preserves finance workflow contracts', () => {
  it('loads principal and scoped context through generated operations', async () => {
    server.use(
      http.get('http://localhost/api/v1/context/:kind', ({ request }) =>
        HttpResponse.json(
          fixtures[new URL(request.url).pathname as keyof typeof fixtures],
        ),
      ),
    );
    expect(await getPrincipal()).toMatchObject({ user_id: 'uat-cfo' });
    expect((await getCompanies())[0]?.company_id).toBe('AURELIA');
    expect((await getPeriods('AURELIA')).length).toBeGreaterThan(0);
    expect((await getScenarios('AURELIA', '2026-08')).length).toBeGreaterThan(0);
  });
  it.each([401, 403, 404, 422, 429, 503, 500])(
    'preserves status %s and renders an actionable error',
    async (status) => {
      server.use(
        http.get('http://localhost/api/v1/context/principal', () =>
          HttpResponse.json({ detail: 'denied' }, { status }),
        ),
      );
      await expect(getPrincipal()).rejects.toMatchObject({
        status,
        payload: { detail: 'denied' },
      });
      expect(
        describeApiError(new ApiContractError('failed', status, {}), 'Report'),
      ).not.toBe('');
    },
  );
  it('distinguishes transport failures and non-JSON bodies', async () => {
    const client = createApiClient(
      async () => new Response('upstream unavailable', { status: 503 }),
    );
    expect((await client.GET('/health/ready')).error).toBe('upstream unavailable');
    await expect(
      createApiClient(async () => {
        throw new TypeError('offline');
      }).GET('/health/ready'),
    ).rejects.toThrow('offline');
    expect(toApiContractError(undefined, null).status).toBeNull();
    expect(describeApiError(new Error('offline'), 'Report')).toBe(
      'Report is unavailable.',
    );
  });
  const starts = [
    ['simulation', () => decisions.startActionSimulation(context, ['A1'])],
    ['prioritization', () => decisions.startActionPrioritization(context, ['A1'])],
    ['benefit', () => decisions.startActionBenefitTracking(context, ['A1'])],
    ['allocation', () => decisions.startCapitalAllocation(context, ['C1'])],
    ['valuation', () => decisions.startCapitalValuation(context, 'C1')],
    ['monte-carlo', () => decisions.startCapitalMonteCarloNpv(context, 'C1')],
    ['funding', () => decisions.startFundingScenario(context, 'F1')],
  ] as const;
  it.each(starts)(
    'retains scope, lineage and idempotency for %s',
    async (_name, start) => {
      server.use(
        http.post('http://localhost/api/v1/*', async ({ request }) => {
          expect(request.headers.get('Idempotency-Key')).toBeTruthy();
          expect(await request.json()).toMatchObject({
            company_id: 'AURELIA',
            source_snapshot_ids: ['uat-snapshot-v1'],
            projection_version: 1,
          });
          return HttpResponse.json({ run_id: 'R1', status: 'succeeded' });
        }),
      );
      expect(await start()).toMatchObject({ run_id: 'R1' });
    },
  );
  it.each(starts)(
    'surfaces rejected %s instead of inventing a run',
    async (_name, start) => {
      server.use(
        http.post('http://localhost/api/v1/*', () =>
          HttpResponse.json({ detail: 'not permitted' }, { status: 403 }),
        ),
      );
      await expect(start()).rejects.toMatchObject({ status: 403 });
    },
  );
  it('routes review transitions and encodes IDs', async () => {
    server.use(
      http.get('http://localhost/api/v1/decision-runs', () =>
        HttpResponse.json([{ run_id: 'R1' }]),
      ),
      http.post('http://localhost/api/v1/decision-runs/:id/:action', ({ params }) =>
        HttpResponse.json({ run_id: params.id, status: params.action }),
      ),
    );
    expect(await decisions.getDecisionRuns(context)).toHaveLength(1);
    expect(await decisions.validateDecisionRun('R1')).toMatchObject({
      status: 'validate',
    });
    expect(await decisions.approveDecisionRun('R1')).toMatchObject({
      status: 'approve',
    });
    expect(await decisions.rejectDecisionRun('R1', 'incorrect input')).toMatchObject({
      status: 'reject',
    });
  });
  it('sends report and copilot commands to their existing routes', async () => {
    server.use(
      http.post('http://localhost/api/v1/*', () =>
        HttpResponse.json({
          run_id: 'report-1',
          session_id: 'session-1',
          answer: 'Approved information',
        }),
      ),
    );
    expect(await createManagementPackRun(context)).toMatchObject({
      run_id: 'report-1',
    });
    expect(await createCopilotSession(context)).toMatchObject({
      session_id: 'session-1',
    });
    expect(await sendCopilotMessage('session-1', 'What changed?')).toMatchObject({
      answer: 'Approved information',
    });
  });
  it('passes abort signals through the generated client', async () => {
    const controller = new AbortController();
    controller.abort();
    await expect(
      createApiClient().GET('/health/ready', { signal: controller.signal }),
    ).rejects.toMatchObject({ name: 'AbortError' });
  });
});

it('propagates authorization failures for review, reporting and copilot workflows', async () => {
  server.use(
    http.all('http://localhost/api/v1/*', () =>
      HttpResponse.json({ detail: 'not authorized' }, { status: 403 }),
    ),
  );
  for (const request of [
    () => decisions.getDecisionRuns(context),
    () => decisions.validateDecisionRun('R1'),
    () => createManagementPackRun(context),
    () => createCopilotSession(context),
    () => sendCopilotMessage('S1', 'question'),
  ])
    await expect(request()).rejects.toMatchObject({ status: 403 });
});
