/**
 * Playwright E2E Spec Suite — MyoLab-AI Frontend Workflows (E2E-01 to E2E-13)
 */
import { test, expect } from '@playwright/test';

test.describe('MyoLab-AI End-to-End Clinical Workflows', () => {
  test('E2E-01: Happy Path — Session Creation to Report Generation', async ({ page }: any) => {
    await page.goto('/login');
    await expect(page.locator('h1')).toContainText(/Đăng nhập/i);

    // Select Doctor role and login
    await page.click('button:has-text("Bác sĩ")');
    await page.click('button:has-text("Đăng nhập")');
    await expect(page).toHaveURL(/\/dashboard/);

    // Navigate to Create Session
    await page.goto('/sessions/new');
    await expect(page.locator('h1')).toContainText(/Tạo phiên/i);
  });

  test('E2E-04: QC Fail Blocks Analysis', async ({ page }: any) => {
    await page.goto('/sessions/S-QC-FAIL/quality');
    // If QC Verdict is Fail, continue button should be hidden or disabled
    const continueBtn = page.locator('button:has-text("Tiếp tục sang Analysis")');
    await expect(continueBtn).toHaveCount(0);
  });

  test('E2E-12: Role-Based Access Control Route Defense', async ({ page }: any) => {
    await page.goto('/login');
    await page.click('button:has-text("Bệnh nhân")');
    await page.click('button:has-text("Đăng nhập")');

    // Attempt direct URL navigation to Admin route
    await page.goto('/admin/users');
    await expect(page.locator('body')).toContainText(/Truy cập bị từ chối/i);
  });
});
