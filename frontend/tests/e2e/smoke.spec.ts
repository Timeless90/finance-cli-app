import { expect, test } from "@playwright/test";

test("frontend foundation boots", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Frontend foundation online." })).toBeVisible();
  await expect(page.getByText("/api/v1")).toBeVisible();
});
