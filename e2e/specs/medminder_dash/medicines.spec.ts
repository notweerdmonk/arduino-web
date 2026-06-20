import { test, expect } from '@playwright/test';

test.describe('medminder_dash Medicines', () => {

  test('api returns mock medicines', async ({ page }) => {
    const response = await page.request.get('/api/medicines');
    expect(response.ok()).toBe(true);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
    expect(data).toHaveLength(3);
    expect(data[0].name).toBe('Aspirin');
    expect(data[1].name).toBe('VitaminD');
    expect(data[2].name).toBe('Ibuprofen');
  });

  test('all mock medicines have valid times', async ({ page }) => {
    const response = await page.request.get('/api/medicines');
    const data = await response.json();
    for (const med of data) {
      expect(med.hour).toBeGreaterThanOrEqual(0);
      expect(med.hour).toBeLessThan(24);
      expect(med.minute).toBeGreaterThanOrEqual(0);
      expect(med.minute).toBeLessThan(60);
      expect(med.enabled).toBe(true);
    }
  });

  test('medicine has expected fields', async ({ page }) => {
    const response = await page.request.get('/api/medicines');
    const data = await response.json();
    const med = data[0];
    expect(med).toHaveProperty('id');
    expect(med).toHaveProperty('name');
    expect(med).toHaveProperty('hour');
    expect(med).toHaveProperty('minute');
    expect(med).toHaveProperty('day_of_week');
    expect(med).toHaveProperty('day_of_month');
    expect(med).toHaveProperty('enabled');
  });

});
