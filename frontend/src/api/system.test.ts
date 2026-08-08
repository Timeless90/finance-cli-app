import { describe, expect, it } from "vitest";

import { createApiClient } from "@/api/client";
import { getPlatformInfo, getReadiness } from "@/api/system";

function createContractFetch(): typeof fetch {
  return (async (input: RequestInfo | URL) => {
    const url =
      typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;

    if (url.endsWith("/health/ready")) {
      return new Response(
        JSON.stringify({
          status: "ready",
          service: "cfo-platform-api",
          environment: "test",
          version: "0.3.0",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      );
    }

    if (url.endsWith("/api/v1/platform")) {
      return new Response(
        JSON.stringify({
          name: "CFO Command Center",
          api_version: "v1",
          capabilities: ["planning-foundation", "risk-foundation"],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      );
    }

    return new Response(null, { status: 404 });
  }) as typeof fetch;
}

describe("FE-03 system contracts", () => {
  it("reads readiness and platform contracts through the typed adapter", async () => {
    const client = createApiClient(createContractFetch());

    await expect(getReadiness(client)).resolves.toMatchObject({ status: "ready" });
    await expect(getPlatformInfo(client)).resolves.toMatchObject({ api_version: "v1" });
  });
});
