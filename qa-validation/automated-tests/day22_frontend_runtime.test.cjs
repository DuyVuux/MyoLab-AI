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
  engineeringConfidence: "engineering_high",
  latency,
  fatigueOverlay: {
    status: "stable",
    source: "scenario_fixture",
    confidenceAdjustmentApplied: false,
    reasonCodes: [],
    evidenceSummaryVi: "Không có cảnh báo thay đổi kỹ thuật trong fixture này.",
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
  history: [firstWindow],
  latencySummary: { ...replay.latencySummary, observedWindowCount: 1, p50Ms: 270, p95Ms: 270 },
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
  visibleReplayWindows(runningReplay).some((window) => window.windowId === secondWindow.windowId),
  false,
  "history must not expose future windows",
);

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

console.log("Day 22 frontend runtime tests passed.");
