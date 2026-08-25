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
  getSignalWindow = (request: Parameters<AutomationRepository["getSignalWindow"]>[0]) =>
    this.bridge.getSignalWindow(request);
  getMetrics = (sessionId: string) => this.bridge.getMetrics(sessionId);
  getEvidence = (sessionId: string) => this.bridge.getEvidence(sessionId);
  listReviewCases = () => this.bridge.listReviewCases();
  getAuditTrail = (sessionId: string) => this.bridge.getAuditTrail(sessionId);
}
