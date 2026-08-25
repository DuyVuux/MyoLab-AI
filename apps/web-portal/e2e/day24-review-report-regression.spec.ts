import { expect, test, type Page } from "@playwright/test";

const HASH = "a".repeat(64);
const REVIEWER_HASH = "b".repeat(64);
const FORBIDDEN_WORDING = /chẩn đoán mỏi cơ|bắt buộc dừng tập|đủ điều kiện thi đấu|xác suất bệnh nhân bị mỏi|clinical sign-off|clinical report|kết luận lâm sàng|báo cáo kết quả lâm sàng/i;

function reviewCase(state = "pending_technical_review") {
  return {
    schemaVersion: "review-workflow.v0.1",
    caseId: "REV-DAY24E2E",
    analysisId: "AN-DAY24-E2E",
    originalResultHash: HASH,
    analysisStatus: "completed_with_warnings",
    state,
    events: state === "approved" ? [
      {
        eventId: "REVT-DAY24CLINICAL",
        reviewType: "clinical",
        action: "approve",
        reviewerRole: "physician",
        reviewerIdHash: REVIEWER_HASH,
        sourceResultHash: HASH,
        checklistVersion: "clinical-review-checklist.v0.1",
        checklistResponses: { limitations_visible: true },
        reasonCodes: [],
        comment: null,
        createdAt: "2026-07-24T09:00:00.000Z",
        immutable: true,
      },
    ] : [],
    safety: {
      originalResultImmutable: true,
      humanReviewRequired: true,
      rawSamplesIncluded: false,
      clinicalUseAllowed: false,
    },
  };
}

function reportFixture(status: "draft" | "final") {
  return {
    schemaVersion: "clinical-report-package.v0.1",
    reportId: status === "draft" ? "RPT-DAY24DRAFT" : "RPT-DAY24FINAL",
    analysisId: "AN-DAY24-E2E",
    status,
    watermark: status === "draft" ? "BẢN NHÁP — CHƯA KÝ DUYỆT" : null,
    templateVersion: "clinical-report-v0.2-review-workflow",
    source: {
      originalResultHash: HASH,
      analysisStatus: "completed",
      protocolVersion: "upper-limb-review@0.2.0",
      modelOrRuleVersion: "day24-review-boundary-v0.1",
      qualityGateVersion: "quality-gate-v0.1",
    },
    sections: {
      summaryVi: "Kết quả kỹ thuật cần human review.",
      evidence: [],
    },
    review: {
      caseId: "REV-DAY24E2E",
      state: status === "final" ? "approved" : "pending_clinical_review",
      eventCount: status === "final" ? 1 : 0,
      clinicalReviewerPresent: status === "final",
    },
    limitations: ["Kết quả hỗ trợ đánh giá, không thay thế quyết định của bác sĩ/KTV."],
    safety: {
      rawSamplesIncluded: false,
      clinicalUseAllowed: false,
      humanReviewRequired: true,
      automaticTreatmentRecommendation: false,
    },
    reportHashSha256: "c".repeat(64),
  };
}

async function seedAuth(page: Page, role = "ktv") {
  await page.addInitScript((mockRole) => {
    window.sessionStorage.setItem("myolab-ai.mock-role", mockRole);
  }, role);
}

async function installDay24Api(page: Page) {
  await page.route("**/v1/review-cases", async (route) => {
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify(reviewCase()),
    });
  });
  await page.route("**/v1/review-cases/*/events", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(reviewCase("pending_clinical_review")),
    });
  });
  await page.route("**/v1/reports/preview", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(reportFixture("draft")),
    });
  });
  await page.route("**/v1/reports/finalize", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(reportFixture("final")),
    });
  });
}

test.describe("Day 24 review and report UI regression", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page);
    await installDay24Api(page);
  });

  test("shows review governance and blocks KTV human review confirmation", async ({ page }) => {
    await page.goto("/reviews/AN-DAY24-E2E");
    await expect(page.getByRole("heading", { name: "Human Review", exact: true })).toBeVisible();
    await expect(page.getByText(HASH)).toBeVisible();
    await expect(page.getByText(/Chỉ reviewer có vai trò bác sĩ/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /Xác nhận đã review/i })).toBeDisabled();
    await expect(page.locator("body")).not.toContainText(FORBIDDEN_WORDING);
  });

  test("shows draft watermark and final hash states", async ({ page }) => {
    await page.goto("/reports/day24-draft");
    await expect(page.getByRole("heading", { name: /Báo cáo bằng chứng sEMG/i })).toBeVisible();
    await expect(page.getByRole("status")).toContainText(/BẢN NHÁP/i);
    await expect(page.locator("body")).not.toContainText(FORBIDDEN_WORDING);

    await page.goto("/reports/day24-final");
    await expect(page.getByText(/Trạng thái: final/i)).toBeVisible();
    await expect(page.getByText("c".repeat(64))).toBeVisible();
    await expect(page.locator("body")).not.toContainText(/BẢN NHÁP/);
  });
});
