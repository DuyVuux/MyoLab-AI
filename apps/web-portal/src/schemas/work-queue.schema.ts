import type { AnalysisStatus, SourceType, UseCaseId } from "./analysis-envelope.schema";

export type SessionWorkflowStatus =
  | "draft"
  | "mapping_required"
  | "qc_ready"
  | "analysis_ready"
  | "review_pending"
  | "completed";

export interface SessionListItem {
  readonly sessionId: string;
  readonly subjectRef: string;
  readonly useCaseId: UseCaseId;
  readonly sourceType: SourceType;
  readonly workflowStatus: SessionWorkflowStatus;
  readonly updatedAt: string;
}

export interface AnalysisQueueItem {
  readonly analysisId: string;
  readonly sessionId: string;
  readonly useCaseId: UseCaseId;
  readonly status: AnalysisStatus;
  readonly reviewStatus: "pending" | "reviewed" | "not_applicable";
  readonly updatedAt: string;
}

export interface FeedbackQueueItem {
  readonly feedbackId: string;
  readonly analysisId: string;
  readonly useCaseId: UseCaseId;
  readonly feedbackType: "accept" | "correct" | "uncertain" | "remeasure";
  readonly reviewStatus: "pending_adjudication" | "reviewed";
  readonly reviewerRole: "ktv" | "physician" | "researcher" | "ml_qa";
  readonly createdAt: string;
}
