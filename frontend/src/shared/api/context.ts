import type {
  CompanyOptionResponse,
  PeriodOptionResponse,
  PrincipalResponse,
  ScenarioOptionResponse,
} from '@/generated/models';
import { useQuery } from '@tanstack/react-query';

import { apiClient, type ApiClient } from '@/shared/api/client';
import { toApiContractError } from '@/shared/api/errors';

// Workspace APIs are reached through the UAT gateway. It attaches the trusted
// identity after the browser request, so the browser must not supply X-* headers.
const gatewayRequest = undefined as never;

type GatewayResponse<T> = {
  data?: T;
  error?: unknown;
  response: Response;
};

async function requireData<T>(request: unknown): Promise<T> {
  const { data, error, response } = (await request) as GatewayResponse<T>;
  if (!data) {
    throw toApiContractError(response, error);
  }
  return data;
}

export function getPrincipal(
  client: ApiClient = apiClient,
): Promise<PrincipalResponse> {
  return requireData<PrincipalResponse>(
    client.GET('/api/v1/context/principal', gatewayRequest),
  );
}

export function getCompanies(
  client: ApiClient = apiClient,
): Promise<CompanyOptionResponse[]> {
  return requireData<CompanyOptionResponse[]>(
    client.GET('/api/v1/context/companies', gatewayRequest),
  );
}

export function getPeriods(
  companyId: string,
  client: ApiClient = apiClient,
): Promise<PeriodOptionResponse[]> {
  return requireData<PeriodOptionResponse[]>(
    client.GET('/api/v1/context/periods', {
      params: { query: { company_id: companyId } },
    } as never),
  );
}

export function getScenarios(
  companyId: string,
  periodId: string,
  client: ApiClient = apiClient,
): Promise<ScenarioOptionResponse[]> {
  return requireData<ScenarioOptionResponse[]>(
    client.GET('/api/v1/context/scenarios', {
      params: { query: { company_id: companyId, period_id: periodId } },
    } as never),
  );
}

export function usePrincipal(enabled: boolean) {
  return useQuery({
    queryKey: ['principal'],
    queryFn: () => getPrincipal(),
    enabled,
    staleTime: 300_000,
  });
}

export function useCompanies(enabled: boolean) {
  return useQuery({
    queryKey: ['context', 'companies'],
    queryFn: () => getCompanies(),
    enabled,
    staleTime: 300_000,
  });
}

export function usePeriods(companyId: string, enabled: boolean) {
  return useQuery({
    queryKey: ['context', 'periods', companyId],
    queryFn: () => getPeriods(companyId),
    enabled: enabled && Boolean(companyId),
    staleTime: 300_000,
  });
}

export function useScenarios(companyId: string, periodId: string, enabled: boolean) {
  return useQuery({
    queryKey: ['context', 'scenarios', companyId, periodId],
    queryFn: () => getScenarios(companyId, periodId),
    enabled: enabled && Boolean(companyId) && Boolean(periodId),
    staleTime: 300_000,
  });
}

export type {
  CompanyOptionResponse,
  PeriodOptionResponse,
  PrincipalResponse,
  ScenarioOptionResponse,
} from '@/generated/models';
