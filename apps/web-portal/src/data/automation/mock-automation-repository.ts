import type { AutomationRepository } from "./automation-repository";

/**
 * UI-I1 intentionally does not rewrite the existing MockWorkflowRepository.
 * The bridge allows existing UC/session demo mocks to be adapted in UI-I2 without
 * coupling the new core automation contracts to legacy fatigue/use-case internals.
 */
export interface LegacyMockAutomationBridge extends AutomationRepository {}

export class MockAutomationRepository implements AutomationRepository {
  constructor(private readonly bridge: LegacyMockAutomationBridge) {}
  listSessions = () => this.bridge.listSessions();
  getSession = (sessionId: string) => this.bridge.getSession(sessionId);
  createImport = (request: Parameters<AutomationRepository["createImport"]>[0]) => this.bridge.createImport(request);
  getPipelineJob = (jobId: string) => this.bridge.getPipelineJob(jobId);
  getQuality = (sessionId: string) => this.bridge.getQuality(sessionId);
  getSignalWindow = (request: Parameters<AutomationRepository["getSignalWindow"]>[0]) => this.bridge.getSignalWindow(request);
  getMetrics = (sessionId: string) => this.bridge.getMetrics(sessionId);
  getEvidence = (sessionId: string) => this.bridge.getEvidence(sessionId);
  listReviewCases = () => this.bridge.listReviewCases();
  getAuditTrail = (sessionId: string) => this.bridge.getAuditTrail(sessionId);
}
