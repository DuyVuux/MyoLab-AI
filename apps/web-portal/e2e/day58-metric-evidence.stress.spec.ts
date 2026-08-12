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

    await page.goto('/dashboard/metric-evidence/TEST_METRIC');
    
    const card = page.locator('.metric-evidence');
    await expect(card).toBeVisible();

    // The reason codes list should exist
    const list = page.locator('ul[aria-label="Metric reason codes"]');
    await expect(list).toBeVisible();
    
    // Check bounding box to ensure it doesn't overflow wildly (e.g. height should be constrained or scrollable)
    const box = await card.boundingBox();
    expect(box?.height).toBeLessThan(2000); // Should not infinitely grow
  });
});
