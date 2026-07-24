import type {
  FeedbackActorRole,
  GestureFeedbackReceipt,
  GestureFeedbackRequest,
} from "../schemas/gesture-feedback-context.schema";
import type {
  GestureInferenceWindow,
  UC1ReplaySession,
} from "../schemas/gesture-inference.schema";
import { isLatencyBreakdownValid } from "../lib/latencyMetrics";

const GESTURE_IDS = [
  "rest",
  "hand_open",
  "hand_close",
  "wrist_flexion",
  "wrist_extension",
] as const;
const ACTIVE_GESTURES = [
  "hand_open",
  "hand_close",
  "wrist_flexion",
  "wrist_extension",
] as const;
const CONFIDENCE_LEVELS = [
  "engineering_high",
  "engineering_moderate",
  "engineering_low",
  "engineering_very_low",
  "not_available",
] as const;
const ACTIVITY_STATES = ["active", "inactive", "uncertain"] as const;
const QUALITY_STATES = ["pass", "warning", "fail"] as const;
const QUALITY_SOURCES = [
  "day20_quality_gate",
  "day17_signal_quality",
  "scenario_fixture",
  "not_available",
] as const;
const FATIGUE_STATES = [
  "stable",
  "warning",
  "abstain",
  "not_available",
] as const;
const FATIGUE_SOURCES = [
  "scenario_fixture",
  "analysis_summary",
  "not_available",
] as const;
const DEVICE_STATES = [
  "connected",
  "reconnecting",
  "disconnected",
] as const;
const REPLAY_STATES = [
  "idle",
  "running",
  "completed",
  "abstained",
  "disconnected",
  "failed",
] as const;
const REPLAY_SCENARIOS = [
  "uc1_golden_correct",
  "uc1_ambiguous_prediction",
  "uc1_no_activity",
  "uc1_fatigue_confidence_drop",
  "uc1_electrode_shift_warning",
  "uc1_qc_fail_abstention",
  "uc1_device_disconnect",
] as const;
const FEEDBACK_ACTIONS = [
  "accept",
  "correct",
  "uncertain",
  "remeasure",
] as const;
const REVIEWER_CERTAINTIES = ["low", "moderate", "high"] as const;
const FEEDBACK_ACTOR_ROLES = [
  "ktv",
  "physician",
  "researcher",
  "ml_qa",
] as const;
const CONFIDENCE_RANK: Readonly<Record<string, number>> = {
  not_available: 0,
  engineering_very_low: 1,
  engineering_low: 2,
  engineering_moderate: 3,
  engineering_high: 4,
};
const SHA256_PATTERN = /^[0-9a-f]{64}$/;
const UUID_V4_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(
  value: Record<string, unknown>,
  required: readonly string[],
  optional: readonly string[] = [],
): boolean {
  const allowed = new Set([...required, ...optional]);
  return (
    required.every((key) => Object.hasOwn(value, key)) &&
    Object.keys(value).every((key) => allowed.has(key))
  );
}

function isOneOf(
  value: unknown,
  choices: readonly string[],
): value is string {
  return typeof value === "string" && choices.includes(value);
}

export function isFeedbackActorRole(
  value: unknown,
): value is FeedbackActorRole {
  return isOneOf(value, FEEDBACK_ACTOR_ROLES);
}

function isNonEmptyText(value: unknown, maxLength = 200): value is string {
  return (
    typeof value === "string" &&
    value.length > 0 &&
    value.length <= maxLength
  );
}

function isFiniteNonNegative(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0;
}

function isFinitePositive(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value > 0;
}

function isIntegerAtLeast(value: unknown, minimum: number): value is number {
  return Number.isInteger(value) && (value as number) >= minimum;
}

function isUniqueTextArray(
  value: unknown,
  minimumItems = 0,
  maximumItems = 32,
  maximumTextLength = 500,
): value is string[] {
  return (
    Array.isArray(value) &&
    value.length >= minimumItems &&
    value.length <= maximumItems &&
    value.every((item) => isNonEmptyText(item, maximumTextLength)) &&
    new Set(value).size === value.length
  );
}

