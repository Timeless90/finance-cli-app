import { describe, expect, it } from "vitest";

import { getPlatformInfo, getReadiness } from "@/api/system";

describe("FE-03 system contracts", () => {
  it("reads readiness and platform contracts through the typed adapter", async () => {
    await expect(getReadiness()).resolves.toMatchObject({ status: "ready" });
    await expect(getPlatformInfo()).resolves.toMatchObject({ api_version: "v1" });
  });
});
