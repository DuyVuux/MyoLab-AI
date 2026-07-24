import type { ReviewCaseContract } from "../../schemas/review-report.schema";
import { ReviewStatusBadge } from "./ReviewStatusBadge";

export interface TechnicalReviewPanelProps {
  reviewCase: ReviewCaseContract;
  onApprove: () => void;
  onRemeasure: () => void;
}

export function TechnicalReviewPanel({
  reviewCase,
  onApprove,
  onRemeasure,
}: TechnicalReviewPanelProps): JSX.Element {
  const enabled = reviewCase.state === "pending_technical_review";
  return (
    <section aria-labelledby="technical-review-title">
      <h2 id="technical-review-title">Review kỹ thuật</h2>
      <ReviewStatusBadge state={reviewCase.state} />
      <p>
        Original result hash: <code>{reviewCase.originalResultHash}</code>
      </p>
      <p>AI output gốc không bị thay đổi bởi thao tác review.</p>
      <button type="button" disabled={!enabled} onClick={onApprove}>
        Xác nhận review kỹ thuật
      </button>
      <button type="button" disabled={!enabled} onClick={onRemeasure}>
        Yêu cầu đo lại
      </button>
    </section>
  );
}
