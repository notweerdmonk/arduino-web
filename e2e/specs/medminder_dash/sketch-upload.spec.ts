import { test, expect } from '@playwright/test';

test.describe('medminder_dash Sketch Upload', () => {

  test('sketch selector visible on admin page', async ({ page }) => {
    await page.goto('/admin');
    const selector = page.locator('#sketch_path');
    await expect(selector).toBeVisible({ timeout: 5000 });
    // Should contain the default or mock sketch
    await expect(selector).toContainText('MedMinderV2');
  });

  test('api sketches endpoint returns sketch list', async ({ page }) => {
    const response = await page.request.get('/api/sketches');
    expect(response.ok()).toBe(true);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBeGreaterThanOrEqual(1);
    expect(data[0]).toHaveProperty('name');
    expect(data[0]).toHaveProperty('path');
  });

});
