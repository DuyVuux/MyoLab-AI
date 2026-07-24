"""Composed Day 20 + Day 21 + Day 22 deterministic prototype API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

import day20_store
from day21_app import app as day21_app
from day21_app import repository as analysis_repository
from gesture_replay_engine import (
    ReplayContext,
    ReplayContextError,
    ReplayRepetition,
)
from repositories.uc1_replay_repo import InMemoryUC1ReplayRepository
from routes.uc1_replays import create_uc1_replay_router, problem_response
from services.uc1_replay_service import UC1ReplayService


def _canonical_protocol_version(protocol_id: str, version: str) -> str:
    numeric = version.removeprefix("v")
    parts = numeric.split(".")
    if len(parts) == 2:
        numeric = f"{numeric}.0"
    return f"{protocol_id}@{numeric}"


def resolve_replay_context(
    session_id: str,
    analysis_id: str,
    summary: Mapping[str, Any],
) -> ReplayContext:
    """Resolve exact Day 20/21 provenance without accepting client overrides."""

    if not isinstance(summary, Mapping):
        raise ReplayContextError("REPLAY_CONTEXT_SUMMARY_INVALID")
    if (
        summary.get("analysis_id") != analysis_id
        or summary.get("session_id") != session_id
    ):
        raise ReplayContextError(
            "REPLAY_CONTEXT_SUMMARY_OWNERSHIP_MISMATCH"
        )

    try:
        session = day20_store.SESSIONS[session_id]
        calibration = day20_store.CALIBRATIONS[session_id]
        quality = day20_store.QUALITY[session_id]
    except KeyError as exc:
        raise ReplayContextError("REPLAY_CONTEXT_UPSTREAM_NOT_READY") from exc

    imports = [
        item
        for item in day20_store.IMPORTS.values()
        if item.sessionId == session_id
    ]
    if not imports:
        raise ReplayContextError("REPLAY_CONTEXT_IMPORT_NOT_FOUND")
    imported = imports[-1]
    mappings = day20_store.MAPPINGS.get(imported.importId)
    if not mappings:
        raise ReplayContextError("REPLAY_CONTEXT_MAPPING_NOT_FOUND")
    if not calibration.repetitions:
        raise ReplayContextError("REPLAY_CONTEXT_REPETITIONS_NOT_FOUND")

    analysis = analysis_repository.get(analysis_id)
    if (
        analysis.sourceHashSha256 != imported.sourceHashSha256
        or any(
            repetition.segmentRef.sourceHashSha256
            != imported.sourceHashSha256
            for repetition in calibration.repetitions
        )
    ):
        raise ReplayContextError("REPLAY_CONTEXT_SOURCE_HASH_MISMATCH")

    sampling_rate_hz = imported.detectedMetadata.samplingRateHz
    if sampling_rate_hz is None:
        raise ReplayContextError("REPLAY_CONTEXT_SAMPLING_RATE_INVALID")

    return ReplayContext(
        session_id=session_id,
        analysis_id=analysis_id,
        source_hash_sha256=imported.sourceHashSha256,
        calibration_id=calibration.calibrationId,
        sampling_rate_hz=sampling_rate_hz,
        channel_ids=tuple(
            mapping.canonicalChannelId for mapping in mappings
        ),
        repetitions=tuple(
            ReplayRepetition(
                repetition_id=repetition.repetitionId,
                gesture_id=repetition.gestureId,
                quality=repetition.quality,
                raw_signal_ref=repetition.segmentRef.rawSignalRef,
                source_hash_sha256=(
                    repetition.segmentRef.sourceHashSha256
                ),
                start_sample=repetition.segmentRef.startSample,
                end_sample_exclusive=repetition.segmentRef.endSample,
                start_time_s=repetition.segmentRef.startTimeS,
                end_time_exclusive_s=repetition.segmentRef.endTimeS,
                channel_ids=tuple(repetition.segmentRef.channelIds),
            )
            for repetition in calibration.repetitions
        ),
        rest_rms_uv=calibration.restRmsUv,
        rest_sigma_uv=calibration.restSigmaUv,
        engineering_k=calibration.engineeringK,
        release_ratio=0.8,
        uncertain_band_ratio=0.1,
        latency_components_ms=(10.0, 200.0, 18.0, 14.0, 28.0),
        engine_id="uc1-deterministic-replay",
        engine_version="0.1.0",
        model_version="gesture-replay-v0.1",
        source_type="synthetic_replay",
        upstream_fatigue_status="not_available",
        upstream_fatigue_reason_codes=(),
        protocol_version=_canonical_protocol_version(
            session.protocol.protocolId,
            session.protocol.protocolVersion,
        ),
        quality_result_id=quality.qualityResultId,
        upstream_quality_status=quality.status,
        upstream_quality_reason_codes=tuple(quality.reasonCodes),
    )


replay_repository = InMemoryUC1ReplayRepository()
replay_service = UC1ReplayService(
    repository=replay_repository,
    analysis_repository=analysis_repository,
    context_resolver=resolve_replay_context,
)

app: FastAPI = day21_app
app.title = "MyoLab-AI Day 22 UC1 Replay Prototype API"
app.version = "0.1.0"
app.include_router(create_uc1_replay_router(replay_service))


@app.exception_handler(RequestValidationError)
async def request_validation_problem(
    request: Request,
    exc: RequestValidationError,
):
    invalid_params = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "code": error["type"],
        }
        for error in exc.errors()
    ]
    return problem_response(
        request,
        status_code=422,
        error_code="REQUEST_VALIDATION_FAILED",
        detail="Request body hoặc parameter không hợp lệ.",
        invalid_params=invalid_params,
    )


# Day 20/21 tests may have already built the shared FastAPI middleware
# stack before this composed module is imported. Force one safe rebuild so
# the Day 22 Problem Details handler participates in ordered integration runs.
app.middleware_stack = None


__all__ = [
    "app",
    "replay_repository",
    "replay_service",
    "resolve_replay_context",
]
