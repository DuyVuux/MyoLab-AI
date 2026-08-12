from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
SEMG_CORE = ROOT / "packages" / "semg-core"
if str(SEMG_CORE) not in sys.path:
    sys.path.insert(0, str(SEMG_CORE))

from semg_core.processing.profile_contract import (  # noqa: E402
    ProcessingProfileAuthorizationError,
    ProcessingProfileConfigurationError,
    ProcessingProfileRuntimeError,
    RuntimeSignalContext,
    bind_profile_to_runtime,
    canonical_profile_payload,
    compute_profile_fingerprint,
    validate_catalog_semantics,
    validate_profile_semantics,
)

SCHEMA_PATH = ROOT / "packages/common-schemas/json/processing-profile.schema.json"
CATALOG_PATH = ROOT / "configs/processing/preprocessing-profiles.v0.1.yaml"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_catalog() -> dict:
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))


def profile() -> dict:
    return deepcopy(load_catalog()["profiles"][0])


def refingerprint(value: dict) -> dict:
    value["config_fingerprint"] = compute_profile_fingerprint(value)
    return value


def runtime(**overrides) -> RuntimeSignalContext:
    values = {
        "sampling_rate_hz": 2000.0,
        "units": "uV",
        "source_window_id": "qcw_sha256_" + "a" * 64,
        "source_id": "src_sha256_" + "b" * 64,
        "partition": "benchmark-development",
        "processing_permission": "ALLOW_PROFILED_PROCESSING",
        "distribution_support_status": "SUPPORTED",
        "protocol_context_ref": None,
        "domain_context_ref": None,
    }
    values.update(overrides)
    return RuntimeSignalContext(**values)


def test_01_schema_is_draft_2020_12() -> None:
    assert load_schema()["$schema"].endswith("2020-12/schema")


def test_02_catalog_validates_against_json_schema() -> None:
    jsonschema.Draft202012Validator(load_schema()).validate(load_catalog())


def test_03_catalog_semantics_pass() -> None:
    validate_catalog_semantics(load_catalog())


def test_04_fingerprint_matches_embedded_value() -> None:
    p = profile()
    assert compute_profile_fingerprint(p) == p["config_fingerprint"]


def test_05_fingerprint_is_deterministic() -> None:
    p = profile()
    assert compute_profile_fingerprint(p) == compute_profile_fingerprint(p)


def test_06_fingerprint_ignores_self_field() -> None:
    p = profile()
    original = compute_profile_fingerprint(p)
    p["config_fingerprint"] = "pprof_sha256_" + "0" * 64
    assert compute_profile_fingerprint(p) == original


def test_07_fingerprint_changes_when_semantic_config_changes() -> None:
    p = profile()
    original = compute_profile_fingerprint(p)
    p["description"] = p["description"] + " changed"
    assert compute_profile_fingerprint(p) != original


def test_08_canonical_payload_is_key_order_independent() -> None:
    p = profile()
    reversed_dict = dict(reversed(list(p.items())))
    assert canonical_profile_payload(p) == canonical_profile_payload(reversed_dict)


def test_09_active_profile_has_no_site_binding() -> None:
    assert profile()["site_binding"] is None


def test_10_sampling_rate_is_runtime_required() -> None:
    assert profile()["input_contract"]["sampling_rate_source"] == "RUNTIME_REQUIRED"


def test_11_units_are_runtime_required() -> None:
    assert profile()["input_contract"]["unit_source"] == "RUNTIME_REQUIRED"


def test_12_no_silent_mains_frequency() -> None:
    notch = profile()["steps"]["notch"]
    assert notch["enabled"] is False
    assert notch["mains_frequency_hz"] is None


def test_13_no_silent_resampling_target() -> None:
    resampling = profile()["grid"]["resampling"]
    assert resampling["enabled"] is False
    assert resampling["target_fs_hz"] is None


def test_14_no_legacy_bandpass_default() -> None:
    bandpass = profile()["steps"]["bandpass"]
    assert bandpass["enabled"] is False
    assert bandpass["low_cut_hz"] is None
    assert bandpass["high_cut_hz"] is None


def test_15_locked_partition_fitting_is_forbidden() -> None:
    assert profile()["execution_policy"]["locked_partition_fitting_allowed"] is False


def test_16_adaptive_processing_is_forbidden() -> None:
    assert profile()["execution_policy"]["adaptive_processing_allowed"] is False


def test_17_normalization_fitting_is_forbidden() -> None:
    normalization = profile()["steps"]["normalization"]
    assert normalization["fitting_allowed"] is False


