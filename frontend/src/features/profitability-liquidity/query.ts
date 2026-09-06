import type {
  LiquidityWorkspaceResponse,
  ProfitabilityWorkspaceResponse,
} from '@/generated/models';
import { useQuery } from '@tanstack/react-query';

import { apiClient } from '@/shared/api/client';
import { apiConfig } from '@/shared/api/config';
import { toApiContractError } from '@/shared/api/errors';

import { getMockLiquiditySnapshot, getMockProfitabilitySnapshot } from './mock';
import type {
  LiquiditySnapshot,
  ProfitabilitySnapshot,
  WorkspaceContextSnapshot,
  WorkspaceSelection,
} from './contracts';

type ApiProfitabilitySnapshot = ProfitabilityWorkspaceResponse;
type ApiLiquiditySnapshot = LiquidityWorkspaceResponse;
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

function upper(value: unknown): string {
  return typeof value === 'string' ? value.toUpperCase() : '';
}

function deltaTone(value: unknown): 'positive' | 'negative' | 'neutral' {
  return value === 'positive' || value === 'negative' ? value : 'neutral';
}

function context(
  snapshot: ApiProfitabilitySnapshot | ApiLiquiditySnapshot,
): WorkspaceContextSnapshot {
  return {
    companyId: snapshot.context.company_id,
    companyLabel: snapshot.context.company_label,
    periodId: snapshot.context.period_id,
    periodLabel: snapshot.context.period_label,
    scenarioId: snapshot.context.scenario_id,
    scenarioLabel: snapshot.context.scenario_label,
    asOf: snapshot.as_of,
  };
}

export function mapProfitabilitySnapshot(
  snapshot: ApiProfitabilitySnapshot,
): ProfitabilitySnapshot {
  const allocation = record(snapshot.allocation_assurance);
  return {
    contractStatus: 'LIVE_API_CONNECTED',
    context: context(snapshot),
    metrics: items(snapshot.metrics).map((metric) => ({
      id: text(metric.metric_id),
      label: text(metric.label),
      value: text(metric.value),
      delta: text(metric.delta),
      deltaTone: deltaTone(metric.delta_tone),
      meta: text(metric.meta),
    })),
    segments: items(snapshot.segments).map((segment) => ({
      id: text(segment.segment_id),
      label: text(segment.label),
      revenue: text(segment.revenue),
      contributionMargin: text(segment.contribution_margin),
      contributionMarginPct: text(segment.contribution_margin_pct),
      ebitda: text(segment.ebitda),
      allocatedCost: text(segment.allocated_cost),
      marginAtRisk: text(segment.margin_at_risk),
      status:
        upper(segment.status) === 'STRONG' ||
        upper(segment.status) === 'WATCH' ||
        upper(segment.status) === 'CRITICAL'
          ? (upper(segment.status) as 'STRONG' | 'WATCH' | 'CRITICAL')
          : 'WATCH',
    })),
    waterfall: items(snapshot.margin_waterfall).map((step) => ({
      id: text(step.id),
      label: text(step.label),
      amount: number(step.amount),
      display: text(step.display),
      type:
        step.type === 'start' ||
        step.type === 'positive' ||
        step.type === 'negative' ||
        step.type === 'end'
          ? step.type
          : 'positive',
    })),
    matrix: items(snapshot.profitability_matrix).map((cell) => ({
      id: text(cell.id),
      product: text(cell.product),
      customer: text(cell.customer),
      channel: text(cell.channel),
      revenue: text(cell.revenue),
      marginPct: text(cell.margin_pct),
      marginAtRisk: text(cell.margin_at_risk),
      status:
        upper(cell.status) === 'STRONG' ||
        upper(cell.status) === 'WATCH' ||
        upper(cell.status) === 'CRITICAL'
          ? (upper(cell.status) as 'STRONG' | 'WATCH' | 'CRITICAL')
          : 'WATCH',
    })),
    sensitivities: items(snapshot.sensitivity_summary).map((item) => ({
      lever: text(item.lever),
      movement: text(item.movement),
      ebitdaImpact: text(item.ebitda_impact),
      marginImpact: text(item.margin_impact),
      tone: item.tone === 'positive' ? 'positive' : 'negative',
    })),
    allocation: {
      versionId: text(allocation.version_id),
      snapshotId: text(allocation.snapshot_id),
      method: text(allocation.method),
      sourceCost: text(allocation.source_cost),
      allocatedCost: text(allocation.allocated_cost),
      reconciliationDifference: text(allocation.reconciliation_difference),
      reconciled: allocation.reconciled === true,
    },
  };
}

