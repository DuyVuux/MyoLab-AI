from datetime import datetime, timezone

from schemas.day24_review_report_schema import FeedbackAdjudicationRequest
from services.day24_feedback_adjudication_service import adjudicate_feedback


def event(*, consent=True, segment=True):
    correction = {
        "correction_type": "gesture_label",
        "original_value": "wrist_flexion",
        "corrected_value": "wrist_extension",
        "correction_scope": "segment",
        "evidence_reference": (
            {
                "start_time_s": 12.5,
                "end_time_s": 13.5,
                "channel_ids": ["CH01", "CH02"],
            }
            if segment
            else None
        ),
    }
    return {
        "schema_version": "ai-feedback-event.v0.1",
        "feedback_id": "FB-DAY24-0001",
        "rating": "down",
        "target": {"source_summary_hash": "a" * 64},
        "correction": correction,
        "consent": {"quality_improvement": True, "model_training": consent},
        "contains_direct_identifier": False,
    }


def request(feedback_event, status="approved_for_training"):
    return FeedbackAdjudicationRequest(
        feedbackId="FB-DAY24-0001",
        feedbackEvent=feedback_event,
        status=status,
        adjudicatorRole="ml_qa",
        adjudicatorIdHash="b" * 64,
        independentReviewConfirmed=True,
        reasonCodes=[],
        createdAt=datetime.now(timezone.utc),
    )


def test_eligible_structured_correction():
    outcome = adjudicate_feedback(request(event()))
    assert outcome.trainingCandidateEligible is True
    assert outcome.destination == "training_candidate_manifest"
    assert outcome.autoRetraining is False
    assert outcome.autoDeployment is False


def test_missing_training_consent_not_eligible():
    outcome = adjudicate_feedback(request(event(consent=False)))
    assert outcome.trainingCandidateEligible is False
    assert "MODEL_TRAINING_CONSENT_REQUIRED" in outcome.reasonCodes


def test_missing_segment_not_eligible():
    outcome = adjudicate_feedback(request(event(segment=False)))
    assert outcome.trainingCandidateEligible is False
    assert "EXACT_SIGNAL_SEGMENT_REQUIRED" in outcome.reasonCodes


def test_quality_improvement_never_training():
    outcome = adjudicate_feedback(
        request(event(), status="approved_for_quality_improvement_only")
    )
    assert outcome.trainingCandidateEligible is False
    assert outcome.destination == "quality_improvement_queue"