function isSegmentReference(value: unknown): boolean {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "rawSignalRef",
      "sourceHashSha256",
      "startSample",
      "endSampleExclusive",
      "startTimeS",
      "endTimeExclusiveS",
      "channelIds",
      "repetitionId",
      "calibrationId",
    ])
  ) {
    return false;
  }

  return (
    isNonEmptyText(value.rawSignalRef) &&
    typeof value.sourceHashSha256 === "string" &&
    SHA256_PATTERN.test(value.sourceHashSha256) &&
    isIntegerAtLeast(value.startSample, 0) &&
    isIntegerAtLeast(value.endSampleExclusive, 1) &&
    value.endSampleExclusive > value.startSample &&
    isFiniteNonNegative(value.startTimeS) &&
    isFinitePositive(value.endTimeExclusiveS) &&
    value.endTimeExclusiveS > value.startTimeS &&
    isUniqueTextArray(value.channelIds, 1, 64, 200) &&
    isNonEmptyText(value.repetitionId) &&
    isNonEmptyText(value.calibrationId)
  );
}

function isActivityGate(value: unknown): boolean {
  return (
    isRecord(value) &&
    hasExactKeys(value, [
      "status",
      "windowRmsUv",
      "activationThresholdUv",
      "releaseThresholdUv",
      "reasonCode",
    ]) &&
    isOneOf(value.status, ACTIVITY_STATES) &&
    isFiniteNonNegative(value.windowRmsUv) &&
    isFinitePositive(value.activationThresholdUv) &&
    isFinitePositive(value.releaseThresholdUv) &&
    isNonEmptyText(value.reasonCode)
  );
}

function isQualityContext(value: unknown): boolean {
  return (
    isRecord(value) &&
    hasExactKeys(value, [
      "source",
      "qualityResultId",
      "status",
      "reasonCodes",
    ]) &&
    isOneOf(value.source, QUALITY_SOURCES) &&
    isNonEmptyText(value.qualityResultId) &&
    isOneOf(value.status, QUALITY_STATES) &&
    isUniqueTextArray(value.reasonCodes)
  );
}

function isFatigueOverlay(value: unknown): boolean {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "source",
      "status",
      "confidenceAdjustmentApplied",
      "reasonCodes",
      "evidenceSummaryVi",
      "counterevidenceVi",
      "limitationsVi",
    ]) ||
    !isOneOf(value.source, FATIGUE_SOURCES) ||
    !isOneOf(value.status, FATIGUE_STATES) ||
    typeof value.confidenceAdjustmentApplied !== "boolean" ||
    !isUniqueTextArray(value.reasonCodes) ||
    !isUniqueTextArray(value.evidenceSummaryVi) ||
    !isUniqueTextArray(value.counterevidenceVi) ||
    !isUniqueTextArray(value.limitationsVi)
  ) {
    return false;
  }

  if (
    (value.source === "not_available") !==
    (value.status === "not_available")
  ) {
    return false;
  }

  return (
    value.status !== "warning" ||
    (value.source !== "not_available" &&
      value.confidenceAdjustmentApplied === true &&
      value.reasonCodes.length > 0 &&
      value.evidenceSummaryVi.length > 0)
  );
}

function isLatency(value: unknown): boolean {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "totalMs",
      "acquisitionMs",
      "windowMs",
      "preprocessMs",
      "inferenceMs",
      "transportRenderMs",
    ]) ||
    ![
      value.totalMs,
      value.acquisitionMs,
      value.windowMs,
      value.preprocessMs,
      value.inferenceMs,
      value.transportRenderMs,
    ].every(isFiniteNonNegative)
  ) {
    return false;
  }
  return isLatencyBreakdownValid(
    value as unknown as GestureInferenceWindow["latency"],
  );
}

function isSafetyBoundary(value: unknown): boolean {
  return (
    isRecord(value) &&
    hasExactKeys(value, [
      "scoreIsProbability",
      "clinicalUseAllowed",
      "rawSamplesIncluded",
      "physicalActuationAllowed",
    ]) &&
    value.scoreIsProbability === false &&
    value.clinicalUseAllowed === false &&
    value.rawSamplesIncluded === false &&
    value.physicalActuationAllowed === false
  );
}

