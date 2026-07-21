"""Nạp và kiểm tra windowing_v0.1.yaml."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


_REQUIRED_PROFILES = {"time_domain", "frequency_domain"}


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} phải là object/map")
    return value


def load_windowing_config(path: Path | str) -> dict[str, Any]:
    config_path = Path(path)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config = dict(_mapping(raw, "windowing config"))

    if config.get("schema_version") != "windowing-config.v0.1":
        raise ValueError("Chỉ hỗ trợ windowing-config.v0.1 trong Day 7")
    if config.get("config_id") != "windowing_v0.1":
        raise ValueError("config_id phải là windowing_v0.1")

    input_contract = _mapping(config.get("input_contract"), "input_contract")
    if input_contract.get("require_preprocessing_downstream_allowed") is not True:
        raise ValueError("Windowing phải yêu cầu preprocessing downstream_allowed=true")
    if input_contract.get("required_preprocess_config_id") != "preprocess_v0.1":
        raise ValueError("Day 7 chỉ khóa dependency preprocess_v0.1")
    if input_contract.get("require_protocol_object") is not True:
        raise ValueError("Day 7 yêu cầu protocol object")
    if input_contract.get("require_protocol_ref_match") is not True:
        raise ValueError("Protocol ref phải khớp signal")
    if input_contract.get("canonical_unit") != "uV":
        raise ValueError("Canonical unit phải là uV")
    if input_contract.get("raw_arrays_in_json") is not False:
        raise ValueError("Raw arrays không được xuất vào JSON")

    segmentation = _mapping(config.get("segmentation"), "segmentation")
    if segmentation.get("phase_source") != "protocol.analysis.active_phase_id":
        raise ValueError("Target phase phải lấy từ protocol.analysis.active_phase_id")
    if segmentation.get("expected_phase_id") != "active_contraction":
        raise ValueError("MVP-0 kỳ vọng active_contraction")
    if segmentation.get("phase_boundary_convention") != "half_open":
        raise ValueError("Day 7 bắt buộc half_open boundary")
    if segmentation.get("boundary_mapping") != "numpy_searchsorted_left":
        raise ValueError("Day 7 dùng numpy_searchsorted_left")

    alignment = _mapping(config.get("protocol_alignment"), "protocol_alignment")
    if alignment.get("validate_default_windowing") is not True:
        raise ValueError("Phải validate config với protocol default_windowing")

    profiles = _mapping(config.get("profiles"), "profiles")
    if set(profiles) != _REQUIRED_PROFILES:
        raise ValueError(
            "Day 7 cần đúng hai profile: time_domain và frequency_domain"
        )
    expected_fields = {
        "time_domain": "time_domain_window_ms",
        "frequency_domain": "frequency_domain_window_ms",
    }
    expected_purposes = {
        "time_domain": "rms_mav",
        "frequency_domain": "psd_mdf_mnf",
    }
    for profile_id in sorted(_REQUIRED_PROFILES):
        profile = _mapping(profiles.get(profile_id), f"profiles.{profile_id}")
        if profile.get("purpose") != expected_purposes[profile_id]:
            raise ValueError(f"Sai purpose cho profile {profile_id}")
        if profile.get("protocol_duration_field") != expected_fields[profile_id]:
            raise ValueError(f"Sai protocol_duration_field cho {profile_id}")
        duration_ms = int(profile.get("duration_ms"))
        overlap = float(profile.get("overlap_fraction"))
        if duration_ms < 1:
            raise ValueError(f"duration_ms của {profile_id} phải > 0")
        if not (0.0 <= overlap < 1.0):
            raise ValueError(
                f"overlap_fraction của {profile_id} phải nằm trong [0, 1)"
            )
        if profile.get("allow_partial_final_window") is not False:
            raise ValueError("MVP-0 không cho partial final window")
        if profile.get("sample_rounding_policy") != "exact_integer_required":
            raise ValueError("Day 7 yêu cầu exact_integer_required")

    validity = _mapping(config.get("validity"), "validity")
    threshold = float(validity.get("minimum_valid_sample_ratio"))
    if not (0.0 <= threshold <= 1.0):
        raise ValueError("minimum_valid_sample_ratio phải nằm trong [0, 1]")
    if validity.get("evaluate_per_channel") is not True:
        raise ValueError("Day 7 phải evaluate_per_channel=true")
    if validity.get("require_all_profiles_for_downstream") is not True:
        raise ValueError("MVP-0 yêu cầu cả hai profile có valid windows")
    if validity.get("block_if_no_valid_windows_in_profile") is not True:
        raise ValueError("Phải block khi một profile không có valid window")

    feature_preparation = _mapping(
        config.get("feature_preparation"), "feature_preparation"
    )
    if feature_preparation.get("apply_taper_during_windowing") is not False:
        raise ValueError("Không được taper tại tầng windowing")
    if feature_preparation.get("spectral_taper_default") != "hann":
        raise ValueError("Taper mặc định cho spectral stage phải là hann")

    output = _mapping(config.get("output_contract"), "output_contract")
    if output.get("create_index_plan_only") is not True:
        raise ValueError("Day 7 phải tạo index plan, không materialize tất cả window")
    if output.get("materialize_overlapping_windows") is not False:
        raise ValueError("Không materialize overlapping windows trong Day 7")
    if output.get("include_raw_samples_in_json") is not False:
        raise ValueError("Raw samples không được có trong JSON")

    return config
