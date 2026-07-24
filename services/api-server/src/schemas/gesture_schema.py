"""Strict Day 22 UC1 replay API contracts.

The API models intentionally use the public camelCase field names.  The pure
replay engine remains snake_case and is adapted explicitly in the service
layer, keeping the domain dependency one-way.
"""

from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


GestureId = Literal[
    "rest",
    "hand_open",
    "hand_close",
    "wrist_flexion",
    "wrist_extension",
]
ActiveGestureId = Literal[
    "hand_open",
    "hand_close",
    "wrist_flexion",
    "wrist_extension",
]
EngineeringConfidence = Literal[
    "engineering_high",
    "engineering_moderate",
    "engineering_low",
    "engineering_very_low",
    "not_available",
]
ReplayScenarioId = Literal[
    "uc1_golden_correct",
    "uc1_ambiguous_prediction",
    "uc1_no_activity",
    "uc1_fatigue_confidence_drop",
    "uc1_electrode_shift_warning",
    "uc1_qc_fail_abstention",
    "uc1_device_disconnect",
]
ReplayState = Literal[
    "idle",
    "running",
    "completed",
    "abstained",
    "disconnected",
    "failed",
]

SHA256_PATTERN = r"^[0-9a-f]{64}$"
CONFIDENCE_RANK: dict[str, int] = {
    "not_available": 0,
    "engineering_very_low": 1,
    "engineering_low": 2,
    "engineering_moderate": 3,
    "engineering_high": 4,
}


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        allow_inf_nan=False,
    )


class GestureSegmentRef(StrictModel):
    rawSignalRef: str = Field(min_length=1)
    sourceHashSha256: str = Field(pattern=SHA256_PATTERN)
    startSample: int = Field(ge=0)
    endSampleExclusive: int = Field(ge=1)
    startTimeS: float = Field(ge=0)
    endTimeExclusiveS: float = Field(gt=0)
    channelIds: list[str] = Field(min_length=1)
    repetitionId: str = Field(min_length=1)
    calibrationId: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_ranges(self) -> "GestureSegmentRef":
        if self.endSampleExclusive <= self.startSample:
            raise ValueError("SEGMENT_RANGE_INVALID")
        if self.endTimeExclusiveS <= self.startTimeS:
            raise ValueError("SEGMENT_RANGE_INVALID")
        if len(set(self.channelIds)) != len(self.channelIds):
            raise ValueError("SEGMENT_CHANNEL_IDS_DUPLICATE")
        if any(not channel.strip() for channel in self.channelIds):
            raise ValueError("SEGMENT_CHANNEL_ID_INVALID")
        return self


class ActivityGateContext(StrictModel):
    status: Literal["active", "inactive", "uncertain"]
    windowRmsUv: float = Field(ge=0)
    activationThresholdUv: float = Field(gt=0)
    releaseThresholdUv: float = Field(gt=0)
    reasonCode: str = Field(min_length=1)


class QualityContext(StrictModel):
    source: Literal[
        "day20_quality_gate",
        "day17_signal_quality",
        "scenario_fixture",
        "not_available",
    ]
    qualityResultId: str = Field(min_length=1)
    status: Literal["pass", "warning", "fail"]
    reasonCodes: list[str] = Field(default_factory=list)


class FatigueOverlay(StrictModel):
    source: Literal["scenario_fixture", "analysis_summary", "not_available"]
    status: Literal["stable", "warning", "abstain", "not_available"]
    confidenceAdjustmentApplied: bool
    reasonCodes: list[str] = Field(default_factory=list)
    evidenceSummaryVi: list[str] = Field(default_factory=list)
    counterevidenceVi: list[str] = Field(default_factory=list)
    limitationsVi: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_provenance(self) -> "FatigueOverlay":
        if (self.source == "not_available") != (
            self.status == "not_available"
        ):
            raise ValueError("FATIGUE_SOURCE_STATUS_MISMATCH")
        if self.status == "warning":
            if (
                not self.confidenceAdjustmentApplied
                or not self.reasonCodes
                or not self.evidenceSummaryVi
            ):
                raise ValueError("FATIGUE_WARNING_PROVENANCE_INVALID")
        return self


class LatencyBreakdown(StrictModel):
    totalMs: float = Field(ge=0)
    acquisitionMs: float = Field(ge=0)
    windowMs: float = Field(ge=0)
    preprocessMs: float = Field(ge=0)
    inferenceMs: float = Field(ge=0)
    transportRenderMs: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_total(self) -> "LatencyBreakdown":
        expected = (
            self.acquisitionMs
            + self.windowMs
            + self.preprocessMs
            + self.inferenceMs
            + self.transportRenderMs
        )
        if not math.isclose(self.totalMs, expected, rel_tol=0, abs_tol=1e-9):
            raise ValueError("LATENCY_TOTAL_MISMATCH")
        return self


class GestureSafety(StrictModel):
    scoreIsProbability: Literal[False] = False
    clinicalUseAllowed: Literal[False] = False
    rawSamplesIncluded: Literal[False] = False
    physicalActuationAllowed: Literal[False] = False


