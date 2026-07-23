import type {
  AnalysisQueueItem,
  FeedbackQueueItem,
  SessionListItem,
} from "../schemas/work-queue.schema";

export const mockSessions: readonly SessionListItem[] = [
  {
    sessionId: "SESSION-DEMO-001",
    subjectRef: "SUBJECT-DEMO-A",
    useCaseId: "uc1",
    sourceType: "synthetic",
    workflowStatus: "analysis_ready",
    updatedAt: "2026-07-23T08:30:00Z",
  },
  {
    sessionId: "SESSION-DEMO-002",
    subjectRef: "SUBJECT-DEMO-B",
    useCaseId: "uc2",
    sourceType: "deidentified",
    workflowStatus: "review_pending",
    updatedAt: "2026-07-23T08:10:00Z",
  },
  {
    sessionId: "SESSION-DEMO-003",
    subjectRef: "SUBJECT-DEMO-C",
    useCaseId: "uc2",
    sourceType: "local_export_mock",
    workflowStatus: "mapping_required",
    updatedAt: "2026-07-23T07:55:00Z",
  },
] as const;

export const mockAnalyses: readonly AnalysisQueueItem[] = [
  {
    analysisId: "ANALYSIS-DEMO-PASS",
    sessionId: "SESSION-DEMO-001",
    useCaseId: "uc1",
    status: "completed",
    reviewStatus: "pending",
    updatedAt: "2026-07-23T08:35:00Z",
  },
  {
    analysisId: "ANALYSIS-DEMO-WARNING",
    sessionId: "SESSION-DEMO-002",
    useCaseId: "uc2",
    status: "completed_with_warnings",
    reviewStatus: "pending",
    updatedAt: "2026-07-23T08:20:00Z",
  },
  {
    analysisId: "ANALYSIS-DEMO-ABSTAIN",
    sessionId: "SESSION-DEMO-004",
    useCaseId: "uc1",
    status: "abstained",
    reviewStatus: "not_applicable",
    updatedAt: "2026-07-23T07:40:00Z",
  },
  {
    analysisId: "ANALYSIS-DEMO-FAILED",
    sessionId: "SESSION-DEMO-005",
    useCaseId: "uc2",
    status: "failed",
    reviewStatus: "not_applicable",
    updatedAt: "2026-07-23T07:20:00Z",
  },
] as const;

export const mockFeedbackInbox: readonly FeedbackQueueItem[] = [
  {
    feedbackId: "FB-DEMO-CORRECT-001",
    analysisId: "ANALYSIS-DEMO-WARNING",
    useCaseId: "uc2",
    feedbackType: "correct",
    reviewStatus: "pending_adjudication",
    reviewerRole: "ktv",
    createdAt: "2026-07-23T08:25:00Z",
  },
  {
    feedbackId: "FB-DEMO-UNCERTAIN-001",
    analysisId: "ANALYSIS-DEMO-PASS",
    useCaseId: "uc1",
    feedbackType: "uncertain",
    reviewStatus: "pending_adjudication",
    reviewerRole: "physician",
    createdAt: "2026-07-23T08:15:00Z",
  },
] as const;
