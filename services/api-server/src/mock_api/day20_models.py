from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ConsentScope(StrictModel):
    qualityImprovement: bool
    modelTraining: bool
    researchExport: bool


class ProtocolRef(StrictModel):
    protocolId: str
    protocolVersion: str


class SessionCreateRequest(StrictModel):
    subjectRef: str
    useCaseId: Literal["uc1", "uc2", "uc3", "uc4"]
    protocol: ProtocolRef
    affectedSide: Literal["left", "right", "bilateral", "not_applicable"]
    referenceSide: Literal["left", "right", "bilateral", "not_applicable"] | None = None
    targetMuscles: list[str]
    sessionType: Literal["baseline", "follow_up", "replay", "research"]
    operatorRef: str
    consent: ConsentScope
    dataSourceIntent: Literal[
        "synthetic_demo",
        "generic_csv_manifest",
        "noraxon_export_mock",
        "deidentified_replay",
    ]
    previousSessionId: str | None = None

    @model_validator(mode="after")
    def validate_semantics(self) -> "SessionCreateRequest":
        if "@" in self.subjectRef or self.subjectRef.isdigit() and len(self.subjectRef) >= 9:
            raise ValueError("DIRECT_IDENTIFIER_NOT_ALLOWED")
        if not self.targetMuscles:
            raise ValueError("TARGET_MUSCLE_REQUIRED")
        if not any(self.consent.model_dump().values()):
            raise ValueError("CONSENT_SCOPE_REQUIRED")
        if self.sessionType == "follow_up" and not self.previousSessionId:
            raise ValueError("PREVIOUS_SESSION_REQUIRED")
        if self.useCaseId in {"uc3", "uc4"} and self.sessionType not in {"research", "replay"}:
            raise ValueError("FEASIBILITY_SESSION_ONLY")
        return self


class SessionRecord(SessionCreateRequest):
    schemaVersion: Literal["session-record.v0.1"] = "session-record.v0.1"
    sessionId: str
    workflowStatus: str
    createdAt: str
    containsDirectIdentifier: Literal[False] = False


class ScenarioRequest(StrictModel):
    scenario_id: str


class DetectedSignalMetadata(StrictModel):
    samplingRateHz: float | None = None
    durationS: float | None = None
    channelCount: int | None = None
    signalUnit: Literal["uV", "mV", "V"] | None = None
    timeColumn: str | None = None
    signalColumns: list[str]
    deviceVendor: str | None = None
    timestampMonotonic: bool | None = None


class ImportRecord(StrictModel):
    schemaVersion: Literal["signal-import-record.v0.1"] = "signal-import-record.v0.1"
    importId: str
    sessionId: str
    sourceType: str
    state: str
    sanitizedFilename: str
    sizeBytes: int = Field(ge=0)
    sourceHashSha256: str
    detectedMetadata: DetectedSignalMetadata
    errorCode: str | None = None
    retryFromState: str | None = None
    rawSamplesIncluded: Literal[False] = False
    containsDirectIdentifier: Literal[False] = False


class ChannelMapping(StrictModel):
    sourceChannel: str
    canonicalChannelId: str
    muscle: str
    side: Literal["left", "right", "bilateral", "not_applicable"]
    unit: Literal["uV", "mV", "V"]
    functionalRole: Literal["flexor", "extensor", "compensation", "reference", "other"]
    electrodePosition: str | None = None


class MappingRequest(StrictModel):
    mappings: list[ChannelMapping]


class PreviewPoint(StrictModel):
    timeS: float
    valueUv: float


class PreflightSummary(StrictModel):
    schemaVersion: Literal["preflight-summary.v0.1"] = "preflight-summary.v0.1"
    preflightId: str
    sessionId: str
    importId: str
    state: Literal["ready", "mapping_required", "import_blocked"]
    samplingRateHz: float | None
    durationS: float | None
    channelCount: int | None
    mappingCompleteness: float = Field(ge=0, le=1)
    timestampMonotonic: bool
    nonFiniteRatio: float = Field(ge=0, le=1)
    flatlineSuspected: bool
    clippingSuspected: bool
    powerlineWarning: bool
    motionArtifactWarning: bool
    sourceHashSha256: str
    preview: list[PreviewPoint]
    reasonCodes: list[str]
    rawSamplesIncluded: Literal[False] = False


class SegmentReference(StrictModel):
    rawSignalRef: str
    sourceHashSha256: str
    startSample: int
    endSample: int
    startTimeS: float
    endTimeS: float
    channelIds: list[str]


class CalibrationRepetition(StrictModel):
    repetitionId: str
    gestureId: str
    quality: Literal["accepted", "rejected"]
    segmentRef: SegmentReference
    reasonCodes: list[str]


class CalibrationRecord(StrictModel):
    schemaVersion: Literal["calibration-record.v0.1"] = "calibration-record.v0.1"
    calibrationId: str
    sessionId: str
    state: Literal["pass", "warning", "fail"]
    restRmsUv: float | None
    restSigmaUv: float | None
    activityThresholdCandidateUv: float | None
    engineeringK: float | None
    plannedRepetitions: int
    acceptedRepetitions: int
    rejectedRepetitions: int
    usableRepetitionRatio: float = Field(ge=0, le=1)
    durationS: float
    warningAcknowledged: bool
    reasonCodes: list[str]
    repetitions: list[CalibrationRepetition]
    rawSamplesIncluded: Literal[False] = False


class DetailedQualityResult(StrictModel):
    schemaVersion: Literal["detailed-quality-result.v0.1"] = "detailed-quality-result.v0.1"
    qualityResultId: str
    sessionId: str
    status: Literal["pass", "warning", "fail"]
    usableWindowRatio: float = Field(ge=0, le=1)
    badChannels: list[str]
    artifactFlags: list[str]
    reasonCodes: list[str]
    mfcvEligibility: Literal["eligible", "not_eligible", "not_assessed"]
    recommendedActionsVi: list[str]
    warningAcknowledgedBy: str | None = None
    warningAcknowledgementReason: str | None = None
    qcVersion: str


class QualityAcknowledgementRequest(StrictModel):
    reviewer_ref: str
    reason: str = Field(min_length=3)


class AnalysisHandoff(StrictModel):
    schemaVersion: Literal["analysis-handoff.v0.1"] = "analysis-handoff.v0.1"
    analysisId: str
    sessionId: str
    useCaseId: Literal["uc1", "uc2", "uc3", "uc4"]
    status: Literal["queued", "queued_with_warnings", "abstained"]
    nextRoute: str | None
    protocolVersion: str
    calibrationId: str | None
    qualityResultId: str
    sourceHashSha256: str
    scoreIsProbability: Literal[False] = False
    clinicalUseAllowed: Literal[False] = False
    humanReviewRequired: Literal[True] = True
    rawSamplesIncluded: Literal[False] = False
    reasonCodes: list[str]
