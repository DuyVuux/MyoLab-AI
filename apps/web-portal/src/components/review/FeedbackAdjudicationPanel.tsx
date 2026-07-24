export interface FeedbackAdjudicationPanelProps {
  feedbackId: string;
  status:
    | "pending"
    | "approved_for_training"
    | "quality_improvement_only"
    | "rejected"
    | "needs_second_review";
}

export function FeedbackAdjudicationPanel({
  feedbackId,
  status,
}: FeedbackAdjudicationPanelProps): JSX.Element {
  return (
    <section aria-labelledby="feedback-adjudication-title">
      <h2 id="feedback-adjudication-title">Adjudication phản hồi</h2>
      <p>
        Mã phản hồi: <code>{feedbackId}</code>
      </p>
      <p>Trạng thái: {status}</p>
      <p>Phản hồi không tự động huấn luyện hoặc triển khai model.</p>
    </section>
  );
}
