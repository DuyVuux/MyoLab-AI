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
      <h2 id="clinical-signoff-title">Ký duyệt lâm sàng</h2>
      {!isPhysician && (
        <p role="alert">Chỉ bác sĩ được thực hiện clinical sign-off.</p>
      )}
      <button type="button" disabled={!enabled} onClick={onApprove}>
        Phê duyệt
      </button>
      <button type="button" disabled={!enabled} onClick={onReject}>
        Từ chối và ghi lý do
      </button>
    </section>
  );
}
