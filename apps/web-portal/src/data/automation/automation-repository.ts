import type {
  AuditEvent,
  CreateImportRequest,
  ImportJob,
  MetricEvidence,
  PageResult,
  PipelineJob,
  QualityAssessment,
  ReviewCase,
  SessionDetail,
  SessionEvidenceBundle,
  SessionSummary,
  SignalWindow,
  SignalWindowRequest,
} from "../../contracts/automation";

export interface AutomationRepository {
  listSessions(): Promise<PageResult<SessionSummary>>;
  getSession(sessionId: string): Promise<SessionDetail>;
  createImport(request: CreateImportRequest): Promise<ImportJob>;
  getPipelineJob(jobId: string): Promise<PipelineJob>;
  getQuality(sessionId: string): Promise<QualityAssessment>;
  getSignalWindow(request: SignalWindowRequest): Promise<SignalWindow>;
  getMetrics(sessionId: string): Promise<MetricEvidence[]>;
  getEvidence(sessionId: string): Promise<SessionEvidenceBundle>;
  listReviewCases(): Promise<ReviewCase[]>;
  getAuditTrail(sessionId: string): Promise<AuditEvent[]>;
}
