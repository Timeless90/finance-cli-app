import type { MarketRiskWorkspaceResponse } from '@/generated/models';
import { useQuery } from '@tanstack/react-query';

import { apiClient } from '@/shared/api/client';
import { apiConfig } from '@/shared/api/config';
import { toApiContractError } from '@/shared/api/errors';

import { getMockMarketRiskSnapshot } from './mock';
import type { MarketRiskSnapshot, WorkspaceSelection } from './contracts';

type ApiSnapshot = MarketRiskWorkspaceResponse;
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

export function mapMarketRiskSnapshot(snapshot: ApiSnapshot): MarketRiskSnapshot {
  const runs = record(snapshot.selected_runs);
  const garch = record(runs.garch);
  const regimes = record(runs.regimes);
  const dependency = record(runs.dependency);
  const simulation = record(runs.simulation);
  const backtest = record(runs.backtest);

  return {
    contractStatus: 'LIVE_API_CONNECTED',
    modelLifecycle: lifecycle(runs.model_lifecycle),
    context: {
      companyId: snapshot.context.company_id,
      companyLabel: snapshot.context.company_label,
      periodId: snapshot.context.period_id,
      periodLabel: snapshot.context.period_label,
      scenarioId: snapshot.context.scenario_id,
      scenarioLabel: snapshot.context.scenario_label,
      asOf: snapshot.as_of,
    },
    assets: items(snapshot.assets).map((asset) => ({
      id: text(asset.asset_id),
      label: text(asset.label),
      assetClass:
        asset.asset_class === 'FX' ||
        asset.asset_class === 'COMMODITY' ||
        asset.asset_class === 'EQUITY' ||
        asset.asset_class === 'RATE'
          ? asset.asset_class
          : 'FX',
      exposure: text(asset.exposure),
      spot: text(asset.spot),
      dailyVol: text(asset.daily_vol),
      annualizedVol: text(asset.annualized_vol),
      var95: text(asset.var95),
      es95: text(asset.es95),
      beta: text(asset.beta),
      status:
        asset.status === 'NORMAL' ||
        asset.status === 'WATCH' ||
        asset.status === 'STRESS'
          ? asset.status
          : 'WATCH',
    })),
    selectedAssetId: text(runs.selected_asset_id),
    garch: {
      model: 'GARCH(1,1)-t',
      runId: text(garch.run_id),
      convergence: 'CONVERGED',
      logLikelihood: text(garch.log_likelihood),
      aic: text(garch.aic),
      bic: text(garch.bic),
      persistence: text(garch.persistence),
      unconditionalVol: text(garch.unconditional_vol),
      parameters: items(garch.parameters).map((item) => ({
        name: text(item.name),
        estimate: text(item.estimate),
        stdError: text(item.std_error),
        tStat: text(item.t_stat),
        pValue: text(item.p_value),
      })),
      volatility: items(garch.volatility).map((point) => ({
        index: number(point.index),
        observed: number(point.observed),
        fitted: number(point.fitted),
        upper: number(point.upper),
        lower: number(point.lower),
      })),
      residuals: items(garch.residuals).map((point) => ({
        index: number(point.index),
        value: number(point.value),
      })),
      qq: items(garch.qq).map((point) => ({
        theoretical: number(point.theoretical),
        observed: number(point.observed),
      })),
    },
    regimes: {
      model: '2-STATE MARKOV SWITCHING',
      runId: text(regimes.run_id),
      currentState:
        regimes.current_state === 'LOW VOL' || regimes.current_state === 'HIGH VOL'
          ? regimes.current_state
          : 'LOW VOL',
      confidence: text(regimes.confidence),
      states: items(regimes.states).map((state) => ({
        id: text(state.id),
        label: text(state.label),
        probability: number(state.probability),
        mean: text(state.mean),
        volatility: text(state.volatility),
      })),
      probabilities: items(regimes.probabilities).map((point) => ({
        index: number(point.index),
        low: number(point.low),
        high: number(point.high),
      })),
      transitionMatrix: matrix(regimes.transition_matrix),
    },
    marginals: items(runs.marginals).map((item) => ({
      assetId: text(item.asset_id),
      family: text(item.family),
      location: text(item.location),
      scale: text(item.scale),
      dof: text(item.dof),
      aic: text(item.aic),
      ksPValue: text(item.ks_p_value),
    })),
    dependency: {
      model: 't-COPULA',
      runId: text(dependency.run_id),
      dof: text(dependency.dof),
      logLikelihood: text(dependency.log_likelihood),
      tailDependence: text(dependency.tail_dependence),
      labels: Array.isArray(dependency.labels)
        ? dependency.labels.map((label) => text(label))
        : [],
      matrix: matrix(dependency.matrix),
      edges: items(dependency.edges).map((edge) => ({
        source: text(edge.source),
        target: text(edge.target),
        correlation: number(edge.correlation),
        tailDependence: number(edge.tail_dependence),
      })),
    },
    simulation: {
      runId: text(simulation.run_id),
      paths: text(simulation.paths),
      horizon: '252D',
      seed: text(simulation.seed),
      var95: text(simulation.var95),
      es95: text(simulation.es95),
      fan: items(simulation.fan).map((point) => ({
        horizon: number(point.horizon),
        p05: number(point.p05),
        p25: number(point.p25),
        p50: number(point.p50),
        p75: number(point.p75),
        p95: number(point.p95),
      })),
    },
    backtest: {
      window: text(backtest.window),
      observations: number(backtest.observations),
      varExceptions: number(backtest.var_exceptions),
      expectedExceptions: text(backtest.expected_exceptions),
      kupiecPValue: text(backtest.kupiec_p_value),
      christoffersenPValue: text(backtest.christoffersen_p_value),
      trafficLight:
        backtest.traffic_light === 'GREEN' ||
        backtest.traffic_light === 'YELLOW' ||
        backtest.traffic_light === 'RED'
          ? backtest.traffic_light
          : 'YELLOW',
      breaches: items(backtest.breaches).map((item) => ({
        date: text(item.date),
        return: text(item.return),
        varLimit: text(item.var_limit),
        severity: text(item.severity),
        documented: item.documented === true,
        note: text(item.note),
      })),
    },
    modelComparison: items(runs.model_comparison).map((item) => ({
      id: text(item.id),
      model: text(item.model),
      aic: text(item.aic),
      bic: text(item.bic),
      outOfSampleLoss: text(item.out_of_sample_loss),
      varCoverage: text(item.var_coverage),
      tailFit: text(item.tail_fit),
      status:
        item.status === 'CANDIDATE' ||
        item.status === 'CHAMPION' ||
        item.status === 'REJECTED'
          ? item.status
          : 'CANDIDATE',
    })),
    thresholds: items(snapshot.threshold_states).map((item) => ({
      id: text(item.threshold_id),
      metric: text(item.metric),
      warning: text(item.warning),
      breach: text(item.breach),
      current: text(item.current),
      status:
        item.status === 'NORMAL' ||
        item.status === 'WARNING' ||
        item.status === 'BREACH'
          ? item.status
          : 'WARNING',
      documentation: text(item.documentation),
    })),
  };
}

export async function getMarketRiskSnapshot(
  selection: WorkspaceSelection,
): Promise<MarketRiskSnapshot> {
  if (apiConfig.mode === 'mock' || import.meta.env.MODE === 'test')
    return getMockMarketRiskSnapshot(selection);
  const { data, error, response } = await apiClient.GET(
    '/api/v1/market-risk/workspace',
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
  return mapMarketRiskSnapshot(data as ApiSnapshot);
}

export function useMarketRiskSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: [
      'market-risk-lab',
      selection.companyId,
      selection.periodId,
      selection.scenarioId,
    ],
    queryFn: () => getMarketRiskSnapshot(selection),
    staleTime: apiConfig.mode === 'live' ? 30_000 : Number.POSITIVE_INFINITY,
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
}
