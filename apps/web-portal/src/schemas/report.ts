export type ReportState = 'draft' | 'pending_signoff' | 'approved' | 'finalized' | 'superseded';

export interface ReportDocument {
  id: string;
  sessionId: string;
  state: ReportState;
  
  // Versions
  templateVersion: string;
  reportVersion: number;
  
  // Separation of concerns
  aiTechnicalSummary: string; // Immutable, from AnalysisOutput
  clinicianApprovedConclusion: string; // From ClinicalReview
  
  // Provenance & Signatures
  reviewerId?: string;
  reviewerName?: string;
  watermark: string; // e.g. "DRAFT - NOT FOR CLINICAL USE" or "FINALIZED"
  
  reportHash?: string; // Hash of the final document content
  resultHash?: string; // Hash of the clinical results included
  
  createdAt: string;
  updatedAt: string;
  finalizedAt?: string;
}
