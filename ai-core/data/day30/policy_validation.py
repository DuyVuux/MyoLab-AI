from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from .sample_rate import SAMPLE_ROUNDING_POLICY, rational_resample_factors


def _load_policy(policy: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(policy, Mapping):
        return dict(policy)
    document = yaml.safe_load(Path(policy).read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("policy root must be a mapping")
    return document


def _result(errors: list[str]) -> dict[str, Any]:
    return {"pass": not errors, "errors": errors}


def validate_sampling_policy(
    policy: str | Path | Mapping[str, Any],
) -> dict[str, Any]:
    document = _load_policy(policy)
    errors: list[str] = []
    primary = document.get("primary", {})
    comparator = document.get("comparator", {})
    if document.get("training_allowed") is not False:
        errors.append("training_must_be_disabled")
    if primary.get("mode") != "native_rate":
        errors.append("primary_must_use_native_rate")
    if primary.get("spectral_features_use_record_sampling_rate") is not True:
        errors.append("spectral_features_must_use_record_fs")
    if primary.get("sample_rounding") != SAMPLE_ROUNDING_POLICY:
        errors.append("sample_rounding_policy_mismatch")
    expected_up, expected_down = rational_resample_factors(2048, 2000)
    if (
        comparator.get("source_hz"),
        comparator.get("target_hz"),
        comparator.get("method"),
        comparator.get("up"),
        comparator.get("down"),
    ) != (2048, 2000, "polyphase", expected_up, expected_down):
        errors.append("invalid_2048_to_2000_comparator")
    return _result(errors)


def validate_channel_policy(
    policy: str | Path | Mapping[str, Any],
) -> dict[str, Any]:
    document = _load_policy(policy)
    errors: list[str] = []
    mendeley = document.get("mendeley", {})
    grabmyo = document.get("grabmyo", {})
    cross_source = document.get("cross_source", {})
    primary = mendeley.get("primary_channels", [])
    quarantined = mendeley.get("quarantined", [])
    excluded = grabmyo.get("excluded", [])
    if document.get("training_allowed") is not False:
        errors.append("training_must_be_disabled")
    if primary != ["EMG_Raw_CH1", "EMG_RAW_CH2", "EMG_RAW_CH3"]:
        errors.append("invalid_mendeley_primary_channels")
    if not any(
        item.get("channel") == "EMG_RAW_CH4"
        and item.get("status") == "QUARANTINED_EXCLUDED_PRIMARY"
        for item in quarantined
        if isinstance(item, dict)
    ):
        errors.append("ch4_not_quarantined")
    if not any(
        item.get("pattern") == "U1-U4"
        and item.get("raw_provenance_retained") is True
        for item in excluded
        if isinstance(item, dict)
    ):
        errors.append("grabmyo_u_channels_not_excluded")
    if cross_source.get("direct_anatomical_mapping_allowed") is not False:
        errors.append("direct_anatomical_mapping_must_be_disabled")
    return _result(errors)


def validate_windowing_policy(
    policy: str | Path | Mapping[str, Any],
) -> dict[str, Any]:
    document = _load_policy(policy)
    errors: list[str] = []
    primary = document.get("primary", {})
    rules = document.get("rules", {})
    if document.get("training_allowed") is not False:
        errors.append("training_must_be_disabled")
    if (primary.get("window_ms"), primary.get("hop_ms")) != (200, 100):
        errors.append("invalid_primary_window")
    required_true = (
        "split_before_windowing",
        "windows_must_stay_within_atomic_unit",
    )
    errors.extend(
        f"{field}_must_be_true"
        for field in required_true
        if rules.get(field) is not True
    )
    if rules.get("test_partition_allowed") is not False:
        errors.append("test_partition_must_be_disabled")
    if rules.get("cross_label_window_allowed") is not False:
        errors.append("cross_label_window_must_be_disabled")
    return _result(errors)


def validate_storage_contract(
    policy: str | Path | Mapping[str, Any],
) -> dict[str, Any]:
    document = _load_policy(policy)
    errors: list[str] = []
    raw_signal = document.get("raw_signal", {})
    if raw_signal.get("copy_or_materialize_windows_by_default") is not False:
        errors.append("raw_windows_must_not_be_materialized")
    required = {
        "dataset_id",
        "source_file_sha256",
        "split_version",
        "label_mapping_version",
        "preprocessing_policy_id",
        "channel_policy_id",
    }
    present = set(document.get("provenance_required", []))
    for field in sorted(required - present):
        errors.append(f"missing_provenance:{field}")
    return _result(errors)

