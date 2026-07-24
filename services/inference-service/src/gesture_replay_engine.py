"""Pure deterministic gesture replay for UC1 contract and safety testing.

This module deliberately has no FastAPI, Pydantic, database, or API-server
dependency.  It produces immutable domain records from an injected replay
context.  The replay scenarios are engineering fixtures; they are not a
trained classifier and make no clinical claim.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from numbers import Real
import re
from typing import Any, Literal

from semg_core.activity_gate import ActivityGateResult, evaluate_activity
from semg_core.latency_metrics import total_latency_ms


ActivityStatus = Literal["active", "inactive", "uncertain"]
ConfidenceCategory = Literal[
    "engineering_high",
    "engineering_moderate",
    "engineering_low",
    "engineering_very_low",
    "not_available",
]
DeviceState = Literal["connected", "disconnected", "reconnecting"]
FatigueStatus = Literal["stable", "warning", "abstain", "not_available"]
GestureId = Literal[
    "hand_open",
    "hand_close",
    "wrist_flexion",
    "wrist_extension",
]
QualityStatus = Literal["pass", "warning", "fail"]

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_GESTURE_IDS = frozenset(
    {"hand_open", "hand_close", "wrist_flexion", "wrist_extension"}
)
_CONFIDENCE_RANK: dict[ConfidenceCategory, int] = {
    "not_available": 0,
    "engineering_very_low": 1,
    "engineering_low": 2,
    "engineering_moderate": 3,
    "engineering_high": 4,
}
_QUALITY_PRIORITY: dict[QualityStatus, int] = {
    "pass": 0,
    "warning": 1,
    "fail": 2,
}
_FATIGUE_PRIORITY: dict[FatigueStatus, int] = {
    "stable": 0,
    "not_available": 1,
    "warning": 2,
    "abstain": 3,
}


class ReplayEngineError(ValueError):
    """Base class for stable typed replay-engine failures."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ReplayContextError(ReplayEngineError):
    """Raised when injected calibration or provenance is invalid."""


class ReplayScenarioError(ReplayEngineError):
    """Raised when a replay scenario is not explicitly registered."""


