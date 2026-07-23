from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

UseCaseId = Literal["uc1", "uc2", "uc3", "uc4"]
JobStatus = Literal[
    "queued", "running", "completed", "completed_with_warnings",
    "abstained", "failed", "cancelled",
]
AnalysisStage = Literal[
    "validating_input", "running_quality_gate", "preprocessing", "windowing",
    "extracting_time_features", "estimating_spectrum",
    "extracting_frequency_features", "computing_trends", "building_evidence",
    "running_rule_engine", "building_explanation",
]

STAGE_ORDER: tuple[AnalysisStage, ...] = (
    "validating_input", "running_quality_gate", "preprocessing", "windowing",
    "extracting_time_features", "estimating_spectrum",
    "extracting_frequency_features", "computing_trends", "building_evidence",
    "running_rule_engine", "building_explanation",
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StageEvent(StrictModel):
    stage: AnalysisStage
    state: Literal["started", "completed", "skipped", "failed"]
    occurredAt: datetime
    durationMs: int | None = Field(default=None, ge=0)


class AnalysisJobError(StrictModel):
    code: str
    messageVi: str
    retryable: bool
    traceId: str


class AnalysisResultLinks(StrictModel):
    self: str
    summary: str | None = None
    manifest: str | None = None


class AnalysisSafety(StrictModel):
    scoreIsProbability: Literal[False] = False
    clinicalUseAllowed: Literal[False] = False
    humanReviewRequired: Literal[True] = True
    rawSamplesIncluded: Literal[False] = False


class AnalysisJobRecord(StrictModel):
    schemaVersion: Literal["analysis-job.v0.1"] = "analysis-job.v0.1"
    analysisId: str
    sessionId: str
    useCaseId: UseCaseId
    sourceHashSha256: str
    status: JobStatus
    progressMode: Literal["stage_only"] = "stage_only"
    currentStage: AnalysisStage | None = None
    completedStages: list[AnalysisStage] = Field(default_factory=list)
    stageHistory: list[StageEvent] = Field(default_factory=list)
    warningCodes: list[str] = Field(default_factory=list)
    reasonCodes: list[str] = Field(default_factory=list)
    resultLinks: AnalysisResultLinks
    error: AnalysisJobError | None = None
    safety: AnalysisSafety = Field(default_factory=AnalysisSafety)
    createdAt: datetime = Field(default_factory=utc_now)
    updatedAt: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_terminal_state(self) -> "AnalysisJobRecord":
        terminal = {"completed", "completed_with_warnings", "abstained", "failed", "cancelled"}
        if self.status in terminal and self.currentStage is not None:
            raise ValueError("Terminal job phải có currentStage=null")
        if self.status == "failed" and self.error is None:
            raise ValueError("Failed job phải có error")
        if self.status != "failed" and self.error is not None:
            raise ValueError("Chỉ failed job mới có error")
        return self


class AnalysisLaunchRequest(StrictModel):
    scenarioId: Literal[
        "golden_completed", "warning_completed", "qc_abstained", "runtime_failed"
    ] = "golden_completed"


class JobAdvanceRequest(StrictModel):
    expectedCurrentStage: AnalysisStage | None = None


class AnalysisRuntimeResult(StrictModel):
    status: Literal["completed", "completed_with_warnings"]
    warningCodes: list[str] = Field(default_factory=list)
    summary: dict
    manifest: dict
