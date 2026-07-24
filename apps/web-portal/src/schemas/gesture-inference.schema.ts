export const ACTIVE_GESTURE_IDS = [
  "hand_open",
  "hand_close",
  "wrist_flexion",
  "wrist_extension",
] as const;

export type ActiveGestureId = (typeof ACTIVE_GESTURE_IDS)[number];

export const GESTURE_IDS = ["rest", ...ACTIVE_GESTURE_IDS] as const;

export type GestureId = (typeof GESTURE_IDS)[number];

export const ENGINEERING_CONFIDENCE_LEVELS = [
  "engineering_high",
  "engineering_moderate",
  "engineering_low",
  "engineering_very_low",
  "not_available",
] as const;

export type EngineeringConfidence =
  (typeof ENGINEERING_CONFIDENCE_LEVELS)[number];

export type ActivityGateStatus = "inactive" | "uncertain" | "active";
export type QualityStatus = "pass" | "warning" | "fail";
export type FatigueOverlayStatus =
  | "stable"
  | "warning"
  | "abstain"
  | "not_available";
export type FatigueEvidenceSource =
  | "scenario_fixture"
  | "analysis_summary"
  | "not_available";
export type DeviceState = "connected" | "reconnecting" | "disconnected";

export interface GestureSegmentReference {
  readonly rawSignalRef: string;
  readonly sourceHashSha256: string;
  readonly startSample: number;
  readonly endSampleExclusive: number;
  readonly startTimeS: number;
  readonly endTimeExclusiveS: number;
  readonly channelIds: readonly string[];
  readonly repetitionId: string;
  readonly calibrationId: string;
}

export interface ActivityGateSummary {
  readonly status: ActivityGateStatus;
  readonly windowRmsUv: number;
  readonly activationThresholdUv: number;
  readonly releaseThresholdUv: number;
  readonly reasonCode: string;
}

export type QualityEvidenceSource =
  | "day20_quality_gate"
  | "day17_signal_quality"
  | "scenario_fixture"
  | "not_available";

export interface GestureQualityContext {
  readonly source: QualityEvidenceSource;
  readonly qualityResultId: string;
  readonly status: QualityStatus;
  readonly reasonCodes: readonly string[];
}

export interface FatigueOverlay {
  readonly source: FatigueEvidenceSource;
  readonly status: FatigueOverlayStatus;
  readonly confidenceAdjustmentApplied: boolean;
  readonly reasonCodes: readonly string[];
  readonly evidenceSummaryVi: readonly string[];
  readonly counterevidenceVi: readonly string[];
  readonly limitationsVi: readonly string[];
}

export interface LatencyBreakdown {
  readonly totalMs: number;
  readonly acquisitionMs: number;
  readonly windowMs: number;
  readonly preprocessMs: number;
  readonly inferenceMs: number;
  readonly transportRenderMs: number;
}

export interface GestureSafetyBoundary {
  readonly scoreIsProbability: false;
  readonly clinicalUseAllowed: false;
  readonly rawSamplesIncluded: false;
  readonly physicalActuationAllowed: false;
}

export interface GestureInferenceWindow {
  readonly schemaVersion: "gesture-inference.v0.1";
  readonly windowId: string;
  readonly sessionId: string;
  readonly analysisId: string;
  readonly protocolVersion: string;
  readonly segmentRef: GestureSegmentReference;
  readonly targetGesture: ActiveGestureId;
  readonly activityGate: ActivityGateSummary;
  readonly predictedGesture: ActiveGestureId | null;
  readonly baseEngineeringConfidence: EngineeringConfidence;
  readonly engineeringConfidence: EngineeringConfidence;
  readonly qualityContext: GestureQualityContext;
  readonly fatigueOverlay: FatigueOverlay;
  readonly deviceState: DeviceState;
  readonly latency: LatencyBreakdown;
  readonly requiresHumanReview: true;
  readonly sourceType: "synthetic_replay";
  readonly modelVersion: string;
  readonly modelValidationStatus: "not_validated";
  readonly resultHashSha256: string;
  readonly safety: GestureSafetyBoundary;
}

export const UC1_REPLAY_SCENARIOS = [
  "uc1_golden_correct",
  "uc1_ambiguous_prediction",
  "uc1_no_activity",
  "uc1_fatigue_confidence_drop",
  "uc1_electrode_shift_warning",
  "uc1_qc_fail_abstention",
  "uc1_device_disconnect",
] as const;

export type UC1ReplayScenarioId = (typeof UC1_REPLAY_SCENARIOS)[number];

export type UC1ReplayState =
  | "idle"
  | "running"
  | "completed"
  | "abstained"
  | "disconnected"
  | "failed";

export interface ReplayLatencySummary {
  readonly observedWindowCount: number;
  readonly p50Ms: number | null;
  readonly p95Ms: number | null;
  readonly droppedWindows: number;
  readonly disconnectTimeoutMs: number;
}

/**
 * Public replay representation. It intentionally has no all-windows collection:
 * `history` contains past windows only; `currentWindow` is the separately
 * emitted cursor window. No future-window collection is allowed.
 */
export interface UC1ReplaySession {
  readonly schemaVersion: "uc1-replay-session.v0.1";
  readonly replayId: string;
  readonly sessionId: string;
  readonly analysisId: string;
  readonly scenarioId: UC1ReplayScenarioId;
  readonly state: UC1ReplayState;
  readonly currentIndex: number;
  readonly revision: number;
  readonly totalWindows: number;
  readonly currentWindow: GestureInferenceWindow | null;
  readonly history: readonly GestureInferenceWindow[];
  readonly latencySummary: ReplayLatencySummary;
  readonly reasonCodes: readonly string[];
  readonly sourceType: "synthetic_replay";
  readonly modelValidationStatus: "not_validated";
  readonly clinicalUseAllowed: false;
  readonly humanReviewRequired: true;
}

export function isUC1ReplayScenarioId(
  value: string,
): value is UC1ReplayScenarioId {
  return (UC1_REPLAY_SCENARIOS as readonly string[]).includes(value);
}
