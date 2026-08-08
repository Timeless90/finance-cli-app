import { expect, test } from "@playwright/test";

test("FE-03 application shell boots and navigates", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL(/\/app\/command-center$/);
  await expect(page.getByRole("heading", { name: "Command Center" })).toBeVisible();
  await expect(page.getByText("LOCAL CONTEXT // NOT YET BACKEND-BOUND")).toBeVisible();

  await page.locator('a[href="/app/planning"]:visible').click();
  await expect(page).toHaveURL(/\/app\/planning$/);
  await expect(page.getByRole("heading", { name: "Planning" })).toBeVisible();
});
