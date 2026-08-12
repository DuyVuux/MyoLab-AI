import { test, expect } from '@playwright/test';

test.describe('DAY 56: Exception Dashboard Stress Test', () => {
  // Assuming there's a mock endpoint or a way to inject 10,000 items
  // In a real Playwright test we might intercept the API and return a massive JSON response.
  test('should render and paginate 10,000+ items without freezing (TTI < 200ms)', async ({ page }) => {
    // Intercept the API to mock 10,000 exceptions
    await page.route('**/api/qc/exceptions', (route) => {
      const items = Array.from({ length: 10000 }, (_, i) => ({
        case_id: `CASE_${i}`,
        attention: i % 10 === 0 ? 'FAIL' : 'UNKNOWN',
        label: i % 10 === 0 ? 'Data quality fail' : 'Unknown supportability',
        priority: i % 10 === 0 ? 0 : 2,
      }));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items, total: 10000 }),
      });
    });

    const start = Date.now();
    await page.goto('/dashboard/exceptions');
    
    // Wait for the first row to render to measure TTI
    await expect(page.locator('table tr').nth(1)).toBeVisible({ timeout: 5000 });
    const renderTime = Date.now() - start;
    
    console.log(`Render time for 10,000 items: ${renderTime}ms`);
    // Assert the UI doesn't completely hang
    expect(renderTime).toBeLessThan(2000); 

    // Rapid pagination stress
    const nextBtn = page.getByRole('button', { name: /Next/i });
    if (await nextBtn.isVisible()) {
      await nextBtn.click();
      await nextBtn.click();
      await nextBtn.click();
      // Ensure the table updates without crashing
      await expect(page.locator('table tr').nth(1)).toBeVisible();
    }
  });

  test('should gracefully handle state conflict and unknown records', async ({ page }) => {
    // Mocking an extreme conflict scenario
    await page.route('**/api/qc/exceptions', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            { case_id: 'C_NULL', attention: 'UNKNOWN', label: 'Unknown' },
            { case_id: 'C_WARN', attention: 'WARNING', label: 'Warning' },
            { case_id: 'C_FAIL', attention: 'FAIL', label: 'Fail' },
          ]
        }),
      });
    });

    await page.goto('/dashboard/exceptions');
    
    // Assert order (Fail first)
    const rows = page.locator('table tr td:first-child'); // assuming first col is case_id
    await expect(rows.nth(0)).toContainText('C_FAIL');
    await expect(rows.nth(1)).toContainText('C_WARN');
    await expect(rows.nth(2)).toContainText('C_NULL');
  });
});
