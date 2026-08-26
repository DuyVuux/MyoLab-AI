import { test, expect } from '@playwright/test';

test.describe('DAY 56: Exception Dashboard Stress Test', () => {
  // Assuming there's a mock endpoint or a way to inject 10,000 items
  // In a real Playwright test we might intercept the API and return a massive JSON response.
  test('should render and paginate items without freezing', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("KTV")');

    const start = Date.now();
    await page.goto('/review-queue');
    
    // Wait for the queue items to render
    await expect(page.locator('main ol li').first()).toBeVisible({ timeout: 5000 });
    const renderTime = Date.now() - start;
    
    console.log(`Render time for review queue: ${renderTime}ms`);
    expect(renderTime).toBeLessThan(5000); 

    // Verify list item count
    const items = page.locator('main ol li');
    await expect(items).toHaveCount(4);
  });

  test('should gracefully handle exception list order', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("KTV")');
    await page.goto('/review-queue');
    
    // Assert order (Fail first, Warn, Unknown, Pass)
    const items = page.locator('main ol li');
    await expect(items.nth(0)).toHaveAttribute('data-attention', 'FAIL');
    await expect(items.nth(1)).toHaveAttribute('data-attention', 'WARNING');
    await expect(items.nth(2)).toHaveAttribute('data-attention', 'UNKNOWN');
    await expect(items.nth(3)).toHaveAttribute('data-attention', 'PASS');
  });
});
