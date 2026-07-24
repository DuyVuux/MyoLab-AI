from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from schemas.day24_review_report_schema import ReviewCase, ReviewEvent
from services.day24_review_workflow_service import (
    InvalidReviewTransition,
    SourceResultChanged,
    apply_review_event,
    can_finalize_report,
)

HASH = "a" * 64
RID = "b" * 64


def event(
    review_type="technical",
    action="approve",
    role="ktv",
    source_hash=HASH,
    reason_codes=None,
):
    return ReviewEvent(
        eventId="REVT-12345678",
        reviewType=review_type,
        action=action,
        reviewerRole=role,
        reviewerIdHash=RID,
        sourceResultHash=source_hash,
        checklistVersion="checklist.v0.1",
        checklistResponses={"required": True},
        reasonCodes=reason_codes or [],
        createdAt=datetime.now(timezone.utc),
    )


def test_happy_path_to_approval():
    case = ReviewCase(
        caseId="REV-12345678",
        analysisId="AN-1",
        originalResultHash=HASH,
        analysisStatus="completed",
    )
    case = apply_review_event(case, event())
    assert case.state == "pending_clinical_review"
    case = apply_review_event(case, event("clinical", "approve", "physician"))
    assert case.state == "approved"
    assert can_finalize_report(case)


def test_ktv_cannot_clinical_signoff():
    with pytest.raises(ValidationError):
        event("clinical", "approve", "ktv")


def test_invalid_transition_blocked():
    case = ReviewCase(
        caseId="REV-12345678",
        analysisId="AN-1",
        originalResultHash=HASH,
        analysisStatus="completed",
    )
    with pytest.raises(InvalidReviewTransition):
        apply_review_event(case, event("clinical", "approve", "physician"))


def test_source_hash_mismatch_blocked():
    case = ReviewCase(
        caseId="REV-12345678",
        analysisId="AN-1",
        originalResultHash=HASH,
        analysisStatus="completed",
    )
    with pytest.raises(SourceResultChanged):
        apply_review_event(case, event(source_hash="c" * 64))
