import type { CommandCenterSnapshotResponse } from '@/generated/models';
import { describe, expect, it } from 'vitest';

import { mapCommandCenterSnapshot } from './query';

describe('command-center live adapter', () => {
  it('maps a published backend projection without calculating finance values', () => {
    const response: CommandCenterSnapshotResponse = {
      context: {
        company_id: 'AURELIA',
        company_label: 'Aurelia Holding',
        period_id: '2026-08',
        period_label: '2026-08',
        scenario_id: 'base',
        scenario_label: 'base',
        currency: 'EUR',
      },
      as_of: '2026-08-09T08:00:00Z',
      projection_version: 1,
      metrics: [
        {
          metric_id: 'ebitda',
          label: 'EBITDA',
          value: '€82.4M',
          delta: '+€3.9M vs plan',
          delta_tone: 'positive',
          meta: 'validated',
        },
      ],
      forecast: {
        title: 'EBITDA',
        subtitle: 'UAT',
        points: [
          { period: 'P08', actual: 82.4, base: 82.4, upside: 82.4, downside: 82.4 },
        ],
      },
      liquidity: {
        cash: '€41.7M',
        runway: '17.4 months',
        minimum_headroom: '€14.2M',
        covenant_headroom: '38%',
        tone: 'positive',
      },
      risk: {
        score: '42 / 100',
        expected_loss: '€6.6M',
        tail_loss: '€18.9M',
        appetite_usage: '61%',
        signals: [],
      },
      variance_drivers: [],
      actions: [],
      briefing: 'Validated base scenario remains above plan.',
      assurance: {
        coverage: 'complete',
        data_freshness: 'current',
        model_status: 'validated',
        lineage_status: 'complete',
      },
    };

    const snapshot = mapCommandCenterSnapshot(response);

    expect(snapshot.contractStatus).toBe('LIVE_API_CONNECTED');
    expect(snapshot.context.companyId).toBe('AURELIA');
    expect(snapshot.metrics[0]).toMatchObject({
      value: '€82.4M',
      deltaTone: 'positive',
    });
    expect(snapshot.liquidity.cash).toBe('€41.7M');
  });
});
