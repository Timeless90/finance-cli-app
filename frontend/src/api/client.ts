import createClient from "openapi-fetch";

import { apiConfig } from "@/api/config";
import type { paths } from "@/api/generated/schema";

export function createApiClient(fetchFn: typeof fetch = (...args) => fetch(...args)) {
  return createClient<paths>({
    baseUrl: apiConfig.baseUrl,
    fetch: fetchFn,
  });
}

export type ApiClient = ReturnType<typeof createApiClient>;

export const apiClient = createApiClient();
