import { describe, expect, it } from 'vitest';
import fixtures from '@/shared/test/fixtures/uat.json';
import { mapCommandCenterSnapshot } from '@/features/command-center/query';
import {
  mapPlanningSnapshot,
  mapPerformanceSnapshot,
} from '@/features/planning-performance/query';
import {
  mapProfitabilitySnapshot,
  mapLiquiditySnapshot,
} from '@/features/profitability-liquidity/query';
import { mapRiskCommandSnapshot } from '@/features/risk-command/query';
import { mapMarketRiskSnapshot } from '@/features/market-risk/query';
import { mapReportingSnapshot } from '@/features/reporting-copilot/query';
import { mapActionCapitalSnapshot } from '@/features/action-capital/query';
const cases = [
  ['/api/v1/command-center/overview', mapCommandCenterSnapshot],
  ['/api/v1/planning/workspace', mapPlanningSnapshot],
  ['/api/v1/performance/workspace', mapPerformanceSnapshot],
  ['/api/v1/profitability/workspace', mapProfitabilitySnapshot],
  ['/api/v1/liquidity/workspace', mapLiquiditySnapshot],
  ['/api/v1/risk/workspace', mapRiskCommandSnapshot],
  ['/api/v1/market-risk/workspace', mapMarketRiskSnapshot],
  ['/api/v1/reporting/workspace', mapReportingSnapshot],
] as const;
describe('Published backend projections survive the client migration', () => {
  it.each(cases)('%s retains selected company, period and scenario', (path, map) => {
    const result = map(fixtures[path] as never);
    expect(result.context).toMatchObject({
      companyId: 'AURELIA',
      periodId: '2026-08',
      scenarioId: 'downside',
    });
    expect(JSON.stringify(result)).not.toContain('NaN');
  });
  it.each(cases)(
    '%s supports empty read models without fabricated metrics',
    (path, map) => {
      const original = fixtures[path];
      const empty = {
        context: original.context,
        as_of: original.as_of,
        projection_version: 1,
      };
      const result = map(empty as never);
      expect(result.context.companyId).toBe('AURELIA');
      expect(JSON.stringify(result)).not.toContain('undefined');
    },
  );
  it('preserves linked action and capital projections', () => {
    const result = mapActionCapitalSnapshot(
      fixtures['/api/v1/actions/workspace'] as never,
      fixtures['/api/v1/capital/workspace'] as never,
    );
    expect(result.context.companyId).toBe('AURELIA');
  });
  it('normalizes optional profitability states and never propagates non-finite amounts', () => {
    const source = fixtures['/api/v1/profitability/workspace'];
    for (const status of ['STRONG', 'WATCH', 'CRITICAL', 'unrecognized']) {
      const result = mapProfitabilitySnapshot({
        ...source,
        segments: [{ status }],
        profitability_matrix: [{ status }],
        margin_waterfall: [
          { type: 'start', amount: 1 },
          { type: 'negative', amount: -1 },
          { type: 'end', amount: 0 },
          { type: 'unknown', amount: NaN },
        ],
        sensitivity_summary: [{ tone: 'positive' }, { tone: 'negative' }],
      } as never);
      expect(result.segments[0]?.status).toBe(
        status === 'unrecognized' ? 'WATCH' : status,
      );
      expect(result.waterfall.at(-1)?.amount).toBe(0);
    }
  });
  it('normalizes liquidity status variants while retaining breach flags', () => {
    for (const status of [
      'ON_TARGET',
      'PASS',
      'NORMAL',
      'WATCH',
      'BREACH',
      'unknown',
    ]) {
      const result = mapLiquiditySnapshot({
        ...fixtures['/api/v1/liquidity/workspace'],
        working_capital: [{ status }],
        debt: [{ status }],
        covenants: [{ status }],
        stresses: [{ breach: true }, { breach: false }],
      } as never);
      expect(result.stresses.map((s) => s.breach)).toEqual([true, false]);
      expect(result.debt[0]?.status).toBe(status === 'NORMAL' ? 'NORMAL' : 'WATCH');
    }
  });
  it.each(['DRAFT', 'REVIEW', 'APPROVED', 'PUBLISHED', 'unknown'])(
    'normalizes report state %s',
    (status) => {
      const result = mapReportingSnapshot({
        ...fixtures['/api/v1/reporting/workspace'],
        active_report: { status },
        versions: [{ status, source_snapshot_ids: ['s1'] }, { status: 'unknown' }],
        sections: [{ status: 'APPROVED' }, { status: 'unknown' }],
        source_pack: [{ status: 'APPROVED' }, { status: 'STALE' }],
        export_targets: [
          { format: 'PDF', status: 'READY' },
          { format: 'XLSX', status: 'BLOCKED' },
        ],
        findings: [{ status: 'RESOLVED' }, { status: 'OPEN' }],
      } as never);
      expect(result.reporting.activeReport.status).toBe(
        status === 'unknown' ? 'DRAFT' : status,
      );
    },
  );
});

