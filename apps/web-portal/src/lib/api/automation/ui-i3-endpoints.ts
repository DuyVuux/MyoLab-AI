export type Verification="VERIFIED"|"CANDIDATE"|"UNAVAILABLE";
export interface EvidenceEndpoint{template:string|null;method?:"GET"|"POST";verification:Verification;evidence?:string}
export interface EvidenceEndpointCatalog{
  signal_index:EvidenceEndpoint;signal_window:EvidenceEndpoint;processing_manifest:EvidenceEndpoint;session_evidence:EvidenceEndpoint;
  review_cases:EvidenceEndpoint;review_case:EvidenceEndpoint;review_action:EvidenceEndpoint;session_audit:EvidenceEndpoint;
}
export const SOURCE_CANDIDATE_EVIDENCE_ENDPOINTS:EvidenceEndpointCatalog={
 signal_index:{template:"/v1/sessions/{sessionId}/signals",method:"GET",verification:"CANDIDATE"},
 signal_window:{template:"/v1/sessions/{sessionId}/signals/{channelId}/window",method:"GET",verification:"CANDIDATE"},
 processing_manifest:{template:"/v1/processing-manifests/{manifestId}",method:"GET",verification:"CANDIDATE"},
 session_evidence:{template:"/v1/sessions/{sessionId}/evidence",method:"GET",verification:"CANDIDATE"},
 review_cases:{template:"/v1/review-cases",method:"GET",verification:"CANDIDATE"},
 review_case:{template:"/v1/review-cases/{caseId}",method:"GET",verification:"CANDIDATE"},
 review_action:{template:"/v1/review-cases/{caseId}/actions",method:"POST",verification:"CANDIDATE"},
 session_audit:{template:"/v1/sessions/{sessionId}/audit",method:"GET",verification:"CANDIDATE"}
};
