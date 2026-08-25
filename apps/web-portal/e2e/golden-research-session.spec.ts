import { expect, test, type Page } from "@playwright/test";

const SESSION_ID = "SESSION-GOLDEN-E2E";
const ANALYSIS_ID = "ANALYSIS-GOLDEN-E2E";
const REPLAY_ID = "REPLAY-GOLDEN-E2E";
const RESULT_HASH = "b".repeat(64);
const SOURCE_HASH = "a".repeat(64);
const FORBIDDEN_CLINICAL_CLAIMS =
  /clinical sign-off|clinical report|báo cáo kết quả lâm sàng|xác suất bệnh nhân bị mỏi|đủ điều kiện thi đấu|bắt buộc dừng tập/i;

function windowFixture() {
  return {
    schemaVersion: "gesture-inference.v0.1",
    windowId: "WIN-GOLDEN-001",
    sessionId: SESSION_ID,
    analysisId: ANALYSIS_ID,
    protocolVersion: "upper-limb-gesture-biofeedback@0.1.0",
    segmentRef: {
      rawSignalRef: "RAW-GOLDEN-001",
      sourceHashSha256: SOURCE_HASH,
      startSample: 1000,
      endSampleExclusive: 2000,
      startTimeS: 1,
      endTimeExclusiveS: 2,
      channelIds: ["CH01", "CH02"],
      repetitionId: "REP-GOLDEN-001",
      calibrationId: "CAL-GOLDEN-001",
    },
    targetGesture: "wrist_extension",
    activityGate: {
      status: "active",
      windowRmsUv: 11,
      activationThresholdUv: 6.6,
      releaseThresholdUv: 5.28,
      reasonCode: "ACTIVITY_ABOVE_THRESHOLD",
    },
    predictedGesture: "wrist_extension",
    baseEngineeringConfidence: "engineering_high",
    engineeringConfidence: "engineering_moderate",
    latency: {
      totalMs: 270,
      acquisitionMs: 10,
      windowMs: 200,
      preprocessMs: 18,
      inferenceMs: 14,
      transportRenderMs: 28,
    },
    fatigueOverlay: {
      source: "scenario_fixture",
      status: "warning",
      confidenceAdjustmentApplied: true,
      reasonCodes: ["FATIGUE_EVIDENCE_LIMITED"],
      evidenceSummaryVi: ["MDF giảm trong cửa sổ demo."],
      counterevidenceVi: ["Không có xác thực lâm sàng."],
      limitationsVi: ["Research-only fatigue overlay; không phải chẩn đoán."],
    },
    deviceState: "connected",
    qualityContext: {
      source: "scenario_fixture",
      qualityResultId: "QC-GOLDEN-001",
      status: "warning",
      reasonCodes: ["WINDOW_QC_WARNING"],
    },
    requiresHumanReview: true,
    sourceType: "synthetic_replay",
    modelValidationStatus: "not_validated",
    modelVersion: "gesture-replay-v0.1-not-validated",
    resultHashSha256: RESULT_HASH,
    safety: {
      scoreIsProbability: false,
      clinicalUseAllowed: false,
      rawSamplesIncluded: false,
      physicalActuationAllowed: false,
    },
  };
}

function replayFixture(currentIndex = -1) {
  const currentWindow = currentIndex >= 0 ? windowFixture() : null;
  return {
    schemaVersion: "uc1-replay-session.v0.1",
    replayId: REPLAY_ID,
    sessionId: SESSION_ID,
    analysisId: ANALYSIS_ID,
    scenarioId: "uc1_golden_correct",
    state: currentIndex >= 0 ? "completed" : "idle",
    currentIndex,
    revision: currentIndex + 1,
    totalWindows: 1,
    currentWindow,
    history: [],
    latencySummary: {
      observedWindowCount: currentWindow === null ? 0 : 1,
      p50Ms: currentWindow === null ? null : 270,
      p95Ms: currentWindow === null ? null : 270,
      droppedWindows: 0,
      disconnectTimeoutMs: 2000,
    },
    reasonCodes: currentWindow === null ? [] : ["REVIEW_REQUIRED_BY_POLICY"],
    sourceType: "synthetic_replay",
    modelValidationStatus: "not_validated",
    clinicalUseAllowed: false,
    humanReviewRequired: true,
  };
}

