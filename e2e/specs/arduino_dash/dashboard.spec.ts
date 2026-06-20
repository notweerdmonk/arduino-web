import { test, expect } from '@playwright/test';

test.describe('arduino_dash Dashboard', () => {

  test('loads with empty state showing no boards', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#board-grid')).toContainText('No boards detected');
    await expect(page.locator('#daemon-badge')).toContainText('Daemon Disconnected');
  });

  test('board grid shows mock board cards', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.board-card')).toHaveCount(2);
    await expect(page.locator('.board-card').first()).toContainText('TestBoard Uno');
    await expect(page.locator('.board-card').first()).toContainText('/dev/ttyTEST0');
    await expect(page.locator('.board-card').first()).toContainText('arduino:avr:uno');
    await expect(page.locator('.board-card').first()).toContainText('Connected');
  });

  test('manage link navigates to board detail', async ({ page }) => {
    await page.goto('/');
    await page.locator('.board-card a:has-text("Manage")').first().click();
    await expect(page).toHaveURL(/\/board\/dev\/ttyTEST0/);
  });

});
