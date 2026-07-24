from __future__ import annotations

from copy import deepcopy

from schemas.day24_review_report_schema import ReviewCase, ReviewEvent


class InvalidReviewTransition(ValueError):
    pass


class SourceResultChanged(ValueError):
    pass


_TRANSITIONS: dict[tuple[str, str, str], str] = {
    ("pending_technical_review", "technical", "approve"): "pending_clinical_review",
    ("pending_technical_review", "technical", "request_remeasurement"): "remeasure_requested",
    ("pending_technical_review", "technical", "request_more_information"): "pending_technical_review",
    ("pending_clinical_review", "clinical", "approve"): "approved",
    ("pending_clinical_review", "clinical", "reject"): "rejected",
    ("pending_clinical_review", "clinical", "request_remeasurement"): "remeasure_requested",
    ("pending_clinical_review", "clinical", "request_more_information"): "pending_clinical_review",
    ("approved", "clinical", "supersede"): "superseded",
}


def apply_review_event(case: ReviewCase, event: ReviewEvent) -> ReviewCase:
    """Trả aggregate mới; không mutate case cũ."""
    if event.sourceResultHash != case.originalResultHash:
        raise SourceResultChanged("SOURCE_RESULT_HASH_MISMATCH")

    next_state = _TRANSITIONS.get((case.state, event.reviewType, event.action))
    if next_state is None:
        raise InvalidReviewTransition(
            f"INVALID_REVIEW_TRANSITION:{case.state}:{event.reviewType}:{event.action}"
        )

    required_responses = list(event.checklistResponses.values())
    if event.action == "approve" and required_responses and not all(required_responses):
        raise InvalidReviewTransition("REQUIRED_CHECKLIST_ITEM_NOT_CONFIRMED")

    return case.model_copy(
        update={
            "state": next_state,
            "events": [*deepcopy(case.events), event],
        }
    )


def can_finalize_report(case: ReviewCase) -> bool:
    return case.state == "approved" and any(
        event.reviewType == "clinical"
        and event.action == "approve"
        and event.reviewerRole == "physician"
        for event in case.events
    )
