import type { DecisionRunResponse } from '@/generated/models';
import { apiClient } from '@/shared/api/client';
import { apiConfig } from '@/shared/api/config';
import { toApiContractError } from '@/shared/api/errors';

export type DecisionRun = DecisionRunResponse;

export type DecisionRunContext = {
  companyId: string;
  periodId: string;
  scenarioId: string;
  sourceSnapshotIds: string[];
  projectionVersion: number;
};

function idempotencyKey(): string {
  return globalThis.crypto?.randomUUID?.() ?? `decision-${Date.now()}`;
}

function liveOnly(): void {
  if (apiConfig.mode !== 'live')
    throw new Error('Decision runs require a live backend connection.');
}

export async function startActionSimulation(
  context: DecisionRunContext,
  actionIds: string[],
): Promise<DecisionRun> {
  liveOnly();
  const { data, error, response } = await apiClient.POST('/api/v1/actions/runs', {
    headers: { 'Idempotency-Key': idempotencyKey() },
    body: {
      company_id: context.companyId,
      period_id: context.periodId,
      scenario_id: context.scenarioId,
      source_snapshot_ids: context.sourceSnapshotIds,
      projection_version: context.projectionVersion,
      model_version: 'action-simulation-ui-v1',
      kind: 'action_simulation',
      action_ids: actionIds,
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return data as DecisionRun;
}

export async function startActionPrioritization(
  context: DecisionRunContext,
  actionIds: string[],
): Promise<DecisionRun> {
  liveOnly();
  const { data, error, response } = await apiClient.POST('/api/v1/actions/runs', {
    headers: { 'Idempotency-Key': idempotencyKey() },
    body: {
      company_id: context.companyId,
      period_id: context.periodId,
      scenario_id: context.scenarioId,
      source_snapshot_ids: context.sourceSnapshotIds,
      projection_version: context.projectionVersion,
      model_version: 'action-prioritization-ui-v1',
      kind: 'action_prioritization',
      action_ids: actionIds,
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return data as DecisionRun;
}

export async function startActionBenefitTracking(
  context: DecisionRunContext,
  actionIds: string[],
): Promise<DecisionRun> {
  liveOnly();
  const { data, error, response } = await apiClient.POST(
    '/api/v1/actions/runs/benefit-tracking',
    {
      headers: { 'Idempotency-Key': idempotencyKey() },
      body: {
        company_id: context.companyId,
        period_id: context.periodId,
        scenario_id: context.scenarioId,
        source_snapshot_ids: context.sourceSnapshotIds,
        projection_version: context.projectionVersion,
        model_version: 'benefit-tracking-ui-v1',
        action_ids: actionIds,
      },
    } as never,
  );
  if (!data) throw toApiContractError(response, error);
  return data as DecisionRun;
}

export async function startCapitalAllocation(
  context: DecisionRunContext,
  candidateIds: string[],
): Promise<DecisionRun> {
  liveOnly();
  const { data, error, response } = await apiClient.POST(
    '/api/v1/capital/runs/allocation',
    {
      headers: { 'Idempotency-Key': idempotencyKey() },
      body: {
        company_id: context.companyId,
        period_id: context.periodId,
        scenario_id: context.scenarioId,
        source_snapshot_ids: context.sourceSnapshotIds,
        projection_version: context.projectionVersion,
        model_version: 'capital-allocation-ui-v1',
        candidate_ids: candidateIds,
        strategic_weight: 0,
      },
    } as never,
  );
  if (!data) throw toApiContractError(response, error);
  return data as DecisionRun;
}

export async function startCapitalValuation(
  context: DecisionRunContext,
  candidateId: string,
): Promise<DecisionRun> {
  return createCapitalRun(
    '/api/v1/capital/runs/valuation',
    context,
    { candidate_ids: [candidateId] },
    'capital-valuation-ui-v1',
  );
}

export async function startCapitalMonteCarloNpv(
  context: DecisionRunContext,
  candidateId: string,
): Promise<DecisionRun> {
  return createCapitalRun(
    '/api/v1/capital/runs/monte-carlo-npv',
    context,
    {
      candidate_ids: [candidateId],
      paths: 10_000,
      seed: 42,
      cash_flow_volatility: 0.15,
      risk_event_probability: 0,
      risk_event_impact: 0,
      scenario_multiplier: 1,
    },
    'capital-monte-carlo-ui-v1',
  );
}

export async function startFundingScenario(
  context: DecisionRunContext,
  fundingOptionId: string,
): Promise<DecisionRun> {
  return createCapitalRun(
    '/api/v1/capital/runs/funding',
    context,
    { funding_option_id: fundingOptionId },
    'funding-scenario-ui-v1',
  );
}

async function createCapitalRun(
  path:
    | '/api/v1/capital/runs/valuation'
    | '/api/v1/capital/runs/monte-carlo-npv'
    | '/api/v1/capital/runs/funding',
  context: DecisionRunContext,
  parameters: Record<string, unknown>,
  modelVersion: string,
): Promise<DecisionRun> {
  liveOnly();
  const { data, error, response } = await apiClient.POST(path, {
    headers: { 'Idempotency-Key': idempotencyKey() },
    body: {
      company_id: context.companyId,
      period_id: context.periodId,
      scenario_id: context.scenarioId,
      source_snapshot_ids: context.sourceSnapshotIds,
      projection_version: context.projectionVersion,
      model_version: modelVersion,
      ...parameters,
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return data as DecisionRun;
}

export async function getDecisionRuns(
  context: DecisionRunContext,
): Promise<DecisionRun[]> {
  liveOnly();
  const { data, error, response } = await apiClient.GET('/api/v1/decision-runs', {
    params: {
      query: {
        company_id: context.companyId,
        period_id: context.periodId,
        scenario_id: context.scenarioId,
      },
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return data as DecisionRun[];
}

async function transition(
  runId: string,
  action: 'validate' | 'approve' | 'reject',
  reason?: string,
): Promise<DecisionRun> {
  liveOnly();
  const { data, error, response } = await apiClient.POST(
    `/api/v1/decision-runs/{run_id}/${action}`,
    {
      params: { path: { run_id: runId } },
      ...(action === 'reject' ? { body: { reason } } : {}),
    },
  );
  if (!data) throw toApiContractError(response, error);
  return data as DecisionRun;
}

export function validateDecisionRun(runId: string): Promise<DecisionRun> {
  return transition(runId, 'validate');
}

export function approveDecisionRun(runId: string): Promise<DecisionRun> {
  return transition(runId, 'approve');
}

export function rejectDecisionRun(runId: string, reason: string): Promise<DecisionRun> {
  return transition(runId, 'reject', reason);
}
