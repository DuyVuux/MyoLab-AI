"""Nạp và kiểm tra cấu hình preprocessing v0.1."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} phải là object/map")
    return value


def load_preprocess_config(path: Path | str) -> dict[str, Any]:
    config_path = Path(path)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config = dict(_mapping(raw, "preprocess config"))

    if config.get("schema_version") != "preprocessing-config.v0.1":
        raise ValueError("Chỉ hỗ trợ preprocessing-config.v0.1 trong Day 5")
    if config.get("config_id") != "preprocess_v0.1":
        raise ValueError("config_id phải là preprocess_v0.1")

    mode = _mapping(config.get("mode"), "mode")
    if mode.get("execution") != "offline":
        raise ValueError("MVP-0 chỉ hỗ trợ execution=offline")
    if mode.get("phase_behavior") != "zero_phase":
        raise ValueError("Day 5 bắt buộc zero_phase")
    if mode.get("implementation") != "scipy_sosfiltfilt":
        raise ValueError("Day 5 bắt buộc scipy_sosfiltfilt")
    if mode.get("near_real_time_compatible") is not False:
        raise ValueError("Cấu hình Day 5 không được claim near-real-time compatibility")

    input_contract = _mapping(config.get("input_contract"), "input_contract")
    required_true = (
        "require_qc_analysis_allowed",
        "require_finite_samples",
        "preserve_time_axis",
        "preserve_sample_count",
        "preserve_channel_identity",
    )
    for key in required_true:
        if input_contract.get(key) is not True:
            raise ValueError(f"input_contract.{key} phải bằng true")
    if input_contract.get("canonical_unit") != "uV":
        raise ValueError("canonical_unit phải là uV")

    steps = _mapping(config.get("steps"), "steps")
    bandpass = _mapping(steps.get("bandpass"), "steps.bandpass")
    if bandpass.get("enabled") is not True:
        raise ValueError("Band-pass phải được bật trong preprocess_v0.1")
    if bandpass.get("family") != "butterworth":
        raise ValueError("Chỉ hỗ trợ Butterworth trong Day 5")
    if bandpass.get("representation") != "second_order_sections":
        raise ValueError("Band-pass phải dùng second_order_sections")
    if bandpass.get("implementation") != "sosfiltfilt":
        raise ValueError("Band-pass phải dùng sosfiltfilt")

    notch = _mapping(steps.get("notch"), "steps.notch")
    if notch.get("enabled") is not True:
        raise ValueError("Notch capability phải được bật, nhưng chạy có điều kiện")
    if notch.get("policy") != "conditional_on_qc_reason_code":
        raise ValueError("Notch phải chạy theo QC reason code")
    if notch.get("trigger_reason_code") != "POWERLINE_NOISE_HIGH":
        raise ValueError("Trigger notch v0.1 phải là POWERLINE_NOISE_HIGH")

    for disabled_step in ("resampling", "rectification", "envelope"):
        item = _mapping(steps.get(disabled_step), f"steps.{disabled_step}")
        if item.get("enabled") is not False:
            raise ValueError(f"{disabled_step} phải tắt trong Day 5")

    output = _mapping(config.get("output_contract"), "output_contract")
    if output.get("sample_dtype") != "float64":
        raise ValueError("sample_dtype phải là float64")
    if output.get("raw_arrays_in_json") is not False:
        raise ValueError("raw_arrays_in_json phải bằng false")

    return config
