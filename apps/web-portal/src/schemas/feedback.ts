export type ReviewerCertainty = 'high' | 'moderate' | 'low' | 'uncertain';
export type AdjudicationStatus = 'pending' | 'accepted' | 'rejected' | 'needs_info';

export interface FeedbackEvent {
  id: string; // e.g. FB-001
  analysisId: string;
  sessionId: string;
  segmentId: string; // Exact segment provenance
  
  // Provenance
  sourceHash: string;
  originalResultHash: string;
  modelVersion: string;
  
  // Correction
  originalPrediction: string;
  correctedPrediction: string;
  reviewerCertainty: ReviewerCertainty;
  
  // Privacy & Consent
  hasPatientConsent: boolean;
  
  // Status
  reviewStatus: AdjudicationStatus;
  createdAt: string;
  createdBy: string;
}

export interface MLAdjudication {
  feedbackId: string;
  mlQaId: string;
  status: AdjudicationStatus;
  
  // Only create candidate if accepted + consent + privacy check passed
  isTrainingCandidate: boolean;
  reasoning: string;
  adjudicatedAt: string;
}