describe('Live workspace requests keep their contract and errors', () => {
  it('uses generated URLs for every live read model', async () => {
    const { vi } = await import('vitest');
    const { http, HttpResponse } = await import('msw');
    const { server } = await import('@/shared/test/server');
    const modules = await Promise.all([
      import('@/features/command-center/query'),
      import('@/features/planning-performance/query'),
      import('@/features/profitability-liquidity/query'),
      import('@/features/risk-command/query'),
      import('@/features/market-risk/query'),
      import('@/features/reporting-copilot/query'),
      import('@/features/action-capital/query'),
    ]);
    const [command, planning, profit, risk, market, report, action] = modules;
    const getters = [
      command.getCommandCenterSnapshot,
      planning.getPlanningSnapshot,
      planning.getPerformanceSnapshot,
      profit.getProfitabilitySnapshot,
      profit.getLiquiditySnapshot,
      risk.getRiskCommandSnapshot,
      market.getMarketRiskSnapshot,
      report.getReportingCopilotSnapshot,
      action.getActionCapitalSnapshot,
    ];
    const selection = {
      companyId: 'AURELIA',
      periodId: '2026-08',
      scenarioId: 'downside',
    };
    vi.stubEnv('MODE', 'development');
    try {
      server.use(
        http.get('http://localhost/api/v1/*', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('company_id')).toBe('AURELIA');
          return HttpResponse.json(fixtures[url.pathname as keyof typeof fixtures]);
        }),
      );
      for (const get of getters)
        expect((await get(selection)).context.companyId).toBe('AURELIA');
      server.use(
        http.get('http://localhost/api/v1/*', () =>
          HttpResponse.json({ detail: 'missing projection' }, { status: 404 }),
        ),
      );
      for (const get of getters)
        await expect(get(selection)).rejects.toMatchObject({ status: 404 });
    } finally {
      vi.unstubAllEnvs();
    }
  });
});

