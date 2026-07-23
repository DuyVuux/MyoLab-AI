export type TechnicalReviewState = 'pending' | 'in_progress' | 'flagged' | 'technical_approved';
export type ClinicalReviewState = 'pending' | 'needs_revision' | 'abstained' | 'clinical_approved';

export type OverridePolicyCode = 
  | 'OVR_ARTIFACT' 
  | 'OVR_FATIGUE_MASK' 
  | 'OVR_CROSSTALK' 
  | 'OVR_CLINICAL_CORRELATION' 
  | 'OVR_OTHER';

export interface TechnicalReview {
  id: string;
  sessionId: string;
  reviewerId: string;
  state: TechnicalReviewState;
  flaggedSegmentIds: string[];
  notes: string;
  reviewedAt: string;
}

export interface ClinicalReview {
  id: string;
  sessionId: string;
  reviewerId: string;
  state: ClinicalReviewState;
  
  // Guardrails
  structuredOverride?: {
    code: OverridePolicyCode;
    detail: string;
  };
  
  // Explicitly separate from AI Technical Conclusion
  clinicalConclusion: string; 
  
  signOffAt?: string;
  signOffHash?: string;
}