function isGestureWindow(value: unknown): value is GestureInferenceWindow {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "schemaVersion",
      "windowId",
      "sessionId",
      "analysisId",
      "protocolVersion",
      "segmentRef",
      "targetGesture",
      "activityGate",
      "predictedGesture",
      "baseEngineeringConfidence",
      "engineeringConfidence",
      "qualityContext",
      "fatigueOverlay",
      "deviceState",
      "latency",
      "requiresHumanReview",
      "sourceType",
      "modelVersion",
      "modelValidationStatus",
      "resultHashSha256",
      "safety",
    ]) ||
    value.schemaVersion !== "gesture-inference.v0.1" ||
    !isNonEmptyText(value.windowId) ||
    !isNonEmptyText(value.sessionId) ||
    !isNonEmptyText(value.analysisId) ||
    !isNonEmptyText(value.protocolVersion) ||
    !isSegmentReference(value.segmentRef) ||
    !isOneOf(value.targetGesture, ACTIVE_GESTURES) ||
    !(
      value.predictedGesture === null ||
      isOneOf(value.predictedGesture, ACTIVE_GESTURES)
    ) ||
    !isOneOf(value.baseEngineeringConfidence, CONFIDENCE_LEVELS) ||
    !isOneOf(value.engineeringConfidence, CONFIDENCE_LEVELS) ||
    !isActivityGate(value.activityGate) ||
    !isQualityContext(value.qualityContext) ||
    !isFatigueOverlay(value.fatigueOverlay) ||
    !isOneOf(value.deviceState, DEVICE_STATES) ||
    !isLatency(value.latency) ||
    value.requiresHumanReview !== true ||
    value.sourceType !== "synthetic_replay" ||
    !isNonEmptyText(value.modelVersion) ||
    value.modelValidationStatus !== "not_validated" ||
    typeof value.resultHashSha256 !== "string" ||
    !SHA256_PATTERN.test(value.resultHashSha256) ||
    !isSafetyBoundary(value.safety)
  ) {
    return false;
  }

  const window = value as unknown as GestureInferenceWindow;
  const blocked =
    window.activityGate.status !== "active" ||
    window.qualityContext.status === "fail" ||
    window.deviceState !== "connected" ||
    window.fatigueOverlay.status === "abstain";
  if (
    (blocked || window.predictedGesture === null) &&
    (window.predictedGesture !== null ||
      window.engineeringConfidence !== "not_available")
  ) {
    return false;
  }

  const baseRank = CONFIDENCE_RANK[window.baseEngineeringConfidence];
  const finalRank = CONFIDENCE_RANK[window.engineeringConfidence];
  if (
    finalRank > baseRank ||
    (window.fatigueOverlay.status === "warning" &&
      finalRank >= baseRank)
  ) {
    return false;
  }

  return (
    window.predictedGesture === null ||
    (window.activityGate.status === "active" &&
      window.qualityContext.status !== "fail" &&
      window.deviceState === "connected" &&
      window.fatigueOverlay.status !== "abstain" &&
      window.engineeringConfidence !== "not_available")
  );
}

function isReplayStateCursorValid(
  state: string,
  currentIndex: number,
  totalWindows: number,
): boolean {
  if (totalWindows === 0) {
    return state === "abstained" && currentIndex === -1;
  }
  if (state === "idle") return currentIndex === -1;
  if (state === "running") {
    return currentIndex >= 0 && currentIndex < totalWindows - 1;
  }
  if (["completed", "abstained", "disconnected"].includes(state)) {
    return currentIndex === totalWindows - 1;
  }
  return (
    state === "failed" && currentIndex >= -1 && currentIndex < totalWindows
  );
}