export function mapLiquiditySnapshot(
  snapshot: ApiLiquiditySnapshot,
): LiquiditySnapshot {
  const forecast = record(snapshot.cash_forecast);
  return {
    contractStatus: 'LIVE_API_CONNECTED',
    context: context(snapshot),
    metrics: items(snapshot.metrics).map((metric) => ({
      id: text(metric.metric_id),
      label: text(metric.label),
      value: text(metric.value),
      delta: text(metric.delta),
      deltaTone: deltaTone(metric.delta_tone),
      meta: text(metric.meta),
    })),
    cashForecast: {
      horizon: '13_WEEK',
      minimumLiquidity: text(forecast.minimum_liquidity),
      minimumHeadroom: text(forecast.minimum_headroom),
      forecastAccuracy: text(forecast.forecast_accuracy),
      points: items(forecast.points).map((point) => ({
        period: text(point.period),
        opening: number(point.opening),
        inflow: number(point.inflow),
        outflow: number(point.outflow),
        closing: number(point.closing),
        minimum: number(point.minimum),
      })),
    },
    workingCapital: items(snapshot.working_capital).map((item) => ({
      id: text(item.metric_id),
      label: text(item.label),
      current: text(item.current),
      target: text(item.target),
      cashImpact: text(item.cash_impact),
      status:
        upper(item.status) === 'ON_TARGET' ||
        upper(item.status) === 'WATCH' ||
        upper(item.status) === 'BREACH'
          ? (upper(item.status) as 'ON_TARGET' | 'WATCH' | 'BREACH')
          : 'WATCH',
    })),
    debt: items(snapshot.debt).map((item) => ({
      id: text(item.debt_id),
      instrument: text(item.instrument),
      principal: text(item.principal),
      rate: text(item.rate),
      maturity: text(item.maturity),
      committedLimit: text(item.committed_limit),
      headroom: text(item.headroom),
      status:
        upper(item.status) === 'NORMAL' || upper(item.status) === 'WATCH'
          ? (upper(item.status) as 'NORMAL' | 'WATCH')
          : 'WATCH',
    })),
    covenants: items(snapshot.covenants).map((item) => ({
      id: text(item.covenant_id),
      metric: text(item.metric),
      actual: text(item.actual),
      threshold: text(item.threshold),
      headroom: text(item.headroom),
      projectedMinimum: text(item.projected_minimum),
      status:
        upper(item.status) === 'PASS' ||
        upper(item.status) === 'WATCH' ||
        upper(item.status) === 'BREACH'
          ? (upper(item.status) as 'PASS' | 'WATCH' | 'BREACH')
          : 'WATCH',
    })),
    stresses: items(snapshot.stresses).map((item) => ({
      id: text(item.stress_id),
      name: text(item.name),
      closingCash: text(item.closing_cash),
      headroom: text(item.headroom),
      breach: item.breach === true,
      mitigation: text(item.mitigation),
    })),
  };
}

export async function getProfitabilitySnapshot(
  selection: WorkspaceSelection,
): Promise<ProfitabilitySnapshot> {
  if (apiConfig.mode === 'mock' || import.meta.env.MODE === 'test')
    return getMockProfitabilitySnapshot(selection);
  const { data, error, response } = await apiClient.GET(
    '/api/v1/profitability/workspace',
    {
      params: {
        query: {
          company_id: selection.companyId,
          period_id: selection.periodId,
          scenario_id: selection.scenarioId,
        },
      },
    } as never,
  );
  if (!data) throw toApiContractError(response, error);
  return mapProfitabilitySnapshot(data as ApiProfitabilitySnapshot);
}

export async function getLiquiditySnapshot(
  selection: WorkspaceSelection,
): Promise<LiquiditySnapshot> {
  if (apiConfig.mode === 'mock' || import.meta.env.MODE === 'test')
    return getMockLiquiditySnapshot(selection);
  const { data, error, response } = await apiClient.GET('/api/v1/liquidity/workspace', {
    params: {
      query: {
        company_id: selection.companyId,
        period_id: selection.periodId,
        scenario_id: selection.scenarioId,
      },
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return mapLiquiditySnapshot(data as ApiLiquiditySnapshot);
}

export function useProfitabilitySnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: [
      'profitability-workspace',
      selection.companyId,
      selection.periodId,
      selection.scenarioId,
    ],
    queryFn: () => getProfitabilitySnapshot(selection),
    staleTime: apiConfig.mode === 'live' ? 30_000 : Number.POSITIVE_INFINITY,
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
}

export function useLiquiditySnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: [
      'liquidity-workspace',
      selection.companyId,
      selection.periodId,
      selection.scenarioId,
    ],
    queryFn: () => getLiquiditySnapshot(selection),
    staleTime: apiConfig.mode === 'live' ? 30_000 : Number.POSITIVE_INFINITY,
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
}
