import { test, expect } from '@playwright/test';

test.describe('medminder_dash Home', () => {

  test('loads with board grid', async ({ page }) => {
    await page.goto('/');
    // Board grid loads via HTMX
    await expect(page.locator('#board-grid')).toBeVisible({ timeout: 5000 });
  });

  test('board grid shows mock boards', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.board-card')).toHaveCount(2, { timeout: 5000 });
    await expect(page.locator('.board-card').first()).toContainText('TestBoard Uno');
    await expect(page.locator('.board-card').last()).toContainText('TestBoard Mega');
  });

  test('daemon badge shows disconnected', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.daemon-badge')).toContainText('Daemon Disconnected');
  });

});
