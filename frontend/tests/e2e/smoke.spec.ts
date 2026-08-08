import { expect, test } from "@playwright/test";

test("FE-04 landing enters the application shell", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /see the future of finance/i })).toBeVisible();
  await expect(page.getByText("PUBLIC LANDING // NO BUSINESS API DEPENDENCY // FE-04")).toBeVisible();

  await page.getByRole("link", { name: "LAUNCH COMMAND CENTER" }).click();
  await expect(page).toHaveURL(/\/app\/command-center$/);
  await expect(page.getByRole("heading", { name: "Command Center" })).toBeVisible();
});