class GestureInferenceWindow(StrictModel):
    schemaVersion: Literal["gesture-inference.v0.1"] = "gesture-inference.v0.1"
    windowId: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)
    analysisId: str = Field(min_length=1)
    protocolVersion: str = Field(min_length=1)
    segmentRef: GestureSegmentRef
    targetGesture: ActiveGestureId
    activityGate: ActivityGateContext
    predictedGesture: ActiveGestureId | None
    baseEngineeringConfidence: EngineeringConfidence
    engineeringConfidence: EngineeringConfidence
    qualityContext: QualityContext
    fatigueOverlay: FatigueOverlay
    deviceState: Literal["connected", "disconnected", "reconnecting"]
    latency: LatencyBreakdown
    requiresHumanReview: Literal[True] = True
    sourceType: Literal["synthetic_replay"] = "synthetic_replay"
    modelVersion: str = Field(min_length=1)
    modelValidationStatus: Literal["not_validated"] = "not_validated"
    resultHashSha256: str = Field(pattern=SHA256_PATTERN)
    safety: GestureSafety = Field(default_factory=GestureSafety)

    @model_validator(mode="after")
    def validate_gating_and_confidence(self) -> "GestureInferenceWindow":
        blocked = (
            self.activityGate.status in {"inactive", "uncertain"}
            or self.qualityContext.status == "fail"
            or self.deviceState in {"disconnected", "reconnecting"}
            or self.fatigueOverlay.status == "abstain"
        )
        if blocked and (
            self.predictedGesture is not None
            or self.engineeringConfidence != "not_available"
        ):
            raise ValueError("BLOCKED_WINDOW_MUST_ABSTAIN")
        if self.predictedGesture is None:
            if self.engineeringConfidence != "not_available":
                raise ValueError("NULL_PREDICTION_CONFIDENCE_INVALID")
        elif blocked or self.engineeringConfidence == "not_available":
            raise ValueError("PREDICTION_GATE_INVALID")

        base_rank = CONFIDENCE_RANK[self.baseEngineeringConfidence]
        final_rank = CONFIDENCE_RANK[self.engineeringConfidence]
        if final_rank > base_rank:
            raise ValueError("ENGINEERING_CONFIDENCE_INCREASE_INVALID")
        if (
            self.fatigueOverlay.status == "warning"
            and final_rank >= base_rank
        ):
            raise ValueError("FATIGUE_CONFIDENCE_NOT_DOWNGRADED")
        return self

class LatencySummary(StrictModel):
    observedWindowCount: int = Field(ge=0)
    p50Ms: float | None = Field(default=None, ge=0)
    p95Ms: float | None = Field(default=None, ge=0)
    droppedWindows: int = Field(ge=0)
    disconnectTimeoutMs: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_percentiles(self) -> "LatencySummary":
        if self.observedWindowCount == 0:
            if self.p50Ms is not None or self.p95Ms is not None:
                raise ValueError("REPLAY_LATENCY_SUMMARY_MISMATCH")
        elif self.p50Ms is None or self.p95Ms is None:
            raise ValueError("REPLAY_LATENCY_SUMMARY_MISMATCH")
        elif self.p95Ms < self.p50Ms:
            raise ValueError("REPLAY_LATENCY_PERCENTILE_ORDER_INVALID")
        return self


