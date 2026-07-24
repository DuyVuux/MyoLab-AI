"""Application service adapting the pure UC1 replay engine to public contracts."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from hashlib import sha256
import json
from threading import RLock
from typing import Any

from gesture_replay_engine import (
    ReplayContext,
    ReplayEngineError,
    ReplayScenarioError,
    build_replay_windows,
)
from repositories.analysis_job_repo import (
    AnalysisJobNotFound,
    InMemoryAnalysisJobRepository,
)
from repositories.uc1_replay_repo import InMemoryUC1ReplayRepository
from schemas.gesture_schema import (
    GestureFeedbackContext,
    GestureFeedbackRecord,
    GestureFeedbackRequest,
    GestureInferenceWindow,
    ReplayAdvanceRequest,
    ReplayCreateRequest,
    UC1ReplaySession,
)


ReplayContextResolver = Callable[[str, str, Mapping[str, Any]], ReplayContext]


class UC1ReplayServiceError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def canonical_payload_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


class UC1ReplayService:
    """Coordinates upstream state, hidden replay windows, and feedback."""

    def __init__(
        self,
        *,
        repository: InMemoryUC1ReplayRepository,
        analysis_repository: InMemoryAnalysisJobRepository,
        context_resolver: ReplayContextResolver,
    ) -> None:
        self.repository = repository
        self.analysis_repository = analysis_repository
        self.context_resolver = context_resolver
        self._lock = RLock()

    def reset(self) -> None:
        with self._lock:
            self.repository.reset()

    def create_replay(
        self,
        *,
        session_id: str,
        request: ReplayCreateRequest,
        idempotency_key: str,
    ) -> UC1ReplaySession:
        with self._lock:
            fingerprint = canonical_payload_hash(
                request.model_dump(mode="json")
            )
            existing = self.repository.get_replay_by_idempotency(
                session_id=session_id,
                idempotency_key=idempotency_key,
                request_fingerprint=fingerprint,
            )
            if existing is not None:
                return existing

            analysis = self._analysis_for_replay(
                request.analysisId,
                session_id=session_id,
            )
            replay_id = "REPLAY-" + sha256(
                (
                    f"{session_id}:{idempotency_key}:{fingerprint}"
                ).encode("utf-8")
            ).hexdigest()[:16]

            if analysis.status == "abstained":
                replay, _ = self.repository.create(
                    replay_id=replay_id,
                    session_id=session_id,
                    analysis_id=analysis.analysisId,
                    scenario_id=request.scenarioId,
                    windows=(),
                    terminal_state="abstained",
                    reason_codes=tuple(analysis.reasonCodes),
                    idempotency_key=idempotency_key,
                    request_fingerprint=fingerprint,
                    initially_abstained=True,
                )
                return replay

            try:
                summary = self.analysis_repository.get_summary(
                    analysis.analysisId
                )
            except (AnalysisJobNotFound, KeyError) as exc:
                raise UC1ReplayServiceError(
                    "ANALYSIS_RESULT_NOT_READY"
                ) from exc

            try:
                context = self.context_resolver(
                    session_id,
                    analysis.analysisId,
                    summary,
                )
                domain_windows = build_replay_windows(
                    context=context,
                    scenario_id=request.scenarioId,
                )
            except ReplayScenarioError as exc:
                raise UC1ReplayServiceError(
                    "REQUEST_VALIDATION_FAILED"
                ) from exc
            except ReplayEngineError as exc:
                raise UC1ReplayServiceError(exc.code) from exc

            windows = tuple(
                self._to_public_window(
                    item.to_dict(),
                    scenario_id=request.scenarioId,
                    upstream_quality_reason_codes=(
                        context.upstream_quality_reason_codes
                    ),
                )
                for item in domain_windows
            )
            terminal_state = {
                "uc1_qc_fail_abstention": "abstained",
                "uc1_device_disconnect": "disconnected",
            }.get(request.scenarioId, "completed")
            terminal_reasons = self._terminal_reason_codes(windows)
            replay, _ = self.repository.create(
                replay_id=replay_id,
                session_id=session_id,
                analysis_id=analysis.analysisId,
                scenario_id=request.scenarioId,
                windows=windows,
                terminal_state=terminal_state,
                reason_codes=terminal_reasons,
                idempotency_key=idempotency_key,
                request_fingerprint=fingerprint,
                initially_abstained=False,
            )
            return replay

    def get_replay(self, replay_id: str) -> UC1ReplaySession:
        with self._lock:
            return self.repository.get(replay_id)

    def advance_replay(
        self,
        replay_id: str,
        request: ReplayAdvanceRequest,
    ) -> UC1ReplaySession:
        with self._lock:
            return self.repository.advance(
                replay_id,
                expected_current_index=request.expectedCurrentIndex,
                expected_revision=request.expectedRevision,
            )

    def create_feedback(
        self,
        *,
        replay_id: str,
        request: GestureFeedbackRequest,
        actor_role: str,
        idempotency_key: str,
    ) -> GestureFeedbackRecord:
        with self._lock:
            request_payload = {
                "actorRole": actor_role,
                "request": request.model_dump(mode="json"),
            }
            fingerprint = canonical_payload_hash(request_payload)
            existing = self.repository.get_feedback_by_idempotency(
                replay_id=replay_id,
                idempotency_key=idempotency_key,
                request_fingerprint=fingerprint,
            )
            if existing is not None:
                return existing

            replay = self.repository.get(replay_id)
            current = replay.currentWindow
            if (
                current is None
                or request.expectedWindowId != current.windowId
                or request.expectedRevision != replay.revision
            ):
                raise UC1ReplayServiceError("STALE_FEEDBACK_CONTEXT")
            self._validate_feedback_correction(request, current)

            segment = current.segmentRef
            context = GestureFeedbackContext(
                analysisId=current.analysisId,
                sessionId=current.sessionId,
                windowId=current.windowId,
                rawSignalRef=segment.rawSignalRef,
                sourceHashSha256=segment.sourceHashSha256,
                startSample=segment.startSample,
                endSampleExclusive=segment.endSampleExclusive,
                startTimeS=segment.startTimeS,
                endTimeExclusiveS=segment.endTimeExclusiveS,
                channelIds=list(segment.channelIds),
                repetitionId=segment.repetitionId,
                calibrationId=segment.calibrationId,
                modelVersion=current.modelVersion,
                originalResultHashSha256=current.resultHashSha256,
            )
            feedback_id = "FEEDBACK-" + sha256(
                (
                    f"{replay_id}:{idempotency_key}:{fingerprint}"
                ).encode("utf-8")
            ).hexdigest()[:16]
            feedback = GestureFeedbackRecord(
                feedbackId=feedback_id,
                replayId=replay_id,
                action=request.action,
                correctedGesture=request.correctedGesture,
                reviewerCertainty=request.reviewerCertainty,
                actorRole=actor_role,
                context=context,
            )
            saved, _ = self.repository.save_feedback(
                replay_id=replay_id,
                idempotency_key=idempotency_key,
                request_fingerprint=fingerprint,
                feedback=feedback,
            )
            return saved

    def _analysis_for_replay(self, analysis_id: str, *, session_id: str):
        try:
            analysis = self.analysis_repository.get(analysis_id)
        except AnalysisJobNotFound as exc:
            raise UC1ReplayServiceError("ANALYSIS_NOT_FOUND") from exc
        if analysis.sessionId != session_id:
            raise UC1ReplayServiceError("ANALYSIS_SESSION_MISMATCH")
        if analysis.useCaseId != "uc1":
            raise UC1ReplayServiceError("ANALYSIS_USE_CASE_MISMATCH")
        if analysis.status in {"queued", "running"}:
            raise UC1ReplayServiceError("ANALYSIS_NOT_TERMINAL")
        if analysis.status in {"failed", "cancelled"}:
            raise UC1ReplayServiceError("ANALYSIS_NOT_REPLAYABLE")
        return analysis

    @staticmethod
    def _to_public_window(
        domain: Mapping[str, Any],
        *,
        scenario_id: str,
        upstream_quality_reason_codes: tuple[str, ...],
    ) -> GestureInferenceWindow:
        segment = domain["segment_ref"]
        gate = domain["activity_gate"]
        quality = domain["quality_overlay"]
        fatigue = domain["fatigue_overlay"]
        latency = domain["latency"]

        fixture_quality = scenario_id in {
            "uc1_electrode_shift_warning",
            "uc1_qc_fail_abstention",
        }
        fatigue_status = fatigue["status"]
        if fatigue_status in {"warning", "abstain"}:
            fatigue_source = "scenario_fixture"
            fatigue_evidence = [
                "Kịch bản replay mô phỏng thay đổi chỉ báo fatigue kỹ thuật."
            ]
            fatigue_limitations = [
                "Đây là deterministic fixture, không phải bằng chứng lâm sàng."
            ]
        else:
            fatigue_source = "not_available"
            fatigue_evidence = []
            fatigue_limitations = [
                "Day 21 không cung cấp fatigue status đủ điều kiện."
            ]

        payload: dict[str, Any] = {
            "schemaVersion": "gesture-inference.v0.1",
            "windowId": domain["window_id"],
            "sessionId": domain["session_id"],
            "analysisId": domain["analysis_id"],
            "protocolVersion": domain["protocol_version"],
            "segmentRef": {
                "rawSignalRef": segment["raw_signal_ref"],
                "sourceHashSha256": segment["source_hash_sha256"],
                "startSample": segment["start_sample"],
                "endSampleExclusive": segment["end_sample_exclusive"],
                "startTimeS": segment["start_time_s"],
                "endTimeExclusiveS": segment["end_time_exclusive_s"],
                "channelIds": list(segment["channel_ids"]),
                "repetitionId": segment["repetition_id"],
                "calibrationId": segment["calibration_id"],
            },
            "targetGesture": domain["target_gesture"],
            "activityGate": {
                "status": gate["status"],
                "windowRmsUv": gate["window_rms_uv"],
                "activationThresholdUv": gate["activation_threshold_uv"],
                "releaseThresholdUv": gate["release_threshold_uv"],
                "reasonCode": gate["reason_code"],
            },
            "predictedGesture": domain["predicted_gesture"],
            "baseEngineeringConfidence": domain[
                "base_engineering_confidence"
            ],
            "engineeringConfidence": domain["engineering_confidence"],
            "qualityContext": {
                "source": (
                    "scenario_fixture"
                    if fixture_quality
                    else "day20_quality_gate"
                ),
                "qualityResultId": quality["quality_result_id"],
                "status": quality["status"],
                "reasonCodes": list(quality["reason_codes"]),
            },
            "fatigueOverlay": {
                "source": fatigue_source,
                "status": fatigue_status,
                "confidenceAdjustmentApplied": fatigue[
                    "confidence_adjustment_applied"
                ],
                "reasonCodes": list(fatigue["reason_codes"]),
                "evidenceSummaryVi": fatigue_evidence,
                "counterevidenceVi": [],
                "limitationsVi": fatigue_limitations,
            },
            "deviceState": domain["device_state"],
            "latency": {
                "totalMs": latency["total_ms"],
                "acquisitionMs": latency["acquisition_ms"],
                "windowMs": latency["window_ms"],
                "preprocessMs": latency["preprocess_ms"],
                "inferenceMs": latency["inference_ms"],
                "transportRenderMs": latency["transport_render_ms"],
            },
            "requiresHumanReview": domain["requires_human_review"],
            "sourceType": domain["source_type"],
            "modelVersion": domain["model_version"],
            "modelValidationStatus": domain["model_validation_status"],
            "resultHashSha256": "0" * 64,
            "safety": {
                "scoreIsProbability": False,
                "clinicalUseAllowed": domain["clinical_use_allowed"],
                "rawSamplesIncluded": domain["raw_samples_included"],
                "physicalActuationAllowed": domain[
                    "physical_actuation_allowed"
                ],
            },
        }
        public = GestureInferenceWindow.model_validate(payload)
        hash_input = public.model_dump(
            mode="json",
            exclude={"resultHashSha256"},
        )
        public_hash = canonical_payload_hash(hash_input)
        return public.model_copy(
            update={"resultHashSha256": public_hash},
        )

    @staticmethod
    def _terminal_reason_codes(
        windows: tuple[GestureInferenceWindow, ...],
    ) -> tuple[str, ...]:
        codes: list[str] = []
        for window in windows:
            codes.extend(window.qualityContext.reasonCodes)
            codes.extend(window.fatigueOverlay.reasonCodes)
            if window.deviceState == "disconnected":
                codes.append("DEVICE_DISCONNECTED")
        return tuple(dict.fromkeys(codes))

    @staticmethod
    def _validate_feedback_correction(
        request: GestureFeedbackRequest,
        current: GestureInferenceWindow,
    ) -> None:
        if request.action == "correct":
            if (
                current.predictedGesture is None
                or request.correctedGesture is None
                or request.correctedGesture == current.predictedGesture
            ):
                raise UC1ReplayServiceError(
                    "FEEDBACK_CORRECTION_INVALID"
                )
        elif request.correctedGesture is not None:
            raise UC1ReplayServiceError("FEEDBACK_CORRECTION_INVALID")


__all__ = [
    "UC1ReplayService",
    "UC1ReplayServiceError",
    "canonical_payload_hash",
]
