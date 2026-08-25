import type {
  ReviewCaseContract,
  ReviewerRole,
} from "../../schemas/review-report.schema";

export interface ClinicalSignoffPanelProps {
  reviewCase: ReviewCaseContract;
  currentRole: ReviewerRole;
  onApprove: () => void;
  onReject: () => void;
}

export function ClinicalSignoffPanel({
  reviewCase,
  currentRole,
  onApprove,
  onReject,
}: ClinicalSignoffPanelProps): JSX.Element {
  const isPhysician = currentRole === "physician";
  const enabled =
    isPhysician && reviewCase.state === "pending_clinical_review";
  return (
    <section aria-labelledby="clinical-signoff-title">
      <h2 id="clinical-signoff-title">Human review xác nhận phạm vi nghiên cứu</h2>
      {!isPhysician && (
        <p role="alert">Chỉ reviewer có vai trò bác sĩ được xác nhận phần human review này.</p>
      )}
      <button type="button" disabled={!enabled} onClick={onApprove}>
        Xác nhận đã review
      </button>
      <button type="button" disabled={!enabled} onClick={onReject}>
        Từ chối và ghi lý do
      </button>
    </section>
  );
}
