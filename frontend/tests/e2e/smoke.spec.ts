import { expect, test } from "@playwright/test";

test("Finance 2060 design system preview boots", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Tactical finance interface." })).toBeVisible();
  await expect(page.getByText("NO BACKEND CONTRACT")).toBeVisible();
});
