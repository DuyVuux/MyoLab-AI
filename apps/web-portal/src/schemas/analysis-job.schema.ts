import type { UseCaseId } from "./analysis-envelope.schema";

export type AnalysisJobStatus =
  | "queued" | "running" | "completed" | "completed_with_warnings"
  | "abstained" | "failed" | "cancelled";

export type AnalysisStage =
  | "validating_input" | "running_quality_gate" | "preprocessing" | "windowing"
  | "extracting_time_features" | "estimating_spectrum"
  | "extracting_frequency_features" | "computing_trends" | "building_evidence"
  | "running_rule_engine" | "building_explanation";

export interface AnalysisStageEvent {
  readonly stage: AnalysisStage;
  readonly state: "started" | "completed" | "skipped" | "failed";
  readonly occurredAt: string;
  readonly durationMs: number | null;
}

export interface AnalysisJob {
  readonly schemaVersion: "analysis-job.v0.1";
  readonly analysisId: string;
  readonly sessionId: string;
  readonly useCaseId: UseCaseId;
  readonly sourceHashSha256: string;
  readonly status: AnalysisJobStatus;
  readonly progressMode: "stage_only";
  readonly currentStage: AnalysisStage | null;
  readonly completedStages: readonly AnalysisStage[];
  readonly stageHistory: readonly AnalysisStageEvent[];
  readonly warningCodes: readonly string[];
  readonly reasonCodes: readonly string[];
  readonly resultLinks: {
    readonly self: string;
    readonly summary: string | null;
    readonly manifest: string | null;
  };
  readonly error: null | {
    readonly code: string;
    readonly messageVi: string;
    readonly retryable: boolean;
    readonly traceId: string;
  };
  readonly safety: {
    readonly scoreIsProbability: false;
    readonly clinicalUseAllowed: false;
    readonly humanReviewRequired: true;
    readonly rawSamplesIncluded: false;
  };
  readonly createdAt: string;
  readonly updatedAt: string;
}

export const TERMINAL_ANALYSIS_STATUSES: readonly AnalysisJobStatus[] = [
  "completed", "completed_with_warnings", "abstained", "failed", "cancelled",
];

export function isTerminalAnalysisStatus(status: AnalysisJobStatus): boolean {
  return TERMINAL_ANALYSIS_STATUSES.includes(status);
}
