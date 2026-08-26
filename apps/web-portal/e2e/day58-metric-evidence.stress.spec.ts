import { test, expect } from '@playwright/test';

test.describe('DAY 58: Metric Evidence Viewer Stress Test', () => {
  test('should render extreme reason codes without breaking layout', async ({ page }) => {
    await page.route('**/api/metrics/evidence', (route) => {
      const reasons = Array.from({ length: 100 }, (_, i) => `EXTREME_REASON_CODE_OVERFLOW_${i}`);
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          metric: {
            metric_name: `RMS_EXTREME`,
            status: 'BLOCKED',
            reason_codes: reasons,
          }
        }),
      });
    });

    await page.goto('/login');
    await page.click('button:has-text("KTV")');
    await page.goto('/review-queue/TEST_METRIC/metrics');
    
    await expect(page.getByRole('heading', { name: /Metric Evidence/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'MFCV' })).toBeVisible();
    await expect(page.getByText(/ELECTRODE_GEOMETRY_NOT_VERIFIED/i)).toBeVisible();
  });
});
