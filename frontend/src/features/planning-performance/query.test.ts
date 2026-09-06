import type {
  PerformanceWorkspaceResponse,
  PlanningWorkspaceResponse,
} from '@/generated/models';
import { describe, expect, it } from 'vitest';

import { mapPerformanceSnapshot, mapPlanningSnapshot } from './query';

const context = {
  company_id: 'AURELIA',
  company_label: 'Aurelia Holding',
  period_id: '2026-08',
  period_label: '2026-08',
  scenario_id: 'downside',
  scenario_label: 'Downside',
  currency: 'EUR',
};

describe('planning and performance live adapters', () => {
  it('maps a published planning projection without calculating its values', () => {
    const response: PlanningWorkspaceResponse = {
      context,
      as_of: '2026-08-09T08:00:00Z',
      projection_version: 1,
      scenarios: [
        {
          scenario_id: 'downside',
          label: 'Downside',
          type: 'DOWNSIDE',
          status: 'APPROVED',
          revenue: '€451.7M',
          ebitda: '€68.9M',
          free_cash_flow: '€24.6M',
          owner: 'Group FP&A',
        },
      ],
      active_forecast: {
        version_id: 'uat-downside-v1',
        snapshot_id: 'uat-snapshot-v1',
        assumption_set_id: 'uat-downside-assumptions',
        model_version: 'uat-planning-v1',
        status: 'approved',
      },
      forecast_series: [
        {
          period: 'P08',
          actual: 68.9,
          plan: 78.5,
          forecast: 68.9,
          lower: 64.9,
          upper: 72.9,
        },
      ],
      financial_statement: [
        {
          line_item: 'EBITDA',
          label: 'EBITDA',
          actual: '€68.9M',
          plan: '€78.5M',
          forecast: '€68.9M',
          variance: '-€9.6M',
          variance_tone: 'negative',
          level: 0,
        },
      ],
      drivers: [
        {
          driver_id: 'volume',
          label: 'Volume growth',
          value: '-2.6',
          unit: '%',
          delta: '-1.0pp',
          owner: 'Commercial Finance',
          status: 'REVIEW',
        },
      ],
      thresholds: [
        {
          metric_id: 'EBITDA margin',
          target: '>= 16.5%',
          warning: '< 15.5%',
          current: '14.9%',
          status: 'WARNING',
        },
      ],
      forecast_assurance: { confidence: '71%', mape: '5.8%', bias: '-1.9%' },
    };

    const snapshot = mapPlanningSnapshot(response);

    expect(snapshot.contractStatus).toBe('LIVE_API_CONNECTED');
    expect(snapshot.activeScenario.status).toBe('APPROVED');
    expect(snapshot.forecast.points[0]).toMatchObject({ actual: 68.9, forecast: 68.9 });
    expect(snapshot.statement[0]?.variance).toBe('-€9.6M');
  });

  it('maps a published performance projection without creating KPI results', () => {
    const response: PerformanceWorkspaceResponse = {
      context,
      as_of: '2026-08-09T08:00:00Z',
      projection_version: 1,
      metrics: [
        {
          metric_id: 'ebitda',
          label: 'EBITDA',
          value: '€68.9M',
          delta: '-€9.6M',
          delta_tone: 'negative',
          meta: 'validated projection',
        },
      ],
      kpi_tree: [
        {
          node_id: 'ebitda',
          label: 'EBITDA',
          value: '€68.9M',
          variance: '-€9.6M',
          tone: 'negative',
        },
      ],
      variance_bridge: {
        baseline: '€78.5M',
        actual: '€68.9M',
        explained: '€9.6M',
        unexplained: '€0.0M',
        fully_explained: true,
        steps: [
          {
            id: 'baseline',
            label: 'Plan',
            amount: 78.5,
            display: '€78.5M',
            type: 'start',
          },
          {
            id: 'actual',
            label: 'Actual',
            amount: 68.9,
            display: '€68.9M',
            type: 'end',
          },
        ],
      },
      trend: [{ period: 'P08', actual: 68.9, plan: 78.5, forecast: 68.9 }],
      anomalies: [
        {
          anomaly_id: 'AN-031',
          period: 'P08',
          kpi: 'EBITDA',
          observation: 'Downside pressure',
          severity: 'HIGH',
          status: 'OPEN',
        },
      ],
      commentary_requirements: [
        {
          commentary_id: 'COM-01',
          kpi: 'EBITDA',
          variance: '-€9.6M',
          threshold: '€2.0M',
          status: 'REQUIRED',
          owner: 'Group FP&A',
        },
      ],
    };

    const snapshot = mapPerformanceSnapshot(response);

    expect(snapshot.contractStatus).toBe('LIVE_API_CONNECTED');
    expect(snapshot.metrics[0]).toMatchObject({
      value: '€68.9M',
      deltaTone: 'negative',
    });
    expect(snapshot.varianceBridge.fullyExplained).toBe(true);
    expect(snapshot.anomalies[0]?.severity).toBe('HIGH');
  });
});
