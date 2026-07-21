"""Nạp và kiểm tra frequency_features_v0.1.yaml."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


class FrequencyFeatureConfigError(ValueError):
    """Lỗi contract của cấu hình MDF/MNF."""


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FrequencyFeatureConfigError(f"{name} phải là object/map")
    return value


def validate_frequency_feature_config(raw: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(_mapping(raw, "frequency feature config"))
    if config.get("schema_version") != "frequency-feature-config.v0.1":
        raise FrequencyFeatureConfigError("Chỉ hỗ trợ frequency-feature-config.v0.1")
    if config.get("config_id") != "frequency_features_v0.1":
        raise FrequencyFeatureConfigError("config_id phải là frequency_features_v0.1")
    if config.get("clinical_validation_status") != "not_validated":
        raise FrequencyFeatureConfigError("clinical_validation_status phải not_validated")

    contract = _mapping(config.get("input_contract"), "input_contract")
    expected = {
        "require_spectral_downstream_allowed": True,
        "required_spectral_config_id": "spectral_estimation_v0.1",
        "required_spectral_result_schema_version": "spectral-estimation-result.v0.1",
        "required_profile_id": "frequency_domain",
        "required_psd_unit": "uV^2/Hz",
        "required_frequency_unit": "Hz",
        "required_analysis_band_low_hz": 20.0,
        "required_analysis_band_high_hz": 400.0,
        "require_uniform_frequency_axis": True,
        "require_computed_spectral_row": True,
        "upstream_not_computed_policy": "emit_not_computed_row",
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            raise FrequencyFeatureConfigError(f"input_contract.{key} phải bằng {value!r}")

    guard = _mapping(config.get("power_guard"), "power_guard")
    if float(guard.get("minimum_band_power_uV2")) < 0:
        raise FrequencyFeatureConfigError("minimum_band_power_uV2 không được âm")
    if guard.get("reject_nonfinite_psd") is not True:
        raise FrequencyFeatureConfigError("reject_nonfinite_psd phải true")
    if guard.get("reject_negative_psd") is not True:
        raise FrequencyFeatureConfigError("reject_negative_psd phải true")

    features = _mapping(config.get("features"), "features")
    mdf = _mapping(features.get("mdf"), "features.mdf")
    mnf = _mapping(features.get("mnf"), "features.mnf")
    if mdf.get("enabled") is not True or mnf.get("enabled") is not True:
        raise FrequencyFeatureConfigError("MDF và MNF phải enabled trong Day 10")
    if float(mdf.get("quantile")) != 0.5:
        raise FrequencyFeatureConfigError("MDF quantile phải bằng 0.5")
    if mdf.get("method") != "cdf_bin_edge_linear_v0.1":
        raise FrequencyFeatureConfigError("MDF method không đúng v0.1")
    if mnf.get("method") != "power_weighted_centroid_v0.1":
        raise FrequencyFeatureConfigError("MNF method không đúng v0.1")

    checks = _mapping(config.get("consistency_checks"), "consistency_checks")
    if checks.get("recompute_band_power_from_psd") is not True:
        raise FrequencyFeatureConfigError("Phải recompute band power")
    tolerance = float(checks.get("band_power_relative_tolerance"))
    if not (0 < tolerance <= 1e-3):
        raise FrequencyFeatureConfigError("band_power_relative_tolerance không hợp lệ")
    if checks.get("require_feature_inside_analysis_band") is not True:
        raise FrequencyFeatureConfigError("Phải kiểm tra feature trong dải")

    output = _mapping(config.get("output_contract"), "output_contract")
    expected_output = {
        "include_all_window_rows": True,
        "include_not_computed_rows": True,
        "include_raw_samples": False,
        "include_psd_vector": False,
        "include_window_geometry": True,
        "include_channel_context": True,
        "include_provenance": True,
        "row_schema_version": "frequency-feature-row.v0.1",
        "result_schema_version": "frequency-feature-extraction-result.v0.1",
        "result_hash_algorithm": "sha256_canonical_json",
    }
    for key, value in expected_output.items():
        if output.get(key) != value:
            raise FrequencyFeatureConfigError(f"output_contract.{key} phải bằng {value!r}")

    future = _mapping(config.get("future_features"), "future_features")
    for name, item in future.items():
        if _mapping(item, f"future_features.{name}").get("enabled") is not False:
            raise FrequencyFeatureConfigError(f"future_features.{name} phải disabled")

    safety = _mapping(config.get("safety"), "safety")
    for key in (
        "block_if_no_computed_rows",
        "do_not_impute_upstream_not_computed_rows",
        "do_not_interpret_fatigue",
        "do_not_generate_frs",
        "do_not_train_ml",
        "synthetic_data_is_not_clinical_evidence",
    ):
        if safety.get(key) is not True:
            raise FrequencyFeatureConfigError(f"safety.{key} phải true")
    return config


def load_frequency_feature_config(path: Path | str) -> dict[str, Any]:
    config_path = Path(path)
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FrequencyFeatureConfigError(f"Không đọc được config: {exc}") from exc
    except yaml.YAMLError as exc:
        raise FrequencyFeatureConfigError(f"YAML không hợp lệ: {exc}") from exc
    return validate_frequency_feature_config(_mapping(raw, "frequency feature config"))
