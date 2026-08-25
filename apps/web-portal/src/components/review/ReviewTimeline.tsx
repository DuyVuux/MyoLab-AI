import type { ReviewEventContract } from "../../schemas/review-report.schema";

export interface ReviewTimelineProps {
  events: ReviewEventContract[];
}

export function ReviewTimeline({
  events,
}: ReviewTimelineProps): JSX.Element {
  return (
    <ol aria-label="Lịch sử review">
      {events.map((event) => (
        <li key={event.eventId}>
          <strong>
            {event.reviewType === "technical"
              ? "Review kỹ thuật"
              : "Human review phạm vi nghiên cứu"}
          </strong>
          <div>
            {event.action} · {event.reviewerRole}
          </div>
          <div>
            {event.reasonCodes.join(", ") || "Không có reason code"}
          </div>
          <time dateTime={event.createdAt}>{event.createdAt}</time>
        </li>
      ))}
    </ol>
  );
}
