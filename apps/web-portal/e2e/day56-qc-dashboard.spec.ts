import { test, expect } from '@playwright/test';

test.describe('Exception-first QC Dashboard', () => {
  test('should render dashboard with correct safe labels and ordering', async ({ page }) => {
    // Navigate to the QC page we just created
    await page.goto('/qc');

    // Verify Title and Research Notice
    await expect(page.locator('h1#qc-dashboard-title')).toHaveText('Exception-first QC queue');
    await expect(page.locator('aside[role="note"]')).toContainText('RESEARCH ONLY');

    // Verify the items are rendered
    const cards = page.locator('article.qc-card');
    await expect(cards).toHaveCount(4); // based on our mock data

    // Test ordering (Exception first: FAIL -> WARNING -> UNKNOWN -> PASS)
    const firstCardLabel = await cards.nth(0).locator('h2').textContent();
    const secondCardLabel = await cards.nth(1).locator('h2').textContent();
    const thirdCardLabel = await cards.nth(2).locator('h2').textContent();
    const fourthCardLabel = await cards.nth(3).locator('h2').textContent();

    expect(firstCardLabel).toBe('Data quality fail');
    expect(secondCardLabel).toBe('Review warning');
    expect(thirdCardLabel).toBe('Not evaluated');
    expect(fourthCardLabel).toBe('Quality pass');

    // Verify reason codes are displayed correctly
    await expect(cards.nth(0).locator('ul[aria-label="Reason codes"] li')).toHaveText(['ARTIFACT_OVERLOAD']);
    
    // Verify missing reasons text
    await expect(cards.nth(2).locator('p[data-reasons="none"]')).toBeVisible();
  });
});
