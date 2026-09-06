import type {
  PerformanceWorkspaceResponse,
  PlanningBaselineResponse,
  PlanningWorkspaceResponse,
} from '@/generated/models';
import { useQuery } from '@tanstack/react-query';

import { apiClient } from '@/shared/api/client';
import { apiConfig } from '@/shared/api/config';
import { toApiContractError } from '@/shared/api/errors';

import { getMockPerformanceSnapshot, getMockPlanningSnapshot } from './mock';
import type {
  PerformanceSnapshot,
  PlanningSnapshot,
  WorkspaceSelection,
} from './contracts';

type ApiPlanningSnapshot = PlanningWorkspaceResponse;
type ApiPerformanceSnapshot = PerformanceWorkspaceResponse;
type ApiPlanningBaseline = PlanningBaselineResponse;
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

function deltaTone(value: unknown): 'positive' | 'negative' | 'neutral' {
  return value === 'positive' || value === 'negative' ? value : 'neutral';
}

function upper(value: unknown): string {
  return typeof value === 'string' ? value.toUpperCase() : '';
}

function context(
  snapshot: ApiPlanningSnapshot | ApiPerformanceSnapshot,
): PlanningSnapshot['context'] {
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

export function mapPlanningSnapshot(snapshot: ApiPlanningSnapshot): PlanningSnapshot {
  const activeForecast = record(snapshot.active_forecast);
  const assurance = record(snapshot.forecast_assurance);

  return {
    contractStatus: 'LIVE_API_CONNECTED',
    context: context(snapshot),
    scenarios: items(snapshot.scenarios).map((scenario) => ({
      id: text(scenario.scenario_id),
      label: text(scenario.label),
      type:
        upper(scenario.type) === 'BASE' ||
        upper(scenario.type) === 'UPSIDE' ||
        upper(scenario.type) === 'DOWNSIDE'
          ? (upper(scenario.type) as 'BASE' | 'UPSIDE' | 'DOWNSIDE')
          : 'BASE',
      status:
        upper(scenario.status) === 'ACTIVE' ||
        upper(scenario.status) === 'APPROVED' ||
        upper(scenario.status) === 'DRAFT'
          ? (upper(scenario.status) as 'ACTIVE' | 'APPROVED' | 'DRAFT')
          : 'DRAFT',
      revenue: text(scenario.revenue),
      ebitda: text(scenario.ebitda),
      freeCashFlow: text(scenario.free_cash_flow),
      owner: text(scenario.owner),
    })),
    activeScenario: {
      id: snapshot.context.scenario_id,
      label: snapshot.context.scenario_label,
      versionId: text(activeForecast.version_id),
      snapshotId: text(activeForecast.snapshot_id),
      assumptionSetId: text(activeForecast.assumption_set_id),
      modelVersion: text(activeForecast.model_version),
      status: upper(activeForecast.status) === 'APPROVED' ? 'APPROVED' : 'DRAFT',
    },
    forecast: {
      kpi: 'EBITDA',
      unit: 'EUR_M',
      horizon: text(activeForecast.horizon, snapshot.context.period_label),
      points: items(snapshot.forecast_series).map((point) => ({
        period: text(point.period),
        ...(typeof point.actual === 'number' ? { actual: point.actual } : {}),
        plan: number(point.plan),
        forecast: number(point.forecast),
        lower: number(point.lower),
        upper: number(point.upper),
      })),
      confidence: text(assurance.confidence),
      mape: text(assurance.mape),
      bias: text(assurance.bias),
    },
    statement: items(snapshot.financial_statement).map((line) => ({
      id: text(line.line_item),
      label: text(line.label),
      level: line.level === 0 ? 0 : 1,
      actual: text(line.actual),
      plan: text(line.plan),
      forecast: text(line.forecast),
      variance: text(line.variance),
      varianceTone: deltaTone(line.variance_tone),
    })),
    drivers: items(snapshot.drivers).map((driver) => ({
      id: text(driver.driver_id),
      label: text(driver.label),
      value: text(driver.value),
      unit: text(driver.unit),
      delta: text(driver.delta),
      owner: text(driver.owner),
      status:
        upper(driver.status) === 'LOCKED' ||
        upper(driver.status) === 'REVIEW' ||
        upper(driver.status) === 'OPEN'
          ? (upper(driver.status) as 'LOCKED' | 'REVIEW' | 'OPEN')
          : 'OPEN',
    })),
    thresholds: items(snapshot.thresholds).map((threshold) => ({
      kpi: text(threshold.metric_id),
      target: text(threshold.target),
      warning: text(threshold.warning),
      current: text(threshold.current),
      status:
        upper(threshold.status) === 'ON_TARGET' ||
        upper(threshold.status) === 'WARNING' ||
        upper(threshold.status) === 'BREACH'
          ? (upper(threshold.status) as 'ON_TARGET' | 'WARNING' | 'BREACH')
          : 'WARNING',
    })),
  };
}

export function mapPerformanceSnapshot(
  snapshot: ApiPerformanceSnapshot,
): PerformanceSnapshot {
  const bridge = record(snapshot.variance_bridge);

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
    kpiTree: items(snapshot.kpi_tree).map((node) => ({
      id: text(node.node_id),
      label: text(node.label),
      value: text(node.value),
      variance: text(node.variance),
      tone: deltaTone(node.tone),
      ...(typeof node.parent_id === 'string' ? { parentId: node.parent_id } : {}),
    })),
    varianceBridge: {
      kpi: 'EBITDA',
      comparison: 'ACTUAL_VS_PLAN',
      baseline: text(bridge.baseline),
      actual: text(bridge.actual),
      explained: text(bridge.explained),
      unexplained: text(bridge.unexplained),
      fullyExplained: bridge.fully_explained === true,
      steps: items(bridge.steps).map((step) => ({
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
    },
    trend: {
      kpi: 'EBITDA_MARGIN',
      unit: 'PERCENT',
      points: items(snapshot.trend).map((point) => ({
        period: text(point.period),
        actual: number(point.actual),
        plan: number(point.plan),
        forecast: number(point.forecast),
      })),
    },
    anomalies: items(snapshot.anomalies).map((anomaly) => ({
      id: text(anomaly.anomaly_id),
      period: text(anomaly.period),
      kpi: text(anomaly.kpi),
      observation: text(anomaly.observation),
      severity:
        upper(anomaly.severity) === 'HIGH' ||
        upper(anomaly.severity) === 'MEDIUM' ||
        upper(anomaly.severity) === 'LOW'
          ? (upper(anomaly.severity) as 'HIGH' | 'MEDIUM' | 'LOW')
          : 'LOW',
      status:
        upper(anomaly.status) === 'OPEN' || upper(anomaly.status) === 'REVIEWED'
          ? (upper(anomaly.status) as 'OPEN' | 'REVIEWED')
          : 'OPEN',
    })),
    commentary: items(snapshot.commentary_requirements).map((requirement) => ({
      id: text(requirement.commentary_id),
      kpi: text(requirement.kpi),
      variance: text(requirement.variance),
      threshold: text(requirement.threshold),
      status:
        upper(requirement.status) === 'REQUIRED' ||
        upper(requirement.status) === 'COMPLETE' ||
        upper(requirement.status) === 'NOT_REQUIRED'
          ? (upper(requirement.status) as 'REQUIRED' | 'COMPLETE' | 'NOT_REQUIRED')
          : 'REQUIRED',
      owner: text(requirement.owner),
    })),
  };
}

export async function getPlanningSnapshot(
  selection: WorkspaceSelection,
): Promise<PlanningSnapshot> {
  if (apiConfig.mode === 'mock' || import.meta.env.MODE === 'test') {
    return getMockPlanningSnapshot(selection);
  }
  const { data, error, response } = await apiClient.GET('/api/v1/planning/workspace', {
    params: {
      query: {
        company_id: selection.companyId,
        period_id: selection.periodId,
        scenario_id: selection.scenarioId,
      },
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return mapPlanningSnapshot(data as ApiPlanningSnapshot);
}

export async function getPerformanceSnapshot(
  selection: WorkspaceSelection,
): Promise<PerformanceSnapshot> {
  if (apiConfig.mode === 'mock' || import.meta.env.MODE === 'test') {
    return getMockPerformanceSnapshot(selection);
  }
  const { data, error, response } = await apiClient.GET(
    '/api/v1/performance/workspace',
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
  return mapPerformanceSnapshot(data as ApiPerformanceSnapshot);
}

export function usePlanningSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: [
      'planning-workspace',
      selection.companyId,
      selection.periodId,
      selection.scenarioId,
    ],
    queryFn: () => getPlanningSnapshot(selection),
    staleTime: apiConfig.mode === 'live' ? 30_000 : Number.POSITIVE_INFINITY,
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
}

export function usePlanningBaselines(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: [
      'planning-baselines',
      selection.companyId,
      selection.periodId,
      selection.scenarioId,
    ],
    enabled: apiConfig.mode === 'live' && import.meta.env.MODE !== 'test',
    queryFn: async () => {
      const { data, error, response } = await apiClient.GET(
        '/api/v1/data/planning-baselines',
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
      return data as ApiPlanningBaseline[];
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function usePerformanceSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: [
      'performance-workspace',
      selection.companyId,
      selection.periodId,
      selection.scenarioId,
    ],
    queryFn: () => getPerformanceSnapshot(selection),
    staleTime: apiConfig.mode === 'live' ? 30_000 : Number.POSITIVE_INFINITY,
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
}
