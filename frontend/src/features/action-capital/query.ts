import type {
  ActionSteeringWorkspaceResponse,
  CapitalAllocationWorkspaceResponse,
} from '@/generated/models';
import { useQuery } from '@tanstack/react-query';

import { apiClient } from '@/shared/api/client';
import { apiConfig } from '@/shared/api/config';
import { toApiContractError } from '@/shared/api/errors';

import { getMockActionCapitalSnapshot } from './mock';
import type {
  ActionCapitalSnapshot,
  CapitalCandidate,
  ManagementAction,
  SteeringTone,
  WorkspaceSelection,
} from './contracts';

type ActionResponse = ActionSteeringWorkspaceResponse;
type CapitalResponse = CapitalAllocationWorkspaceResponse;
type Payload = Record<string, unknown>;

function record(value: unknown): Payload {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? (value as Payload)
    : {};
}

function items(value: unknown): Payload[] {
  return Array.isArray(value) ? value.map(record) : [];
}

function text(value: unknown, fallback = '—'): string {
  return typeof value === 'string' || typeof value === 'number'
    ? String(value)
    : fallback;
}

function number(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function actionStatus(value: unknown): ManagementAction['status'] {
  return value === 'PROPOSED' ||
    value === 'APPROVED' ||
    value === 'IN_EXECUTION' ||
    value === 'AT_RISK' ||
    value === 'COMPLETED'
    ? value
    : 'PROPOSED';
}

function candidateStatus(value: unknown): CapitalCandidate['status'] {
  return value === 'PROPOSED' ||
    value === 'SCREENED' ||
    value === 'APPROVED' ||
    value === 'DEFERRED' ||
    value === 'REJECTED'
    ? value
    : 'PROPOSED';
}

function tone(value: unknown): SteeringTone {
  return value === 'positive' ||
    value === 'warning' ||
    value === 'negative' ||
    value === 'neutral'
    ? value
    : 'neutral';
}

export function mapActionCapitalSnapshot(
  actionsResponse: ActionResponse,
  capitalResponse: CapitalResponse,
): ActionCapitalSnapshot {
  const actionMetrics = items(record(actionsResponse.metrics).items);
  const queue = items(actionsResponse.actions).map(
    (action): ManagementAction => ({
      id: text(action.action_id),
      title: text(action.title),
      source: text(action.source),
      owner: text(action.owner),
      sponsor: text(action.sponsor),
      due: text(action.due),
      status: actionStatus(action.status),
      priority:
        action.priority === 'P0' || action.priority === 'P1' || action.priority === 'P2'
          ? action.priority
          : 'P2',
      confidence: text(action.confidence),
      expectedEbitda: text(action.expected_ebitda),
      expectedCash: text(action.expected_cash),
      realizedEbitda: text(action.realized_ebitda),
      realizedCash: text(action.realized_cash),
      realizationPct: text(action.realization_pct),
      riskReduction: text(action.risk_reduction),
      evidence: text(action.evidence),
      nextGate: text(action.next_gate),
    }),
  );
  const portfolio = record(capitalResponse.portfolio);

  return {
    contractStatus: 'LIVE_API_CONNECTED',
    sourceSnapshotIds: actionsResponse.source_snapshot_ids ?? [],
    projectionVersion: actionsResponse.projection_version,
    context: {
      companyId: actionsResponse.context.company_id,
      companyLabel: actionsResponse.context.company_label,
      periodId: actionsResponse.context.period_id,
      periodLabel: actionsResponse.context.period_label,
      scenarioId: actionsResponse.context.scenario_id,
      scenarioLabel: actionsResponse.context.scenario_label,
      asOf: actionsResponse.as_of,
    },
    actions: {
      metrics: actionMetrics.map((metric) => ({
        id: text(metric.metric_id),
        label: text(metric.label),
        value: text(metric.value),
        delta: text(metric.delta),
        deltaTone: tone(metric.delta_tone),
        meta: text(metric.meta),
      })),
      queue,
      benefitTrend: items(actionsResponse.benefit_series).map((point) => ({
        period: text(point.period),
        expected: number(point.expected),
        realized: number(point.realized),
      })),
      statusMix: (
        ['PROPOSED', 'APPROVED', 'IN_EXECUTION', 'AT_RISK', 'COMPLETED'] as const
      ).map((status) => ({
        status,
        count: queue.filter((action) => action.status === status).length,
      })),
      dependencies: items(actionsResponse.dependencies).map((dependency) => ({
        actionId: text(dependency.action_id),
        dependsOn: text(dependency.depends_on),
        type: dependency.type === 'BLOCKING' ? 'BLOCKING' : 'ENABLING',
      })),
    },
    capital: {
      budget: text(portfolio.budget),
      committed: text(portfolio.committed),
      approved: text(portfolio.approved),
      unallocated: text(portfolio.unallocated),
      liquidityReserve: text(portfolio.liquidity_reserve),
      expectedPortfolioNpv: text(portfolio.expected_portfolio_npv),
      downsideCapitalAtRisk: text(portfolio.downside_capital_at_risk),
      candidates: items(capitalResponse.candidates).map(
        (candidate): CapitalCandidate => ({
          id: text(candidate.candidate_id),
          name: text(candidate.name),
          category: text(candidate.category),
          sponsor: text(candidate.sponsor),
          capitalRequired: text(candidate.capital_required),
          npv: text(candidate.npv),
          irr: text(candidate.irr),
          payback: text(candidate.payback),
          riskAdjustedScore: number(candidate.risk_adjusted_score),
          strategicFit: number(candidate.strategic_fit),
          liquidityImpact: text(candidate.liquidity_impact),
          downsideLoss: text(candidate.downside_loss),
          status: candidateStatus(candidate.status),
        }),
      ),
      frontier: items(capitalResponse.frontier_points).map((point) => ({
        id: text(point.portfolio_id),
        label: text(point.label),
        risk: number(point.risk),
        return: number(point.return),
        selected: point.selected === true,
      })),
      constraints: items(capitalResponse.constraints).map((constraint) => ({
        id: text(constraint.constraint_id),
        label: text(constraint.label),
        limit: text(constraint.limit),
        used: text(constraint.used),
        headroom: text(constraint.headroom),
        status:
          constraint.status === 'PASS' ||
          constraint.status === 'WATCH' ||
          constraint.status === 'BREACH'
            ? constraint.status
            : 'WATCH',
      })),
      allocation: items(capitalResponse.allocation).map((item) => ({
        category: text(item.category),
        amount: text(item.amount),
        share: number(item.share),
        expectedNpv: text(item.expected_npv),
      })),
      approvals: items(capitalResponse.approvals).map((approval) => ({
        id: text(approval.approval_id),
        candidateId: text(approval.candidate_id),
        gate: text(approval.gate),
        owner: text(approval.owner),
        status:
          approval.status === 'APPROVED' || approval.status === 'REJECTED'
            ? approval.status
            : 'PENDING',
        due: text(approval.due),
      })),
      fundingOptions: items(capitalResponse.funding_options).map((option) => ({
        id: text(option.option_id),
        label: text(option.label),
        status: text(option.status),
      })),
    },
  };
}

export async function getActionCapitalSnapshot(
  selection: WorkspaceSelection,
): Promise<ActionCapitalSnapshot> {
  if (apiConfig.mode === 'mock' || import.meta.env.MODE === 'test')
    return getMockActionCapitalSnapshot(selection);
  const params = {
    params: {
      query: {
        company_id: selection.companyId,
        period_id: selection.periodId,
        scenario_id: selection.scenarioId,
      },
    },
  } as never;
  const [actions, capital] = (await Promise.all([
    apiClient.GET('/api/v1/actions/workspace', params),
    apiClient.GET('/api/v1/capital/workspace', params),
  ])) as [
    { data?: ActionResponse; error?: unknown; response?: Response },
    { data?: CapitalResponse; error?: unknown; response?: Response },
  ];
  if (!actions.data) throw toApiContractError(actions.response, actions.error);
  if (!capital.data) throw toApiContractError(capital.response, capital.error);
  return mapActionCapitalSnapshot(actions.data, capital.data);
}

export function useActionCapitalSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: [
      'action-capital',
      selection.companyId,
      selection.periodId,
      selection.scenarioId,
    ],
    queryFn: () => getActionCapitalSnapshot(selection),
    staleTime: apiConfig.mode === 'live' ? 30_000 : Number.POSITIVE_INFINITY,
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
}
