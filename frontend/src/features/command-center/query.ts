import type { CommandCenterSnapshotResponse } from '@/generated/models';
import { useQuery } from '@tanstack/react-query';

import { apiConfig } from '@/shared/api/config';
import { apiClient } from '@/shared/api/client';
import { toApiContractError } from '@/shared/api/errors';

import { getMockCommandCenterSnapshot } from './mock';
import type {
  CommandCenterContext,
  CommandCenterSnapshot,
  SignalTone,
} from './contracts';

type ApiSnapshot = CommandCenterSnapshotResponse;
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

function tone(value: unknown): SignalTone {
  return value === 'positive' ||
    value === 'negative' ||
    value === 'warning' ||
    value === 'neutral'
    ? value
    : 'neutral';
}

function deltaTone(value: unknown): 'positive' | 'negative' | 'neutral' {
  return value === 'positive' || value === 'negative' ? value : 'neutral';
}

export function mapCommandCenterSnapshot(snapshot: ApiSnapshot): CommandCenterSnapshot {
  const forecast = record(snapshot.forecast);
  const liquidity = record(snapshot.liquidity);
  const risk = record(snapshot.risk);
  const assurance = record(snapshot.assurance);
  const briefing =
    snapshot.briefing ?? 'No management briefing was published for this context.';

  return {
    contractStatus: 'LIVE_API_CONNECTED',
    source: 'backend-projection',
    context: {
      companyId: snapshot.context.company_id,
      companyLabel: snapshot.context.company_label,
      periodId: snapshot.context.period_id,
      periodLabel: snapshot.context.period_label,
      scenarioId: snapshot.context.scenario_id,
      scenarioLabel: snapshot.context.scenario_label,
      currency: snapshot.context.currency === 'EUR' ? 'EUR' : 'EUR',
      asOf: snapshot.as_of,
    },
    metrics: items(snapshot.metrics).map((metric) => ({
      id: text(metric.metric_id),
      label: text(metric.label),
      value: text(metric.value),
      delta: text(metric.delta),
      deltaTone: deltaTone(metric.delta_tone),
      meta: text(metric.meta),
    })),
    forecast: {
      title: text(forecast.title, 'Forecast'),
      subtitle: text(forecast.subtitle, 'Backend projection'),
      points: items(forecast.points).map((point) => ({
        period: text(point.period),
        ...(typeof point.actual === 'number' ? { actual: point.actual } : {}),
        base: number(point.base),
        upside: number(point.upside),
        downside: number(point.downside),
      })),
    },
    liquidity: {
      cash: text(liquidity.cash),
      runway: text(liquidity.runway),
      minimumHeadroom: text(liquidity.minimum_headroom),
      covenantHeadroom: text(liquidity.covenant_headroom),
      tone: tone(liquidity.tone),
    },
    risk: {
      score: text(risk.score),
      expectedLoss: text(risk.expected_loss),
      tailLoss: text(risk.tail_loss),
      appetiteUsage: text(risk.appetite_usage),
      signals: items(risk.signals).map((signal) => ({
        id: text(signal.risk_id),
        title: text(signal.title),
        owner: text(signal.owner),
        exposure: text(signal.exposure),
        severity:
          signal.severity === 'HIGH' ||
          signal.severity === 'MEDIUM' ||
          signal.severity === 'LOW'
            ? signal.severity
            : 'LOW',
        trend:
          signal.trend === 'UP' || signal.trend === 'DOWN' || signal.trend === 'STABLE'
            ? signal.trend
            : 'STABLE',
      })),
    },
    varianceDrivers: items(snapshot.variance_drivers).map((driver) => ({
      label: text(driver.label),
      amount: text(driver.amount),
      share: text(driver.share),
      tone: tone(driver.tone),
    })),
    actions: items(snapshot.actions).map((action) => ({
      id: text(action.action_id),
      title: text(action.title),
      owner: text(action.owner),
      due: text(action.due),
      status:
        action.status === 'ON TRACK' ||
        action.status === 'AT RISK' ||
        action.status === 'BLOCKED'
          ? action.status
          : 'AT RISK',
      impact: text(action.impact),
      confidence: text(action.confidence),
    })),
    briefing: { headline: briefing, summary: briefing, decisions: [] },
    assurance: {
      dataFreshness: text(assurance.data_freshness),
      coverage: text(assurance.coverage),
      modelStatus: text(assurance.model_status),
      lineageStatus: text(assurance.lineage_status),
    },
  };
}

export async function getCommandCenterSnapshot(
  context: CommandCenterContext,
): Promise<CommandCenterSnapshot> {
  if (apiConfig.mode === 'mock' || import.meta.env.MODE === 'test') {
    return Promise.resolve(getMockCommandCenterSnapshot(context));
  }
  const { data, error, response } = await apiClient.GET(
    '/api/v1/command-center/overview',
    {
      params: {
        query: {
          company_id: context.companyId,
          period_id: context.periodId,
          scenario_id: context.scenarioId,
        },
      },
    } as never,
  );
  if (!data) {
    throw toApiContractError(response, error);
  }
  return mapCommandCenterSnapshot(data as ApiSnapshot);
}

export function useCommandCenterSnapshot(context: CommandCenterContext) {
  return useQuery({
    queryKey: [
      'command-center',
      context.companyId,
      context.periodId,
      context.scenarioId,
    ],
    queryFn: () => getCommandCenterSnapshot(context),
    staleTime: apiConfig.mode === 'live' ? 30_000 : Number.POSITIVE_INFINITY,
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
}
