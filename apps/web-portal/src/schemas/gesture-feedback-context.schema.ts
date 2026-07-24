import type { UserRole } from "./role.schema";
export type FeedbackActorRole = Exclude<UserRole, "patient" | "admin">;

import type {
  GestureId,
  GestureInferenceWindow,
} from "./gesture-inference.schema";

export interface GestureFeedbackContext {
  readonly schemaVersion: "gesture-feedback-context.v0.1";
  readonly analysisId: string;
  readonly sessionId: string;
  readonly windowId: string;
  readonly rawSignalRef: string;
  readonly sourceHashSha256: string;
  readonly startSample: number;
  readonly endSampleExclusive: number;
  readonly startTimeS: number;
  readonly endTimeExclusiveS: number;
  readonly channelIds: readonly string[];
  readonly repetitionId: string;
  readonly calibrationId: string;
  readonly modelVersion: string;
  readonly originalResultHashSha256: string;
}

export type ReviewerCertainty = "low" | "moderate" | "high";

export type GestureFeedbackDecision =
  | {
      readonly action: "accept" | "uncertain" | "remeasure";
      readonly reviewerCertainty: ReviewerCertainty;
      readonly correctedGesture?: never;
    }
  | {
      readonly action: "correct";
      readonly reviewerCertainty: ReviewerCertainty;
      readonly correctedGesture: GestureId;
    };

export type GestureFeedbackRequest = GestureFeedbackDecision & {
  readonly expectedWindowId: string;
  readonly expectedRevision: number;
};

export interface GestureFeedbackReceipt {
  readonly schemaVersion: "gesture-feedback.v0.1";
  readonly feedbackId: string;
  readonly replayId: string;
  readonly action: GestureFeedbackDecision["action"];
  readonly correctedGesture: GestureId | null;
  readonly reviewerCertainty: ReviewerCertainty;
  readonly actorRole: FeedbackActorRole;
  readonly automaticTrainingCandidate: false;
  readonly context: GestureFeedbackContext;
}

/**
 * Converts an already-revealed, server-issued window into the exact context shape.
 * This helper copies provenance; it never generates a model version or result hash.
 */
export function feedbackContextFromWindow(
  window: GestureInferenceWindow,
): GestureFeedbackContext {
  return {
    schemaVersion: "gesture-feedback-context.v0.1",
    analysisId: window.analysisId,
    sessionId: window.sessionId,
    windowId: window.windowId,
    rawSignalRef: window.segmentRef.rawSignalRef,
    sourceHashSha256: window.segmentRef.sourceHashSha256,
    startSample: window.segmentRef.startSample,
    endSampleExclusive: window.segmentRef.endSampleExclusive,
    startTimeS: window.segmentRef.startTimeS,
    endTimeExclusiveS: window.segmentRef.endTimeExclusiveS,
    channelIds: [...window.segmentRef.channelIds],
    repetitionId: window.segmentRef.repetitionId,
    calibrationId: window.segmentRef.calibrationId,
    modelVersion: window.modelVersion,
    originalResultHashSha256: window.resultHashSha256,
  };
}
