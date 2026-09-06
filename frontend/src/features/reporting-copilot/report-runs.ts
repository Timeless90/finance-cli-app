import type { ReportRunResponse } from '@/generated/models';
import { apiClient } from '@/shared/api/client';
import { toApiContractError } from '@/shared/api/errors';

export type ReportRun = ReportRunResponse;

export async function createManagementPackRun(input: {
  companyId: string;
  periodId: string;
  scenarioId: string;
  sourceSnapshotIds: string[];
  projectionVersion: number;
}): Promise<ReportRun> {
  const { data, error, response } = await apiClient.POST('/api/v1/reporting/runs', {
    body: {
      company_id: input.companyId,
      period_id: input.periodId,
      scenario_id: input.scenarioId,
      template_id: 'management-pack',
      template_version: 1,
      source_snapshot_ids: input.sourceSnapshotIds,
      projection_version: input.projectionVersion,
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return data as ReportRun;
}
