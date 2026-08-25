import type {
  AuditEvent, ProcessingManifestEvidence, ReviewActionReceipt, ReviewActionRequest,
  ReviewCaseDetail, SessionEvidenceDetail, SignalIndex, SignalWindow, SignalWindowRequest
} from "../../contracts/automation";

export interface AutomationEvidenceRepository {
  getSignalIndex(sessionId:string):Promise<SignalIndex>;
  getSignalWindow(request:SignalWindowRequest):Promise<SignalWindow>;
  getProcessingManifest(manifestId:string):Promise<ProcessingManifestEvidence>;
  getSessionEvidence(sessionId:string):Promise<SessionEvidenceDetail>;
  listReviewCases(sessionId?:string):Promise<ReviewCaseDetail[]>;
  getReviewCase(caseId:string):Promise<ReviewCaseDetail>;
  submitReviewAction(caseId:string,request:ReviewActionRequest):Promise<ReviewActionReceipt>;
  getAuditTrail(sessionId:string):Promise<AuditEvent[]>;
}
