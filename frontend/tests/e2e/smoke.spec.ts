import { expect, test } from "@playwright/test";

test("FE-08 downside context flows across core finance and risk workspaces", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /see the future of finance/i })).toBeVisible();
  await page.getByRole("link", { name: "LAUNCH COMMAND CENTER" }).click();
  await expect(page).toHaveURL(/\/app\/command-center$/);
  await page.getByRole("combobox", { name: "SCENARIO", exact: true }).selectOption("local-downside");

  await page.locator('a[href="/app/planning"]:visible').click();
  await expect(page.getByRole("heading", { name: "Planning" })).toBeVisible();
  await expect(page.getByText("fcst-fy26-p08-downside-v3")).toBeVisible();

  await page.locator('a[href="/app/performance"]:visible').click();
  await expect(page.getByRole("heading", { name: "Performance" })).toBeVisible();
  await expect(page.getByText("AN-031")).toBeVisible();

  await page.locator('a[href="/app/profitability"]:visible').click();
  await expect(page.getByRole("heading", { name: "Profitability" })).toBeVisible();
  await expect(page.getByText("€24.7M", { exact: true })).toBeVisible();

  await page.locator('a[href="/app/liquidity"]:visible').click();
  await expect(page.getByRole("heading", { name: "Liquidity" })).toBeVisible();
  await expect(page.getByText("78d", { exact: true })).toBeVisible();
  await expect(page.getByText(/Emergency liquidity plan/i)).toBeVisible();

  await page.locator('a[href="/app/risk"]:visible').click();
  await expect(page).toHaveURL(/\/app\/risk$/);
  await expect(page.getByRole("heading", { name: "Risk Command Center" })).toBeVisible();
  await expect(page.getByText("€36.7M", { exact: true })).toHaveCount(2);
  await expect(page.getByText("Combined downside")).toBeVisible();
});
