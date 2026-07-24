const assert = require("node:assert/strict");
const path = require("node:path");

const buildRoot = path.resolve(process.cwd(), ".day22-build");
const {
  isLatencyBreakdownValid,
  nearestRankPercentile,
  totalLatencyMs,
} = require(path.join(buildRoot, "lib/latencyMetrics.js"));
const {
  feedbackContextFromWindow,
} = require(path.join(buildRoot, "schemas/gesture-feedback-context.schema.js"));
const {
  currentReplayWindow,
  visibleReplayWindows,
} = require(path.join(buildRoot, "utils/replayView.js"));
const {
  HttpUC1ReplayClient,
  UC1ReplayClientError,
} = require(path.join(buildRoot, "lib/uc1-replay-client.js"));
const {
  canApplyReplayMutation,
  getOrCreateOpaqueIdempotencyKey,
  isFeedbackActorRole,
  isFeedbackReceiptFor,
  isFeedbackRequestForReplay,
  isReplayAdvanceFor,
  isReplayCreatedFor,
  isSafeReplayPayload,
  SecureIdempotencyUnavailableError,
} = require(path.join(buildRoot, "utils/uc1ReplayValidation.js"));

assert.equal(
  canApplyReplayMutation(4, 4, false),
  true,
  "the active request generation may update state",
);
assert.equal(
  canApplyReplayMutation(3, 4, false),
  false,
  "a stale request generation must not update state",
);
assert.equal(
  canApplyReplayMutation(4, 4, true),
  false,
  "an aborted request must not update state",
);

const latency = Object.freeze({
  totalMs: 270,
  acquisitionMs: 10,
  windowMs: 200,
  preprocessMs: 18,
  inferenceMs: 14,
  transportRenderMs: 28,
});

assert.equal(
  nearestRankPercentile([100, 200, 300, 400], 0.5),
  200,
  "nearest-rank p50 must select rank ceil(0.5 * N)",
);
assert.equal(
  nearestRankPercentile([100, 200, 300, 400], 0.95),
  400,
  "nearest-rank p95 must select rank ceil(0.95 * N)",
);
assert.equal(
  totalLatencyMs(10, 200, 18, 14, 28),
  270,
  "total latency must include every acquisition-to-render component",
);
assert.equal(
  isLatencyBreakdownValid(latency),
  true,
  "a matching total must validate",
);
assert.equal(
  isLatencyBreakdownValid({ ...latency, totalMs: 269 }),
  false,
  "a mismatched total must be rejected",
);

