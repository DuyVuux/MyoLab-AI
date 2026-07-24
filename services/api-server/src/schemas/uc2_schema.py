"""Pydantic models for Day 23 UC2 quantitative assessment API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionDescriptor(StrictModel):
    sessionId: str
    subjectRef: str
    affectedSide: str
    referenceSide: str | None
    targetMuscles: list[str]
    protocolId: str
    protocolVersion: str
    gestureVocabularyVersion: str
    unit: str
    samplingRateHz: float = Field(gt=0)
    channelMapVersion: str
    preprocessingVersion: str
    featureVersion: str
    qcStatus: Literal["pass", "warning", "fail"]


class CompatibilityCheck(StrictModel):
    field: str
    status: Literal["match", "mismatch", "not_available"]
    baselineValue: Any
    comparisonValue: Any
    reasonCode: str | None = None


class LongitudinalSafety(StrictModel):
    rawSamplesIncluded: Literal[False] = False
    clinicalUseAllowed: Literal[False] = False
    humanReviewRequired: Literal[True] = True


class LongitudinalCompatibility(StrictModel):
    schemaVersion: Literal["longitudinal-compatibility.v0.1"] = (
        "longitudinal-compatibility.v0.1"
    )
    subjectRef: str
    baselineSessionId: str
    comparisonSessionIds: list[str]
    status: Literal["compatible", "blocked"]
    conclusionAllowed: bool
    checks: list[CompatibilityCheck]
    reasonCodes: list[str]
    safety: LongitudinalSafety = Field(default_factory=LongitudinalSafety)

    @model_validator(mode="after")
    def _validate_status(self):
        if self.status == "compatible" and not self.conclusionAllowed:
            raise ValueError("COMPATIBLE_MUST_ALLOW_CONCLUSION")
        if self.status == "blocked" and self.conclusionAllowed:
            raise ValueError("BLOCKED_MUST_NOT_ALLOW_CONCLUSION")
        return self


class QuantitativeMetric(StrictModel):
    metricId: str
    labelVi: str
    status: Literal["computed", "not_available", "blocked", "experimental"]
    value: float | int | None
    unit: str | None
    formulaVersion: str
    validationStatus: Literal["not_validated"] = "not_validated"
    sourceSessionIds: list[str]
    limitations: list[str]

    @model_validator(mode="after")
    def _validate_value(self):
        if self.status in {"not_available", "blocked"} and self.value is not None:
            raise ValueError("UNAVAILABLE_METRIC_MUST_HAVE_NULL_VALUE")
        return self


class AssessmentSafety(StrictModel):
    scoreIsProbability: Literal[False] = False
    rawSamplesIncluded: Literal[False] = False
    clinicalUseAllowed: Literal[False] = False
    humanReviewRequired: Literal[True] = True
    isClinicalConclusion: Literal[False] = False


class UC2QuantitativeAssessment(StrictModel):
    schemaVersion: Literal["uc2-quantitative-assessment.v0.1"] = (
        "uc2-quantitative-assessment.v0.1"
    )
    assessmentId: str
    subjectRef: str
    sessionIds: list[str]
    status: Literal["completed", "completed_with_warnings", "blocked"]
    metrics: list[QuantitativeMetric]
    compatibility: LongitudinalCompatibility
    limitations: list[str]
    reviewStatus: Literal["pending_human_review"] = "pending_human_review"
    safety: AssessmentSafety = Field(default_factory=AssessmentSafety)


class UC2AssessmentRequest(StrictModel):
    scenarioId: Literal[
        "golden_uc2_longitudinal",
        "uc2_protocol_incompatible",
        "uc2_missing_baseline",
        "uc2_qc_fail_session",
        "uc2_bilateral_unavailable",
    ]


__all__ = [
    "SessionDescriptor",
    "CompatibilityCheck",
    "LongitudinalCompatibility",
    "QuantitativeMetric",
    "UC2QuantitativeAssessment",
    "UC2AssessmentRequest",
    "AssessmentSafety",
    "LongitudinalSafety",
]
