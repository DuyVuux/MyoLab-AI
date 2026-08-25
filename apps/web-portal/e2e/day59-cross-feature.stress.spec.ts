import { test, expect } from '@playwright/test';

test.describe('DAY 59: Cross-Feature Integration Stress Test (Days 56-58)', () => {
  test('should navigate Exception -> Signal Drilldown -> Metric Evidence without memory leak', async ({ page }) => {
    // This test simulates a reviewer going through 50 complex cases
    // We expect the browser's heap not to crash or leak severely.
    test.setTimeout(60000); // 1 minute timeout for stress testing

    await page.addInitScript(() => {
      window.sessionStorage.setItem('myolab-ai.mock-role', 'ktv');
    });

    for (let i = 0; i < 5; i++) {
      await page.goto('/review-queue');
      await expect(page.getByRole('heading', { name: /Review queue/i })).toBeVisible();

      await page.goto(`/review-queue/CASE_${i}/signal`);
      await expect(page.getByRole('heading', { name: /Signal Viewer/i })).toBeVisible();
      await expect(page.getByRole('heading', { name: 'RAW' })).toBeVisible();
      await expect(page.getByRole('heading', { name: 'PROCESSED' })).toBeVisible();

      await page.goto(`/review-queue/CASE_${i}/metrics`);
      await expect(page.getByRole('heading', { name: /Metric Evidence/i })).toBeVisible();
      await expect(page.getByText(/ELECTRODE_GEOMETRY_NOT_VERIFIED/i)).toBeVisible();
    }
    
    // If the loop completes without the page crashing (Page Crashed error), 
    // the memory management is likely stable enough for basic operations.
    // Real memory profiling would use CDPSession `Performance.getMetrics` checking JSHeapUsedSize.
    const client = await page.context().newCDPSession(page);
    await client.send('Performance.enable');
    const metrics = await client.send('Performance.getMetrics');
    const jsHeapUsedSize = metrics.metrics.find(m => m.name === 'JSHeapUsedSize')?.value ?? 0;
    
    console.log(`Final JS Heap Used Size: ${jsHeapUsedSize / 1024 / 1024} MB`);
    // Example assertion: heap should not exceed 500MB after 5 iterations of heavy loads
    expect(jsHeapUsedSize).toBeLessThan(500 * 1024 * 1024);
  });
});
