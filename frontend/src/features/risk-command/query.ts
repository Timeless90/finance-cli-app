import type { RiskWorkspaceResponse } from '@/generated/models';
import { useQuery } from '@tanstack/react-query';

import { apiClient } from '@/shared/api/client';
import { apiConfig } from '@/shared/api/config';
import { toApiContractError } from '@/shared/api/errors';

import { getMockRiskCommandSnapshot } from './mock';
import type { RiskCommandSnapshot, RiskTone, WorkspaceSelection } from './contracts';

type ApiSnapshot = RiskWorkspaceResponse;
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

function matrix(value: unknown): number[][] {
  return Array.isArray(value)
    ? value.map((row) => (Array.isArray(row) ? row.map((item) => number(item)) : []))
    : [];
}

function lifecycle(value: unknown): 'MODEL_CONTRACT_PENDING' | 'LIVE_RUN_AVAILABLE' {
  return value === 'LIVE_RUN_AVAILABLE' ? value : 'MODEL_CONTRACT_PENDING';
}

export function mapRiskCommandSnapshot(snapshot: ApiSnapshot): RiskCommandSnapshot {
  const portfolio = record(snapshot.portfolio);
  const correlation = record(snapshot.correlation);
  const regimes = record(snapshot.regimes);
  const tail = record(snapshot.tail);
  const scenario = record(snapshot.scenario);

  return {
    contractStatus: 'LIVE_API_CONNECTED',
    context: {
      companyId: snapshot.context.company_id,
      companyLabel: snapshot.context.company_label,
      periodId: snapshot.context.period_id,
      periodLabel: snapshot.context.period_label,
      scenarioId: snapshot.context.scenario_id,
      scenarioLabel: snapshot.context.scenario_label,
      asOf: snapshot.as_of,
    },
    portfolio: {
      meanGrossLoss: text(portfolio.mean_gross_loss),
      meanNetLoss: text(portfolio.mean_net_loss),
      p50NetLoss: text(portfolio.p50_net_loss),
      p95NetLoss: text(portfolio.p95_net_loss),
      p99NetLoss: text(portfolio.p99_net_loss),
      expectedShortfall95: text(portfolio.expected_shortfall_95),
      appetiteUsage: text(portfolio.appetite_usage),
      paths: text(portfolio.paths),
      seed: text(portfolio.seed),
      distribution: items(snapshot.percentile_curve).map((point) => ({
        percentile: number(point.percentile),
        loss: number(point.loss),
      })),
    },
    risks: items(snapshot.risks).map((risk) => ({
      id: text(risk.risk_id),
      title: text(risk.title),
      category: text(risk.category),
      owner: text(risk.owner),
      probability: number(risk.probability),
      impact: number(risk.impact),
      expectedLoss: text(risk.expected_loss),
      p95Loss: text(risk.p95_loss),
      residualLoss: text(risk.residual_loss),
      mitigationEffect: text(risk.mitigation_effect),
      appetiteUsage: text(risk.appetite_usage),
      status:
        risk.status === 'HEALTHY' ||
        risk.status === 'WARNING' ||
        risk.status === 'BREACHED'
          ? risk.status
          : 'WARNING',
      trend:
        risk.trend === 'UP' || risk.trend === 'DOWN' || risk.trend === 'STABLE'
          ? risk.trend
          : 'STABLE',
    })),
    categories: items(snapshot.categories).map((category) => ({
      id: text(category.category_id),
      label: text(category.label),
      grossExposure: number(category.gross_exposure),
      residualExposure: number(category.residual_exposure),
      appetite: number(category.appetite),
      tone: (category.tone === 'positive' ||
      category.tone === 'warning' ||
      category.tone === 'negative' ||
      category.tone === 'neutral'
        ? category.tone
        : 'neutral') as RiskTone,
    })),
    radar: items(snapshot.appetite_radar).map((item) => ({
      dimension: text(item.dimension),
      exposure: number(item.exposure),
      appetite: number(item.appetite),
    })),
    correlation: {
      labels: Array.isArray(correlation.labels)
        ? correlation.labels.map((label) => text(label))
        : [],
      matrix: matrix(correlation.matrix),
    },
    regimes: {
      lifecycle: lifecycle(regimes.lifecycle),
      currentState: text(regimes.current_state),
      stateConfidence: text(regimes.state_confidence),
      states: items(regimes.states).map((state) => ({
        id: text(state.id),
        label: text(state.label),
        probability: number(state.probability),
        expectedLossMultiplier: text(state.expected_loss_multiplier),
      })),
      transitionMatrix: matrix(regimes.transition_matrix),
    },
    tail: {
      lifecycle: lifecycle(tail.lifecycle),
      threshold: text(tail.threshold),
      shape: text(tail.shape),
      scale: text(tail.scale),
      expectedShortfall: text(tail.expected_shortfall),
      qq: items(tail.qq).map((point) => ({
        theoretical: number(point.theoretical),
        observed: number(point.observed),
      })),
    },
    scenario: {
      name: text(scenario.name),
      description: text(scenario.description),
      earningsAtRisk: text(scenario.earnings_at_risk),
      cashAtRisk: text(scenario.cash_at_risk),
      probability: text(scenario.probability),
      topDrivers: Array.isArray(scenario.top_drivers)
        ? scenario.top_drivers.map((driver) => text(driver))
        : [],
    },
    controls: items(snapshot.controls).map((control) => ({
      id: text(control.control_id),
      riskId: text(control.risk_id),
      name: text(control.name),
      owner: text(control.owner),
      effectiveness: text(control.effectiveness),
      annualCost: text(control.annual_cost),
      avoidedLoss: text(control.avoided_loss),
      status:
        control.status === 'ACTIVE' ||
        control.status === 'PLANNED' ||
        control.status === 'INEFFECTIVE'
          ? control.status
          : 'PLANNED',
    })),
  };
}

export async function getRiskCommandSnapshot(
  selection: WorkspaceSelection,
): Promise<RiskCommandSnapshot> {
  if (apiConfig.mode === 'mock' || import.meta.env.MODE === 'test')
    return getMockRiskCommandSnapshot(selection);
  const { data, error, response } = await apiClient.GET('/api/v1/risk/workspace', {
    params: {
      query: {
        company_id: selection.companyId,
        period_id: selection.periodId,
        scenario_id: selection.scenarioId,
      },
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return mapRiskCommandSnapshot(data as ApiSnapshot);
}

export function useRiskCommandSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: [
      'risk-command',
      selection.companyId,
      selection.periodId,
      selection.scenarioId,
    ],
    queryFn: () => getRiskCommandSnapshot(selection),
    staleTime: apiConfig.mode === 'live' ? 30_000 : Number.POSITIVE_INFINITY,
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
}
