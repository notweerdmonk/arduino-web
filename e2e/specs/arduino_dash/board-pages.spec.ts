import { test, expect } from '@playwright/test';

test.describe('arduino_dash Board Pages', () => {

  test('board detail page shows board info', async ({ page }) => {
    await page.goto('/board/dev/ttyTEST0');
    await expect(page.locator('text=TestBoard Uno')).toBeVisible();
    await expect(page.locator('text=/dev/ttyTEST0')).toBeVisible();
    await expect(page.locator('text=arduino:avr:uno')).toBeVisible();
  });

  test('connection badge shows connected', async ({ page }) => {
    await page.goto('/board/dev/ttyTEST0/connection-status');
    await expect(page.locator('text=Connected')).toBeVisible();
  });

  test('connection badge shows disconnected for unknown port', async ({ page }) => {
    await page.goto('/board/dev/ttyNOPE/connection-status');
    await expect(page.locator('text=Disconnected')).toBeVisible();
  });

  test('daemon status shows disconnected', async ({ page }) => {
    await page.goto('/daemon/status');
    await expect(page.locator('.daemon-badge')).toContainText('Daemon Disconnected');
  });

});