describe('Enum and optional-field compatibility across generated models', () => {
  it('retains all action/capital lifecycle states and falls back on unknown values', () => {
    const statuses = [
      'PROPOSED',
      'APPROVED',
      'IN_EXECUTION',
      'AT_RISK',
      'COMPLETED',
      'SCREENED',
      'DEFERRED',
      'REJECTED',
      'unknown',
    ];
    const result = mapActionCapitalSnapshot(
      {
        ...fixtures['/api/v1/actions/workspace'],
        source_snapshot_ids: undefined,
        metrics: {
          items: ['positive', 'warning', 'negative', 'neutral', 'unknown'].map(
            (delta_tone) => ({ delta_tone }),
          ),
        },
        actions: statuses.map((status, index) => ({
          status,
          priority: ['P0', 'P1', 'P2', 'unknown'][index % 4],
        })),
        benefit_series: [{}, { expected: 1, realized: 0 }],
        dependencies: [{ type: 'BLOCKING' }, { type: 'ENABLING' }],
      } as never,
      {
        ...fixtures['/api/v1/capital/workspace'],
        candidates: statuses.map((status) => ({ status })),
        constraints: ['PASS', 'WATCH', 'BREACH', 'unknown'].map((status) => ({
          status,
        })),
        approvals: ['APPROVED', 'REJECTED', 'PENDING'].map((status) => ({ status })),
        frontier_points: [{ selected: true }, { selected: false }],
      } as never,
    );
    expect(result.actions.queue.slice(0, 5).map((item) => item.status)).toEqual(
      statuses.slice(0, 5),
    );
    expect(result.capital.candidates.at(-1)?.status).toBe('PROPOSED');
    expect(result.sourceSnapshotIds).toEqual([]);
  });
  it('preserves planning workflow states and incomplete read models', () => {
    const result = mapPlanningSnapshot({
      ...fixtures['/api/v1/planning/workspace'],
      active_forecast: { status: 'approved' },
      scenarios: [
        { type: 'BASE', status: 'ACTIVE' },
        { type: 'UPSIDE', status: 'APPROVED' },
        { type: 'DOWNSIDE', status: 'DRAFT' },
        { type: null, status: null },
      ],
      drivers: ['LOCKED', 'REVIEW', 'OPEN', 'unknown'].map((status) => ({ status })),
      thresholds: ['ON_TARGET', 'WARNING', 'BREACH', 'unknown'].map((status) => ({
        status,
      })),
      forecast_series: [{ actual: 1 }, { actual: null }],
      financial_statement: [
        { level: 0, variance_tone: 'negative' },
        { level: 1, variance_tone: 'neutral' },
      ],
    } as never);
    expect(result.scenarios.map((item) => item.type)).toEqual([
      'BASE',
      'UPSIDE',
      'DOWNSIDE',
      'BASE',
    ]);
    expect(result.drivers.map((item) => item.status)).toEqual([
      'LOCKED',
      'REVIEW',
      'OPEN',
      'OPEN',
    ]);
    expect(result.thresholds.at(-1)?.status).toBe('WARNING');
  });
  it('preserves signs and unknown waterfall steps in performance projections', () => {
    const result = mapPerformanceSnapshot({
      ...fixtures['/api/v1/performance/workspace'],
      metrics: [
        { delta_tone: 'positive' },
        { delta_tone: 'negative' },
        { delta_tone: 'other' },
      ],
      variance_bridge: {
        steps: ['start', 'positive', 'negative', 'end', 'unknown'].map((type) => ({
          type,
          amount: -2,
        })),
      },
      kpi_tree: [{ parent_id: 'root' }, { parent_id: null }],
    } as never);
    expect(result.varianceBridge.steps.map((item) => item.type)).toEqual([
      'start',
      'positive',
      'negative',
      'end',
      'positive',
    ]);
    expect(result.varianceBridge.steps.every((item) => item.amount === -2)).toBe(true);
  });
});

it('keeps market classifications and defensive defaults stable across the new generated models', () => {
  const source = fixtures['/api/v1/market-risk/workspace'];
  const classes = ['FX', 'COMMODITY', 'EQUITY', 'RATE', 'unknown'];
  const statuses = ['NORMAL', 'WATCH', 'STRESS', 'unknown'];
  for (const [index, assetClass] of classes.entries()) {
    const result = mapMarketRiskSnapshot({
      ...source,
      assets: [{ asset_class: assetClass, status: statuses[index % 4] }],
      threshold_states: ['NORMAL', 'WARNING', 'BREACH', 'unknown'].map((status) => ({
        status,
      })),
      selected_runs: {
        model_lifecycle: 'LIVE_RUN_AVAILABLE',
        regimes: { current_state: 'HIGH VOL', transition_matrix: [[0.9, 0.1], null] },
        backtest: { traffic_light: index % 2 ? 'GREEN' : 'RED' },
        model_comparison: ['CANDIDATE', 'CHAMPION', 'REJECTED', 'unknown'].map(
          (status) => ({ status }),
        ),
      },
    } as never);
    expect(result.assets[0]?.assetClass).toBe(
      assetClass === 'unknown' ? 'FX' : assetClass,
    );
    expect(result.regimes.currentState).toBe('HIGH VOL');
    expect(result.thresholds.at(-1)?.status).toBe('WARNING');
  }
});
