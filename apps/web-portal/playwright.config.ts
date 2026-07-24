import { tmpdir } from "node:os";
import { join } from "node:path";

import { defineConfig, devices } from "@playwright/test";


const baseURL =
  process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3100";
const webServerCommand =
  process.env.PLAYWRIGHT_WEB_SERVER_COMMAND ?? "npm run dev";

function shouldReuseExistingServer(): boolean {
  const configured = process.env.PLAYWRIGHT_REUSE_EXISTING_SERVER;
  if (configured === undefined) return !process.env.CI;
  if (configured === "true") return true;
  if (configured === "false") return false;
  throw new Error(
    "PLAYWRIGHT_REUSE_EXISTING_SERVER must be true or false",
  );
}

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  outputDir: join(tmpdir(), "myolab-ai-playwright-results"),
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: webServerCommand,
    url: baseURL,
    reuseExistingServer: shouldReuseExistingServer(),
    timeout: 120_000,
  },
});
