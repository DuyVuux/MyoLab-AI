"""Pure deterministic activity-gating utilities for UC1 gesture replay.

The threshold is personalized from a session's rest calibration.  These
utilities expose engineering states and reason codes only; they do not make a
clinical claim about effort, fatigue, or patient intent.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real
from typing import Literal


ActivityStatus = Literal["active", "inactive", "uncertain"]


class ActivityGateError(ValueError):
    """Stable typed error raised for invalid activity-gate inputs."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class ActivityGateResult:
    """Engineering activity decision for one signal window."""

    status: ActivityStatus
    window_rms_uv: float
    activation_threshold_uv: float
    release_threshold_uv: float
    reason_code: str


def _finite_real(value: object, *, error_code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ActivityGateError(error_code)
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ActivityGateError(error_code)
    return numeric


def activity_threshold(
    rest_rms_uv: float,
    rest_sigma_uv: float,
    engineering_k: float = 3.0,
) -> float:
    """Return ``rest_rms_uv + engineering_k * rest_sigma_uv``.

    ``engineering_k`` is a versioned engineering parameter, not a universal
    clinical cut-off.
    """

    raw_values = (rest_rms_uv, rest_sigma_uv, engineering_k)
    if any(isinstance(value, bool) or not isinstance(value, Real) for value in raw_values):
        raise ActivityGateError("ACTIVITY_GATE_INPUT_TYPE_INVALID")

    values = tuple(float(value) for value in raw_values)
    if not all(math.isfinite(value) for value in values):
        raise ActivityGateError("ACTIVITY_GATE_NONFINITE_INPUT")

    rest_rms, rest_sigma, k_value = values
    if rest_rms < 0.0 or rest_sigma < 0.0 or k_value <= 0.0:
        raise ActivityGateError("ACTIVITY_GATE_INPUT_OUT_OF_RANGE")
    return rest_rms + k_value * rest_sigma


def evaluate_activity(
    window_rms_uv: float,
    *,
    rest_rms_uv: float,
    rest_sigma_uv: float,
    engineering_k: float = 3.0,
    previous_active: bool = False,
    release_ratio: float = 0.80,
    uncertain_band_ratio: float = 0.10,
) -> ActivityGateResult:
    """Evaluate one RMS window while carrying the prior hysteresis state.

    Boundaries are intentional:

    - activation is inclusive;
    - release is inclusive while the prior state is active;
    - the lower uncertain-band boundary is inclusive;
    - ``release_ratio`` must be strictly lower than one.
    """

    rms = _finite_real(window_rms_uv, error_code="WINDOW_RMS_INVALID")
    if rms < 0.0:
        raise ActivityGateError("WINDOW_RMS_INVALID")
    if not isinstance(previous_active, bool):
        raise ActivityGateError("PREVIOUS_ACTIVE_INVALID")

    release = _finite_real(release_ratio, error_code="RELEASE_RATIO_INVALID")
    if not 0.0 < release < 1.0:
        raise ActivityGateError("RELEASE_RATIO_INVALID")

    uncertain = _finite_real(
        uncertain_band_ratio,
        error_code="UNCERTAIN_BAND_INVALID",
    )
    if not 0.0 <= uncertain < 1.0:
        raise ActivityGateError("UNCERTAIN_BAND_INVALID")

    activation_threshold = activity_threshold(
        rest_rms_uv,
        rest_sigma_uv,
        engineering_k,
    )
    release_threshold = activation_threshold * release
    uncertain_lower_bound = activation_threshold * (1.0 - uncertain)

    if previous_active and rms >= release_threshold:
        status: ActivityStatus = "active"
        reason_code = "ACTIVITY_HELD_BY_HYSTERESIS"
    elif rms >= activation_threshold:
        status = "active"
        reason_code = "ACTIVITY_ABOVE_THRESHOLD"
    elif rms >= uncertain_lower_bound:
        status = "uncertain"
        reason_code = "ACTIVITY_NEAR_THRESHOLD"
    else:
        status = "inactive"
        reason_code = "NO_ACTIVITY_DETECTED"

    return ActivityGateResult(
        status=status,
        window_rms_uv=rms,
        activation_threshold_uv=activation_threshold,
        release_threshold_uv=release_threshold,
        reason_code=reason_code,
    )


__all__ = [
    "ActivityGateError",
    "ActivityGateResult",
    "ActivityStatus",
    "activity_threshold",
    "evaluate_activity",
]
