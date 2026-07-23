import type { AnalysisHandoff } from "../schemas/analysis-handoff.schema";
import type { CalibrationRecord } from "../schemas/calibration.schema";
import type { ChannelMapping } from "../schemas/channel-mapping.schema";
import type { SignalImportRecord } from "../schemas/import-workflow.schema";
import type { PreflightSummary } from "../schemas/preflight.schema";
import type { DetailedQualityResult } from "../schemas/quality-gate.schema";

export type Day20ScenarioId =
  | "golden_intake_pass"
  | "import_missing_unit"
  | "import_duplicate"
  | "import_rejected_corrupt_file"
  | "calibration_warning"
  | "calibration_fail"
  | "qc_warning_powerline"
  | "qc_fail_flatline";

export const goldenMappings: readonly ChannelMapping[] = [
  { sourceChannel: "Sensor 1", canonicalChannelId: "CH01", muscle: "Flexor carpi radialis", side: "right", unit: "uV", functionalRole: "flexor" },
  { sourceChannel: "Sensor 2", canonicalChannelId: "CH02", muscle: "Extensor carpi radialis", side: "right", unit: "uV", functionalRole: "extensor" },
  { sourceChannel: "Sensor 3", canonicalChannelId: "CH03", muscle: "Biceps brachii", side: "right", unit: "uV", functionalRole: "compensation" },
  { sourceChannel: "Sensor 4", canonicalChannelId: "CH04", muscle: "Upper trapezius", side: "right", unit: "uV", functionalRole: "compensation" },
];

export const goldenImport: SignalImportRecord = {
  schemaVersion: "signal-import-record.v0.1",
  importId: "IMPORT-D20-001",
  sessionId: "SESSION-D20-001",
  sourceType: "generic_csv_manifest",
  state: "qc_ready",
  sanitizedFilename: "session_demo_001.csv",
  sizeBytes: 7680000,
  sourceHashSha256: "sha256:d20-source-001",
  detectedMetadata: {
    samplingRateHz: 1000,
    durationS: 70,
    channelCount: 4,
    signalUnit: "uV",
    timeColumn: "time_s",
    signalColumns: ["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"],
    deviceVendor: "synthetic",
    timestampMonotonic: true,
  },
  rawSamplesIncluded: false,
  containsDirectIdentifier: false,
};

export const goldenPreflight: PreflightSummary = {
  schemaVersion: "preflight-summary.v0.1",
  preflightId: "PREFLIGHT-D20-001",
  sessionId: "SESSION-D20-001",
  importId: "IMPORT-D20-001",
  state: "ready",
  samplingRateHz: 1000,
  durationS: 70,
  channelCount: 4,
  mappingCompleteness: 1,
  timestampMonotonic: true,
  nonFiniteRatio: 0,
  flatlineSuspected: false,
  clippingSuspected: false,
  powerlineWarning: false,
  motionArtifactWarning: false,
  sourceHashSha256: "sha256:d20-source-001",
  preview: [
    { timeS: 0, valueUv: 0 },
    { timeS: 0.1, valueUv: 15 },
    { timeS: 0.2, valueUv: -9 },
  ],
  reasonCodes: [],
  rawSamplesIncluded: false,
};

const segment = {
  rawSignalRef: "RAW-REF-D20-001",
  sourceHashSha256: "sha256:d20-source-001",
  startSample: 5000,
  endSample: 6000,
  startTimeS: 5,
  endTimeS: 6,
  channelIds: ["CH01", "CH02", "CH03", "CH04"],
} as const;

export const goldenCalibration: CalibrationRecord = {
  schemaVersion: "calibration-record.v0.1",
  calibrationId: "CAL-D20-001",
  sessionId: "SESSION-D20-001",
  state: "pass",
  restRmsUv: 4.2,
  restSigmaUv: 0.8,
  activityThresholdCandidateUv: 6.6,
  engineeringK: 3,
  plannedRepetitions: 15,
  acceptedRepetitions: 14,
  rejectedRepetitions: 1,
  usableRepetitionRatio: 14 / 15,
  durationS: 142,
  warningAcknowledged: false,
  reasonCodes: [],
  repetitions: [
    { repetitionId: "REP-D20-001", gestureId: "wrist_extension", quality: "accepted", segmentRef: segment, reasonCodes: [] },
  ],
  rawSamplesIncluded: false,
};

export const qualityPass: DetailedQualityResult = {
  schemaVersion: "detailed-quality-result.v0.1",
  qualityResultId: "QC-D20-PASS",
  sessionId: "SESSION-D20-001",
  status: "pass",
  usableWindowRatio: 0.94,
  badChannels: [],
  artifactFlags: [],
  reasonCodes: [],
  mfcvEligibility: "not_assessed",
  recommendedActionsVi: [],
  qcVersion: "qc_v0.1",
};

export const qualityWarning: DetailedQualityResult = {
  ...qualityPass,
  qualityResultId: "QC-D20-WARNING",
  status: "warning",
  usableWindowRatio: 0.82,
  artifactFlags: ["POWERLINE_NOISE_HIGH"],
  reasonCodes: ["POWERLINE_NOISE_HIGH"],
  mfcvEligibility: "not_eligible",
  recommendedActionsVi: ["KTV xác nhận cảnh báo trước khi tiếp tục."],
};

export const qualityFail: DetailedQualityResult = {
  ...qualityPass,
  qualityResultId: "QC-D20-FAIL",
  status: "fail",
  usableWindowRatio: 0.31,
  badChannels: ["CH02"],
  artifactFlags: ["FLATLINE_EXCESSIVE"],
  reasonCodes: ["FLATLINE_EXCESSIVE"],
  mfcvEligibility: "not_eligible",
  recommendedActionsVi: ["Kiểm tra lại điện cực và đo lại."],
};

export const queuedHandoff: AnalysisHandoff = {
  schemaVersion: "analysis-handoff.v0.1",
  analysisId: "AN-D20-001",
  sessionId: "SESSION-D20-001",
  useCaseId: "uc1",
  status: "queued",
  nextRoute: "/uc1/session/SESSION-D20-001",
  protocolVersion: "upper-limb-gesture.v0.1",
  calibrationId: "CAL-D20-001",
  qualityResultId: "QC-D20-PASS",
  sourceHashSha256: "sha256:d20-source-001",
  scoreIsProbability: false,
  clinicalUseAllowed: false,
  humanReviewRequired: true,
  rawSamplesIncluded: false,
  reasonCodes: [],
};
