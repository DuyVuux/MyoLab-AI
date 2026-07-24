import type {
  ReviewCaseContract,
  ReviewerRole,
} from "../../schemas/review-report.schema";
import { ClinicalSignoffPanel } from "../../components/review/ClinicalSignoffPanel";
import { FeedbackAdjudicationPanel } from "../../components/review/FeedbackAdjudicationPanel";
import { ReviewTimeline } from "../../components/review/ReviewTimeline";
import { TechnicalReviewPanel } from "../../components/review/TechnicalReviewPanel";

export interface Day24ReviewPageProps {
  reviewCase: ReviewCaseContract;
  currentRole: ReviewerRole;
  onTechnicalApprove?: () => void;
  onTechnicalRemeasure?: () => void;
  onClinicalApprove?: () => void;
  onClinicalReject?: () => void;
}

export function Day24ReviewPage({
  reviewCase,
  currentRole,
  onTechnicalApprove = () => undefined,
  onTechnicalRemeasure = () => undefined,
  onClinicalApprove = () => undefined,
  onClinicalReject = () => undefined,
}: Day24ReviewPageProps): JSX.Element {
  return (
    <main>
      <h1>Human Review</h1>
      <TechnicalReviewPanel
        reviewCase={reviewCase}
        onApprove={onTechnicalApprove}
        onRemeasure={onTechnicalRemeasure}
      />
      <ClinicalSignoffPanel
        reviewCase={reviewCase}
        currentRole={currentRole}
        onApprove={onClinicalApprove}
        onReject={onClinicalReject}
      />
      <ReviewTimeline events={reviewCase.events} />
      <FeedbackAdjudicationPanel
        feedbackId={`FB-${reviewCase.caseId}`}
        status="pending"
      />
    </main>
  );
}
