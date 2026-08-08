import createClient from "openapi-fetch";

import type { paths } from "@/api/generated/schema";
import { apiConfig } from "@/api/config";

export const apiClient = createClient<paths>({
  baseUrl: apiConfig.baseUrl,
});