function isLatencySummary(value: unknown, observedWindows: number): boolean {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "observedWindowCount",
      "p50Ms",
      "p95Ms",
      "droppedWindows",
      "disconnectTimeoutMs",
    ]) ||
    !isIntegerAtLeast(value.observedWindowCount, 0) ||
    value.observedWindowCount !== observedWindows ||
    !isIntegerAtLeast(value.droppedWindows, 0) ||
    !isIntegerAtLeast(value.disconnectTimeoutMs, 1)
  ) {
    return false;
  }

  if (observedWindows === 0) {
    return value.p50Ms === null && value.p95Ms === null;
  }
  return (
    isFiniteNonNegative(value.p50Ms) &&
    isFiniteNonNegative(value.p95Ms) &&
    value.p50Ms <= value.p95Ms
  );
}

export function isSafeReplayPayload(
  value: unknown,
): value is UC1ReplaySession {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "schemaVersion",
      "replayId",
      "sessionId",
      "analysisId",
      "scenarioId",
      "state",
      "currentIndex",
      "revision",
      "totalWindows",
      "currentWindow",
      "history",
      "latencySummary",
      "reasonCodes",
      "sourceType",
      "modelValidationStatus",
      "clinicalUseAllowed",
      "humanReviewRequired",
    ]) ||
    value.schemaVersion !== "uc1-replay-session.v0.1" ||
    !isNonEmptyText(value.replayId) ||
    !isNonEmptyText(value.sessionId) ||
    !isNonEmptyText(value.analysisId) ||
    !isOneOf(value.scenarioId, REPLAY_SCENARIOS) ||
    !isOneOf(value.state, REPLAY_STATES) ||
    !isIntegerAtLeast(value.currentIndex, -1) ||
    !isIntegerAtLeast(value.revision, 0) ||
    !isIntegerAtLeast(value.totalWindows, 0) ||
    !Array.isArray(value.history) ||
    value.history.length > 10000 ||
    !isUniqueTextArray(value.reasonCodes) ||
    value.sourceType !== "synthetic_replay" ||
    value.modelValidationStatus !== "not_validated" ||
    value.clinicalUseAllowed !== false ||
    value.humanReviewRequired !== true
  ) {
    return false;
  }

  if (
    value.revision !== Math.max(0, value.currentIndex + 1) ||
    value.history.length !== Math.max(0, value.currentIndex) ||
    !isReplayStateCursorValid(
      value.state,
      value.currentIndex,
      value.totalWindows,
    ) ||
    (value.currentIndex === -1 && value.currentWindow !== null)
  ) {
    return false;
  }

  if (value.currentIndex === -1) {
    return isLatencySummary(value.latencySummary, 0);
  }
  if (
    value.currentIndex >= value.totalWindows ||
    !isGestureWindow(value.currentWindow)
  ) {
    return false;
  }

  const windows: GestureInferenceWindow[] = [];
  for (const historyWindow of value.history) {
    if (!isGestureWindow(historyWindow)) return false;
    windows.push(historyWindow);
  }
  windows.push(value.currentWindow);

  const windowIds = new Set<string>();
  let previousStartSample = -1;
  let previousStartTimeS = -1;
  for (const window of windows) {
    if (
      window.sessionId !== value.sessionId ||
      window.analysisId !== value.analysisId ||
      windowIds.has(window.windowId) ||
      window.segmentRef.startSample <= previousStartSample ||
      window.segmentRef.startTimeS <= previousStartTimeS
    ) {
      return false;
    }
    windowIds.add(window.windowId);
    previousStartSample = window.segmentRef.startSample;
    previousStartTimeS = window.segmentRef.startTimeS;
  }

  return isLatencySummary(value.latencySummary, windows.length);
}


function jsonValuesEqual(left: unknown, right: unknown): boolean {
  if (Object.is(left, right)) return true;
  if (Array.isArray(left) && Array.isArray(right)) {
    return (
      left.length === right.length &&
      left.every((item, index) => jsonValuesEqual(item, right[index]))
    );
  }
  if (isRecord(left) && isRecord(right)) {
    const leftKeys = Object.keys(left);
    const rightKeys = Object.keys(right);
    return (
      leftKeys.length === rightKeys.length &&
      leftKeys.every(
        (key) =>
          Object.hasOwn(right, key) &&
          jsonValuesEqual(left[key], right[key]),
      )
    );
  }
  return false;
}

