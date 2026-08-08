import { expect, test } from "@playwright/test";

test("FE-06 scenario context flows from command center into planning and performance", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /see the future of finance/i })).toBeVisible();
  await page.getByRole("link", { name: "LAUNCH COMMAND CENTER" }).click();
  await expect(page).toHaveURL(/\/app\/command-center$/);
  await expect(page.getByRole("heading", { name: "Command Center" })).toBeVisible();

  await page.getByRole("combobox", { name: "SCENARIO", exact: true }).selectOption("local-downside");
  await expect(page.getByText(/Downside scenario requires immediate margin and cash protection/i)).toBeVisible();

  await page.locator('a[href="/app/planning"]:visible').click();
  await expect(page).toHaveURL(/\/app\/planning$/);
  await expect(page.getByRole("heading", { name: "Planning" })).toBeVisible();
  await expect(page.getByText("fcst-fy26-p08-downside-v3")).toBeVisible();
  await expect(page.getByText("15.3%", { exact: true })).toBeVisible();

  await page.locator('a[href="/app/performance"]:visible').click();
  await expect(page).toHaveURL(/\/app\/performance$/);
  await expect(page.getByRole("heading", { name: "Performance" })).toBeVisible();
  await expect(page.getByText("-2.6%", { exact: true })).toBeVisible();
  await expect(page.getByText("AN-031")).toBeVisible();
});