def test_18_mask_is_preserved_and_not_deleted() -> None:
    mask = profile()["mask_policy"]
    assert mask["delete_masked_samples"] is False
    assert mask["preserve_sample_alignment"] is True
    assert mask["raw_deleted"] is False


def test_19_every_declared_step_has_version_and_effect_metadata() -> None:
    p = profile()
    steps = [
        p["grid"]["resampling"],
        p["steps"]["bandpass"],
        p["steps"]["notch"],
        p["steps"]["rectification"],
        p["steps"]["smoothing"],
        p["steps"]["normalization"],
    ]
    for step in steps:
        assert step["step_version"]
        assert step["parameter_origin"]
        assert step["effect"]


def test_20_binding_preserves_native_grid_for_safe_profile() -> None:
    result = bind_profile_to_runtime(profile(), runtime())
    assert result.native_fs_hz == 2000.0
    assert result.processed_fs_hz == 2000.0
    assert result.is_resampled is False


def test_21_binding_preserves_physical_units() -> None:
    result = bind_profile_to_runtime(profile(), runtime(units="V"))
    assert result.input_unit == "V"
    assert result.output_unit == "V"


@pytest.mark.parametrize(
    "permission",
    ["BLOCK_UNSUPPORTED_METRIC", "HOLD_FOR_REVIEW", "ABSTAIN"],
)
def test_22_non_allow_permissions_cannot_bind(permission: str) -> None:
    with pytest.raises(ProcessingProfileAuthorizationError):
        bind_profile_to_runtime(profile(), runtime(processing_permission=permission))


def test_23_missing_or_nonpositive_fs_fails_closed() -> None:
    with pytest.raises(ProcessingProfileRuntimeError):
        runtime(sampling_rate_hz=0.0)


def test_24_missing_units_fail_closed() -> None:
    with pytest.raises(ProcessingProfileRuntimeError):
        runtime(units="")


def test_25_unsupported_unit_fails_closed() -> None:
    with pytest.raises(ProcessingProfileRuntimeError, match="INPUT_UNIT_UNSUPPORTED"):
        bind_profile_to_runtime(profile(), runtime(units="mV"))


