import type {
  ActionSteeringWorkspaceResponse,
  CapitalAllocationWorkspaceResponse,
} from '@/generated/models';
import { describe, expect, it } from 'vitest';

import { mapActionCapitalSnapshot } from './query';

const context = {
  company_id: 'AURELIA',
  company_label: 'Aurelia Holding',
  period_id: '2026-08',
  period_label: '2026-08',
  scenario_id: 'downside',
  scenario_label: 'Downside',
  currency: 'EUR',
};

describe('action and capital live adapter', () => {
  it('maps published read models without recreating finance values', () => {
    const actions: ActionSteeringWorkspaceResponse = {
      context,
      as_of: '2026-08-09T08:00:00Z',
      projection_version: 1,
      metrics: {
        items: [
          {
            metric_id: 'impact',
            label: 'EXPECTED EBITDA IMPACT',
            value: '+€18.9M',
            delta: '+€6.2M protection',
            delta_tone: 'positive',
            meta: 'published action projection',
          },
        ],
      },
      actions: [
        {
          action_id: 'ACT-042',
          title: 'Accelerate price corridor update',
          source: 'Performance / DACH',
          owner: 'Commercial Finance',
          sponsor: 'CCO',
          due: 'P09 W2',
          status: 'AT_RISK',
          priority: 'P0',
          confidence: '61%',
          expected_ebitda: '+€2.8M',
          expected_cash: '+€2.2M',
          realized_ebitda: '+€1.7M',
          realized_cash: '+€1.3M',
          realization_pct: '61%',
          risk_reduction: '€0.9M',
          evidence: 'Pricing wave approved',
          next_gate: 'P09 W1 review',
        },
      ],
      benefit_series: [{ period: 'P09', expected: 14.8, realized: 10.7 }],
      dependencies: [{ action_id: 'ACT-042', depends_on: 'ACT-036', type: 'ENABLING' }],
    };
    const capital: CapitalAllocationWorkspaceResponse = {
      context,
      as_of: '2026-08-09T08:00:00Z',
      projection_version: 1,
      portfolio: {
        budget: '€96.0M',
        committed: '€58.4M',
        approved: '€18.6M',
        unallocated: '€9.0M',
        liquidity_reserve: '€20.0M',
        expected_portfolio_npv: '€61.7M',
        downside_capital_at_risk: '€27.8M',
      },
      candidates: [
        {
          candidate_id: 'INV-104',
          name: 'Digital pricing platform',
          category: 'Digital',
          sponsor: 'CCO',
          capital_required: '€8.4M',
          npv: '€19.6M',
          irr: '31%',
          payback: '2.1y',
          risk_adjusted_score: 86,
          strategic_fit: 92,
          liquidity_impact: '-€5.1M Y1',
          downside_loss: '€3.2M',
          status: 'APPROVED',
        },
      ],
      constraints: [
        {
          constraint_id: 'CAP-LIQ',
          label: 'Minimum liquidity reserve',
          limit: '>= €20.0M',
          used: '€5.7M',
          headroom: '-€14.3M',
          status: 'BREACH',
        },
      ],
      allocation: [
        { category: 'Digital', amount: '€16.8M', share: 22, expected_npv: '€26.3M' },
      ],
      frontier_points: [
        { portfolio_id: 'P2', label: 'Balanced', risk: 31, return: 67, selected: true },
      ],
      approvals: [
        {
          approval_id: 'APR-209',
          candidate_id: 'INV-104',
          gate: 'Investment Committee',
          owner: 'CFO',
          status: 'APPROVED',
          due: 'P08 W3',
        },
      ],
    };

    const snapshot = mapActionCapitalSnapshot(actions, capital);

    expect(snapshot.contractStatus).toBe('LIVE_API_CONNECTED');
    expect(snapshot.actions.queue[0]).toMatchObject({
      id: 'ACT-042',
      status: 'AT_RISK',
      expectedEbitda: '+€2.8M',
    });
    expect(snapshot.capital).toMatchObject({
      liquidityReserve: '€20.0M',
      expectedPortfolioNpv: '€61.7M',
    });
    expect(snapshot.capital.constraints[0]?.status).toBe('BREACH');
  });
});
