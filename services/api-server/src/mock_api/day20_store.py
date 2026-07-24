from __future__ import annotations

from copy import deepcopy
from hashlib import sha256

from day20_models import (
    AnalysisHandoff,
    CalibrationRecord,
    CalibrationRepetition,
    ChannelMapping,
    DetailedQualityResult,
    DetectedSignalMetadata,
    ImportRecord,
    PreflightSummary,
    PreviewPoint,
    SegmentReference,
    SessionCreateRequest,
    SessionRecord,
)

SESSIONS: dict[str, SessionRecord] = {}
IMPORTS: dict[str, ImportRecord] = {}
MAPPINGS: dict[str, list[ChannelMapping]] = {}
CALIBRATIONS: dict[str, CalibrationRecord] = {}
QUALITY: dict[str, DetailedQualityResult] = {}
HANDOFFS: dict[str, AnalysisHandoff] = {}
IDEMPOTENCY: dict[str, str] = {}


def reset_store() -> None:
    SESSIONS.clear(); IMPORTS.clear(); MAPPINGS.clear(); CALIBRATIONS.clear(); QUALITY.clear(); HANDOFFS.clear(); IDEMPOTENCY.clear()


def create_session(request: SessionCreateRequest, key: str) -> SessionRecord:
    if key in IDEMPOTENCY:
        return SESSIONS[IDEMPOTENCY[key]]
    session_id = f"SESSION-D20-{len(SESSIONS)+1:03d}"
    record = SessionRecord(**request.model_dump(), sessionId=session_id, workflowStatus="intake_in_progress", createdAt="2026-07-23T00:00:00Z")
    SESSIONS[session_id] = record
    IDEMPOTENCY[key] = session_id
    return record


def create_import(session_id: str, scenario_id: str) -> ImportRecord:
    index = len(IMPORTS) + 1
    state = "mapping_required"
    metadata = DetectedSignalMetadata(
        samplingRateHz=1000,
        durationS=70,
        channelCount=4,
        signalUnit="uV",
        timeColumn="time_s",
        signalColumns=["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"],
        deviceVendor="synthetic",
        timestampMonotonic=True,
    )
    error_code = None
    retry = None
    if scenario_id == "import_missing_unit":
        metadata.signalUnit = None
    elif scenario_id == "import_duplicate":
        state = "duplicate_detected"
    elif scenario_id == "import_rejected_corrupt_file":
        state = "import_rejected"
        metadata = DetectedSignalMetadata(signalColumns=[])
        error_code = "CSV_PARSE_FAILED"
        retry = "file_selected"
    import_id = f"IMPORT-D20-{index:03d}"
    source_hash = sha256(
        (
            "myolab-day20-import:v0.1:"
            f"{session_id}:{import_id}:{scenario_id}"
        ).encode("utf-8")
    ).hexdigest()
    record = ImportRecord(
        importId=import_id,
        sessionId=session_id,
        sourceType=SESSIONS[session_id].dataSourceIntent,
        state=state,
        sanitizedFilename=f"session_{session_id.lower()}.csv",
        sizeBytes=7680000,
        sourceHashSha256=source_hash,
        detectedMetadata=metadata,
        errorCode=error_code,
        retryFromState=retry,
    )
    IMPORTS[import_id] = record
    return record


def save_mapping(import_id: str, mappings: list[ChannelMapping]) -> ImportRecord:
    expected = IMPORTS[import_id].detectedMetadata.signalColumns
    if len(mappings) != len(expected):
        raise ValueError("MAPPING_INCOMPLETE")
    source_ids = [item.sourceChannel for item in mappings]
    canonical_ids = [item.canonicalChannelId for item in mappings]
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("DUPLICATE_SOURCE_CHANNEL")
    if len(set(canonical_ids)) != len(canonical_ids):
        raise ValueError("DUPLICATE_CANONICAL_CHANNEL")
    if set(source_ids) != set(expected):
        raise ValueError("SOURCE_CHANNEL_MISMATCH")
    MAPPINGS[import_id] = deepcopy(mappings)
    current = IMPORTS[import_id]
    updated = current.model_copy(update={"state": "qc_ready", "detectedMetadata": current.detectedMetadata.model_copy(update={"signalUnit": mappings[0].unit})})
    IMPORTS[import_id] = updated
    return updated


