export type CalibrationState =
  | "not_started"
  | "setup_check"
  | "rest_baseline"
  | "gesture_repetitions"
  | "summary"
  | "pass"
  | "warning"
  | "fail"
  | "cancelled";

export interface SegmentReference {
  readonly rawSignalRef: string;
  readonly sourceHashSha256: string;
  readonly startSample: number;
  readonly endSample: number;
  readonly startTimeS: number;
  readonly endTimeS: number;
  readonly channelIds: readonly string[];
}

export interface CalibrationRepetition {
  readonly repetitionId: string;
  readonly gestureId: string;
  readonly quality: "accepted" | "rejected";
  readonly segmentRef: SegmentReference;
  readonly reasonCodes: readonly string[];
}

export interface CalibrationRecord {
  readonly schemaVersion: "calibration-record.v0.1";
  readonly calibrationId: string;
  readonly sessionId: string;
  readonly state: CalibrationState;
  readonly restRmsUv: number | null;
  readonly restSigmaUv: number | null;
  readonly activityThresholdCandidateUv: number | null;
  readonly engineeringK: number | null;
  readonly plannedRepetitions: number;
  readonly acceptedRepetitions: number;
  readonly rejectedRepetitions: number;
  readonly usableRepetitionRatio: number;
  readonly durationS: number;
  readonly warningAcknowledged: boolean;
  readonly reasonCodes: readonly string[];
  readonly repetitions: readonly CalibrationRepetition[];
  readonly rawSamplesIncluded: false;
}

export const usableRepetitionRatio = (accepted: number, planned: number): number =>
  planned > 0 ? accepted / planned : 0;
