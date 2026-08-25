import type {
  AuditEvent,
  CreateImportRequest,
  ImportJob,
  MappingResolutionReceipt,
  MappingResolutionRequest,
  MetricEvidence,
  PageResult,
  PipelineJob,
  ProcessingManifestEvidence,
  QualityAssessment,
  ReviewActionReceipt,
  ReviewActionRequest,
  ReviewCase,
  ReviewCaseDetail,
  SessionDetail,
  SessionEvidenceDetail,
  SessionEvidenceBundle,
  SessionMappingState,
  SessionPreflight,
  SessionSummary,
  SignalIndex,
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

  getSignalIndex(sessionId: string): Promise<SignalIndex>;
  getSignalWindow(request: SignalWindowRequest): Promise<SignalWindow>;
  getProcessingManifest(manifestId: string): Promise<ProcessingManifestEvidence>;
  getMetrics(sessionId: string): Promise<MetricEvidence[]>;
  getEvidence(sessionId: string): Promise<SessionEvidenceBundle>;
  getSessionEvidenceDetail(sessionId: string): Promise<SessionEvidenceDetail>;
  listReviewCases(): Promise<ReviewCase[]>;
  listReviewCaseDetails(sessionId?: string): Promise<ReviewCaseDetail[]>;
  getReviewCase(caseId: string): Promise<ReviewCaseDetail>;
  submitReviewAction(caseId: string, request: ReviewActionRequest): Promise<ReviewActionReceipt>;
  getAuditTrail(sessionId: string): Promise<AuditEvent[]>;
}
