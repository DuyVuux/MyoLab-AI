import { mkdirSync } from "node:fs";
import { join } from "node:path";

import { expect, test, type Page } from "@playwright/test";

const evidenceDir = join(
  process.cwd(),
  "../../qa-validation/evidence/full-ui-audit-2026-08-25",
);

const viewports = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "laptop", width: 1280, height: 800 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "mobile", width: 390, height: 844 },
] as const;

const routes = [
  { name: "dashboard", path: "/dashboard", heading: /tổng quan|operations|dashboard/i, role: "ktv" },
  { name: "sessions-auto-intake", path: "/sessions/auto-intake", heading: /auto|intake|quality/i, role: "ktv" },
  { name: "use-cases", path: "/use-cases", heading: /use case/i, role: "ktv" },
  { name: "sessions", path: "/sessions", heading: /phiên|session/i, role: "ktv" },
  { name: "imports", path: "/imports", heading: /import/i, role: "ktv" },
  { name: "analyses", path: "/analyses", heading: /phân tích|analysis/i, role: "ktv" },
  { name: "feedback-inbox", path: "/feedback/inbox", heading: /phản hồi|feedback/i, role: "researcher" },
  { name: "data-quality-issues", path: "/data-quality/issues", heading: /quality|chất lượng|issue/i, role: "ktv" },
  { name: "uc1-intro", path: "/uc1/intro", heading: /uc1|biofeedback|cử chỉ/i, role: "ktv" },
  { name: "uc2-intro", path: "/uc2/intro", heading: /uc2|định lượng|quantitative/i, role: "ktv" },
  { name: "uc3-intro", path: "/uc3/intro", heading: /uc3|chi giả|prosthetic/i, role: "ktv" },
  { name: "uc4-intro", path: "/uc4/intro", heading: /uc4|hmi|vô trùng/i, role: "ktv" },
  { name: "devices", path: "/devices", heading: /thiết bị|device/i, role: "admin" },
  { name: "protocols", path: "/protocols", heading: /protocol/i, role: "admin" },
  { name: "audit", path: "/audit", heading: /audit/i, role: "admin" },
  { name: "admin-users", path: "/admin/users", heading: /admin|người dùng|user/i, role: "admin" },
  { name: "review-queue", path: "/review-queue", heading: /review|hàng đợi|queue/i, role: "ktv" },
  { name: "qc", path: "/qc", heading: /qc|quality/i, role: "ktv" },
] as const;

test.describe("full UI quality audit", () => {
  test.beforeAll(() => {
    mkdirSync(evidenceDir, { recursive: true });
  });

  for (const viewport of viewports) {
    test.describe(`${viewport.name} ${viewport.width}x${viewport.height}`, () => {
      test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
      });

      for (const route of routes) {
        test(`${route.name} renders safely`, async ({ page }) => {
          await page.goto("/login", { waitUntil: "domcontentloaded" });
          await page.waitForLoadState("networkidle", { timeout: 15_000 }).catch(() => undefined);
          await page.evaluate((role) => {
            window.sessionStorage.setItem("myolab-ai.mock-role", role);
          }, route.role);

          const consoleErrors = collectConsoleErrors(page);
          const failedRequests = collectFailedRequests(page);

          await page.goto(route.path, { waitUntil: "domcontentloaded" });
          await page.waitForLoadState("networkidle", { timeout: 15_000 }).catch(() => undefined);

          await page.screenshot({
            path: join(evidenceDir, `${route.name}-${viewport.name}.png`),
            fullPage: true,
          });

          await expect(page.locator("main#main-content")).toBeVisible();
          await expect(page.locator("body")).not.toContainText(/Unhandled Runtime Error|Application error|Internal Server Error/i);
          await expect(page.getByRole("heading", { name: route.heading }).first()).toBeVisible();

          await assertNoHorizontalOverflow(page);
          await assertControlsHaveAccessibleNames(page);
          await assertNoObviousTextOverlap(page);

          expect(consoleErrors, "serious console errors").toEqual([]);
          expect(failedRequests, "failed network requests").toEqual([]);
        });
      }
    });
  }
});

function collectConsoleErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on("console", (message) => {
    if (message.type() !== "error") return;
    const text = message.text();
    if (/favicon\.ico/i.test(text)) return;
    errors.push(sanitizeEvidence(text));
  });
  page.on("pageerror", (error) => {
    errors.push(sanitizeEvidence(error.message));
  });
  return errors;
}

function collectFailedRequests(page: Page): string[] {
  const failures: string[] = [];
  page.on("requestfailed", (request) => {
    const failure = request.failure();
    const url = new URL(request.url());
    const errorText = failure?.errorText ?? "request failed";
    if (url.pathname === "/favicon.ico") return;
    if (url.pathname.startsWith("/_next/static/") && errorText === "net::ERR_ABORTED") return;
    failures.push(`${request.method()} ${url.origin}${url.pathname}: ${errorText}`);
  });
  return failures;
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const metrics = await page.evaluate(() => ({
    documentWidth: document.documentElement.scrollWidth,
    viewportWidth: window.innerWidth,
    bodyWidth: document.body.scrollWidth,
  }));
  const overflow = Math.max(metrics.documentWidth, metrics.bodyWidth) - metrics.viewportWidth;
  expect(overflow, `horizontal overflow ${JSON.stringify(metrics)}`).toBeLessThanOrEqual(2);
}

async function assertControlsHaveAccessibleNames(page: Page): Promise<void> {
  const unnamedControls = await page.locator("button, input, select, textarea").evaluateAll((elements) => {
    return elements.flatMap((element) => {
      const control = element as HTMLElement;
      if (control.hasAttribute("disabled")) return [];
      const ariaLabel = control.getAttribute("aria-label")?.trim();
      const labelledBy = control.getAttribute("aria-labelledby")?.trim();
      const title = control.getAttribute("title")?.trim();
      const text = control.innerText?.trim();
      const id = control.getAttribute("id");
      const label = id ? document.querySelector(`label[for="${CSS.escape(id)}"]`)?.textContent?.trim() : "";
      const placeholder = control.getAttribute("placeholder")?.trim();
      const type = control.getAttribute("type");

      if (type === "hidden") return [];
      if (ariaLabel || labelledBy || title || text || label || placeholder) return [];

      return [control.outerHTML.slice(0, 160)];
    });
  });

  expect(unnamedControls).toEqual([]);
}

async function assertNoObviousTextOverlap(page: Page): Promise<void> {
  const overlaps = await page.locator("main :is(h1,h2,h3,p,span,a,button,label,dd,dt,li)").evaluateAll((elements) => {
    const visible = elements
      .map((element, index) => {
        const el = element as HTMLElement;
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return {
          index,
          text: el.innerText?.trim() || el.textContent?.trim() || "",
          display: style.display,
          visibility: style.visibility,
          position: style.position,
          width: rect.width,
          height: rect.height,
          top: rect.top,
          left: rect.left,
          right: rect.right,
          bottom: rect.bottom,
        };
      })
      .filter((item) => (
        item.text.length > 0 &&
        item.display !== "none" &&
        item.visibility !== "hidden" &&
        item.width > 8 &&
        item.height > 8 &&
        item.bottom > 0 &&
        item.right > 0
      ));

    const found: string[] = [];
    for (let i = 0; i < visible.length; i += 1) {
      for (let j = i + 1; j < visible.length; j += 1) {
        const a = visible[i];
        const b = visible[j];
        if (elements[a.index].contains(elements[b.index]) || elements[b.index].contains(elements[a.index])) continue;
        if (a.position === "sticky" || b.position === "sticky") continue;
        const horizontal = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const vertical = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        const minArea = Math.min(a.width * a.height, b.width * b.height);
        const overlapArea = horizontal * vertical;
        if (horizontal > 6 && vertical > 6 && overlapArea / minArea > 0.75) {
          found.push(`${a.text.slice(0, 48)} <> ${b.text.slice(0, 48)}`);
        }
      }
    }
    return found.slice(0, 5);
  });

  expect(overlaps).toEqual([]);
}

function sanitizeEvidence(value: string): string {
  return value
    .replace(/data-platform\/raw\/[^\s"'`)]*/gi, "data-platform/raw/[redacted]")
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, "[redacted-email]")
    .replace(/\b\d{9,}\b/g, "[redacted-number]");
}
