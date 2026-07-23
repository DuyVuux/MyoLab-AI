import type { UseCaseId } from "./analysis-envelope.schema";

export interface AnalysisHandoff {
  readonly schemaVersion: "analysis-handoff.v0.1";
  readonly analysisId: string;
  readonly sessionId: string;
  readonly useCaseId: UseCaseId;
  readonly status: "queued" | "queued_with_warnings" | "abstained";
  readonly nextRoute: string | null;
  readonly protocolVersion: string;
  readonly calibrationId: string | null;
  readonly qualityResultId: string;
  readonly sourceHashSha256: string;
  readonly scoreIsProbability: false;
  readonly clinicalUseAllowed: false;
  readonly humanReviewRequired: true;
  readonly rawSamplesIncluded: false;
  readonly reasonCodes: readonly string[];
}