async function installGoldenReplayApi(page: Page) {
  let activeWindow: ReturnType<typeof windowFixture> | null = null;

  await page.route("**/v1/uc1/sessions/*/replays", async (route) => {
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify(replayFixture(-1)),
    });
  });

  await page.route("**/v1/uc1/replays/*/advance", async (route) => {
    activeWindow = windowFixture();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(replayFixture(0)),
    });
  });

  await page.route("**/v1/uc1/replays/*/feedback", async (route) => {
    const decision = (await route.request().postDataJSON()) as Record<string, unknown>;
    const currentWindow = activeWindow ?? windowFixture();
    const segment = currentWindow.segmentRef;
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        schemaVersion: "gesture-feedback.v0.1",
        feedbackId: "FB-GOLDEN-001",
        replayId: REPLAY_ID,
        action: decision.action,
        correctedGesture: decision.correctedGesture ?? null,
        reviewerCertainty: decision.reviewerCertainty,
        actorRole: route.request().headers()["x-actor-role"],
        automaticTrainingCandidate: false,
        context: {
          schemaVersion: "gesture-feedback-context.v0.1",
          analysisId: currentWindow.analysisId,
          sessionId: currentWindow.sessionId,
          windowId: currentWindow.windowId,
          rawSignalRef: segment.rawSignalRef,
          sourceHashSha256: segment.sourceHashSha256,
          startSample: segment.startSample,
          endSampleExclusive: segment.endSampleExclusive,
          startTimeS: segment.startTimeS,
          endTimeExclusiveS: segment.endTimeExclusiveS,
          channelIds: segment.channelIds,
          repetitionId: segment.repetitionId,
          calibrationId: segment.calibrationId,
          modelVersion: currentWindow.modelVersion,
          originalResultHashSha256: currentWindow.resultHashSha256,
        },
      }),
    });
  });
}

async function loginAsKtv(page: Page) {
  await page.goto("/login");
  await page.getByRole("button", { name: /KTV Phục hồi chức năng/i }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test.describe("Golden research session", () => {
  test("runs deterministic technical evidence demo without clinical-use claims", async ({ page }) => {
    await installGoldenReplayApi(page);
    await loginAsKtv(page);

    await page.keyboard.press("Tab");
    await expect(page.getByRole("link", { name: /Chuyển tới nội dung chính/i })).toBeVisible();
    await page.keyboard.press("Enter");
    await expect(page.locator("#main-content")).toBeFocused();

    await page.goto(
      `/uc1/session/${SESSION_ID}?analysisId=${ANALYSIS_ID}&scenarioId=uc1_golden_correct`,
    );
    await expect(page.getByText(/RESEARCH ONLY|Phạm vi an toàn/i)).toBeVisible();
    await expect(page.getByText(/Nguồn mô phỏng/i)).toBeVisible();
    await expect(page.getByText(/Model chưa được xác thực/i)).toBeVisible();
    await expect(page.locator("body")).not.toContainText(FORBIDDEN_CLINICAL_CLAIMS);

    await page.getByRole("button", { name: /Bắt đầu replay/i }).click();
    await expect(page.getByText(/WINDOW_QC_WARNING/i)).toBeVisible();
    await expect(page.getByText(/ACTIVITY_ABOVE_THRESHOLD/i)).toBeVisible();
    await expect(page.getByText(/FATIGUE_EVIDENCE_LIMITED/i)).toBeVisible();
    await expect(page.getByText(RESULT_HASH)).toBeVisible();
    await expect(page.getByText(SOURCE_HASH)).toBeVisible();

    await page.getByRole("button", { name: /Chưa chắc/i }).click();
    await expect(page.getByText(/Feedback đã được ghi nhận/i)).toBeVisible();

    await page.goto("/review-queue/CASE-GOLDEN/qc");
    await expect(page.getByRole("heading", { name: /QC Evidence/i })).toBeVisible();
    await expect(page.getByText(/UNKNOWN is not PASS/i)).toBeVisible();

    await page.goto("/review-queue/CASE-GOLDEN/signal");
    await expect(page.getByRole("heading", { name: /Signal Viewer/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: "RAW" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "PROCESSED" })).toBeVisible();

    await page.goto("/review-queue/CASE-GOLDEN/metrics");
    await expect(page.getByRole("heading", { name: /Metric Evidence/i })).toBeVisible();
    await expect(page.getByText(/MFCV/i)).toBeVisible();
    await expect(page.getByText(/UNSUPPORTED/i)).toBeVisible();
    await expect(page.getByText(/ELECTRODE_GEOMETRY_NOT_VERIFIED|SITE_GEOMETRY_NOT_VERIFIED/i)).toBeVisible();
    await expect(page.locator("body")).not.toContainText(FORBIDDEN_CLINICAL_CLAIMS);
  });
});
