"""Nạp và kiểm tra features_semg_v0.1.yaml cho Day 8."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


_REQUIRED_FEATURES = {"rms", "mav"}


class FeatureConfigError(ValueError):
    """Lỗi contract của cấu hình feature extractor."""


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FeatureConfigError(f"{name} phải là object/map")
    return value


def validate_feature_config(raw: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(_mapping(raw, "feature config"))

    if config.get("schema_version") != "feature-extractor-config.v0.1":
        raise FeatureConfigError(
            "Chỉ hỗ trợ feature-extractor-config.v0.1 trong Day 8"
        )
    if config.get("config_id") != "features_semg_v0.1":
        raise FeatureConfigError("config_id phải là features_semg_v0.1")
    if config.get("clinical_validation_status") != "not_validated":
        raise FeatureConfigError(
            "Day 8 phải giữ clinical_validation_status=not_validated"
        )

    contract = _mapping(config.get("input_contract"), "input_contract")
    expected_contract = {
        "require_windowing_downstream_allowed": True,
        "required_windowing_config_id": "windowing_v0.1",
        "required_preprocess_config_id": "preprocess_v0.1",
        "required_profile_id": "time_domain",
        "required_profile_purpose": "rms_mav",
        "canonical_amplitude_unit": "uV",
        "require_window_status_valid": True,
        "compute_only_valid_windows": True,
        "require_finite_samples": True,
        "require_untapered_samples": True,
        "invalid_window_policy": "emit_not_computed_row",
    }
    for key, expected in expected_contract.items():
        if contract.get(key) != expected:
            raise FeatureConfigError(
                f"input_contract.{key} phải bằng {expected!r}"
            )

    semantics = _mapping(
        config.get("preprocessing_semantics"), "preprocessing_semantics"
    )
    if semantics.get("expected_signal_path") != "bandpassed_unrectified":
        raise FeatureConfigError(
            "expected_signal_path phải là bandpassed_unrectified"
        )
    for key in (
        "apply_rectification_before_rms",
        "apply_rectification_before_mav",
        "apply_taper",
        "remove_window_mean_again",
    ):
        if semantics.get(key) is not False:
            raise FeatureConfigError(f"{key} phải là false trong v0.1")

    features = _mapping(config.get("features"), "features")
    if set(features) != _REQUIRED_FEATURES:
        raise FeatureConfigError("Day 8 cần đúng hai feature rms và mav")
    expected_formula = {"rms": "sqrt_mean_square", "mav": "mean_absolute_value"}
    for feature_id in sorted(_REQUIRED_FEATURES):
        item = _mapping(features.get(feature_id), f"features.{feature_id}")
        if item.get("enabled") is not True:
            raise FeatureConfigError(f"{feature_id} phải enabled=true")
        if item.get("output_field") != feature_id:
            raise FeatureConfigError(
                f"output_field của {feature_id} phải là {feature_id}"
            )
        if item.get("unit") != "uV":
            raise FeatureConfigError(f"unit của {feature_id} phải là uV")
        if item.get("formula") != expected_formula[feature_id]:
            raise FeatureConfigError(f"Sai formula cho {feature_id}")
        if item.get("denominator") != "N":
            raise FeatureConfigError(f"denominator của {feature_id} phải là N")
        if item.get("normalization") != "none":
            raise FeatureConfigError("Day 8 chưa cho phép normalization")

    future = _mapping(config.get("future_features"), "future_features")
    if any(
        _mapping(item, f"future_features.{name}").get("enabled") is not False
        for name, item in future.items()
    ):
        raise FeatureConfigError("MDF/MNF/slope/MFCV phải disabled trong Day 8")

    normalization = _mapping(config.get("normalization"), "normalization")
    normalization_expected = {
        "mode": "none",
        "mvc_normalized": False,
        "baseline_normalized": False,
        "allow_cross_session_amplitude_comparison": False,
        "allow_cross_subject_amplitude_comparison": False,
    }
    for key, expected in normalization_expected.items():
        if normalization.get(key) != expected:
            raise FeatureConfigError(f"normalization.{key} phải bằng {expected!r}")

    output = _mapping(config.get("output_contract"), "output_contract")
    output_expected = {
        "include_all_window_rows": True,
        "include_not_computed_rows": True,
        "include_raw_samples": False,
        "include_window_geometry": True,
        "include_channel_context": True,
        "include_provenance": True,
        "row_schema_version": "feature-row.v0.1",
        "result_schema_version": "time-domain-feature-extraction-result.v0.1",
        "result_hash_algorithm": "sha256_canonical_json",
    }
    for key, expected in output_expected.items():
        if output.get(key) != expected:
            raise FeatureConfigError(
                f"output_contract.{key} phải bằng {expected!r}"
            )

    aggregation = _mapping(config.get("aggregation"), "aggregation")
    for key in (
        "enabled",
        "emit_cross_channel_aggregate",
        "emit_session_mean",
        "trend_features_in_scope",
    ):
        if aggregation.get(key) is not False:
            raise FeatureConfigError(f"aggregation.{key} phải false trong Day 8")

    safety = _mapping(config.get("safety"), "safety")
    for key in (
        "block_if_no_computed_rows",
        "do_not_impute_invalid_windows",
        "do_not_interpret_fatigue",
        "do_not_generate_frs",
        "do_not_train_ml",
        "synthetic_data_is_not_clinical_evidence",
    ):
        if safety.get(key) is not True:
            raise FeatureConfigError(f"safety.{key} phải true")
    return config


def load_feature_config(path: Path | str) -> dict[str, Any]:
    config_path = Path(path)
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FeatureConfigError(f"Không đọc được config: {exc}") from exc
    except yaml.YAMLError as exc:
        raise FeatureConfigError(f"YAML không hợp lệ: {exc}") from exc
    return validate_feature_config(_mapping(raw, "feature config"))
