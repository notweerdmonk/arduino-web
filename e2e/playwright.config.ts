import { defineConfig } from '@playwright/test';

/**
 * Playwright E2E test configuration for Arduino Web dashboards.
 *
 * Defines two projects (arduino-dash, medminder-dash) with auto-managed
 * mock Flask servers via webServer entries.
 *
 * @module e2e/playwright.config
 */

export default defineConfig({
  testDir: './specs',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  timeout: 30000,
  use: {
    baseURL: 'http://127.0.0.1:8765',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    viewport: { width: 1280, height: 720 },
  },
  projects: [
    {
      name: 'arduino-dash',
      testMatch: 'specs/arduino_dash/**',
      use: {
        baseURL: 'http://127.0.0.1:8765',
      },
    },
    {
      name: 'medminder-dash',
      testMatch: 'specs/medminder_dash/**',
      use: {
        baseURL: 'http://127.0.0.1:8766',
      },
    },
  ],
  webServer: [
    {
      command: 'python3 e2e/servers/arduino_dash_server.py --mock --port 8765',
      port: 8765,
      reuseExistingServer: !process.env.CI,
      cwd: '../',
    },
    {
      command: 'python3 e2e/servers/medminder_dash_server.py --mock --port 8766',
      port: 8766,
      reuseExistingServer: !process.env.CI,
      cwd: '../',
    },
  ],
});
