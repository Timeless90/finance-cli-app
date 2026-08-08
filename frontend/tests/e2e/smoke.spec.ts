import { expect, test } from "@playwright/test";

test("FE-05 landing enters the executive command center", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /see the future of finance/i })).toBeVisible();
  await expect(page.getByText("PUBLIC LANDING // NO BUSINESS API DEPENDENCY // FE-04")).toBeVisible();

  await page.getByRole("link", { name: "LAUNCH COMMAND CENTER" }).click();
  await expect(page).toHaveURL(/\/app\/command-center$/);
  await expect(page.getByRole("heading", { name: "Command Center" })).toBeVisible();
  await expect(page.getByText("MOCK CONNECTED")).toBeVisible();
  await expect(page.getByText("€82.4M")).toBeVisible();

  await page.getByRole("combobox", { name: "SCENARIO", exact: true }).selectOption("local-downside");
  await expect(page.getByText("€68.9M")).toBeVisible();
  await expect(page.getByText(/Downside scenario requires immediate margin and cash protection/i)).toBeVisible();
});
