import type { SignalQualitySummary } from "./analysis-envelope.schema";
import type { UserRole } from "./role.schema";

export interface DetailedQualityResult {
  readonly schemaVersion: "detailed-quality-result.v0.1";
  readonly qualityResultId: string;
  readonly sessionId: string;
  readonly status: "pass" | "warning" | "fail";
  readonly usableWindowRatio: number;
  readonly badChannels: readonly string[];
  readonly artifactFlags: readonly string[];
  readonly reasonCodes: readonly string[];
  readonly mfcvEligibility: "eligible" | "not_eligible" | "not_assessed";
  readonly recommendedActionsVi: readonly string[];
  readonly warningAcknowledgedBy?: string;
  readonly warningAcknowledgementReason?: string;
  readonly qcVersion: string;
}

export const canProceedFromQuality = (
  result: DetailedQualityResult,
  role: UserRole,
): boolean => {
  if (result.status === "fail") return false;
  if (result.status === "pass") return true;
  return (
    ["ktv", "physician"].includes(role) &&
    Boolean(result.warningAcknowledgedBy && result.warningAcknowledgementReason)
  );
};

export const toAnalysisQualitySummary = (
  result: DetailedQualityResult,
  role: UserRole,
): SignalQualitySummary => ({
  status: result.status,
  usableWindowRatio: result.usableWindowRatio,
  reasonCodes: result.reasonCodes,
  analysisAllowed: canProceedFromQuality(result, role),
});