def preflight(session_id: str) -> PreflightSummary:
    candidates = [item for item in IMPORTS.values() if item.sessionId == session_id]
    if not candidates:
        raise KeyError("IMPORT_NOT_FOUND")
    item = candidates[-1]
    completeness = 1.0 if item.importId in MAPPINGS else 0.0
    if item.state == "import_rejected" or not item.detectedMetadata.samplingRateHz:
        state = "import_blocked"
    elif completeness < 1:
        state = "mapping_required"
    else:
        state = "ready"
    return PreflightSummary(
        preflightId=f"PREFLIGHT-{session_id}", sessionId=session_id, importId=item.importId,
        state=state, samplingRateHz=item.detectedMetadata.samplingRateHz,
        durationS=item.detectedMetadata.durationS, channelCount=item.detectedMetadata.channelCount,
        mappingCompleteness=completeness, timestampMonotonic=bool(item.detectedMetadata.timestampMonotonic),
        nonFiniteRatio=0, flatlineSuspected=False, clippingSuspected=False,
        powerlineWarning=False, motionArtifactWarning=False, sourceHashSha256=item.sourceHashSha256,
        preview=[PreviewPoint(timeS=0, valueUv=0), PreviewPoint(timeS=0.1, valueUv=15)],
        reasonCodes=[] if state == "ready" else [state.upper()],
    )


def calibration(session_id: str, scenario_id: str) -> CalibrationRecord:
    state = "pass"
    reasons: list[str] = []
    rejected_indices: set[int] = set()
    if scenario_id == "calibration_warning":
        state = "warning"
        reasons = ["GESTURE_SEPARABILITY_LOW"]
        rejected_indices = {10, 11}
    if scenario_id == "calibration_fail":
        state = "fail"
        reasons = ["CALIBRATION_QUALITY_INSUFFICIENT"]
        rejected_indices = set(range(7))
    import_items = [
        item for item in IMPORTS.values() if item.sessionId == session_id
    ]
    if not import_items:
        raise KeyError("IMPORT_NOT_FOUND")
    import_item = import_items[-1]
    sampling_rate_hz = import_item.detectedMetadata.samplingRateHz
    if sampling_rate_hz is None or sampling_rate_hz <= 0:
        raise ValueError("SAMPLING_RATE_REQUIRED")
    mappings = MAPPINGS.get(import_item.importId)
    if not mappings:
        raise ValueError("MAPPING_REQUIRED")
    channel_ids = [item.canonicalChannelId for item in mappings]
    raw_signal_ref = f"RAW-REF-{import_item.importId}"
    gestures = (
        "hand_open",
        "hand_close",
        "wrist_flexion",
        "wrist_extension",
    )
    repetition_plan = tuple(
        (gesture_id, occurrence)
        for occurrence in range(1, 4)
        for gesture_id in gestures
    )
    repetitions = []
    for index, (gesture_id, occurrence) in enumerate(repetition_plan):
        start_sample = 5_000 + index * 1_250
        end_sample = start_sample + 1_000
        quality = "rejected" if index in rejected_indices else "accepted"
        repetitions.append(
            CalibrationRepetition(
                repetitionId=(
                    f"REP-{session_id}-{gesture_id.upper()}-{occurrence:02d}"
                ),
                gestureId=gesture_id,
                quality=quality,
                segmentRef=SegmentReference(
                    rawSignalRef=raw_signal_ref,
                    sourceHashSha256=import_item.sourceHashSha256,
                    startSample=start_sample,
                    endSample=end_sample,
                    startTimeS=start_sample / sampling_rate_hz,
                    endTimeS=end_sample / sampling_rate_hz,
                    channelIds=channel_ids,
                ),
                reasonCodes=(
                    ["CALIBRATION_REPETITION_REJECTED"]
                    if quality == "rejected"
                    else []
                ),
            )
        )
    planned_repetitions = len(repetitions)
    accepted_repetitions = sum(
        repetition.quality == "accepted" for repetition in repetitions
    )
    rejected_repetitions = planned_repetitions - accepted_repetitions
    record = CalibrationRecord(
        calibrationId=f"CAL-{session_id}", sessionId=session_id, state=state,
        restRmsUv=4.2, restSigmaUv=0.8, activityThresholdCandidateUv=6.6, engineeringK=3,
        plannedRepetitions=planned_repetitions,
        acceptedRepetitions=accepted_repetitions,
        rejectedRepetitions=rejected_repetitions,
        usableRepetitionRatio=accepted_repetitions / planned_repetitions, durationS=142, warningAcknowledged=False,
        reasonCodes=reasons,
        repetitions=repetitions,
    )
    CALIBRATIONS[session_id] = record
    return record