export function isReplayCreatedFor(
  value: unknown,
  expectedSessionId: string,
  expectedAnalysisId: string,
  expectedScenarioId: string,
): value is UC1ReplaySession {
  if (!isSafeReplayPayload(value)) return false;

  const initialIdle =
    value.state === "idle" &&
    value.currentIndex === -1 &&
    value.revision === 0 &&
    value.currentWindow === null &&
    value.history.length === 0;
  const zeroWindowAbstention =
    value.state === "abstained" &&
    value.totalWindows === 0 &&
    value.currentIndex === -1 &&
    value.revision === 0 &&
    value.currentWindow === null &&
    value.history.length === 0;

  return (
    value.sessionId === expectedSessionId &&
    value.analysisId === expectedAnalysisId &&
    value.scenarioId === expectedScenarioId &&
    (initialIdle || zeroWindowAbstention)
  );
}

export function isReplayAdvanceFor(
  value: unknown,
  previousReplay: UC1ReplaySession,
): value is UC1ReplaySession {
  if (
    !isSafeReplayPayload(previousReplay) ||
    !isSafeReplayPayload(value) ||
    !["idle", "running"].includes(previousReplay.state)
  ) {
    return false;
  }

  const expectedHistory =
    previousReplay.currentWindow === null
      ? [...previousReplay.history]
      : [...previousReplay.history, previousReplay.currentWindow];

  return (
    value.replayId === previousReplay.replayId &&
    value.sessionId === previousReplay.sessionId &&
    value.analysisId === previousReplay.analysisId &&
    value.scenarioId === previousReplay.scenarioId &&
    value.totalWindows === previousReplay.totalWindows &&
    value.currentIndex === previousReplay.currentIndex + 1 &&
    value.revision === previousReplay.revision + 1 &&
    jsonValuesEqual(value.history, expectedHistory)
  );
}

export function isFeedbackRequestForReplay(
  value: unknown,
  replayId: string,
  actorRole: unknown,
  expectedReplay: UC1ReplaySession,
): value is GestureFeedbackRequest {
  if (
    !isFeedbackActorRole(actorRole) ||
    !isSafeReplayPayload(expectedReplay) ||
    expectedReplay.replayId !== replayId ||
    expectedReplay.currentWindow === null ||
    !isRecord(value) ||
    !hasExactKeys(
      value,
      [
        "action",
        "reviewerCertainty",
        "expectedWindowId",
        "expectedRevision",
      ],
      ["correctedGesture"],
    ) ||
    !isOneOf(value.action, FEEDBACK_ACTIONS) ||
    !isOneOf(value.reviewerCertainty, REVIEWER_CERTAINTIES) ||
    !isNonEmptyText(value.expectedWindowId) ||
    value.expectedWindowId !== expectedReplay.currentWindow.windowId ||
    !isIntegerAtLeast(value.expectedRevision, 0) ||
    value.expectedRevision !== expectedReplay.revision
  ) {
    return false;
  }

  if (value.action === "correct") {
    return (
      expectedReplay.currentWindow.predictedGesture !== null &&
      isOneOf(value.correctedGesture, GESTURE_IDS) &&
      value.correctedGesture !==
        expectedReplay.currentWindow.predictedGesture
    );
  }
  return !Object.hasOwn(value, "correctedGesture");
}
function feedbackContextMatchesWindow(
  value: unknown,
  window: GestureInferenceWindow,
): boolean {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "schemaVersion",
      "analysisId",
      "sessionId",
      "windowId",
      "rawSignalRef",
      "sourceHashSha256",
      "startSample",
      "endSampleExclusive",
      "startTimeS",
      "endTimeExclusiveS",
      "channelIds",
      "repetitionId",
      "calibrationId",
      "modelVersion",
      "originalResultHashSha256",
    ])
  ) {
    return false;
  }

  const segment = window.segmentRef;
  return (
    value.schemaVersion === "gesture-feedback-context.v0.1" &&
    value.analysisId === window.analysisId &&
    value.sessionId === window.sessionId &&
    value.windowId === window.windowId &&
    value.rawSignalRef === segment.rawSignalRef &&
    value.sourceHashSha256 === segment.sourceHashSha256 &&
    value.startSample === segment.startSample &&
    value.endSampleExclusive === segment.endSampleExclusive &&
    value.startTimeS === segment.startTimeS &&
    value.endTimeExclusiveS === segment.endTimeExclusiveS &&
    Array.isArray(value.channelIds) &&
    value.channelIds.length === segment.channelIds.length &&
    value.channelIds.every(
      (channelId, index) => channelId === segment.channelIds[index],
    ) &&
    value.repetitionId === segment.repetitionId &&
    value.calibrationId === segment.calibrationId &&
    value.modelVersion === window.modelVersion &&
    value.originalResultHashSha256 === window.resultHashSha256
  );
}

