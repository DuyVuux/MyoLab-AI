import { test, expect } from "@playwright/test";

test("real auto-data browser path: Noraxon single CSV -> quality evidence", async ({ page }) => {
  const fixture = process.env.UI_I4_NORAXON_SINGLE_CSV;
  test.skip(!fixture, "UI_I4_NORAXON_SINGLE_CSV is required for the real final smoke");

  await page.addInitScript(() => {
    sessionStorage.setItem("myolab-ai.mock-role", "ktv");
  });

  await page.goto("/sessions/auto-intake");

  const input = page.locator('input[type="file"]');
  await input.setInputFiles(fixture!);

  await page.getByRole("button", { name: /Import and run automatically/i }).click();

  await expect(page.getByText("Source hash", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "5. Quality evidence" })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByText(/Overall/i)).toBeVisible();

  // This final real-path spec intentionally contains no page.route interception.
});
