import { test, expect } from '@playwright/test';

test.describe('arduino_dash Admin', () => {

  test('loads all sections', async ({ page }) => {
    await page.goto('/admin');
    // Board selector loads via HTMX
    await expect(page.locator('#admin-board-selector-container')).toBeVisible({ timeout: 5000 });
    // Sketch upload card
    await expect(page.locator('text=Sketch Upload')).toBeVisible();
    // Compile/Upload card
    await expect(page.locator('#compile-upload-card')).toBeVisible();
  });

  test('board selector shows mock ports', async ({ page }) => {
    await page.goto('/admin');
    // Wait for HTMX to populate the selector
    const selector = page.locator('#admin-board-selector-container select');
    await expect(selector).toBeVisible({ timeout: 5000 });
    const options = selector.locator('option');
    await expect(options).toHaveCount(3); // placeholder + 2 mock ports
    await expect(options.nth(1)).toContainText('/dev/ttyTEST0');
    await expect(options.nth(2)).toContainText('/dev/ttyTEST1');
  });

  test('compile upload card shows disabled without active board', async ({ page }) => {
    await page.goto('/admin');
    // Without an active board, compile/upload buttons should be disabled
    await expect(page.locator('#compile-upload-card button')).toHaveAttribute('disabled', '');
  });

});
