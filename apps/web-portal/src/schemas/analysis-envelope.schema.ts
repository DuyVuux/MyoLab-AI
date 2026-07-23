export const analysisStatuses = [
  "queued",
  "running",
  "completed",
  "completed_with_warnings",
  "abstained",
  "failed",
] as const;

export type AnalysisStatus = (typeof analysisStatuses)[number];
export type UseCaseId = "uc1" | "uc2" | "uc3" | "uc4";
export type SourceType = "synthetic" | "deidentified" | "local_export_mock";
export type QualityStatus = "pass" | "warning" | "fail";

export interface SignalQualitySummary {
  readonly status: QualityStatus;
  readonly usableWindowRatio: number | null;
  readonly reasonCodes: readonly string[];
  readonly analysisAllowed: boolean;
}

export interface AnalysisSource {
  readonly type: SourceType;
  readonly sourceHashSha256: string;
  readonly rawSamplesIncluded: false;
}

export interface AnalysisProvenance {
  readonly protocolVersion: string;
  readonly preprocessingVersion: string;
  readonly featureVersion: string;
  readonly modelOrRuleVersion: string;
  readonly summaryHashSha256: string;
}

export interface EngineeringConfidence {
  readonly category:
    | "engineering_high"
    | "engineering_moderate"
    | "engineering_low"
    | "engineering_very_low"
    | "not_available";
  readonly score: number | null;
  readonly scoreIsProbability: false;
  readonly clinicalCalibrationStatus: "not_calibrated";
}

export interface AnalysisEnvelope<TPayload> {
  readonly analysisId: string;
  readonly sessionId: string;
  readonly useCaseId: UseCaseId;
  readonly status: AnalysisStatus;
  readonly source: AnalysisSource;
  readonly quality: SignalQualitySummary;
  readonly confidence: EngineeringConfidence;
  readonly provenance: AnalysisProvenance;
  readonly humanReviewRequired: true;
  readonly clinicalUseAllowed: false;
  readonly payload: TPayload;
}
