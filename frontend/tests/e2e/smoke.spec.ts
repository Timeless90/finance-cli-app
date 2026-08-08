import { expect, test } from "@playwright/test";

test("FE-09 downside context flows through risk and market model labs", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /see the future of finance/i })).toBeVisible();
  await page.getByRole("link", { name: "LAUNCH COMMAND CENTER" }).click();
  await expect(page).toHaveURL(/\/app\/command-center$/);
  await page.getByRole("combobox", { name: "SCENARIO", exact: true }).selectOption("local-downside");

  await page.locator('a[href="/app/risk"]:visible').click();
  await expect(page.getByRole("heading", { name: "Risk Command Center" })).toBeVisible();
  await expect(page.getByText("€36.7M", { exact: true })).toHaveCount(2);
  await expect(page.getByText("Combined downside")).toBeVisible();

  await page.locator('a[href="/app/market-risk"]:visible').click();
  await expect(page).toHaveURL(/\/app\/market-risk$/);
  await expect(page.getByRole("heading", { name: "Market Risk Lab" })).toBeVisible();
  await expect(page.getByText("42.8%", { exact: true })).toHaveCount(2);
  await expect(page.getByText("€8.9M", { exact: true })).toBeVisible();
  await expect(page.getByText("ACTION REQUIRED")).toBeVisible();
});
