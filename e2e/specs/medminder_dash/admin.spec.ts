import { test, expect } from '@playwright/test';

test.describe('medminder_dash Admin', () => {

  test('loads all sections', async ({ page }) => {
    await page.goto('/admin');
    // Board selector
    await expect(page.locator('#admin-board-selector-container')).toBeVisible({ timeout: 5000 });
    // Medicine management
    await expect(page.locator('text=Medicines')).toBeVisible();
    // Compile-upload card
    await expect(page.locator('#compile-upload-card')).toBeVisible({ timeout: 5000 });
  });

  test('board selector contains mock ports', async ({ page }) => {
    await page.goto('/admin');
    const selector = page.locator('#admin-board-selector-container select');
    await expect(selector).toBeVisible({ timeout: 5000 });
    await expect(selector).toContainText('/dev/ttyTEST0');
    await expect(selector).toContainText('/dev/ttyTEST1');
  });

});
