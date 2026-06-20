import { test, expect } from '@playwright/test';

test.describe('arduino_dash Sketch Upload', () => {

  test('sketch selector shows mock sketch', async ({ page }) => {
    await page.goto('/admin');
    // The sketch path selector loads via HTMX from /last-upload
    const selector = page.locator('#sketch_path');
    await expect(selector).toBeVisible({ timeout: 5000 });
    // Should contain the mock sketch entry
    await expect(selector).toContainText('mysketch');
    // Should show board label
    await expect(selector).toContainText('TestBoard Uno');
  });

  test('api sketches endpoint returns sketch list', async ({ page }) => {
    const response = await page.request.get('/api/sketches');
    expect(response.ok()).toBe(true);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBeGreaterThanOrEqual(1);
    expect(data[0]).toHaveProperty('name');
    expect(data[0]).toHaveProperty('path');
    expect(data[0]).toHaveProperty('timestamp');
  });

});
