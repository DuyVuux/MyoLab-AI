"""Nạp và kiểm tra spectral_estimation_v0.1.yaml cho Day 9."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


class SpectralConfigError(ValueError):
    """Lỗi contract của cấu hình spectral estimator."""


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SpectralConfigError(f"{name} phải là object/map")
    return value


def validate_spectral_config(raw: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(_mapping(raw, "spectral config"))
    if config.get("schema_version") != "spectral-estimation-config.v0.1":
        raise SpectralConfigError("Chỉ hỗ trợ spectral-estimation-config.v0.1")
    if config.get("config_id") != "spectral_estimation_v0.1":
        raise SpectralConfigError("config_id phải là spectral_estimation_v0.1")
    if config.get("clinical_validation_status") != "not_validated":
        raise SpectralConfigError(
            "Day 9 phải giữ clinical_validation_status=not_validated"
        )

    contract = _mapping(config.get("input_contract"), "input_contract")
    expected_contract = {
        "require_windowing_downstream_allowed": True,
        "required_windowing_config_id": "windowing_v0.1",
        "required_preprocess_config_id": "preprocess_v0.1",
        "required_profile_id": "frequency_domain",
        "required_profile_purpose": "psd_mdf_mnf",
        "canonical_amplitude_unit": "uV",
        "require_window_status_valid": True,
        "require_finite_samples": True,
        "require_untapered_outer_window": True,
        "invalid_window_policy": "emit_not_computed_row",
    }
    for key, expected in expected_contract.items():
        if contract.get(key) != expected:
            raise SpectralConfigError(f"input_contract.{key} phải bằng {expected!r}")

    estimator = _mapping(config.get("estimator"), "estimator")
    expected_estimator = {
        "method": "welch",
        "return_onesided": True,
        "taper": "hann",
        "detrend": "constant",
        "scaling": "density",
        "average": "mean",
        "nperseg_policy": "full_outer_window",
        "noverlap_samples": 0,
        "nfft_policy": "equal_outer_window_length",
        "zero_padding_enabled": False,
    }
    for key, expected in expected_estimator.items():
        if estimator.get(key) != expected:
            raise SpectralConfigError(f"estimator.{key} phải bằng {expected!r}")

    band = _mapping(config.get("analysis_band"), "analysis_band")
    low = float(band.get("low_hz"))
    high = float(band.get("high_hz"))
    if low < 0 or high <= low:
        raise SpectralConfigError("analysis_band không hợp lệ")
    if band.get("include_endpoints") is not True:
        raise SpectralConfigError("Day 9 yêu cầu include_endpoints=true")
    if int(band.get("minimum_frequency_bin_count")) < 2:
        raise SpectralConfigError("minimum_frequency_bin_count phải >= 2")

    guard = _mapping(config.get("power_guard"), "power_guard")
    if float(guard.get("minimum_band_power_uV2")) < 0:
        raise SpectralConfigError("minimum_band_power_uV2 không được âm")
    if guard.get("low_power_policy") != "emit_not_computed_row":
        raise SpectralConfigError("low_power_policy phải emit_not_computed_row")
    lower = float(guard.get("parseval_ratio_warning_lower"))
    upper = float(guard.get("parseval_ratio_warning_upper"))
    if not (0 < lower < upper):
        raise SpectralConfigError("Parseval warning bounds không hợp lệ")
    if guard.get("parseval_warning_blocks_downstream") is not False:
        raise SpectralConfigError("Parseval warning không được block trong v0.1")

    output = _mapping(config.get("output_contract"), "output_contract")
    expected_output = {
        "include_all_window_rows": True,
        "include_not_computed_rows": True,
        "include_raw_samples": False,
        "include_full_psd_axis": False,
        "include_analysis_band_frequency_axis_once": True,
        "include_analysis_band_psd_per_row": True,
        "include_window_geometry": True,
        "include_channel_context": True,
        "include_provenance": True,
        "row_schema_version": "spectral-window-row.v0.1",
        "result_schema_version": "spectral-estimation-result.v0.1",
        "result_hash_algorithm": "sha256_canonical_json",
    }
    for key, expected in expected_output.items():
        if output.get(key) != expected:
            raise SpectralConfigError(f"output_contract.{key} phải bằng {expected!r}")

    future = _mapping(config.get("future_features"), "future_features")
    if any(
        _mapping(item, f"future_features.{name}").get("enabled") is not False
        for name, item in future.items()
    ):
        raise SpectralConfigError("MDF/MNF/slope/entropy/MFCV phải disabled trong Day 9")

    safety = _mapping(config.get("safety"), "safety")
    for key in (
        "block_if_no_computed_rows",
        "do_not_impute_invalid_windows",
        "do_not_compute_mdf_mnf",
        "do_not_interpret_fatigue",
        "do_not_generate_frs",
        "do_not_train_ml",
        "synthetic_data_is_not_clinical_evidence",
    ):
        if safety.get(key) is not True:
            raise SpectralConfigError(f"safety.{key} phải true")
    return config


def load_spectral_config(path: Path | str) -> dict[str, Any]:
    config_path = Path(path)
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SpectralConfigError(f"Không đọc được config: {exc}") from exc
    except yaml.YAMLError as exc:
        raise SpectralConfigError(f"YAML không hợp lệ: {exc}") from exc
    return validate_spectral_config(_mapping(raw, "spectral config"))
