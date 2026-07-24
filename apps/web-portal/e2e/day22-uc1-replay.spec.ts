import { expect, test, type Page } from "@playwright/test";


const SESSION_ID = "SESSION-D22-E2E";
const ANALYSIS_ID = "ANALYSIS-D22-E2E";
const REPLAY_ID = "REPLAY-D22-E2E";
const MODEL_VERSION = "gesture-replay-v0.1-not-validated";
const RESULT_HASH = "b".repeat(64);

type ReplayState =
  | "idle"
  | "running"
  | "paused"
  | "completed"
  | "abstained"
  | "disconnected";

interface ReplayOptions {
  initial?: ReturnType<typeof replayFixture>;
  advances?: Array<ReturnType<typeof replayFixture>>;
  launchErrorStatus?: number;
}

function windowFixture(overrides: Record<string, unknown> = {}) {
  return {
    schemaVersion: "gesture-inference.v0.1",
    windowId: "WIN-D22-E2E-001",
    sessionId: SESSION_ID,
    analysisId: ANALYSIS_ID,
    protocolVersion: "upper-limb-gesture-biofeedback@0.1.0",
    segmentRef: {
      rawSignalRef: "RAW-D22-E2E",
      sourceHashSha256: "a".repeat(64),
      startSample: 1000,
      endSampleExclusive: 2000,
      startTimeS: 1,
      endTimeExclusiveS: 2,
      channelIds: ["CH01", "CH02"],
      repetitionId: "REP-D22-E2E-001",
      calibrationId: "CAL-D22-E2E",
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
    engineeringConfidence: "engineering_high",
    latency: {
      totalMs: 270,
      acquisitionMs: 10,
      windowMs: 200,
      preprocessMs: 18,
      inferenceMs: 14,
      transportRenderMs: 28,
    },
    fatigueOverlay: {
      source: "not_available",
      status: "stable",
      confidenceAdjustmentApplied: false,
      reasonCodes: [],
      evidenceSummaryVi: [],
      counterevidenceVi: [],
      limitationsVi: ["Deterministic replay, không phải kết luận lâm sàng."],
    },
    deviceState: "connected",
    qualityContext: {
      source: "scenario_fixture",
      qualityResultId: "QC-D22-001",
      status: "pass",
      reasonCodes: [],
    },
    requiresHumanReview: true,
    sourceType: "synthetic_replay",
    modelValidationStatus: "not_validated",
    modelVersion: MODEL_VERSION,
    resultHashSha256: RESULT_HASH,
    safety: {
      scoreIsProbability: false,
      clinicalUseAllowed: false,
      rawSamplesIncluded: false,
      physicalActuationAllowed: false,
    },
    ...overrides,
  };
}

function replayFixture(
  state: ReplayState = "idle",
  currentIndex = -1,
  fixtureWindows = [windowFixture()],
) {
  const history =
    currentIndex >= 0 ? fixtureWindows.slice(0, currentIndex + 1) : [];
  const currentWindow =
    currentIndex >= 0 && currentIndex < fixtureWindows.length
      ? fixtureWindows[currentIndex]
      : null;
  return {
    schemaVersion: "uc1-replay-session.v0.1",
    replayId: REPLAY_ID,
    sessionId: SESSION_ID,
    analysisId: ANALYSIS_ID,
    scenarioId: "uc1_golden_correct",
    state,
    currentIndex,
    revision: Math.max(0, currentIndex + 1),
    totalWindows: fixtureWindows.length,
    currentWindow,
    history,
    latencySummary: {
      observedWindowCount: history.length,
      p50Ms: history.length > 0 ? 270 : null,
      p95Ms: history.length > 0 ? 270 : null,
      droppedWindows: 0,
      disconnectTimeoutMs: 2000,
    },
    reasonCodes: [],
    sourceType: "synthetic_replay",
    modelValidationStatus: "not_validated",
    clinicalUseAllowed: false,
    humanReviewRequired: true,
  };
}

async function installReplayApi(
  page: Page,
  options: ReplayOptions = {},
) {
  const initial = options.initial ?? replayFixture();
  const advances = [...(options.advances ?? [])];
  let activeWindow = initial.currentWindow;
  let feedbackBody: unknown = null;

  await page.route("**/v1/uc1/sessions/*/replays", async (route) => {
    if (options.launchErrorStatus) {
      await route.fulfill({
        status: options.launchErrorStatus,
        contentType: "application/json",
        body: JSON.stringify({ detail: "REPLAY_SERVICE_UNAVAILABLE" }),
      });
      return;
    }
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify(initial),
    });
  });

  await page.route("**/v1/uc1/replays/*/advance", async (route) => {
    const next = advances.shift() ?? initial;
    activeWindow = next.currentWindow;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(next),
    });
  });

  await page.route("**/v1/uc1/replays/*/feedback", async (route) => {
    feedbackBody = await route.request().postDataJSON();
    const currentWindow = activeWindow ?? windowFixture();
    const segment = currentWindow.segmentRef;
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        feedbackId: "FB-D22-E2E-001",
        action: "uncertain",
        reviewerCertainty: "moderate",
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

  return {
    feedbackBody: () => feedbackBody,
  };
}

async function openAuthenticatedReplay(
  page: Page,
  scenarioId = "uc1_golden_correct",
  actorRole: "ktv" | "patient" = "ktv",
) {
  await page.goto("/login");
  const loginName =
    actorRole === "patient"
      ? /Đăng nhập với vai trò Bệnh nhân/i
      : /Đăng nhập với vai trò KTV Phục hồi chức năng/i;
  await page.getByRole("button", { name: loginName }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  const target =
    `/uc1/session/${SESSION_ID}` +
    `?analysisId=${ANALYSIS_ID}&scenarioId=${scenarioId}`;
  await page.evaluate((url) => {
    window.history.pushState(null, "", url);
    window.dispatchEvent(new PopStateEvent("popstate"));
  }, target);
  await expect(page).toHaveURL(new RegExp(`/uc1/session/${SESSION_ID}`));
  await expect(
    page.getByRole("heading", { name: /UC1.*Biofeedback/i }),
  ).toBeVisible();
}

test.describe("Day 22 UC1 deterministic replay", () => {
  test("keeps idle prediction empty, then reveals only the advanced window", async ({
    page,
  }) => {
    const futureWindow = windowFixture({
      windowId: "WIN-D22-E2E-FUTURE",
      resultHashSha256: "c".repeat(64),
    });
    const first = windowFixture();
    await installReplayApi(page, {
      initial: replayFixture("idle", -1, [first, futureWindow]),
      advances: [replayFixture("running", 0, [first, futureWindow])],
    });

    await openAuthenticatedReplay(page);
    await expect(page.getByText(/Replay chưa bắt đầu/i)).toBeVisible();
    await expect(
      page.getByText(/Hệ thống replay đã ghi nhận nỗ lực/i),
    ).toHaveCount(0);
    await expect(page.getByText("WIN-D22-E2E-FUTURE")).toHaveCount(0);

    await page.getByRole("button", { name: /Bắt đầu replay/i }).click();
    await expect(
      page.getByText(/Hệ thống replay đã ghi nhận nỗ lực/i),
    ).toBeVisible();
    await expect(page.getByText("WIN-D22-E2E-FUTURE")).toHaveCount(0);
  });

  test("distinguishes no activity from an API failure", async ({ page }) => {
    const noActivity = windowFixture({
      activityGate: {
        status: "inactive",
        windowRmsUv: 4.5,
        activationThresholdUv: 6.6,
        releaseThresholdUv: 5.28,
        reasonCode: "ACTIVITY_BELOW_THRESHOLD",
      },
      predictedGesture: null,
      engineeringConfidence: "not_available",
    });
    await installReplayApi(page, {
      initial: replayFixture("idle", -1, [noActivity]),
      advances: [replayFixture("running", 0, [noActivity])],
    });

    await openAuthenticatedReplay(page, "uc1_no_activity");
    await page.getByRole("button", { name: /Bắt đầu replay/i }).click();
    await expect(
      page.getByText(/chưa đủ bằng chứng hoạt động cơ/i),
    ).toBeVisible();
    await expect(
      page.getByText(/Không tải được kết quả kỹ thuật/i),
    ).toHaveCount(0);
  });

  test("shows an API error without presenting it as no activity", async ({
    page,
  }) => {
    await installReplayApi(page, { launchErrorStatus: 503 });

    await openAuthenticatedReplay(page);
    await expect(
      page.getByText(/Không tải được kết quả kỹ thuật/i),
    ).toBeVisible();
    await expect(
      page.getByText(/chưa đủ bằng chứng hoạt động cơ/i),
    ).toHaveCount(0);
  });

  for (const blocked of [
    {
      name: "QC fail",
      scenario: "uc1_qc_fail_abstention",
      state: "abstained" as const,
      window: windowFixture({
        qualityContext: {
          source: "scenario_fixture",
          qualityResultId: "QC-D22-E2E",
          status: "fail",
          reasonCodes: ["WINDOW_QUALITY_FAILED"],
        },
        predictedGesture: null,
        engineeringConfidence: "not_available",
      }),
      copy: /không đạt điều kiện chất lượng/i,
    },
    {
      name: "device disconnect",
      scenario: "uc1_device_disconnect",
      state: "disconnected" as const,
      window: windowFixture({
        deviceState: "disconnected",
        predictedGesture: null,
        engineeringConfidence: "not_available",
      }),
      copy: /kết nối replay bị gián đoạn/i,
    },
  ]) {
    test(`${blocked.name} never renders a prediction`, async ({ page }) => {
      await installReplayApi(page, {
        initial: replayFixture("idle", -1, [blocked.window]),
        advances: [replayFixture(blocked.state, 0, [blocked.window])],
      });

      await openAuthenticatedReplay(page, blocked.scenario);
      await page.getByRole("button", { name: /Bắt đầu replay/i }).click();
      await expect(page.getByText(blocked.copy)).toBeVisible();
      await expect(
        page.getByText(/Hệ thống replay đã ghi nhận nỗ lực/i),
      ).toHaveCount(0);
    });
  }


  test("keeps technical feedback controls hidden for patient role", async ({
    page,
  }) => {
    const current = windowFixture();
    await installReplayApi(page, {
      initial: replayFixture("idle", -1, [current]),
      advances: [replayFixture("running", 0, [current])],
    });

    await openAuthenticatedReplay(
      page,
      "uc1_golden_correct",
      "patient",
    );
    await page.getByRole("button", { name: /Bắt đầu replay/i }).click();
    await expect(
      page.getByText(/Hệ thống replay đã ghi nhận nỗ lực/i),
    ).toBeVisible();
    for (const actionName of [
      /Chấp nhận kết quả/i,
      /Chưa chắc/i,
      /Cần sửa/i,
      /Đề nghị đo lại/i,
    ]) {
      await expect(
        page.getByRole("button", { name: actionName }),
      ).toHaveCount(0);
    }
  });

  test("submits feedback without client-fabricated provenance", async ({
    page,
  }) => {
    const current = windowFixture();
    const api = await installReplayApi(page, {
      initial: replayFixture("idle", -1, [current]),
      advances: [replayFixture("running", 0, [current])],
    });

    await openAuthenticatedReplay(page);
    await page.getByRole("button", { name: /Bắt đầu replay/i }).click();
    const feedbackRequest = page.waitForRequest(
      (request) =>
        request.url().includes("/v1/uc1/replays/") &&
        request.url().endsWith("/feedback") &&
        request.method() === "POST",
    );
    await page.getByRole("button", { name: /Chưa chắc/i }).click();
    const request = await feedbackRequest;

    const body = api.feedbackBody() as {
      expectedWindowId?: string;
      expectedRevision?: number;
      action?: string;
      reviewerCertainty?: string;
      context?: Record<string, unknown>;
    };
    expect(body).toEqual({
      expectedWindowId: current.windowId,
      expectedRevision: 1,
      action: "uncertain",
      reviewerCertainty: "moderate",
    });
    expect(body.context).toBeUndefined();
    expect(request.headers()["idempotency-key"]).toBeTruthy();
    expect(request.headers()["x-actor-role"]).toBe("ktv");
    await expect(page.getByText(/feedback đã được ghi nhận/i)).toBeVisible();
  });
});
