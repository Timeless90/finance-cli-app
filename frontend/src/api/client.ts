import createClient from "openapi-fetch";

import type { paths } from "@/api/generated/schema";
import { apiConfig } from "@/api/config";

export const apiClient = createClient<paths>({
  baseUrl: apiConfig.baseUrl,
  // Resolve the current global fetch at request time. This keeps the production
  // client compatible with browser fetch while allowing MSW/test transports to
  // intercept requests without changing generated API contracts.
  fetch: (...args) => fetch(...args),
});