def test_26_enabled_bandpass_requires_parameters_schema() -> None:
    catalog = load_catalog()
    p = catalog["profiles"][0]
    p["steps"]["bandpass"]["enabled"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(load_schema()).validate(catalog)


def test_27_enabled_notch_requires_explicit_mains_schema() -> None:
    catalog = load_catalog()
    notch = catalog["profiles"][0]["steps"]["notch"]
    notch["enabled"] = True
    notch["method"] = "IIR_NOTCH"
    notch["q_factor"] = 30.0
    notch["parameter_origin"] = "EXPLICIT_PROFILE"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(load_schema()).validate(catalog)


def test_28_bandpass_low_must_be_lower_than_high() -> None:
    p = profile()
    bp = p["steps"]["bandpass"]
    bp.update({
        "enabled": True,
        "method": "BUTTERWORTH_SOS",
        "low_cut_hz": 200.0,
        "high_cut_hz": 100.0,
        "filter_order": 4,
        "phase_mode": "ZERO_PHASE_OFFLINE",
        "parameter_origin": "ANALYTICAL_RESEARCH",
    })
    refingerprint(p)
    with pytest.raises(ProcessingProfileConfigurationError):
        validate_profile_semantics(p)


def test_29_runtime_nyquist_rejects_bandpass_high_cut() -> None:
    p = profile()
    bp = p["steps"]["bandpass"]
    bp.update({
        "enabled": True,
        "method": "BUTTERWORTH_SOS",
        "low_cut_hz": 10.0,
        "high_cut_hz": 600.0,
        "filter_order": 4,
        "phase_mode": "ZERO_PHASE_OFFLINE",
        "parameter_origin": "ANALYTICAL_RESEARCH",
    })
    refingerprint(p)
    with pytest.raises(ProcessingProfileRuntimeError, match="NYQUIST"):
        bind_profile_to_runtime(p, runtime(sampling_rate_hz=1000.0))


def test_30_runtime_nyquist_rejects_notch_above_nyquist() -> None:
    p = profile()
    notch = p["steps"]["notch"]
    notch.update({
        "enabled": True,
        "method": "IIR_NOTCH",
        "mains_frequency_hz": 60.0,
        "q_factor": 30.0,
        "bandwidth_hz": None,
        "parameter_origin": "ANALYTICAL_RESEARCH",
    })
    refingerprint(p)
    with pytest.raises(ProcessingProfileRuntimeError, match="NYQUIST"):
        bind_profile_to_runtime(p, runtime(sampling_rate_hz=100.0))


def test_31_enabled_decimation_requires_explicit_anti_aliasing_policy() -> None:
    p = profile()
    rs = p["grid"]["resampling"]
    rs.update({
        "enabled": True,
        "target_fs_hz": 1000.0,
        "method": "POLYPHASE_FIR",
        "anti_aliasing_policy": "NOT_APPLICABLE_FOR_UPSAMPLING",
        "parameter_origin": "ANALYTICAL_RESEARCH",
    })
    refingerprint(p)
    with pytest.raises(ProcessingProfileRuntimeError, match="ANTI_ALIASING"):
        bind_profile_to_runtime(p, runtime(sampling_rate_hz=2000.0))


def test_32_distribution_shift_does_not_block_dsp_independent_profile() -> None:
    result = bind_profile_to_runtime(
        profile(),
        runtime(distribution_support_status="SHIFTED"),
    )
    assert result.distribution_support_status == "SHIFTED"


def test_33_distribution_required_profile_holds_shifted_domain() -> None:
    p = profile()
    p["execution_policy"]["distribution_support_required"] = True
    refingerprint(p)
    with pytest.raises(ProcessingProfileAuthorizationError, match="SHIFT"):
        bind_profile_to_runtime(p, runtime(distribution_support_status="SHIFTED"))


def test_34_distribution_required_profile_abstains_unknown() -> None:
    p = profile()
    p["execution_policy"]["distribution_support_required"] = True
    refingerprint(p)
    with pytest.raises(ProcessingProfileAuthorizationError, match="ABSTAIN"):
        bind_profile_to_runtime(p, runtime(distribution_support_status="UNKNOWN"))


def test_35_duplicate_profile_identity_is_rejected() -> None:
    catalog = load_catalog()
    catalog["profiles"].append(deepcopy(catalog["profiles"][0]))
    with pytest.raises(ProcessingProfileConfigurationError, match="duplicate"):
        validate_catalog_semantics(catalog)


def test_36_fingerprint_mismatch_fails_closed() -> None:
    p = profile()
    p["config_fingerprint"] = "pprof_sha256_" + "0" * 64
    with pytest.raises(ProcessingProfileConfigurationError, match="FINGERPRINT"):
        validate_profile_semantics(p)


def test_37_raw_and_processed_identity_metadata_are_mandatory() -> None:
    required = set(profile()["required_output_metadata"])
    expected = {
        "source_window_id", "native_fs_hz", "processed_fs_hz",
        "input_hash", "output_hash",
    }
    assert expected <= required


def test_38_profile_claim_scope_remains_research_only() -> None:
    assert profile()["claim_scope"] == "RESEARCH_ONLY"
    assert load_catalog()["claim_scope"] == "RESEARCH_ONLY"


def test_39_profile_is_contract_only_not_filter_implementation() -> None:
    p = profile()
    assert all(
        step["implementation_status"] == "CONTRACT_ONLY"
        for step in [
            p["grid"]["resampling"], p["steps"]["bandpass"], p["steps"]["notch"],
            p["steps"]["rectification"], p["steps"]["smoothing"], p["steps"]["normalization"]
        ]
    )


def test_40_config_contains_no_legacy_hardcoded_bandpass_or_notch_defaults() -> None:
    text = CATALOG_PATH.read_text(encoding="utf-8")
    assert "20-450" not in text
    assert "low_cut_hz: 20" not in text
    assert "high_cut_hz: 450" not in text
    assert "mains_frequency_hz: 50" not in text


def test_41_site_binding_mutation_is_rejected_semantically() -> None:
    p = profile()
    p["site_binding"] = "vinmec-motionlab"
    refingerprint(p)
    with pytest.raises(ProcessingProfileConfigurationError, match="site-specific"):
        validate_profile_semantics(p)


def test_42_locked_partition_can_be_processed_but_not_fitted() -> None:
    result = bind_profile_to_runtime(profile(), runtime(partition="benchmark-locked"))
    assert result.is_resampled is False
    assert profile()["execution_policy"]["locked_partition_fitting_allowed"] is False


def test_43_required_output_effect_summary_is_present() -> None:
    result = bind_profile_to_runtime(profile(), runtime())
    assert result.effect_summary["sampling_grid"] == "UNCHANGED"
    assert result.effect_summary["spectral_content"] == "UNCHANGED"


def test_44_profile_config_is_json_serializable_canonically() -> None:
    payload = canonical_profile_payload(profile())
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert encoded.startswith("{")
