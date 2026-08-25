import type { AutomationRepository } from "./automation-repository";

export interface LegacyMockAutomationBridge extends AutomationRepository {}

export class MockAutomationRepository implements AutomationRepository {
  constructor(private readonly bridge: LegacyMockAutomationBridge) {}
  listSessions = () => this.bridge.listSessions();
  getSession = (sessionId: string) => this.bridge.getSession(sessionId);
  createImport = (request: Parameters<AutomationRepository["createImport"]>[0]) =>
    this.bridge.createImport(request);
  uploadImport = (request: Parameters<AutomationRepository["uploadImport"]>[0]) =>
    this.bridge.uploadImport(request);
  getPipelineJob = (jobId: string) => this.bridge.getPipelineJob(jobId);
  getPreflight = (sessionId: string) => this.bridge.getPreflight(sessionId);
  getMapping = (sessionId: string) => this.bridge.getMapping(sessionId);
  resolveMapping = (
    sessionId: string,
    request: Parameters<AutomationRepository["resolveMapping"]>[1],
  ) => this.bridge.resolveMapping(sessionId, request);
  getQuality = (sessionId: string) => this.bridge.getQuality(sessionId);
  getSignalIndex = (sessionId: string) => this.bridge.getSignalIndex(sessionId);
  getSignalWindow = (request: Parameters<AutomationRepository["getSignalWindow"]>[0]) =>
    this.bridge.getSignalWindow(request);
  getProcessingManifest = (manifestId: string) => this.bridge.getProcessingManifest(manifestId);
  getMetrics = (sessionId: string) => this.bridge.getMetrics(sessionId);
  getEvidence = (sessionId: string) => this.bridge.getEvidence(sessionId);
  getSessionEvidenceDetail = (sessionId: string) => this.bridge.getSessionEvidenceDetail(sessionId);
  listReviewCases = () => this.bridge.listReviewCases();
  listReviewCaseDetails = (sessionId?: string) => this.bridge.listReviewCaseDetails(sessionId);
  getReviewCase = (caseId: string) => this.bridge.getReviewCase(caseId);
  submitReviewAction = (
    caseId: string,
    request: Parameters<AutomationRepository["submitReviewAction"]>[1],
  ) => this.bridge.submitReviewAction(caseId, request);
  getAuditTrail = (sessionId: string) => this.bridge.getAuditTrail(sessionId);
}
