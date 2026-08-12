"""DAY40 processing-profile contract and deterministic runtime binding.

This module intentionally does not implement signal filters. It validates versioned
preprocessing profiles, computes deterministic fingerprints, and enforces the frozen
QC-to-processing authorization boundary before later DAY41+ DSP implementations run.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping


FINGERPRINT_PREFIX = "pprof_sha256_"
FINGERPRINT_ALGORITHM = "sha256-canonical-json-v1"
ALLOW_PROFILED_PROCESSING = "ALLOW_PROFILED_PROCESSING"


class ProcessingProfileError(ValueError):
    """Base typed error for DAY40 profile-contract failures."""


class ProcessingProfileConfigurationError(ProcessingProfileError):
    """Raised when a profile is internally contradictory or under-specified."""


class ProcessingProfileAuthorizationError(ProcessingProfileError):
    """Raised when upstream QC/eligibility forbids automatic processing."""


class ProcessingProfileRuntimeError(ProcessingProfileError):
    """Raised when runtime signal context cannot support a declared profile."""


@dataclass(frozen=True)
class RuntimeSignalContext:
    sampling_rate_hz: float
    units: str
    source_window_id: str
    source_id: str
    partition: str
    processing_permission: str
    distribution_support_status: str
    protocol_context_ref: str | None = None
    domain_context_ref: str | None = None

    def __post_init__(self) -> None:
        if self.sampling_rate_hz <= 0:
            raise ProcessingProfileRuntimeError("SAMPLING_RATE_REQUIRED_POSITIVE")
        if not self.units:
            raise ProcessingProfileRuntimeError("INPUT_UNIT_REQUIRED")
        if not self.source_window_id:
            raise ProcessingProfileRuntimeError("SOURCE_WINDOW_ID_REQUIRED")
        if not self.source_id:
            raise ProcessingProfileRuntimeError("SOURCE_ID_REQUIRED")
        if not self.partition:
            raise ProcessingProfileRuntimeError("PARTITION_REQUIRED")


@dataclass(frozen=True)
class ProfileBindingResult:
    profile_id: str
    profile_version: str
    config_fingerprint: str
    source_window_id: str
    native_fs_hz: float
    processed_fs_hz: float
    input_unit: str
    output_unit: str
    is_resampled: bool
    distribution_support_status: str
    effect_summary: Mapping[str, Any]


def _canonicalize(value: Any) -> Any:
    """Return a JSON-safe canonical structure for deterministic hashing."""

    if isinstance(value, Mapping):
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    return value


def canonical_profile_payload(profile: Mapping[str, Any]) -> dict[str, Any]:
    """Canonicalize profile content excluding its self-referential fingerprint."""

    payload = deepcopy(dict(profile))
    payload.pop("config_fingerprint", None)
    return _canonicalize(payload)


def compute_profile_fingerprint(profile: Mapping[str, Any]) -> str:
    payload = canonical_profile_payload(profile)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return FINGERPRINT_PREFIX + hashlib.sha256(encoded).hexdigest()


def _require_disabled_step_nulls(step: Mapping[str, Any], fields: tuple[str, ...]) -> None:
    if step.get("enabled") is False:
        for field in fields:
            if step.get(field) is not None:
                raise ProcessingProfileConfigurationError(
                    f"{step.get('step_id')} disabled step must keep {field}=null"
                )
        if step.get("parameter_origin") != "NOT_APPLICABLE":
            raise ProcessingProfileConfigurationError(
                f"{step.get('step_id')} disabled step must use NOT_APPLICABLE"
            )


def validate_profile_semantics(profile: Mapping[str, Any]) -> None:
    """Apply semantic invariants that JSON Schema cannot express cleanly."""

    if profile.get("claim_scope") != "RESEARCH_ONLY":
        raise ProcessingProfileConfigurationError("DAY40 claim_scope must be RESEARCH_ONLY")
    if profile.get("site_binding") is not None:
        raise ProcessingProfileConfigurationError("DAY40 forbids site-specific profile binding")

    execution = profile.get("execution_policy", {})
    if execution.get("automatic_processing_permission") != ALLOW_PROFILED_PROCESSING:
        raise ProcessingProfileConfigurationError(
            "automatic processing must inherit DAY31 ALLOW_PROFILED_PROCESSING"
        )
    if execution.get("locked_partition_fitting_allowed") is not False:
        raise ProcessingProfileConfigurationError("NO_LOCKED_SET_FITTING")
    if execution.get("adaptive_processing_allowed") is not False:
        raise ProcessingProfileConfigurationError("adaptive processing is disabled in DAY40")

    input_contract = profile.get("input_contract", {})
    if input_contract.get("sampling_rate_source") != "RUNTIME_REQUIRED":
        raise ProcessingProfileConfigurationError("NO_SILENT_DEFAULT_FS")
    if input_contract.get("unit_source") != "RUNTIME_REQUIRED":
        raise ProcessingProfileConfigurationError("INPUT_UNIT_MUST_BE_EXPLICIT")

    steps = profile.get("steps", {})
    bandpass = steps.get("bandpass", {})
    notch = steps.get("notch", {})
    rectification = steps.get("rectification", {})
    smoothing = steps.get("smoothing", {})
    normalization = steps.get("normalization", {})
    resampling = profile.get("grid", {}).get("resampling", {})

    _require_disabled_step_nulls(
        bandpass,
        ("method", "low_cut_hz", "high_cut_hz", "filter_order", "phase_mode"),
    )
    _require_disabled_step_nulls(
        notch,
        ("method", "mains_frequency_hz", "q_factor", "bandwidth_hz"),
    )
    _require_disabled_step_nulls(
        resampling,
        ("target_fs_hz", "method", "anti_aliasing_policy"),
    )

    if bandpass.get("enabled"):
        low_cut = float(bandpass["low_cut_hz"])
        high_cut = float(bandpass["high_cut_hz"])
        if low_cut >= high_cut:
            raise ProcessingProfileConfigurationError(
                "bandpass low_cut_hz must be lower than high_cut_hz"
            )

    if notch.get("enabled"):
        if notch.get("mains_frequency_hz") is None:
            raise ProcessingProfileConfigurationError("NO_SILENT_DEFAULT_MAINS_FREQUENCY")
        q_set = notch.get("q_factor") is not None
        bw_set = notch.get("bandwidth_hz") is not None
        if q_set == bw_set:
            raise ProcessingProfileConfigurationError(
                "enabled notch requires exactly one of q_factor or bandwidth_hz"
            )

    if rectification.get("enabled") is False and rectification.get("method") != "NONE":
        raise ProcessingProfileConfigurationError("disabled rectification must use NONE")

    if smoothing.get("enabled") is False:
        if smoothing.get("method") != "NONE":
            raise ProcessingProfileConfigurationError("disabled smoothing must use NONE")
        for field in ("window_ms", "cutoff_hz", "filter_order"):
            if smoothing.get(field) is not None:
                raise ProcessingProfileConfigurationError(
                    f"disabled smoothing must keep {field}=null"
                )

    if normalization.get("fitting_allowed") is not False:
        raise ProcessingProfileConfigurationError("normalization fitting forbidden in DAY40")
    if normalization.get("enabled") is False:
        if normalization.get("method") != "NONE":
            raise ProcessingProfileConfigurationError("disabled normalization must use NONE")
        if normalization.get("reference_id") is not None:
            raise ProcessingProfileConfigurationError(
                "disabled normalization must not carry a reference"
            )

    mask_policy = profile.get("mask_policy", {})
    if mask_policy.get("delete_masked_samples") is not False:
        raise ProcessingProfileConfigurationError("MASK_NOT_DELETE")
    if mask_policy.get("raw_deleted") is not False:
        raise ProcessingProfileConfigurationError("RAW_IS_IMMUTABLE")

    expected = compute_profile_fingerprint(profile)
    if profile.get("config_fingerprint") != expected:
        raise ProcessingProfileConfigurationError(
            "CONFIG_FINGERPRINT_MISMATCH"
        )


def validate_catalog_semantics(catalog: Mapping[str, Any]) -> None:
    if catalog.get("fingerprint_algorithm") != FINGERPRINT_ALGORITHM:
        raise ProcessingProfileConfigurationError("unsupported fingerprint algorithm")
    if catalog.get("claim_scope") != "RESEARCH_ONLY":
        raise ProcessingProfileConfigurationError("catalog claim scope must be RESEARCH_ONLY")

    identities: set[tuple[str, str]] = set()
    for profile in catalog.get("profiles", []):
        identity = (str(profile.get("profile_id")), str(profile.get("version")))
        if identity in identities:
            raise ProcessingProfileConfigurationError(
                f"duplicate processing profile identity: {identity}"
            )
        identities.add(identity)
        validate_profile_semantics(profile)


def bind_profile_to_runtime(
    profile: Mapping[str, Any],
    runtime: RuntimeSignalContext,
) -> ProfileBindingResult:
    """Validate profile against runtime signal/QC context without applying DSP."""

    validate_profile_semantics(profile)

    if runtime.processing_permission != ALLOW_PROFILED_PROCESSING:
        raise ProcessingProfileAuthorizationError(
            f"PROCESSING_NOT_AUTHORIZED:{runtime.processing_permission}"
        )

    allowed_units = profile["input_contract"]["allowed_units"]
    if runtime.units not in allowed_units:
        raise ProcessingProfileRuntimeError(
            f"INPUT_UNIT_UNSUPPORTED:{runtime.units}"
        )

    required_fields = set(profile["protocol_binding"]["required_runtime_fields"])
    runtime_values = {
        "sampling_rate_hz": runtime.sampling_rate_hz,
        "units": runtime.units,
        "source_window_id": runtime.source_window_id,
        "source_id": runtime.source_id,
        "protocol_context_ref": runtime.protocol_context_ref,
        "domain_context_ref": runtime.domain_context_ref,
    }
    for field in required_fields:
        value = runtime_values[field]
        if value is None or value == "":
            raise ProcessingProfileRuntimeError(f"RUNTIME_FIELD_REQUIRED:{field}")

    distribution_required = profile["execution_policy"]["distribution_support_required"]
    if distribution_required:
        if runtime.distribution_support_status == "SHIFTED":
            raise ProcessingProfileAuthorizationError("DISTRIBUTION_SHIFT_REVIEW_REQUIRED")
        if runtime.distribution_support_status in {"UNKNOWN", "NOT_EVALUATED"}:
            raise ProcessingProfileAuthorizationError("DISTRIBUTION_SUPPORT_ABSTAIN")
        if runtime.distribution_support_status != "SUPPORTED":
            raise ProcessingProfileAuthorizationError("DISTRIBUTION_SUPPORT_INVALID")

    native_fs = float(runtime.sampling_rate_hz)
    nyquist = native_fs / 2.0
    bandpass = profile["steps"]["bandpass"]
    notch = profile["steps"]["notch"]
    smoothing = profile["steps"]["smoothing"]
    resampling = profile["grid"]["resampling"]

    if bandpass["enabled"] and float(bandpass["high_cut_hz"]) >= nyquist:
        raise ProcessingProfileRuntimeError("BANDPASS_HIGH_CUT_VIOLATES_NYQUIST")
    if notch["enabled"] and float(notch["mains_frequency_hz"]) >= nyquist:
        raise ProcessingProfileRuntimeError("NOTCH_FREQUENCY_VIOLATES_NYQUIST")
    if smoothing["enabled"] and smoothing["method"] == "BUTTERWORTH_LOWPASS":
        if float(smoothing["cutoff_hz"]) >= nyquist:
            raise ProcessingProfileRuntimeError("SMOOTHING_CUTOFF_VIOLATES_NYQUIST")

    processed_fs = native_fs
    if resampling["enabled"]:
        processed_fs = float(resampling["target_fs_hz"])
        if processed_fs < native_fs:
            if resampling["anti_aliasing_policy"] != "EXPLICIT_FIR_REQUIRED_FOR_DECIMATION":
                raise ProcessingProfileRuntimeError("ANTI_ALIASING_REQUIRED_FOR_DECIMATION")

    normalization = profile["steps"]["normalization"]
    output_unit = runtime.units
    if normalization["enabled"]:
        output_unit = "NORMALIZED_RATIO"

    return ProfileBindingResult(
        profile_id=str(profile["profile_id"]),
        profile_version=str(profile["version"]),
        config_fingerprint=str(profile["config_fingerprint"]),
        source_window_id=runtime.source_window_id,
        native_fs_hz=native_fs,
        processed_fs_hz=processed_fs,
        input_unit=runtime.units,
        output_unit=output_unit,
        is_resampled=bool(resampling["enabled"]),
        distribution_support_status=runtime.distribution_support_status,
        effect_summary=dict(profile["distribution_effect"]),
    )
