from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


ReviewState = Literal[
    "pending_technical_review",
    "pending_clinical_review",
    "approved",
    "rejected",
    "remeasure_requested",
    "superseded",
]
ReviewerRole = Literal["ktv", "motion_lab_technician", "physician", "ml_qa", "admin"]


class ReviewSafety(StrictModel):
    originalResultImmutable: Literal[True] = True
    humanReviewRequired: Literal[True] = True
    rawSamplesIncluded: Literal[False] = False
    clinicalUseAllowed: Literal[False] = False


class ReviewEvent(StrictModel):
    eventId: str = Field(pattern=r"^REVT-[A-Za-z0-9_-]{8,64}$")
    reviewType: Literal["technical", "clinical"]
    action: Literal[
        "approve",
        "reject",
        "request_remeasurement",
        "request_more_information",
        "supersede",
    ]
    reviewerRole: ReviewerRole
    reviewerIdHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    sourceResultHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    checklistVersion: str
    checklistResponses: dict[str, bool] = Field(default_factory=dict)
    reasonCodes: list[str] = Field(default_factory=list)
    comment: str | None = Field(default=None, max_length=1000)
    createdAt: datetime
    immutable: Literal[True] = True

    @model_validator(mode="after")
    def enforce_role(self) -> "ReviewEvent":
        if self.reviewType == "clinical" and self.reviewerRole != "physician":
            raise ValueError("CLINICAL_REVIEW_REQUIRES_PHYSICIAN")
        if self.reviewType == "technical" and self.reviewerRole not in {
            "ktv", "motion_lab_technician", "physician"
        }:
            raise ValueError("TECHNICAL_REVIEW_ROLE_NOT_ALLOWED")
        if self.action in {"reject", "request_remeasurement", "supersede"} and not self.reasonCodes:
            raise ValueError("REASON_CODE_REQUIRED")
        return self


class ReviewCase(StrictModel):
    schemaVersion: Literal["review-workflow.v0.1"] = "review-workflow.v0.1"
    caseId: str = Field(pattern=r"^REV-[A-Za-z0-9_-]{8,64}$")
    analysisId: str
    originalResultHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    analysisStatus: Literal["completed", "completed_with_warnings", "abstained"]
    state: ReviewState = "pending_technical_review"
    events: list[ReviewEvent] = Field(default_factory=list)
    safety: ReviewSafety = Field(default_factory=ReviewSafety)


class ReportSafety(StrictModel):
    rawSamplesIncluded: Literal[False] = False
    clinicalUseAllowed: Literal[False] = False
    humanReviewRequired: Literal[True] = True
    automaticTreatmentRecommendation: Literal[False] = False


class ClinicalReportPackage(StrictModel):
    schemaVersion: Literal["clinical-report-package.v0.1"] = "clinical-report-package.v0.1"
    reportId: str = Field(pattern=r"^RPT-[A-Za-z0-9_-]{8,64}$")
    analysisId: str
    status: Literal["draft", "final"]
    watermark: str | None
    templateVersion: str
    source: dict[str, Any]
    sections: dict[str, Any]
    review: dict[str, Any]
    limitations: list[str]
    safety: ReportSafety = Field(default_factory=ReportSafety)
    reportHashSha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_final_state(self) -> "ClinicalReportPackage":
        review_state = self.review.get("state")
        if self.status == "final" and review_state != "approved":
            raise ValueError("FINAL_REPORT_REQUIRES_APPROVED_REVIEW")
        if self.status == "draft" and not self.watermark:
            raise ValueError("DRAFT_REPORT_REQUIRES_WATERMARK")
        return self


class CreateReviewCaseRequest(StrictModel):
    analysisId: str
    originalResultHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    analysisStatus: Literal["completed", "completed_with_warnings", "abstained"]


class ReportBuildRequest(StrictModel):
    reviewCase: ReviewCase
    analysisSummary: dict[str, Any]
    finalize: bool = False
    templateVersion: str = "clinical-report-v0.2-review-workflow"


class FeedbackAdjudicationRequest(StrictModel):
    schemaVersion: Literal["feedback-adjudication.v0.1"] = "feedback-adjudication.v0.1"
    feedbackId: str = Field(min_length=8)
    feedbackEvent: dict[str, Any]
    status: Literal[
        "approved_for_training",
        "approved_for_quality_improvement_only",
        "needs_second_review",
        "rejected",
    ]
    adjudicatorRole: Literal["physician", "ml_qa"]
    adjudicatorIdHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    independentReviewConfirmed: bool
    reasonCodes: list[str] = Field(default_factory=list)
    comment: str | None = Field(default=None, max_length=1000)
    createdAt: datetime
    immutable: Literal[True] = True

    @model_validator(mode="after")
    def validate_adjudication(self) -> "FeedbackAdjudicationRequest":
        event_id = self.feedbackEvent.get("feedback_id")
        if event_id != self.feedbackId:
            raise ValueError("FEEDBACK_ID_MISMATCH")
        if self.status in {"rejected", "needs_second_review"} and not self.reasonCodes:
            raise ValueError("ADJUDICATION_REASON_REQUIRED")
        if self.status == "approved_for_training" and not self.independentReviewConfirmed:
            raise ValueError("INDEPENDENT_REVIEW_REQUIRED_FOR_TRAINING")
        return self