class UC1ReplaySession(StrictModel):
    schemaVersion: Literal["uc1-replay-session.v0.1"] = (
        "uc1-replay-session.v0.1"
    )
    replayId: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)
    analysisId: str = Field(min_length=1)
    scenarioId: ReplayScenarioId
    state: ReplayState
    currentIndex: int = Field(ge=-1)
    revision: int = Field(ge=0)
    totalWindows: int = Field(ge=0)
    currentWindow: GestureInferenceWindow | None
    history: list[GestureInferenceWindow] = Field(default_factory=list)
    latencySummary: LatencySummary
    reasonCodes: list[str] = Field(default_factory=list)
    sourceType: Literal["synthetic_replay"] = "synthetic_replay"
    modelValidationStatus: Literal["not_validated"] = "not_validated"
    clinicalUseAllowed: Literal[False] = False
    humanReviewRequired: Literal[True] = True

    @model_validator(mode="after")
    def validate_aggregate(self) -> "UC1ReplaySession":
        if self.currentIndex == -1:
            if self.currentWindow is not None or self.history:
                raise ValueError("REPLAY_CURSOR_MISMATCH")
        elif self.currentWindow is None:
            raise ValueError("REPLAY_CURSOR_MISMATCH")

        history_ids = [item.windowId for item in self.history]
        if len(set(history_ids)) != len(history_ids):
            raise ValueError("REPLAY_HISTORY_DUPLICATE")
        if (
            self.currentWindow is not None
            and self.currentWindow.windowId in history_ids
        ):
            raise ValueError("REPLAY_HISTORY_CONTAINS_CURRENT")

        expected_history_count = max(0, self.currentIndex)
        if len(self.history) != expected_history_count:
            raise ValueError("REPLAY_HISTORY_CURSOR_MISMATCH")

        visible = [
            *self.history,
            *([self.currentWindow] if self.currentWindow is not None else []),
        ]
        if any(
            later.segmentRef.startSample <= earlier.segmentRef.startSample
            or later.segmentRef.startTimeS <= earlier.segmentRef.startTimeS
            for earlier, later in zip(visible, visible[1:])
        ):
            raise ValueError("REPLAY_HISTORY_ORDER_INVALID")

        expected_visible_count = max(0, self.currentIndex + 1)
        if len(visible) != expected_visible_count:
            raise ValueError("REPLAY_HISTORY_CURSOR_MISMATCH")
        if any(
            item.sessionId != self.sessionId
            or item.analysisId != self.analysisId
            for item in visible
        ):
            raise ValueError("REPLAY_WINDOW_CONTEXT_MISMATCH")
        if self.latencySummary.observedWindowCount != len(visible):
            raise ValueError("REPLAY_LATENCY_SUMMARY_MISMATCH")
        if self.revision != expected_visible_count:
            raise ValueError("REPLAY_REVISION_MISMATCH")

        zero_window_abstention = (
            self.totalWindows == 0
            and self.state == "abstained"
            and self.currentIndex == -1
        )
        if self.totalWindows == 0 and not zero_window_abstention:
            raise ValueError("REPLAY_TOTAL_WINDOWS_MISMATCH")
        if self.totalWindows > 0 and self.currentIndex >= self.totalWindows:
            raise ValueError("REPLAY_TOTAL_WINDOWS_MISMATCH")
        if len(visible) > self.totalWindows:
            raise ValueError("REPLAY_TOTAL_WINDOWS_MISMATCH")

        if self.totalWindows > 0:
            last_index = self.totalWindows - 1
            if (self.state == "idle") != (self.currentIndex == -1):
                raise ValueError("REPLAY_STATE_CURSOR_MISMATCH")
            if self.state == "running" and not (
                0 <= self.currentIndex < last_index
            ):
                raise ValueError("REPLAY_STATE_CURSOR_MISMATCH")
            if (
                self.state in {"completed", "abstained", "disconnected"}
                and self.currentIndex != last_index
            ):
                raise ValueError("REPLAY_STATE_CURSOR_MISMATCH")
            # A failed replay may stop before reveal, partially, or at the end.
        return self


class ReplayCreateRequest(StrictModel):
    analysisId: str = Field(min_length=1)
    scenarioId: ReplayScenarioId


class ReplayAdvanceRequest(StrictModel):
    expectedCurrentIndex: int = Field(ge=-1)
    expectedRevision: int = Field(ge=0)


class GestureFeedbackContext(StrictModel):
    schemaVersion: Literal["gesture-feedback-context.v0.1"] = (
        "gesture-feedback-context.v0.1"
    )
    analysisId: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)
    windowId: str = Field(min_length=1)
    rawSignalRef: str = Field(min_length=1)
    sourceHashSha256: str = Field(pattern=SHA256_PATTERN)
    startSample: int = Field(ge=0)
    endSampleExclusive: int = Field(ge=1)
    startTimeS: float = Field(ge=0)
    endTimeExclusiveS: float = Field(gt=0)
    channelIds: list[str] = Field(min_length=1)
    repetitionId: str = Field(min_length=1)
    calibrationId: str = Field(min_length=1)
    modelVersion: str = Field(min_length=1)
    originalResultHashSha256: str = Field(pattern=SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_ranges(self) -> "GestureFeedbackContext":
        if (
            self.endSampleExclusive <= self.startSample
            or self.endTimeExclusiveS <= self.startTimeS
        ):
            raise ValueError("FEEDBACK_SEGMENT_RANGE_INVALID")
        if len(set(self.channelIds)) != len(self.channelIds):
            raise ValueError("FEEDBACK_CHANNEL_IDS_DUPLICATE")
        return self


class GestureFeedbackRequest(StrictModel):
    action: Literal["accept", "correct", "uncertain", "remeasure"]
    correctedGesture: GestureId | None = None
    reviewerCertainty: Literal["low", "moderate", "high"]
    expectedWindowId: str = Field(min_length=1)
    expectedRevision: int = Field(ge=0)


class GestureFeedbackRecord(StrictModel):
    schemaVersion: Literal["gesture-feedback.v0.1"] = "gesture-feedback.v0.1"
    feedbackId: str = Field(min_length=1)
    replayId: str = Field(min_length=1)
    action: Literal["accept", "correct", "uncertain", "remeasure"]
    correctedGesture: GestureId | None = None
    reviewerCertainty: Literal["low", "moderate", "high"]
    actorRole: Literal["ktv", "physician", "researcher", "ml_qa"]
    context: GestureFeedbackContext
    automaticTrainingCandidate: Literal[False] = False


__all__ = [
    "GestureFeedbackContext",
    "GestureFeedbackRecord",
    "GestureFeedbackRequest",
    "GestureInferenceWindow",
    "ReplayAdvanceRequest",
    "ReplayCreateRequest",
    "ReplayScenarioId",
    "UC1ReplaySession",
]
