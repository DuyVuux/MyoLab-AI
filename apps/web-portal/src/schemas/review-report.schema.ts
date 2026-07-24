export type ReviewState =
  | "pending_technical_review"
  | "pending_clinical_review"
  | "approved"
  | "rejected"
  | "remeasure_requested"
  | "superseded";

export type ReviewerRole =
  | "ktv"
  | "motion_lab_technician"
  | "physician"
  | "ml_qa"
  | "admin";

export interface ReviewEventContract {
  eventId: string;
  reviewType: "technical" | "clinical";
  action:
    | "approve"
    | "reject"
    | "request_remeasurement"
    | "request_more_information"
    | "supersede";
  reviewerRole: ReviewerRole;
  reviewerIdHash: string;
  sourceResultHash: string;
  checklistVersion: string;
  checklistResponses: Record<string, boolean>;
  reasonCodes: string[];
  comment: string | null;
  createdAt: string;
  immutable: true;
}

export interface ReviewCaseContract {
  schemaVersion: "review-workflow.v0.1";
  caseId: string;
  analysisId: string;
  originalResultHash: string;
  analysisStatus: "completed" | "completed_with_warnings" | "abstained";
  state: ReviewState;
  events: ReviewEventContract[];
  safety: {
    originalResultImmutable: true;
    humanReviewRequired: true;
    rawSamplesIncluded: false;
    clinicalUseAllowed: false;
  };
}

export interface ClinicalReportPackageContract {
  schemaVersion: "clinical-report-package.v0.1";
  reportId: string;
  analysisId: string;
  status: "draft" | "final";
  watermark: string | null;
  templateVersion: string;
  source: Record<string, unknown>;
  sections: Record<string, unknown>;
  review: { caseId: string; state: ReviewState; eventCount: number };
  limitations: string[];
  safety: {
    rawSamplesIncluded: false;
    clinicalUseAllowed: false;
    humanReviewRequired: true;
    automaticTreatmentRecommendation: false;
  };
  reportHashSha256: string;
}
