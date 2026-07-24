import type { FeedbackActorRole } from "./gesture-feedback-context.schema";

import type {
  ActiveGestureId,
  GestureId,
  GestureInferenceWindow,
} from "./gesture-inference.schema";

const activeGesture: ActiveGestureId = "wrist_extension";
const feedbackActor: FeedbackActorRole = "ktv";
const correctionGesture: GestureId = "rest";
const targetGesture: GestureInferenceWindow["targetGesture"] = activeGesture;
const predictedGesture: NonNullable<
  GestureInferenceWindow["predictedGesture"]
> = activeGesture;

// @ts-expect-error Rest is feedback vocabulary, never an active target.
const invalidRestTarget: GestureInferenceWindow["targetGesture"] = "rest";
// @ts-expect-error Rest is feedback vocabulary, never an active prediction.
const invalidRestPrediction: NonNullable<
  GestureInferenceWindow["predictedGesture"]
> = "rest";

// @ts-expect-error Patient feedback is never accepted by the technical API.
const invalidPatientActor: FeedbackActorRole = "patient";
// @ts-expect-error Admin feedback is never accepted by the technical API.
const invalidAdminActor: FeedbackActorRole = "admin";

void [
  correctionGesture,
  feedbackActor,
  invalidPatientActor,
  invalidAdminActor,
  targetGesture,
  predictedGesture,
  invalidRestTarget,
  invalidRestPrediction,
];
