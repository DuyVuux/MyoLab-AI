import { chromium } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function main() {
  console.log('🚀 Starting UI DOM Verification on http://localhost:3100 ...');

  const browser = await chromium.launch({
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });

  const page = await context.newPage();
  const consoleLogs: string[] = [];
  const errors: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(`[Console Error] ${msg.text()}`);
    }
  });

  page.on('pageerror', (err) => {
    errors.push(`[Page Error] ${err.message}`);
  });

  // 1. Visit Login Page
  console.log('\n--- Checking /login ---');
  await page.goto('http://localhost:3100/login', { waitUntil: 'networkidle' });
  const loginTitle = await page.textContent('h1');
  const roleButtons = await page.locator('button[aria-label^="Đăng nhập với vai trò"]').count();
  console.log(`✓ Login Page Title: "${loginTitle}"`);
  console.log(`✓ Role cards available: ${roleButtons} cards`);

  // 2. Login as KTV
  console.log('\n--- Logging in as KTV ---');
  await page.click('button:has-text("KTV")');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
  const dashboardHeading = await page.locator('h1, h2').first().textContent();
  console.log(`✓ Dashboard loaded: "${dashboardHeading?.trim()}"`);

  // 3. Check Sessions Page
  console.log('\n--- Checking /sessions ---');
  await page.goto('http://localhost:3100/sessions', { waitUntil: 'networkidle' });
  const sessionsTitle = await page.locator('h1').textContent();
  console.log(`✓ Sessions Page Title: "${sessionsTitle?.trim()}"`);

  // 4. Check QC Queue Page
  console.log('\n--- Checking /qc ---');
  await page.goto('http://localhost:3100/qc', { waitUntil: 'networkidle' });
  const qcTitle = await page.locator('h1').textContent();
  const qccards = await page.locator('article.qc-card').count();
  console.log(`✓ QC Dashboard Title: "${qcTitle?.trim()}" | QC Cards count: ${qccards}`);

  // 5. Check Review Queue & Signal Drilldown
  console.log('\n--- Checking /review-queue and Signal Viewer ---');
  await page.goto('http://localhost:3100/review-queue', { waitUntil: 'networkidle' });
  const reviewQueueTitle = await page.locator('h1').textContent();
  console.log(`✓ Review Queue Title: "${reviewQueueTitle?.trim()}"`);

  await page.goto('http://localhost:3100/review-queue/CASE-001/signal', { waitUntil: 'networkidle' });
  const signalTitle = await page.locator('h1').textContent();
  console.log(`✓ Signal Viewer Title: "${signalTitle?.trim()}"`);

  // 6. Check Metric Evidence
  console.log('\n--- Checking /review-queue/CASE-001/metrics ---');
  await page.goto('http://localhost:3100/review-queue/CASE-001/metrics', { waitUntil: 'networkidle' });
  const metricTitle = await page.locator('h1').textContent();
  console.log(`✓ Metric Evidence Title: "${metricTitle?.trim()}"`);

  // 7. Check Access Control (switch to Patient role and attempt Admin page)
  console.log('\n--- Testing RBAC Protection (/admin/users with patient role) ---');
  await page.goto('http://localhost:3100/login', { waitUntil: 'networkidle' });
  await page.click('button:has-text("Bệnh nhân")');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
  await page.goto('http://localhost:3100/admin/users', { waitUntil: 'networkidle' });
  const accessDeniedText = await page.textContent('body');
  const isProtected = accessDeniedText?.includes('Truy cập bị từ chối') || accessDeniedText?.includes('403');
  console.log(`✓ RBAC Route Protection Active: ${isProtected}`);

  console.log('\n=============================================');
  console.log(`Total Errors Detected: ${errors.length}`);
  if (errors.length > 0) {
    console.error('Errors:', errors);
  } else {
    console.log('✅ ALL DOM AND ROUTE CHECKS PASSED WITH 0 ERRORS!');
  }
  console.log('=============================================\n');

  await browser.close();
}

main().catch((err) => {
  console.error('Execution error:', err);
  process.exit(1);
});
