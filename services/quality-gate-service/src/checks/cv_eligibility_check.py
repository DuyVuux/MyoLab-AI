"""MFCV/CV capability eligibility gate; no conduction velocity is calculated."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from typing import Any

import numpy as np

from semg_core.io import NormalizedSignal
from semg_core.qc import pearson_correlation

from result_models import CheckResult, MFCVEligibilityResult
from checks.common import active_channel_samples, get_nested


def _as_positive_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed) or parsed <= 0:
        return None
    return parsed


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> tuple[CheckResult, MFCVEligibilityResult]:
    requirements = get_nested(config, "mfcv_eligibility", "requirements", default={})
    electrode = signal.source_manifest.get("electrode_config", {})
    if not isinstance(electrode, Mapping):
        electrode = {}

    reasons: list[str] = []
    linear_array_confirmed = bool(electrode.get("linear_array_confirmed"))
    spacing_mm = _as_positive_float(electrode.get("interelectrode_distance_mm"))
    orientation_confirmed = bool(electrode.get("orientation_along_fibres_confirmed"))
    minimum_channels = int(requirements.get("minimum_adjacent_channels", 3))
    minimum_fs = float(requirements.get("minimum_sampling_rate_hz", 1000.0))
    correlation_threshold = float(
        requirements.get("adjacent_correlation_threshold_reference", 0.75)
    )

    if not linear_array_confirmed:
        reasons.append("MFCV_LINEAR_ARRAY_NOT_CONFIRMED")
    if spacing_mm is None:
        reasons.append("MFCV_INTERELECTRODE_DISTANCE_UNKNOWN")
    if not orientation_confirmed:
        reasons.append("MFCV_ORIENTATION_NOT_CONFIRMED")
    if signal.channel_count < minimum_channels:
        reasons.append("MFCV_INSUFFICIENT_ADJACENT_CHANNELS")
    if signal.sampling_rate_hz < minimum_fs:
        reasons.append("MFCV_SAMPLING_RATE_INSUFFICIENT")

    active = active_channel_samples(signal, protocol)
    configured_order = electrode.get("adjacent_channel_order")
    correlations: list[float] = []
    correlation_evaluated = False
    if (
        not reasons
        and isinstance(configured_order, Sequence)
        and not isinstance(configured_order, (str, bytes))
        and len(configured_order) >= minimum_channels
    ):
        ordered_ids = [str(item) for item in configured_order]
        if all(channel_id in active for channel_id in ordered_ids):
            correlation_evaluated = True
            for left_id, right_id in zip(ordered_ids, ordered_ids[1:]):
                corr = pearson_correlation(active[left_id], active[right_id])
                correlations.append(corr)
            finite_correlations = [value for value in correlations if np.isfinite(value)]
            if (
                not finite_correlations
                or min(finite_correlations) < correlation_threshold
            ):
                reasons.append("MFCV_ADJACENT_CORRELATION_LOW")

    if not reasons and not correlation_evaluated:
        # Metadata may claim an array but channel order is still needed before
        # treating adjacent correlation as checked.
        reasons.append("MFCV_ADJACENT_CORRELATION_LOW")

    reasons = list(dict.fromkeys(reasons))
    eligible = not reasons
    details = {
        "capability_only": True,
        "linear_array_confirmed": linear_array_confirmed,
        "interelectrode_distance_mm": spacing_mm,
        "orientation_along_fibres_confirmed": orientation_confirmed,
        "channel_count": signal.channel_count,
        "minimum_adjacent_channels": minimum_channels,
        "sampling_rate_hz": float(signal.sampling_rate_hz),
        "minimum_sampling_rate_hz": minimum_fs,
        "adjacent_correlation_threshold_reference": correlation_threshold,
        "adjacent_correlation_evaluated": correlation_evaluated,
        "adjacent_correlations": [value if math.isfinite(value) else None for value in correlations],
        "threshold_status": "research_reference_not_clinically_validated",
        "cv_calculated": False,
    }
    check = CheckResult(
        check_id="mfcv_eligibility",
        status="pass" if eligible else "not_applicable",
        severity="info",
        reason_codes=tuple(reasons),
        details=details,
    )
    return check, MFCVEligibilityResult(eligible=eligible, reason_codes=tuple(reasons))