def quality(session_id: str, scenario_id: str) -> DetailedQualityResult:
    status = "pass"; ratio = 0.94; bad: list[str] = []; flags: list[str] = []; reasons: list[str] = []; actions: list[str] = []
    if scenario_id == "qc_warning_powerline":
        status = "warning"; ratio = 0.82; flags = ["POWERLINE_NOISE_HIGH"]; reasons = ["POWERLINE_NOISE_HIGH"]; actions = ["KTV xác nhận cảnh báo trước khi tiếp tục."]
    if scenario_id == "qc_fail_flatline":
        status = "fail"; ratio = 0.31; bad = ["CH02"]; flags = ["FLATLINE_EXCESSIVE"]; reasons = ["FLATLINE_EXCESSIVE"]; actions = ["Kiểm tra lại điện cực và đo lại."]
    result = DetailedQualityResult(
        qualityResultId=f"QC-{session_id}", sessionId=session_id, status=status,
        usableWindowRatio=ratio, badChannels=bad, artifactFlags=flags, reasonCodes=reasons,
        mfcvEligibility="not_eligible", recommendedActionsVi=actions, qcVersion="qc_v0.1",
    )
    QUALITY[session_id] = result
    return result


def acknowledge_quality(session_id: str, reviewer_ref: str, reason: str) -> DetailedQualityResult:
    result = QUALITY[session_id]
    if result.status != "warning":
        raise ValueError("QUALITY_NOT_WARNING")
    updated = result.model_copy(update={"warningAcknowledgedBy": reviewer_ref, "warningAcknowledgementReason": reason})
    QUALITY[session_id] = updated
    return updated


def analysis_handoff(session_id: str) -> AnalysisHandoff:
    session = SESSIONS[session_id]
    quality_result = QUALITY.get(session_id)
    if quality_result is None:
        raise ValueError("QUALITY_REQUIRED")
    calibration_result = CALIBRATIONS.get(session_id)
    import_item = next(item for item in IMPORTS.values() if item.sessionId == session_id)
    if calibration_result and calibration_result.state == "fail":
        status = "abstained"; next_route = None; reasons = ["CALIBRATION_QUALITY_INSUFFICIENT"]
    elif quality_result.status == "fail":
        status = "abstained"; next_route = None; reasons = list(quality_result.reasonCodes)
    elif quality_result.status == "warning" and not quality_result.warningAcknowledgedBy:
        raise ValueError("QUALITY_WARNING_ACK_REQUIRED")
    else:
        status = "queued_with_warnings" if quality_result.status == "warning" else "queued"
        next_route = f"/{session.useCaseId}/session/{session_id}" if session.useCaseId == "uc1" else f"/{session.useCaseId}/assessment/{session_id}"
        reasons = list(quality_result.reasonCodes)
    handoff = AnalysisHandoff(
        analysisId=f"AN-{session_id}", sessionId=session_id, useCaseId=session.useCaseId,
        status=status, nextRoute=next_route,
        protocolVersion=f"{session.protocol.protocolId}.{session.protocol.protocolVersion}",
        calibrationId=calibration_result.calibrationId if calibration_result else None,
        qualityResultId=quality_result.qualityResultId,
        sourceHashSha256=import_item.sourceHashSha256,
        reasonCodes=reasons,
    )
    HANDOFFS[session_id] = handoff
    return handoff