export function isFeedbackReceiptFor(
  value: unknown,
  replayId: string,
  request: GestureFeedbackRequest,
  actorRole: FeedbackActorRole,
  expectedReplay: UC1ReplaySession,
): value is GestureFeedbackReceipt {
  const expectedWindow = expectedReplay.currentWindow;
  if (
    expectedWindow === null ||
    !isFeedbackRequestForReplay(
      request,
      replayId,
      actorRole,
      expectedReplay,
    ) ||
    !isRecord(value) ||
    !hasExactKeys(value, [
      "schemaVersion",
      "feedbackId",
      "replayId",
      "action",
      "correctedGesture",
      "reviewerCertainty",
      "actorRole",
      "context",
      "automaticTrainingCandidate",
    ]) ||
    value.schemaVersion !== "gesture-feedback.v0.1" ||
    !isNonEmptyText(value.feedbackId) ||
    value.replayId !== replayId ||
    !isOneOf(value.action, FEEDBACK_ACTIONS) ||
    value.action !== request.action ||
    !isOneOf(value.reviewerCertainty, REVIEWER_CERTAINTIES) ||
    value.reviewerCertainty !== request.reviewerCertainty ||
    !isFeedbackActorRole(value.actorRole) ||
    value.actorRole !== actorRole ||
    value.automaticTrainingCandidate !== false ||
    !feedbackContextMatchesWindow(value.context, expectedWindow)
  ) {
    return false;
  }

  const expectedCorrection =
    request.action === "correct" ? request.correctedGesture : null;
  return value.correctedGesture === expectedCorrection;
}

export class SecureIdempotencyUnavailableError extends Error {
  public readonly code = "SECURE_IDEMPOTENCY_UNAVAILABLE";

  public constructor() {
    super("SECURE_IDEMPOTENCY_UNAVAILABLE");
    this.name = "SecureIdempotencyUnavailableError";
  }
}

export function canApplyReplayMutation(
  requestGeneration: number,
  activeGeneration: number,
  aborted: boolean,
): boolean {
  return (
    Number.isSafeInteger(requestGeneration) &&
    requestGeneration >= 0 &&
    Number.isSafeInteger(activeGeneration) &&
    activeGeneration >= 0 &&
    requestGeneration === activeGeneration &&
    !aborted
  );
}

export function getOrCreateOpaqueIdempotencyKey(
  cache: Map<string, string>,
  logicalFingerprint: string,
): string {
  const cached = cache.get(logicalFingerprint);
  if (cached !== undefined) return cached;

  const webCrypto = globalThis.crypto;
  if (typeof webCrypto?.randomUUID !== "function") {
    throw new SecureIdempotencyUnavailableError();
  }

  let generated: string;
  try {
    generated = webCrypto.randomUUID();
  } catch {
    throw new SecureIdempotencyUnavailableError();
  }
  if (!UUID_V4_PATTERN.test(generated)) {
    throw new SecureIdempotencyUnavailableError();
  }
  cache.set(logicalFingerprint, generated);
  return generated;
}