def _require_string(value: object, *, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReplayContextError(code)
    return value


def _require_real(
    value: object,
    *,
    code: str,
    minimum: float | None = None,
    exclusive_minimum: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ReplayContextError(code)
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ReplayContextError(code)
    if minimum is not None and numeric < minimum:
        raise ReplayContextError(code)
    if exclusive_minimum is not None and numeric <= exclusive_minimum:
        raise ReplayContextError(code)
    return numeric


def _require_positive_int(value: object, *, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReplayContextError(code)
    return value


def _require_nonnegative_int(value: object, *, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ReplayContextError(code)
    return value


def _require_string_tuple(
    values: object,
    *,
    code: str,
    unique: bool,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ReplayContextError(code)
    try:
        items = tuple(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ReplayContextError(code) from exc
    if not items or any(
        not isinstance(item, str) or not item.strip()
        for item in items
    ):
        raise ReplayContextError(code)
    if unique and len(set(items)) != len(items):
        raise ReplayContextError(code)
    return items


def _deduplicate_codes(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(code for group in groups for code in group))


def canonical_result_hash(payload: Mapping[str, Any]) -> str:
    """Return lowercase SHA-256 of canonical JSON.

    Callers must omit ``result_hash_sha256`` from ``payload``.  The replay
    engine does this centrally before assigning the immutable result hash.
    """

    try:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ReplayEngineError("RESULT_HASH_PAYLOAD_NOT_CANONICAL_JSON") from exc
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class ReplayRepetition:
    """One exact Day 20 calibration repetition and its source segment."""

    repetition_id: str
    gesture_id: GestureId
    quality: Literal["accepted", "rejected"]
    raw_signal_ref: str
    source_hash_sha256: str
    start_sample: int
    end_sample_exclusive: int
    start_time_s: float
    end_time_exclusive_s: float
    channel_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_string(
            self.repetition_id,
            code="REPLAY_REPETITION_ID_INVALID",
        )
        _require_string(
            self.raw_signal_ref,
            code="REPLAY_REPETITION_RAW_SIGNAL_REF_INVALID",
        )
        if self.gesture_id not in _GESTURE_IDS:
            raise ReplayContextError("REPLAY_REPETITION_GESTURE_INVALID")
        if self.quality not in {"accepted", "rejected"}:
            raise ReplayContextError("REPLAY_REPETITION_QUALITY_INVALID")
        if not _SHA256_PATTERN.fullmatch(self.source_hash_sha256):
            raise ReplayContextError("REPLAY_REPETITION_SOURCE_HASH_INVALID")
        start_sample = _require_nonnegative_int(
            self.start_sample,
            code="REPLAY_REPETITION_SAMPLE_RANGE_INVALID",
        )
        end_sample = _require_positive_int(
            self.end_sample_exclusive,
            code="REPLAY_REPETITION_SAMPLE_RANGE_INVALID",
        )
        if end_sample <= start_sample:
            raise ReplayContextError("REPLAY_REPETITION_SAMPLE_RANGE_INVALID")
        start_time = _require_real(
            self.start_time_s,
            code="REPLAY_REPETITION_TIME_RANGE_INVALID",
            minimum=0.0,
        )
        end_time = _require_real(
            self.end_time_exclusive_s,
            code="REPLAY_REPETITION_TIME_RANGE_INVALID",
            exclusive_minimum=0.0,
        )
        if end_time <= start_time:
            raise ReplayContextError("REPLAY_REPETITION_TIME_RANGE_INVALID")
        channels = _require_string_tuple(
            self.channel_ids,
            code="REPLAY_REPETITION_CHANNEL_IDS_INVALID",
            unique=True,
        )
        object.__setattr__(self, "start_time_s", start_time)
        object.__setattr__(self, "end_time_exclusive_s", end_time)
        object.__setattr__(self, "channel_ids", channels)


@dataclass(frozen=True, slots=True)
class ReplayContext:
    """Injected calibration, exact repetition records, and replay metadata."""

    session_id: str
    analysis_id: str
    source_hash_sha256: str
    calibration_id: str
    sampling_rate_hz: float
    channel_ids: tuple[str, ...]
    repetitions: tuple[ReplayRepetition, ...]
    rest_rms_uv: float
    rest_sigma_uv: float
    engineering_k: float
    release_ratio: float
    uncertain_band_ratio: float
    latency_components_ms: tuple[float, float, float, float, float]
    engine_id: str
    engine_version: str
    model_version: str
    source_type: str
    upstream_fatigue_status: FatigueStatus
    upstream_fatigue_reason_codes: tuple[str, ...]
    protocol_version: str | None = None
    quality_result_id: str | None = None
    upstream_quality_status: QualityStatus = "pass"
    upstream_quality_reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "session_id",
            "analysis_id",
            "calibration_id",
            "engine_id",
            "engine_version",
            "model_version",
            "source_type",
        ):
            _require_string(
                getattr(self, field_name),
                code=f"REPLAY_CONTEXT_{field_name.upper()}_INVALID",
            )

        if not _SHA256_PATTERN.fullmatch(self.source_hash_sha256):
            raise ReplayContextError("REPLAY_CONTEXT_SOURCE_HASH_INVALID")
        if self.source_type not in {"synthetic_replay", "deidentified_replay"}:
            raise ReplayContextError("REPLAY_CONTEXT_SOURCE_TYPE_INVALID")

        sampling_rate = _require_real(
            self.sampling_rate_hz,
            code="REPLAY_CONTEXT_SAMPLING_RATE_INVALID",
            exclusive_minimum=0.0,
        )
        channels = _require_string_tuple(
            self.channel_ids,
            code="REPLAY_CONTEXT_CHANNEL_IDS_INVALID",
            unique=True,
        )
        if isinstance(self.repetitions, (str, bytes)):
            raise ReplayContextError("REPLAY_CONTEXT_REPETITIONS_INVALID")
        try:
            repetitions = tuple(self.repetitions)
        except TypeError as exc:
            raise ReplayContextError(
                "REPLAY_CONTEXT_REPETITIONS_INVALID"
            ) from exc
        if not repetitions or any(
            not isinstance(repetition, ReplayRepetition)
            for repetition in repetitions
        ):
            raise ReplayContextError("REPLAY_CONTEXT_REPETITIONS_INVALID")
        repetition_ids = [
            repetition.repetition_id for repetition in repetitions
        ]
        if len(repetition_ids) != len(set(repetition_ids)):
            raise ReplayContextError("REPLAY_CONTEXT_REPETITION_IDS_DUPLICATE")
        gesture_counts = {
            gesture_id: sum(
                repetition.gesture_id == gesture_id
                for repetition in repetitions
            )
            for gesture_id in _GESTURE_IDS
        }
        if any(count != 3 for count in gesture_counts.values()):
            raise ReplayContextError(
                "REPLAY_CONTEXT_REPETITION_COVERAGE_INVALID"
            )
        for repetition in repetitions:
            if repetition.source_hash_sha256 != self.source_hash_sha256:
                raise ReplayContextError(
                    "REPLAY_CONTEXT_REPETITION_SOURCE_HASH_MISMATCH"
                )
            if repetition.channel_ids != channels:
                raise ReplayContextError(
                    "REPLAY_CONTEXT_REPETITION_CHANNELS_MISMATCH"
                )
            if not math.isclose(
                repetition.start_time_s,
                repetition.start_sample / sampling_rate,
                rel_tol=0.0,
                abs_tol=1e-9,
            ) or not math.isclose(
                repetition.end_time_exclusive_s,
                repetition.end_sample_exclusive / sampling_rate,
                rel_tol=0.0,
                abs_tol=1e-9,
            ):
                raise ReplayContextError(
                    "REPLAY_CONTEXT_REPETITION_TIME_SAMPLE_MISMATCH"
                )
        for gesture_id in _GESTURE_IDS:
            if not any(
                repetition.gesture_id == gesture_id
                and repetition.quality == "accepted"
                for repetition in repetitions
            ):
                raise ReplayContextError(
                    "REPLAY_CONTEXT_ACCEPTED_REPETITION_MISSING"
                )

        rest_rms = _require_real(
            self.rest_rms_uv,
            code="REPLAY_CONTEXT_REST_RMS_INVALID",
            minimum=0.0,
        )
        rest_sigma = _require_real(
            self.rest_sigma_uv,
            code="REPLAY_CONTEXT_REST_SIGMA_INVALID",
            minimum=0.0,
        )
        engineering_k = _require_real(
            self.engineering_k,
            code="REPLAY_CONTEXT_ENGINEERING_K_INVALID",
            exclusive_minimum=0.0,
        )
        release_ratio = _require_real(
            self.release_ratio,
            code="REPLAY_CONTEXT_RELEASE_RATIO_INVALID",
            exclusive_minimum=0.0,
        )
        uncertain_ratio = _require_real(
            self.uncertain_band_ratio,
            code="REPLAY_CONTEXT_UNCERTAIN_BAND_INVALID",
            minimum=0.0,
        )
        if release_ratio >= 1.0:
            raise ReplayContextError("REPLAY_CONTEXT_RELEASE_RATIO_INVALID")
        if uncertain_ratio >= 1.0:
            raise ReplayContextError("REPLAY_CONTEXT_UNCERTAIN_BAND_INVALID")

        if isinstance(self.latency_components_ms, (str, bytes)):
            raise ReplayContextError("REPLAY_CONTEXT_LATENCY_INVALID")
        try:
            latency = tuple(self.latency_components_ms)
        except TypeError as exc:
            raise ReplayContextError("REPLAY_CONTEXT_LATENCY_INVALID") from exc
        if len(latency) != 5:
            raise ReplayContextError("REPLAY_CONTEXT_LATENCY_INVALID")
        try:
            total_latency_ms(*latency)
        except ValueError as exc:
            raise ReplayContextError("REPLAY_CONTEXT_LATENCY_INVALID") from exc

        fatigue_reasons = _require_optional_codes(
            self.upstream_fatigue_reason_codes,
            code="REPLAY_CONTEXT_FATIGUE_REASONS_INVALID",
        )
        quality_reasons = _require_optional_codes(
            self.upstream_quality_reason_codes,
            code="REPLAY_CONTEXT_QUALITY_REASONS_INVALID",
        )
        if self.upstream_fatigue_status not in _FATIGUE_PRIORITY:
            raise ReplayContextError("REPLAY_CONTEXT_FATIGUE_STATUS_INVALID")
        if self.upstream_quality_status not in _QUALITY_PRIORITY:
            raise ReplayContextError("REPLAY_CONTEXT_QUALITY_STATUS_INVALID")

        if self.protocol_version is not None:
            _require_string(
                self.protocol_version,
                code="REPLAY_CONTEXT_PROTOCOL_VERSION_INVALID",
            )
        if self.quality_result_id is not None:
            _require_string(
                self.quality_result_id,
                code="REPLAY_CONTEXT_QUALITY_RESULT_ID_INVALID",
            )

        object.__setattr__(self, "sampling_rate_hz", sampling_rate)
        object.__setattr__(self, "channel_ids", channels)
        object.__setattr__(self, "repetitions", repetitions)
        object.__setattr__(self, "rest_rms_uv", rest_rms)
        object.__setattr__(self, "rest_sigma_uv", rest_sigma)
        object.__setattr__(self, "engineering_k", engineering_k)
        object.__setattr__(self, "release_ratio", release_ratio)
        object.__setattr__(self, "uncertain_band_ratio", uncertain_ratio)
        object.__setattr__(self, "latency_components_ms", latency)
        object.__setattr__(
            self,
            "upstream_fatigue_reason_codes",
            fatigue_reasons,
        )
        object.__setattr__(
            self,
            "upstream_quality_reason_codes",
            quality_reasons,
        )

def _require_optional_codes(values: object, *, code: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ReplayContextError(code)
    try:
        items = tuple(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ReplayContextError(code) from exc
    if any(not isinstance(item, str) or not item.strip() for item in items):
        raise ReplayContextError(code)
    return tuple(dict.fromkeys(items))


@dataclass(frozen=True, slots=True)
class GestureSegmentRef:
    """Exact half-open signal window reference; never contains raw samples."""

    raw_signal_ref: str
    source_hash_sha256: str
    start_sample: int
    end_sample_exclusive: int
    start_time_s: float
    end_time_exclusive_s: float
    channel_ids: tuple[str, ...]
    repetition_id: str
    calibration_id: str

    def __post_init__(self) -> None:
        if not _SHA256_PATTERN.fullmatch(self.source_hash_sha256):
            raise ReplayContextError("SEGMENT_SOURCE_HASH_INVALID")
        if self.start_sample < 0 or self.end_sample_exclusive <= self.start_sample:
            raise ReplayContextError("SEGMENT_SAMPLE_RANGE_INVALID")
        if (
            not math.isfinite(self.start_time_s)
            or not math.isfinite(self.end_time_exclusive_s)
            or self.start_time_s < 0.0
            or self.end_time_exclusive_s <= self.start_time_s
        ):
            raise ReplayContextError("SEGMENT_TIME_RANGE_INVALID")
        _require_string(self.raw_signal_ref, code="SEGMENT_RAW_SIGNAL_REF_INVALID")
        _require_string(self.repetition_id, code="SEGMENT_REPETITION_ID_INVALID")
        _require_string(self.calibration_id, code="SEGMENT_CALIBRATION_ID_INVALID")
        _require_string_tuple(
            self.channel_ids,
            code="SEGMENT_CHANNEL_IDS_INVALID",
            unique=True,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_signal_ref": self.raw_signal_ref,
            "source_hash_sha256": self.source_hash_sha256,
            "start_sample": self.start_sample,
            "end_sample_exclusive": self.end_sample_exclusive,
            "start_time_s": self.start_time_s,
            "end_time_exclusive_s": self.end_time_exclusive_s,
            "channel_ids": list(self.channel_ids),
            "repetition_id": self.repetition_id,
            "calibration_id": self.calibration_id,
        }


@dataclass(frozen=True, slots=True)
class LatencyBreakdown:
    """Latency components for one replay window."""

    acquisition_ms: float
    window_ms: float
    preprocess_ms: float
    inference_ms: float
    transport_render_ms: float
    total_ms: float

    @classmethod
    def from_components(
        cls,
        components_ms: tuple[float, float, float, float, float],
    ) -> LatencyBreakdown:
        acquisition, window, preprocess, inference, render = components_ms
        return cls(
            acquisition_ms=acquisition,
            window_ms=window,
            preprocess_ms=preprocess,
            inference_ms=inference,
            transport_render_ms=render,
            total_ms=total_latency_ms(*components_ms),
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "acquisition_ms": self.acquisition_ms,
            "window_ms": self.window_ms,
            "preprocess_ms": self.preprocess_ms,
            "inference_ms": self.inference_ms,
            "transport_render_ms": self.transport_render_ms,
            "total_ms": self.total_ms,
        }


@dataclass(frozen=True, slots=True)
class QualityOverlay:
    status: QualityStatus
    reason_codes: tuple[str, ...]
    quality_result_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "quality_result_id": self.quality_result_id,
        }


@dataclass(frozen=True, slots=True)
class FatigueOverlay:
    status: FatigueStatus
    confidence_adjustment_applied: bool
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "confidence_adjustment_applied": self.confidence_adjustment_applied,
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True, slots=True)
class GestureInferenceWindow:
    """Immutable replay output for one exact signal window."""

    window_id: str
    session_id: str
    analysis_id: str
    segment_ref: GestureSegmentRef
    target_gesture: GestureId
    activity_gate: ActivityGateResult
    predicted_gesture: GestureId | None
    base_engineering_confidence: ConfidenceCategory
    engineering_confidence: ConfidenceCategory
    latency: LatencyBreakdown
    fatigue_overlay: FatigueOverlay
    quality_overlay: QualityOverlay
    device_state: DeviceState
    engine_id: str
    engine_version: str
    model_version: str
    source_type: str
    protocol_version: str | None
    result_hash_sha256: str
    model_validation_status: Literal["not_validated"] = "not_validated"
    requires_human_review: Literal[True] = True
    clinical_use_allowed: Literal[False] = False
    raw_samples_included: Literal[False] = False
    physical_actuation_allowed: Literal[False] = False

    def to_dict(self) -> dict[str, Any]:
        payload = self._hash_payload()
        payload["result_hash_sha256"] = self.result_hash_sha256
        return payload

    def _hash_payload(self) -> dict[str, Any]:
        return {
            "window_id": self.window_id,
            "session_id": self.session_id,
            "analysis_id": self.analysis_id,
            "segment_ref": self.segment_ref.to_dict(),
            "target_gesture": self.target_gesture,
            "activity_gate": {
                "status": self.activity_gate.status,
                "window_rms_uv": self.activity_gate.window_rms_uv,
                "activation_threshold_uv": (
                    self.activity_gate.activation_threshold_uv
                ),
                "release_threshold_uv": self.activity_gate.release_threshold_uv,
                "reason_code": self.activity_gate.reason_code,
            },
            "predicted_gesture": self.predicted_gesture,
            "base_engineering_confidence": self.base_engineering_confidence,
            "engineering_confidence": self.engineering_confidence,
            "latency": self.latency.to_dict(),
            "fatigue_overlay": self.fatigue_overlay.to_dict(),
            "quality_overlay": self.quality_overlay.to_dict(),
            "device_state": self.device_state,
            "engine_id": self.engine_id,
            "engine_version": self.engine_version,
            "model_version": self.model_version,
            "source_type": self.source_type,
            "protocol_version": self.protocol_version,
            "model_validation_status": self.model_validation_status,
            "requires_human_review": self.requires_human_review,
            "clinical_use_allowed": self.clinical_use_allowed,
            "raw_samples_included": self.raw_samples_included,
            "physical_actuation_allowed": self.physical_actuation_allowed,
        }


@dataclass(frozen=True, slots=True)
class _WindowSpec:
    target_gesture: GestureId
    window_rms_uv: float
    predicted_gesture: GestureId | None
    confidence: ConfidenceCategory
    quality_status: QualityStatus = "pass"
    quality_reason_codes: tuple[str, ...] = ()
    fatigue_status: FatigueStatus = "stable"
    fatigue_reason_codes: tuple[str, ...] = ()
    device_state: DeviceState = "connected"


_SCENARIO_REGISTRY: dict[str, tuple[_WindowSpec, ...]] = {
    "uc1_golden_correct": tuple(
        _WindowSpec(
            target_gesture=gesture,
            window_rms_uv=11.0 + index,
            predicted_gesture=gesture,
            confidence="engineering_high",
        )
        for index, gesture in enumerate(
            ("hand_open", "hand_close", "wrist_flexion", "wrist_extension")
        )
    ),
    "uc1_ambiguous_prediction": (
        _WindowSpec(
            target_gesture="wrist_extension",
            window_rms_uv=9.0,
            predicted_gesture="hand_open",
            confidence="engineering_low",
        ),
    ),
    "uc1_no_activity": (
        _WindowSpec(
            target_gesture="wrist_extension",
            window_rms_uv=4.5,
            predicted_gesture=None,
            confidence="not_available",
        ),
    ),
    "uc1_fatigue_confidence_drop": (
        _WindowSpec(
            target_gesture="wrist_extension",
            window_rms_uv=12.0,
            predicted_gesture="wrist_extension",
            confidence="engineering_high",
        ),
        _WindowSpec(
            target_gesture="wrist_extension",
            window_rms_uv=13.0,
            predicted_gesture="wrist_extension",
            confidence="engineering_high",
            fatigue_status="warning",
            fatigue_reason_codes=(
                "MDF_DECLINE_OBSERVED",
                "CONFIDENCE_DOWNGRADED",
            ),
        ),
    ),
    "uc1_electrode_shift_warning": (
        _WindowSpec(
            target_gesture="wrist_extension",
            window_rms_uv=11.0,
            predicted_gesture="wrist_extension",
            confidence="engineering_moderate",
            quality_status="warning",
            quality_reason_codes=("ELECTRODE_SHIFT_SUSPECTED",),
        ),
    ),
    "uc1_qc_fail_abstention": (
        _WindowSpec(
            target_gesture="wrist_extension",
            window_rms_uv=12.0,
            predicted_gesture=None,
            confidence="not_available",
            quality_status="fail",
            quality_reason_codes=("SIGNAL_QUALITY_NOT_SUFFICIENT",),
            fatigue_status="not_available",
        ),
    ),
    "uc1_device_disconnect": (
        _WindowSpec(
            target_gesture="wrist_extension",
            window_rms_uv=12.0,
            predicted_gesture="wrist_extension",
            confidence="engineering_high",
        ),
        _WindowSpec(
            target_gesture="wrist_extension",
            window_rms_uv=0.0,
            predicted_gesture=None,
            confidence="not_available",
            fatigue_status="not_available",
            device_state="disconnected",
        ),
    ),
}

SCENARIO_IDS = frozenset(_SCENARIO_REGISTRY)


def _higher_priority_quality(
    left: QualityStatus,
    right: QualityStatus,
) -> QualityStatus:
    return left if _QUALITY_PRIORITY[left] >= _QUALITY_PRIORITY[right] else right


def _higher_priority_fatigue(
    left: FatigueStatus,
    right: FatigueStatus,
) -> FatigueStatus:
    return left if _FATIGUE_PRIORITY[left] >= _FATIGUE_PRIORITY[right] else right


def _cap_confidence(
    confidence: ConfidenceCategory,
    cap: ConfidenceCategory,
) -> ConfidenceCategory:
    return confidence if _CONFIDENCE_RANK[confidence] <= _CONFIDENCE_RANK[cap] else cap


def _build_quality_overlay(
    context: ReplayContext,
    spec: _WindowSpec,
) -> QualityOverlay:
    status = _higher_priority_quality(
        context.upstream_quality_status,
        spec.quality_status,
    )
    return QualityOverlay(
        status=status,
        reason_codes=_deduplicate_codes(
            context.upstream_quality_reason_codes,
            spec.quality_reason_codes,
        ),
        quality_result_id=context.quality_result_id,
    )


def _build_fatigue_overlay(
    context: ReplayContext,
    spec: _WindowSpec,
) -> FatigueOverlay:
    status = _higher_priority_fatigue(
        context.upstream_fatigue_status,
        spec.fatigue_status,
    )
    return FatigueOverlay(
        status=status,
        confidence_adjustment_applied=status in {"warning", "abstain"},
        reason_codes=_deduplicate_codes(
            context.upstream_fatigue_reason_codes,
            spec.fatigue_reason_codes,
        ),
    )


def _segment_ref(
    context: ReplayContext,
    repetition: ReplayRepetition,
) -> GestureSegmentRef:
    return GestureSegmentRef(
        raw_signal_ref=repetition.raw_signal_ref,
        source_hash_sha256=repetition.source_hash_sha256,
        start_sample=repetition.start_sample,
        end_sample_exclusive=repetition.end_sample_exclusive,
        start_time_s=repetition.start_time_s,
        end_time_exclusive_s=repetition.end_time_exclusive_s,
        channel_ids=repetition.channel_ids,
        repetition_id=repetition.repetition_id,
        calibration_id=context.calibration_id,
    )

def _finalize_window(
    *,
    context: ReplayContext,
    spec: _WindowSpec,
    repetition: ReplayRepetition,
    index: int,
    gate: ActivityGateResult,
) -> GestureInferenceWindow:
    quality = _build_quality_overlay(context, spec)
    fatigue = _build_fatigue_overlay(context, spec)
    predicted = spec.predicted_gesture
    confidence = spec.confidence

    blocking = (
        gate.status != "active"
        or quality.status == "fail"
        or fatigue.status == "abstain"
        or spec.device_state == "disconnected"
    )
    if blocking:
        predicted = None
        confidence = "not_available"
    else:
        if fatigue.status == "warning":
            confidence = _cap_confidence(
                confidence,
                "engineering_moderate",
            )
        if quality.status == "warning":
            confidence = _cap_confidence(
                confidence,
                "engineering_moderate",
            )

    segment = _segment_ref(context, repetition)
    base_fields: dict[str, Any] = {
        "window_id": f"{context.analysis_id}-W{index + 1:04d}",
        "session_id": context.session_id,
        "analysis_id": context.analysis_id,
        "segment_ref": segment,
        "target_gesture": spec.target_gesture,
        "activity_gate": gate,
        "predicted_gesture": predicted,
        "base_engineering_confidence": spec.confidence,
        "engineering_confidence": confidence,
        "latency": LatencyBreakdown.from_components(
            context.latency_components_ms
        ),
        "fatigue_overlay": fatigue,
        "quality_overlay": quality,
        "device_state": spec.device_state,
        "engine_id": context.engine_id,
        "engine_version": context.engine_version,
        "model_version": context.model_version,
        "source_type": context.source_type,
        "protocol_version": context.protocol_version,
    }
    provisional = GestureInferenceWindow(
        **base_fields,
        result_hash_sha256="",
    )
    result_hash = canonical_result_hash(provisional._hash_payload())
    return GestureInferenceWindow(
        **base_fields,
        result_hash_sha256=result_hash,
    )


def build_replay_windows(
    *,
    context: ReplayContext,
    scenario_id: str,
) -> tuple[GestureInferenceWindow, ...]:
    """Build deterministic typed windows for one registered scenario."""

    try:
        specs = _SCENARIO_REGISTRY[scenario_id]
    except (KeyError, TypeError) as exc:
        raise ReplayScenarioError(
            f"UNKNOWN_REPLAY_SCENARIO:{scenario_id}"
        ) from exc

    windows: list[GestureInferenceWindow] = []
    occurrence_by_gesture: dict[GestureId, int] = {}
    previous_active = False
    for index, spec in enumerate(specs):
        accepted_repetitions = tuple(
            repetition
            for repetition in context.repetitions
            if repetition.gesture_id == spec.target_gesture
            and repetition.quality == "accepted"
        )
        occurrence = occurrence_by_gesture.get(spec.target_gesture, 0)
        try:
            repetition = accepted_repetitions[occurrence]
        except IndexError as exc:
            raise ReplayContextError(
                "REPLAY_CONTEXT_ACCEPTED_REPETITIONS_INSUFFICIENT"
            ) from exc
        occurrence_by_gesture[spec.target_gesture] = occurrence + 1
        gate = evaluate_activity(
            spec.window_rms_uv,
            rest_rms_uv=context.rest_rms_uv,
            rest_sigma_uv=context.rest_sigma_uv,
            engineering_k=context.engineering_k,
            previous_active=previous_active,
            release_ratio=context.release_ratio,
            uncertain_band_ratio=context.uncertain_band_ratio,
        )
        windows.append(
            _finalize_window(
                context=context,
                spec=spec,
                repetition=repetition,
                index=index,
                gate=gate,
            )
        )
        previous_active = gate.status == "active"
    return tuple(windows)


__all__ = [
    "FatigueOverlay",
    "GestureInferenceWindow",
    "GestureSegmentRef",
    "LatencyBreakdown",
    "QualityOverlay",
    "ReplayContext",
    "ReplayContextError",
    "ReplayEngineError",
    "ReplayRepetition",
    "ReplayScenarioError",
    "SCENARIO_IDS",
    "build_replay_windows",
    "canonical_result_hash",
]
