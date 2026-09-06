import { expect, test } from '@playwright/test';

test.skip(!process.env.CFO_LIVE_E2E, 'Requires the local UAT API and gateway.');

test('UAT context drives all currently published live workspaces', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('link', { name: 'LAUNCH COMMAND CENTER' }).click();

  await expect(page.getByRole('heading', { name: 'Command Center' })).toBeVisible();
  await expect(page.getByText('LIVE API CONNECTED', { exact: true })).toBeVisible();
  await page
    .getByRole('combobox', { name: 'PERIOD', exact: true })
    .selectOption('2026-08');
  await page
    .getByRole('combobox', { name: 'SCENARIO', exact: true })
    .selectOption('downside');

  const workspaces: Array<[string, string]> = [
    ['/app/risk', 'Risk Command Center'],
    ['/app/market-risk', 'Market Risk Lab'],
    ['/app/planning', 'Planning'],
    ['/app/performance', 'Performance'],
    ['/app/profitability', 'Profitability'],
    ['/app/liquidity', 'Liquidity'],
    ['/app/actions', 'Action Steering'],
    ['/app/capital', 'Capital Allocation'],
    ['/app/reports', 'Reporting Studio'],
    ['/app/data', 'Data & Governance'],
    ['/app/copilot', 'Financial Copilot'],
  ];
  for (const [route, heading] of workspaces) {
    await page.goto(route);
    await expect(
      page.getByRole('heading', { name: heading, exact: true }),
    ).toBeVisible();
    await expect(page.getByText('LIVE API CONNECTED', { exact: true })).toBeVisible();
  }

  await page.goto('/app/reports');
  await page.getByRole('button', { name: 'CREATE MANAGEMENT PACK' }).click();
  await expect(page.getByText(/DRAFT \/\//)).toBeVisible();

  await page.goto('/app/copilot');
  await page.getByRole('button', { name: 'START SECURE SESSION' }).click();
  await expect(page.getByText(/SOURCES uat-snapshot-v1/)).toBeVisible();
  await page.getByLabel('QUESTION').fill('Summarize the published source.');
  await page.getByRole('button', { name: 'SEND' }).click();
  await expect(page.getByText('APPROVED_FACTS:')).toBeVisible();
  await expect(page.getByText('uat-snapshot-v1').first()).toBeVisible();

  await page.goto('/app/actions');
  await page.getByRole('button', { name: 'START SIMULATION' }).click();
  await expect(page.getByText(/DRAFT \/\/ RUN/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'VALIDATE' }).first()).toBeVisible();
  await page.getByRole('button', { name: 'PRIORITIZE ACTIONS' }).click();
  await expect(page.getByText('VIEW SERVER RESULT & LINEAGE').first()).toBeVisible();
  await page.getByRole('button', { name: 'TRACK BENEFITS' }).click();
  await expect(page.getByText('VIEW SERVER RESULT & LINEAGE').first()).toBeVisible();

  await page.goto('/app/capital');
  await page.getByRole('button', { name: 'START ALLOCATION' }).click();
  await expect(page.getByText(/DRAFT \/\/ RUN/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'VALIDATE' }).first()).toBeVisible();
  await page.getByRole('button', { name: 'VALUE CANDIDATE' }).click();
  await expect(page.getByText('VIEW SERVER RESULT & LINEAGE').first()).toBeVisible();
  await page.getByRole('button', { name: 'SIMULATE NPV' }).click();
  await expect(page.getByText('VIEW SERVER RESULT & LINEAGE').first()).toBeVisible();
  await page.getByRole('button', { name: 'EVALUATE FUNDING' }).click();
  await expect(page.getByText('VIEW SERVER RESULT & LINEAGE').first()).toBeVisible();
});
