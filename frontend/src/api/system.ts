import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";
import type { HealthResponse, PlatformResponse } from "@/api/contracts";
import { toApiContractError } from "@/api/errors";

export async function getReadiness(): Promise<HealthResponse> {
  const { data, error, response } = await apiClient.GET("/health/ready");
  if (!data) {
    throw toApiContractError(response, error);
  }
  return data;
}

export async function getPlatformInfo(): Promise<PlatformResponse> {
  const { data, error, response } = await apiClient.GET("/api/v1/platform");
  if (!data) {
    throw toApiContractError(response, error);
  }
  return data;
}

export function useSystemContract() {
  return useQuery({
    queryKey: ["system-contract"],
    queryFn: async () => {
      const [readiness, platform] = await Promise.all([getReadiness(), getPlatformInfo()]);
      return { readiness, platform };
    },
    staleTime: 30_000,
    refetchInterval: 60_000,
    retry: 1,
  });
}
