import { defineConfig, devices } from '@playwright/test';
const live = process.env.CFO_LIVE_E2E === '1';
const frontendPort = live ? 15173 : 15174;
export default defineConfig({
  testDir: './e2e',
  testMatch: live ? '**/live-uat.spec.ts' : '**/smoke.spec.ts',
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: `http://127.0.0.1:${frontendPort}`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    ...(live
      ? [
          {
            command:
              'uv run --project ../backend uvicorn app.main:app --host 127.0.0.1 --port 18000',
            url: 'http://127.0.0.1:18000/health/ready',
            reuseExistingServer: false,
            env: { CFO_ENVIRONMENT: 'uat', CFO_TELEMETRY_ENABLED: 'false' },
            timeout: 120000,
          },
        ]
      : []),
    {
      command: `pnpm exec vite --host 127.0.0.1 --port ${frontendPort} --strictPort --mode ${live ? 'uat' : 'test'}`,
      url: `http://127.0.0.1:${frontendPort}`,
      reuseExistingServer: false,
      timeout: 120000,
      env: {
        VITE_API_MODE: live ? 'live' : 'mock',
        CFO_UAT_GATEWAY: 'true',
        CFO_API_TARGET: 'http://127.0.0.1:18000',
      },
    },
  ],
});
