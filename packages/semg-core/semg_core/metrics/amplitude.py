"""DAY46 deterministic RMS/MAV metrics with fail-closed eligibility and provenance."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json
from typing import Any, Mapping
import numpy as np

FORMULA_VERSIONS = {
    "RMS": "rms-v1",
    "MAV": "mav-v1",
}


@dataclass(frozen=True, slots=True)
class AmplitudeMetricResult:
    metric_id: str
    metric_name: str
    formula_version: str
    value: float | None
    units: str | None
    status: str
    reason_codes: tuple[str, ...]
    provenance: Mapping[str, Any]


def _canon(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _id(payload: Mapping[str, Any]) -> str:
    return "metric_sha256_" + hashlib.sha256(_canon(payload)).hexdigest()


def _extract_manifest_dict(pm: Any) -> dict[str, Any] | None:
    if pm is None:
        return None
    if is_dataclass(pm) and hasattr(pm, "to_dict"):
        return pm.to_dict()
    if is_dataclass(pm):
        return asdict(pm)
    if isinstance(pm, Mapping):
        return dict(pm)
    return None


def evaluate_amplitude_metric(
    *,
    metric_name: str,
    values: np.ndarray,
    units: str,
    processing_permission: str,
    qc_signal_quality: str | None,
    mask: np.ndarray,
    processing_manifest: Any,
) -> AmplitudeMetricResult:
    """Evaluate deterministic RMS or MAV metric with fail-closed provenance gates."""
    if metric_name not in FORMULA_VERSIONS:
        raise ValueError("UNSUPPORTED_METRIC")

    x = np.asarray(values, dtype=float)
    m = np.asarray(mask, dtype=bool)

    reasons: list[str] = []

    if processing_permission != "ALLOW_PROFILED_PROCESSING":
        reasons.append("METRIC_NOT_ELIGIBLE")
    if qc_signal_quality == "FAIL":
        reasons.append("QC_FAIL_BLOCKS_METRIC")
    if x.ndim != 1 or m.shape != x.shape:
        reasons.append("INVALID_SIGNAL_OR_MASK_SHAPE")
    elif m.any():
        reasons.append("MASKED_WINDOW_EXCLUDED_FROM_METRIC")
    if x.size == 0:
        reasons.append("INSUFFICIENT_SAMPLES")
    if x.size > 0 and not np.isfinite(x).all():
        reasons.append("NONFINITE_INPUT")

    pm_dict = _extract_manifest_dict(processing_manifest)
    required_keys = ["manifest_id", "processing_run_id", "final_artifact", "window", "profile"]
    if pm_dict is None or any(k not in pm_dict or pm_dict[k] is None for k in required_keys):
        reasons.append("PROCESSING_PROVENANCE_INCOMPLETE")

    if reasons:
        sorted_reasons = tuple(sorted(set(reasons)))
        payload = {
            "metric_name": metric_name,
            "formula_version": FORMULA_VERSIONS[metric_name],
            "manifest_id": pm_dict.get("manifest_id") if pm_dict else None,
            "status": "UNAVAILABLE",
            "reason_codes": list(sorted_reasons),
        }
        return AmplitudeMetricResult(
            metric_id=_id(payload),
            metric_name=metric_name,
            formula_version=FORMULA_VERSIONS[metric_name],
            value=None,
            units=None,
            status="UNAVAILABLE",
            reason_codes=sorted_reasons,
            provenance=payload,
        )

    if metric_name == "RMS":
        value = float(np.sqrt(np.mean(np.square(x))))
    else:
        value = float(np.mean(np.abs(x)))

    final_artifact = pm_dict["final_artifact"]
    artifact_id = final_artifact.get("artifact_id") if isinstance(final_artifact, dict) else getattr(final_artifact, "artifact_id", None)

    window = pm_dict["window"]
    window_id = window.get("window_id") if isinstance(window, dict) else getattr(window, "window_id", None)

    profile = pm_dict["profile"]
    profile_id = profile.get("profile_id") if isinstance(profile, dict) else getattr(profile, "profile_id", None)
    config_fingerprint = profile.get("config_fingerprint") if isinstance(profile, dict) else getattr(profile, "config_fingerprint", None)

    prov = {
        "manifest_id": pm_dict["manifest_id"],
        "processing_run_id": pm_dict["processing_run_id"],
        "processed_artifact_id": artifact_id,
        "window_id": window_id,
        "profile_id": profile_id,
        "profile_fingerprint": config_fingerprint,
        "formula_version": FORMULA_VERSIONS[metric_name],
        "sample_count": int(x.size),
        "input_units": units,
        "distribution_fingerprint_role": "MONITORING_RESEARCH_ONLY",
    }
    payload = {
        "metric_name": metric_name,
        "value": value,
        "units": units,
        "provenance": prov,
    }
    return AmplitudeMetricResult(
        metric_id=_id(payload),
        metric_name=metric_name,
        formula_version=FORMULA_VERSIONS[metric_name],
        value=value,
        units=units,
        status="AVAILABLE",
        reason_codes=(),
        provenance=prov,
    )
