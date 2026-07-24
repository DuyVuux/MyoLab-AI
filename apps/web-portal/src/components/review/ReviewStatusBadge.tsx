import type { ReviewState } from "../../schemas/review-report.schema";

export interface ReviewStatusBadgeProps {
  state: ReviewState;
}

const LABELS: Record<ReviewState, string> = {
  pending_technical_review: "Chờ review kỹ thuật",
  pending_clinical_review: "Chờ review lâm sàng",
  approved: "Đã phê duyệt",
  rejected: "Đã từ chối",
  remeasure_requested: "Yêu cầu đo lại",
  superseded: "Đã được thay thế",
};

export function ReviewStatusBadge({
  state,
}: ReviewStatusBadgeProps): JSX.Element {
  return (
    <span
      data-review-state={state}
      aria-label={`Trạng thái review: ${LABELS[state]}`}
    >
      {LABELS[state]}
    </span>
  );
}
