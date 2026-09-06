import { apiClient } from '@/shared/api/client';
import { toApiContractError } from '@/shared/api/errors';

export type CopilotSession = {
  session_id: string;
  source_refs: string[];
  route_id: string;
  model_status: string;
};
export type CopilotAnswer = {
  answer: {
    text: string;
    route_id: string;
    selected_deployment: string;
    source_refs: string[];
  };
};

export async function createCopilotSession(context: {
  companyId: string;
  periodId: string;
  scenarioId: string;
}): Promise<CopilotSession> {
  const { data, error, response } = await apiClient.POST('/api/v1/copilot/sessions', {
    body: {
      module: 'general',
      workload: 'general_qa',
      company_id: context.companyId,
      period_id: context.periodId,
      scenario_id: context.scenarioId,
    },
  } as never);
  if (!data) throw toApiContractError(response, error);
  return data as CopilotSession;
}

export async function sendCopilotMessage(
  sessionId: string,
  question: string,
): Promise<CopilotAnswer> {
  const { data, error, response } = await apiClient.POST(
    '/api/v1/copilot/sessions/{session_id}/messages',
    { params: { path: { session_id: sessionId } }, body: { question } } as never,
  );
  if (!data) throw toApiContractError(response, error);
  return data as CopilotAnswer;
}
