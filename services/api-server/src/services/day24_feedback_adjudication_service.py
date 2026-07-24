from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from schemas.day24_review_report_schema import FeedbackAdjudicationRequest


@dataclass(frozen=True)
class AdjudicationOutcome:
    destination: str
    trainingCandidateEligible: bool
    reasonCodes: tuple[str, ...]
    autoRetraining: bool = False
    autoDeployment: bool = False


def _has_exact_segment(correction: Mapping[str, Any] | None) -> bool:
    if not correction:
        return False
    reference = correction.get("evidence_reference") or correction.get("evidenceReference")
    if not isinstance(reference, Mapping):
        return False
    start = reference.get("start_time_s", reference.get("startTimeS"))
    end = reference.get("end_time_s", reference.get("endTimeS"))
    channels = reference.get("channel_ids", reference.get("channelIds", []))
    return (
        isinstance(start, (int, float))
        and isinstance(end, (int, float))
        and end >= start
        and isinstance(channels, list)
        and bool(channels)
    )


def adjudicate_feedback(request: FeedbackAdjudicationRequest) -> AdjudicationOutcome:
    """Đánh giá eligibility; không sửa event feedback gốc và không train tự động."""
    event = request.feedbackEvent
    consent = event.get("consent") or {}
    correction = event.get("correction")
    target = event.get("target") or {}
    reasons: list[str] = []

    if request.status != "approved_for_training":
        if request.status == "approved_for_quality_improvement_only":
            destination = "quality_improvement_queue"
        elif request.status == "needs_second_review":
            destination = "second_review_queue"
        else:
            destination = "rejected_feedback_archive"
        return AdjudicationOutcome(
            destination=destination,
            trainingCandidateEligible=False,
            reasonCodes=tuple(request.reasonCodes),
        )

    if event.get("contains_direct_identifier") is not False:
        reasons.append("DIRECT_IDENTIFIER_FLAG_NOT_FALSE")
    if event.get("rating") not in {"down", "needs_review"}:
        reasons.append("TRAINING_CANDIDATE_REQUIRES_CORRECTIVE_FEEDBACK")
    if not correction:
        reasons.append("STRUCTURED_CORRECTION_REQUIRED")
    if not bool(consent.get("model_training")):
        reasons.append("MODEL_TRAINING_CONSENT_REQUIRED")
    if not target.get("source_summary_hash"):
        reasons.append("SOURCE_SUMMARY_HASH_REQUIRED")
    if not _has_exact_segment(correction):
        reasons.append("EXACT_SIGNAL_SEGMENT_REQUIRED")
    if request.adjudicatorRole not in {"physician", "ml_qa"}:
        reasons.append("ADJUDICATOR_ROLE_NOT_ALLOWED")
    if not request.independentReviewConfirmed:
        reasons.append("INDEPENDENT_REVIEW_REQUIRED")

    eligible = not reasons
    return AdjudicationOutcome(
        destination=(
            "training_candidate_manifest"
            if eligible
            else "second_review_queue"
        ),
        trainingCandidateEligible=eligible,
        reasonCodes=tuple(reasons or request.reasonCodes),
    )