const firstWindow = Object.freeze({
  schemaVersion: "gesture-inference.v0.1",
  windowId: "WIN-D22-0001",
  sessionId: "SESSION-D22-001",
  analysisId: "ANALYSIS-D22-001",
  protocolVersion: "upper-limb-gesture-biofeedback@0.1.0",
  segmentRef: {
    rawSignalRef: "RAW-D22-001",
    sourceHashSha256: "a".repeat(64),
    startSample: 1000,
    endSampleExclusive: 2000,
    startTimeS: 1,
    endTimeExclusiveS: 2,
    channelIds: ["CH01", "CH02"],
    repetitionId: "REP-D22-001",
    calibrationId: "CAL-D22-001",
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
  latency,
  fatigueOverlay: {
    status: "stable",
    source: "scenario_fixture",
    confidenceAdjustmentApplied: false,
    reasonCodes: [],
    evidenceSummaryVi: ["Không có cảnh báo thay đổi kỹ thuật trong fixture này."],
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
  modelVersion: "gesture-replay-v0.1-not-validated",
  resultHashSha256: "b".repeat(64),
  safety: {
    scoreIsProbability: false,
    clinicalUseAllowed: false,
    rawSamplesIncluded: false,
    physicalActuationAllowed: false,
  },
});

const secondWindow = Object.freeze({
  ...firstWindow,
  windowId: "WIN-D22-0002",
  resultHashSha256: "c".repeat(64),
  segmentRef: {
    ...firstWindow.segmentRef,
    startSample: 1250,
    endSampleExclusive: 2250,
    startTimeS: 1.25,
    endTimeExclusiveS: 2.25,
    repetitionId: "REP-D22-002",
  },
});

const replay = Object.freeze({
  schemaVersion: "uc1-replay-session.v0.1",
  replayId: "REPLAY-D22-001",
  sessionId: "SESSION-D22-001",
  analysisId: "ANALYSIS-D22-001",
  scenarioId: "uc1_golden_correct",
  state: "idle",
  currentIndex: -1,
  revision: 0,
  totalWindows: 2,
  currentWindow: null,
  history: [],
  latencySummary: {
    observedWindowCount: 0,
    p50Ms: null,
    p95Ms: null,
    droppedWindows: 0,
    disconnectTimeoutMs: 2000,
  },
  reasonCodes: [],
  sourceType: "synthetic_replay",
  modelValidationStatus: "not_validated",
  clinicalUseAllowed: false,
  humanReviewRequired: true,
});

const runningReplay = Object.freeze({
  ...replay,
  state: "running",
  currentIndex: 0,
  revision: 1,
  currentWindow: firstWindow,
  history: [],
  latencySummary: { ...replay.latencySummary, observedWindowCount: 1, p50Ms: 270, p95Ms: 270 },
});

const secondRunningReplay = Object.freeze({
  ...runningReplay,
  state: "completed",
  currentIndex: 1,
  revision: 2,
  currentWindow: secondWindow,
  history: [firstWindow],
  latencySummary: {
    ...runningReplay.latencySummary,
    observedWindowCount: 2,
  },
});

assert.equal(
  currentReplayWindow(replay),
  null,
  "idle replay must not leak the first future result",
);
assert.equal(
  currentReplayWindow({ ...runningReplay, currentIndex: 2 }),
  null,
  "an out-of-range index must return a safe null",
);
assert.deepEqual(
  visibleReplayWindows(replay),
  [],
  "idle history must be empty",
);
assert.deepEqual(
  visibleReplayWindows(runningReplay).map((window) => window.windowId),
  ["WIN-D22-0001"],
  "history must contain revealed windows only",
);
assert.equal(
  currentReplayWindow(secondRunningReplay)?.windowId,
  "WIN-D22-0002",
  "current window must be separate from its past-only history",
);
assert.deepEqual(
  visibleReplayWindows(secondRunningReplay).map((window) => window.windowId),
  ["WIN-D22-0001", "WIN-D22-0002"],
  "visible windows must append currentWindow after past history",
);
assert.equal(
  currentReplayWindow({ ...secondRunningReplay, history: [secondWindow] }),
  null,
  "currentWindow must never be duplicated inside history",
);
assert.equal(
  visibleReplayWindows(runningReplay).some((window) => window.windowId === secondWindow.windowId),
  false,
  "history must not expose future windows",
);

assert.equal(isSafeReplayPayload(replay), true, "idle replay must validate");
assert.equal(
  isSafeReplayPayload(runningReplay),
  true,
  "partial running replay must validate",
);
assert.equal(
  isSafeReplayPayload(secondRunningReplay),
  true,
  "last-window completed replay must validate",
);

for (const [label, invalidReplay] of [
  ["all-windows collection", { ...runningReplay, windows: [firstWindow] }],
  ["idle replay with zero windows", { ...replay, totalWindows: 0 }],
  ["running state at last cursor", { ...secondRunningReplay, state: "running" }],
  ["completed state before last cursor", { ...runningReplay, state: "completed" }],
  ["zero-window failed state", { ...replay, state: "failed", totalWindows: 0 }],
  [
    "unsafe clinical-use flag",
    {
      ...runningReplay,
      currentWindow: {
        ...firstWindow,
        safety: { ...firstWindow.safety, clinicalUseAllowed: true },
      },
    },
  ],
  [
    "blocked window with prediction",
    {
      ...runningReplay,
      currentWindow: {
        ...firstWindow,
        activityGate: {
          ...firstWindow.activityGate,
          status: "inactive",
          reasonCode: "ACTIVITY_BELOW_THRESHOLD",
        },
      },
    },
  ],
  [
    "invalid latency sum",
    {
      ...runningReplay,
      currentWindow: {
        ...firstWindow,
        latency: { ...firstWindow.latency, totalMs: 269 },
      },
    },
  ],
  [
    "confidence increase above base",
    {
      ...runningReplay,
      currentWindow: {
        ...firstWindow,
        baseEngineeringConfidence: "engineering_low",
        engineeringConfidence: "engineering_high",
      },
    },
  ],
  [
    "fatigue warning without confidence downgrade",
    {
      ...runningReplay,
      currentWindow: {
        ...firstWindow,
        fatigueOverlay: {
          ...firstWindow.fatigueOverlay,
          status: "warning",
          confidenceAdjustmentApplied: true,
          reasonCodes: ["FATIGUE_TECHNICAL_WARNING"],
        },
      },
    },
  ],
  [
    "history time moves backwards",
    {
      ...secondRunningReplay,
      currentWindow: {
        ...secondWindow,
        segmentRef: {
          ...secondWindow.segmentRef,
          startTimeS: 0.75,
          endTimeExclusiveS: 1.75,
        },
      },
    },
  ],
]) {
  assert.equal(
    isSafeReplayPayload(invalidReplay),
    false,
    `${label} must fail closed`,
  );
}


const zeroWindowAbstention = Object.freeze({
  ...replay,
  state: "abstained",
  totalWindows: 0,
});
assert.equal(
  isReplayCreatedFor(
    replay,
    replay.sessionId,
    replay.analysisId,
    replay.scenarioId,
  ),
  true,
  "create response must accept the exact initial idle envelope",
);
assert.equal(
  isReplayCreatedFor(
    zeroWindowAbstention,
    replay.sessionId,
    replay.analysisId,
    replay.scenarioId,
  ),
  true,
  "create response must preserve canonical zero-window abstention",
);
assert.equal(
  isReplayCreatedFor(
    { ...replay, sessionId: "SESSION-FOREIGN" },
    replay.sessionId,
    replay.analysisId,
    replay.scenarioId,
  ),
  false,
  "create response must reject a foreign session",
);
assert.equal(
  isReplayCreatedFor(
    secondRunningReplay,
    replay.sessionId,
    replay.analysisId,
    replay.scenarioId,
  ),
  false,
  "create response must not reveal a terminal history",
);
assert.equal(
  isReplayAdvanceFor(runningReplay, replay),
  true,
  "advance response must reveal exactly one next window",
);
assert.equal(
  isReplayAdvanceFor(
    { ...runningReplay, replayId: "REPLAY-FOREIGN" },
    replay,
  ),
  false,
  "advance response must reject a foreign replay",
);
assert.equal(
  isReplayAdvanceFor(secondRunningReplay, replay),
  false,
  "advance response must reject a skipped cursor and revision",
);
assert.equal(
  isReplayAdvanceFor(
    {
      ...secondRunningReplay,
      history: [
        { ...firstWindow, resultHashSha256: "d".repeat(64) },
      ],
    },
    runningReplay,
  ),
  false,
  "advance response must preserve the immutable visible prefix",
);
const logicalFingerprint = JSON.stringify([
  "feedback",
  replay.replayId,
  firstWindow.windowId,
  "uncertain",
  "moderate",
]);
const idempotencyCache = new Map();
const opaqueKey = getOrCreateOpaqueIdempotencyKey(
  idempotencyCache,
  logicalFingerprint,
);
assert.match(
  opaqueKey,
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
  "idempotency key must be an opaque UUID v4",
);
for (const token of [
  replay.replayId,
  firstWindow.windowId,
  "uncertain",
  "moderate",
]) {
  assert.equal(opaqueKey.includes(token), false, `key must not expose ${token}`);
}
assert.equal(
  getOrCreateOpaqueIdempotencyKey(idempotencyCache, logicalFingerprint),
  opaqueKey,
  "same logical request must reuse its opaque key",
);
assert.notEqual(
  getOrCreateOpaqueIdempotencyKey(idempotencyCache, `${logicalFingerprint}:new`),
  opaqueKey,
  "different logical requests must not share an idempotency key",
);

const cryptoDescriptor = Object.getOwnPropertyDescriptor(globalThis, "crypto");
try {
  Object.defineProperty(globalThis, "crypto", {
    configurable: true,
    value: undefined,
  });
  assert.throws(
    () => getOrCreateOpaqueIdempotencyKey(new Map(), "uncached-request"),
    SecureIdempotencyUnavailableError,
    "missing secure Web Crypto must fail closed",
  );
} finally {
  if (cryptoDescriptor === undefined) {
    delete globalThis.crypto;
  } else {
    Object.defineProperty(globalThis, "crypto", cryptoDescriptor);
  }
}

const feedbackContext = feedbackContextFromWindow(firstWindow);
assert.equal(feedbackContext.analysisId, firstWindow.analysisId);
assert.equal(feedbackContext.sessionId, firstWindow.sessionId);
assert.equal(feedbackContext.windowId, firstWindow.windowId);
assert.equal(feedbackContext.rawSignalRef, firstWindow.segmentRef.rawSignalRef);
assert.equal(
  feedbackContext.sourceHashSha256,
  firstWindow.segmentRef.sourceHashSha256,
);
assert.deepEqual(feedbackContext.channelIds, firstWindow.segmentRef.channelIds);
assert.equal(
  feedbackContext.modelVersion,
  firstWindow.modelVersion,
  "feedback must copy the server-provided model version",
);
assert.equal(
  feedbackContext.originalResultHashSha256,
  firstWindow.resultHashSha256,
  "feedback must copy the canonical result hash instead of synthesizing one",
);

const feedbackRequest = Object.freeze({
  expectedWindowId: firstWindow.windowId,
  expectedRevision: 1,
  action: "uncertain",
  reviewerCertainty: "moderate",
});
const feedbackReceipt = Object.freeze({
  schemaVersion: "gesture-feedback.v0.1",
  feedbackId: "FEEDBACK-D22-001",
  replayId: replay.replayId,
  action: "uncertain",
  correctedGesture: null,
  reviewerCertainty: "moderate",
  actorRole: "ktv",
  automaticTrainingCandidate: false,
  context: feedbackContext,
});
assert.equal(isFeedbackActorRole("ktv"), true);
assert.equal(isFeedbackActorRole("patient"), false);
assert.equal(isFeedbackActorRole("admin"), false);
assert.equal(
  isFeedbackRequestForReplay(
    feedbackRequest,
    replay.replayId,
    "ktv",
    runningReplay,
  ),
  true,
  "feedback request must bind the current replay revision and window",
);

const noPredictionWindow = Object.freeze({
  ...firstWindow,
  activityGate: {
    ...firstWindow.activityGate,
    status: "inactive",
    reasonCode: "ACTIVITY_BELOW_THRESHOLD",
  },
  predictedGesture: null,
  engineeringConfidence: "not_available",
});
const noPredictionReplay = Object.freeze({
  ...runningReplay,
  currentWindow: noPredictionWindow,
});
for (const [label, invalidRequest, expectedReplay] of [
  [
    "unknown correction gesture",
    {
      ...feedbackRequest,
      action: "correct",
      correctedGesture: "__invalid__",
    },
    runningReplay,
  ],
  [
    "correction equals prediction",
    {
      ...feedbackRequest,
      action: "correct",
      correctedGesture: firstWindow.predictedGesture,
    },
    runningReplay,
  ],
  [
    "correction without prediction",
    {
      ...feedbackRequest,
      action: "correct",
      correctedGesture: "hand_open",
    },
    noPredictionReplay,
  ],
  [
    "non-correction carries correctedGesture",
    { ...feedbackRequest, correctedGesture: "rest" },
    runningReplay,
  ],
  [
    "stale feedback revision",
    { ...feedbackRequest, expectedRevision: 0 },
    runningReplay,
  ],
]) {
  assert.equal(
    isFeedbackRequestForReplay(
      invalidRequest,
      replay.replayId,
      "ktv",
      expectedReplay,
    ),
    false,
    `${label} must fail closed`,
  );
}
assert.equal(
  isFeedbackRequestForReplay(
    feedbackRequest,
    replay.replayId,
    "patient",
    runningReplay,
  ),
  false,
  "patient feedback must fail closed before transport",
);
assert.equal(
  isFeedbackReceiptFor(
    feedbackReceipt,
    replay.replayId,
    feedbackRequest,
    "ktv",
    runningReplay,
  ),
  true,
  "feedback receipt must bind the exact request, actor, and source window",
);
assert.equal(
  isFeedbackReceiptFor(
    { ...feedbackReceipt, actorRole: "patient" },
    replay.replayId,
    feedbackRequest,
    "patient",
    runningReplay,
  ),
  false,
  "unauthorized mirrored actor role must not satisfy the receipt guard",
);
for (const [label, invalidReceipt] of [
  ["actor role", { ...feedbackReceipt, actorRole: "researcher" }],
  ["action", { ...feedbackReceipt, action: "accept" }],
  [
    "result hash",
    {
      ...feedbackReceipt,
      context: {
        ...feedbackReceipt.context,
        originalResultHashSha256: "d".repeat(64),
      },
    },
  ],
]) {
  assert.equal(
    isFeedbackReceiptFor(
      invalidReceipt,
      replay.replayId,
      feedbackRequest,
      "ktv",
      runningReplay,
    ),
    false,
    `mismatched feedback ${label} must fail closed`,
  );
}

async function withJsonResponse(payload, operation) {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => ({
    ok: true,
    json: async () => payload,
  });
  try {
    return await operation();
  } finally {
    globalThis.fetch = originalFetch;
  }
}

async function runClientValidationChecks() {
  const client = new HttpUC1ReplayClient("https://example.invalid");
  const createInput = {
    analysisId: replay.analysisId,
    scenarioId: replay.scenarioId,
  };

  const acceptedCreate = await withJsonResponse(replay, () =>
    client.createReplay(
      replay.sessionId,
      createInput,
      { idempotencyKey: opaqueKey },
    ),
  );
  assert.deepEqual(
    acceptedCreate,
    replay,
    "HTTP client must accept only the bound initial replay envelope",
  );

  for (const [label, invalidCreate] of [
    ["foreign session", { ...replay, sessionId: "SESSION-FOREIGN" }],
    ["terminal reveal", secondRunningReplay],
  ]) {
    await assert.rejects(
      () =>
        withJsonResponse(invalidCreate, () =>
          client.createReplay(
            replay.sessionId,
            createInput,
            { idempotencyKey: opaqueKey },
          ),
        ),
      (error) =>
        error instanceof UC1ReplayClientError &&
        error.code === "INVALID_REPLAY_RESPONSE",
      `HTTP create must reject ${label}`,
    );
  }

  const advanceInput = {
    expectedCurrentIndex: replay.currentIndex,
    expectedRevision: replay.revision,
  };
  const acceptedAdvance = await withJsonResponse(runningReplay, () =>
    client.advanceReplay(replay.replayId, advanceInput, {
      expectedReplay: replay,
    }),
  );
  assert.deepEqual(
    acceptedAdvance,
    runningReplay,
    "HTTP advance must accept exactly one bound transition",
  );

  const rewrittenPrefix = {
    ...secondRunningReplay,
    history: [
      { ...firstWindow, resultHashSha256: "d".repeat(64) },
    ],
  };
  const unsafeAdvance = {
    ...runningReplay,
    currentWindow: {
      ...firstWindow,
      safety: { ...firstWindow.safety, rawSamplesIncluded: true },
    },
  };
  for (const [label, invalidAdvance, previousReplay] of [
    [
      "foreign replay",
      { ...runningReplay, replayId: "REPLAY-FOREIGN" },
      replay,
    ],
    ["skipped cursor", secondRunningReplay, replay],
    ["rewritten visible prefix", rewrittenPrefix, runningReplay],
    ["unsafe safety literal", unsafeAdvance, replay],
  ]) {
    await assert.rejects(
      () =>
        withJsonResponse(invalidAdvance, () =>
          client.advanceReplay(
            previousReplay.replayId,
            {
              expectedCurrentIndex: previousReplay.currentIndex,
              expectedRevision: previousReplay.revision,
            },
            { expectedReplay: previousReplay },
          ),
        ),
      (error) =>
        error instanceof UC1ReplayClientError &&
        error.code === "INVALID_REPLAY_RESPONSE",
      `HTTP advance must reject ${label}`,
    );
  }

  await assert.rejects(
    () =>
      client.advanceReplay(
        replay.replayId,
        { ...advanceInput, expectedRevision: 99 },
        { expectedReplay: replay },
      ),
    (error) =>
      error instanceof UC1ReplayClientError &&
      error.code === "INVALID_REPLAY_ADVANCE_CONTEXT",
    "HTTP advance must reject a caller-supplied stale envelope",
  );

  const acceptedReceipt = await withJsonResponse(feedbackReceipt, () =>
    client.submitFeedback(replay.replayId, feedbackRequest, {
      actorRole: "ktv",
      expectedReplay: runningReplay,
      idempotencyKey: opaqueKey,
    }),
  );
  assert.deepEqual(
    acceptedReceipt,
    feedbackReceipt,
    "HTTP client must accept an exactly bound feedback receipt",
  );

  const mismatchedReceipt = {
    ...feedbackReceipt,
    context: {
      ...feedbackReceipt.context,
      sourceHashSha256: "e".repeat(64),
    },
  };
  await assert.rejects(
    () =>
      withJsonResponse(mismatchedReceipt, () =>
        client.submitFeedback(replay.replayId, feedbackRequest, {
          actorRole: "ktv",
          expectedReplay: runningReplay,
          idempotencyKey: opaqueKey,
        }),
      ),
    (error) =>
      error instanceof UC1ReplayClientError &&
      error.code === "INVALID_FEEDBACK_RESPONSE",
    "HTTP client must reject mismatched feedback provenance",
  );

  await assert.rejects(
    () =>
      withJsonResponse(
        { ...feedbackReceipt, actorRole: "patient" },
        () =>
          client.submitFeedback(replay.replayId, feedbackRequest, {
            actorRole: "patient",
            expectedReplay: runningReplay,
            idempotencyKey: opaqueKey,
          }),
      ),
    (error) =>
      error instanceof UC1ReplayClientError &&
      error.code === "FEEDBACK_ROLE_FORBIDDEN",
    "HTTP client must reject patient feedback before transport",
  );

  for (const [label, invalidRequest] of [
    [
      "unknown correction",
      {
        ...feedbackRequest,
        action: "correct",
        correctedGesture: "__invalid__",
      },
    ],
    [
      "same-as-prediction correction",
      {
        ...feedbackRequest,
        action: "correct",
        correctedGesture: firstWindow.predictedGesture,
      },
    ],
    ["stale revision", { ...feedbackRequest, expectedRevision: 0 }],
  ]) {
    await assert.rejects(
      () =>
        withJsonResponse(feedbackReceipt, () =>
          client.submitFeedback(replay.replayId, invalidRequest, {
            actorRole: "ktv",
            expectedReplay: runningReplay,
            idempotencyKey: opaqueKey,
          }),
        ),
      (error) =>
        error instanceof UC1ReplayClientError &&
        error.code === "INVALID_FEEDBACK_REQUEST_CONTEXT",
      `HTTP feedback must reject ${label}`,
    );
  }
}

runClientValidationChecks()
  .then(() => console.log("Day 22 frontend runtime tests passed."))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
