import type {
  AuditEvent,
  CreateImportRequest,
  ImportJob,
  MappingResolutionReceipt,
  MappingResolutionRequest,
  MetricEvidence,
  PageResult,
  PipelineJob,
  QualityAssessment,
  ReviewCase,
  SessionDetail,
  SessionEvidenceBundle,
  SessionMappingState,
  SessionPreflight,
  SessionSummary,
  SignalWindow,
  SignalWindowRequest,
  UploadImportRequest,
} from "../../contracts/automation";

export interface AutomationRepository {
  listSessions(): Promise<PageResult<SessionSummary>>;
  getSession(sessionId: string): Promise<SessionDetail>;

  createImport(request: CreateImportRequest): Promise<ImportJob>;
  uploadImport(request: UploadImportRequest): Promise<ImportJob>;
  getPipelineJob(jobId: string): Promise<PipelineJob>;

  getPreflight(sessionId: string): Promise<SessionPreflight>;
  getMapping(sessionId: string): Promise<SessionMappingState>;
  resolveMapping(
    sessionId: string,
    request: MappingResolutionRequest,
  ): Promise<MappingResolutionReceipt>;

  getQuality(sessionId: string): Promise<QualityAssessment>;

  getSignalWindow(request: SignalWindowRequest): Promise<SignalWindow>;
  getMetrics(sessionId: string): Promise<MetricEvidence[]>;
  getEvidence(sessionId: string): Promise<SessionEvidenceBundle>;
  listReviewCases(): Promise<ReviewCase[]>;
  getAuditTrail(sessionId: string): Promise<AuditEvent[]>;
}
