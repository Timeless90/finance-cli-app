import { http, HttpResponse } from "msw";

import type { HealthResponse, PlatformResponse } from "@/api/contracts";

const readiness: HealthResponse = {
  status: "ready",
  service: "cfo-platform-api",
  environment: "mock",
  version: "0.3.0",
};

const platform: PlatformResponse = {
  name: "CFO Command Center",
  api_version: "v1",
  capabilities: [
    "enterprise-domain",
    "model-execution-ports",
    "planning-foundation",
    "risk-foundation",
    "background-jobs",
  ],
};

export const handlers = [
  http.get("*/health/ready", () => HttpResponse.json(readiness)),
  http.get("*/api/v1/platform", () => HttpResponse.json(platform)),
];
