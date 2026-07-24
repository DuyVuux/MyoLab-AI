import { expect, test, type Page } from "@playwright/test";

const SESSION_ID = "SESSION-D23-E2E";
const SUBJECT_REF = "SUBJ-D23-E2E";
const FORBIDDEN_UC2_UI = /Khác biệt so với UC1|Đa chiều|Clinical Focus|📊|📈|🔬/;

function workflowStore() {
  return {
    sessions: {
      [SESSION_ID]: {
        sessionId: SESSION_ID,
        subjectRef: SUBJECT_REF,
        useCaseId: "uc2",
        protocolId: "PROT-UC2-001",
        protocolVersion: "2.0",
        affectedSide: "right",
        referenceSide: "left",
        targetMuscles: ["FCR", "ECR"],
        sessionType: "baseline",
        operator: "KTV-D23",
        consentScope: ["analysis", "reporting"],
        dataSourceIntent: "synthetic",
        createdAt: "2026-07-24T00:00:00.000Z",
        electrodeLayout: [],
        requiresCalibration: true,
        state: "analysis_complete",
      },
    },
    imports: {},
    mappings: {},
    preflights: {},
    calibrations: {},
    qcResults: {},
    analysisJobs: {},
    segments: {},
    technicalReviews: {},
    clinicalReviews: {},
    reports: {},
    feedbackEvents: {},
    adjudications: {},
    issues: {},
    auditLog: [],
  };
}

function assessmentFixture(scenarioId: string) {
  const blocked = scenarioId === "uc2_protocol_incompatible";
  const comparisonSessionIds = blocked ? ["S-WEEK4-D23"] : ["S-WEEK4-D23"];
  const compatibility = {
    schemaVersion: "longitudinal-compatibility.v0.1",
    subjectRef: SUBJECT_REF,
    baselineSessionId: "S-BASE-D23",
    comparisonSessionIds,
    status: blocked ? "blocked" : "compatible",
    conclusionAllowed: !blocked,
    checks: blocked
      ? [
          {
            field: "S-WEEK4-D23:protocolVersion",
            status: "mismatch",
            baselineValue: "v0.1",
            comparisonValue: "v0.2",
            reasonCode: "PROTOCOLVERSION_MISMATCH",
          },
        ]
      : [
          {
            field: "S-WEEK4-D23:protocolVersion",
            status: "match",
            baselineValue: "v0.1",
            comparisonValue: "v0.1",
            reasonCode: null,
          },
        ],
    reasonCodes: blocked ? ["PROTOCOLVERSION_MISMATCH"] : [],
    safety: {
      rawSamplesIncluded: false,
      clinicalUseAllowed: false,
      humanReviewRequired: true,
    },
  };

  return {
    schemaVersion: "uc2-quantitative-assessment.v0.1",
    assessmentId: `UC2-E2E-${scenarioId}`,
    subjectRef: SUBJECT_REF,
    sessionIds: ["S-BASE-D23", ...comparisonSessionIds],
    status: blocked ? "blocked" : "completed_with_warnings",
    metrics: blocked
      ? [
          {
            metricId: "longitudinal_summary",
            labelVi: "Tóm tắt so sánh dọc",
            status: "blocked",
            value: null,
            unit: null,
            formulaVersion: "compatibility-gate-v0.1",
            validationStatus: "not_validated",
            sourceSessionIds: ["S-BASE-D23", ...comparisonSessionIds],
            limitations: ["PROTOCOLVERSION_MISMATCH"],
          },
        ]
      : [
          {
            metricId: "repeatability_cov",
            labelVi: "Độ biến thiên giữa lần lặp",
            status: "experimental",
            value: 7.07,
            unit: "% CoV",
            formulaVersion: "cov-population-v0.1",
            validationStatus: "not_validated",
            sourceSessionIds: ["S-BASE-D23", ...comparisonSessionIds],
            limitations: ["Chỉ số kỹ thuật."],
          },
          {
            metricId: "symmetry_ratio",
            labelVi: "Tỷ lệ đối xứng affected/reference",
            status: "experimental",
            value: 80,
            unit: "%",
            formulaVersion: "symmetry-ratio-v0.1",
            validationStatus: "not_validated",
            sourceSessionIds: ["S-BASE-D23", ...comparisonSessionIds],
            limitations: ["Chỉ diễn giải khi protocol tương thích."],
          },
          {
            metricId: "time_to_fatigue_change",
            labelVi: "Thay đổi thời gian tới mệt",
            status: "experimental",
            value: 20,
            unit: "%",
            formulaVersion: "percent-change-v0.1",
            validationStatus: "not_validated",
            sourceSessionIds: ["S-BASE-D23", ...comparisonSessionIds],
            limitations: ["Không phải kết luận lâm sàng."],
          },
        ],
    compatibility,
    limitations: ["Human review bắt buộc."],
    reviewStatus: "pending_human_review",
    safety: {
      scoreIsProbability: false,
      rawSamplesIncluded: false,
      clinicalUseAllowed: false,
      humanReviewRequired: true,
      isClinicalConclusion: false,
    },
  };
}

async function installWorkflowStore(page: Page) {
  await page.addInitScript((store) => {
    window.sessionStorage.setItem("myolab-ai.mock-role", "ktv");
    window.sessionStorage.setItem("myolab_workflow_state", JSON.stringify(store));
  }, workflowStore());
}

async function installUC2Api(page: Page) {
  await page.route("**/v1/uc2/assessments", async (route) => {
    const request = route.request();
    const body = request.postDataJSON() as { scenarioId?: string };
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify(assessmentFixture(body.scenarioId ?? "golden_uc2_longitudinal")),
    });
  });
}

test.describe("Day 23 UC2 UI regression", () => {
  test.beforeEach(async ({ page }) => {
    await installWorkflowStore(page);
    await installUC2Api(page);
  });

  test("removes deprecated UC2 comparison cards from intro", async ({ page }) => {
    await page.goto("/uc2/intro");
    await expect(page.getByRole("heading", { level: 1, name: /UC2 .*Đánh giá định lượng/i })).toBeVisible();
    await expect(page.locator("body")).not.toContainText(FORBIDDEN_UC2_UI);
  });

  test("renders assessment dashboard without deprecated UC2 UI", async ({ page }) => {
    await page.goto(`/uc2/assessment/${SESSION_ID}`);
    await expect(page.getByRole("heading", { name: /UC2: Dashboard định lượng/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Chỉ số định lượng/i })).toBeVisible();
    await expect(page.getByRole("table", { name: /Kiểm tra compatibility/i })).toBeVisible();
    await expect(page.locator("body")).not.toContainText(FORBIDDEN_UC2_UI);
  });

  test("blocks incompatible longitudinal trend and keeps accessible table", async ({ page }) => {
    await page.goto(`/uc2/longitudinal/${SUBJECT_REF}?scenario=uc2_protocol_incompatible`);
    await expect(page.getByRole("heading", { name: /Longitudinal Trend/i })).toBeVisible();
    await expect(page.getByRole("table", { name: /Kiểm tra compatibility/i })).toBeVisible();
    await expect(page.getByRole("status")).toContainText(/không tương thích/i);
    await expect(page.locator("body")).not.toContainText(FORBIDDEN_UC2_UI);
  });
});
