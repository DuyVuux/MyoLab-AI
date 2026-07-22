"""Nạp và kiểm tra technical_confidence_v0.1.yaml."""
from __future__ import annotations
from collections.abc import Mapping
from pathlib import Path
from typing import Any
import math
import yaml


class ConfidenceConfigError(ValueError):
    pass


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfidenceConfigError(f"{name} phải là object/map")
    return value


def validate_confidence_config(raw: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(_mapping(raw, "confidence config"))
    if config.get("schema_version") != "technical-confidence-config.v0.1":
        raise ConfidenceConfigError("Sai schema_version")
    if config.get("config_id") != "technical_confidence_v0.1":
        raise ConfidenceConfigError("Sai config_id")
    if config.get("clinical_calibration_status") != "not_calibrated":
        raise ConfidenceConfigError("Phải not_calibrated")
    if config.get("clinical_validation_status") != "not_validated":
        raise ConfidenceConfigError("Phải not_validated")

    weights = _mapping(config.get("weights"), "weights")
    expected_keys = {"qc_quality", "usable_window_ratio", "trend_quality", "evidence_consistency"}
    if set(weights) != expected_keys:
        raise ConfidenceConfigError("weights không đúng contract")
    total = sum(float(value) for value in weights.values())
    if not math.isclose(total, 1.0, abs_tol=1e-9, rel_tol=0.0):
        raise ConfidenceConfigError("Tổng weights phải bằng 1.0")
    if any(float(value) < 0 for value in weights.values()):
        raise ConfidenceConfigError("Weights không được âm")

    thresholds = _mapping(config.get("category_thresholds"), "category_thresholds")
    low = float(thresholds["engineering_low_min"])
    moderate = float(thresholds["engineering_moderate_min"])
    high = float(thresholds["engineering_high_min"])
    if not (0 <= low <= moderate <= high <= 1):
        raise ConfidenceConfigError("Category thresholds không hợp lệ")

    output = _mapping(config.get("output_contract"), "output_contract")
    if output.get("score_is_probability") is not False:
        raise ConfidenceConfigError("score_is_probability phải false")

    safety = _mapping(config.get("safety"), "safety")
    required_true = (
        "engineering_confidence_is_not_probability",
        "do_not_claim_calibration",
        "do_not_generate_frs",
        "do_not_generate_treatment_recommendation",
        "do_not_generate_return_to_play_decision",
        "require_human_review",
        "synthetic_data_is_not_clinical_evidence",
    )
    for key in required_true:
        if safety.get(key) is not True:
            raise ConfidenceConfigError(f"safety.{key} phải true")
    if safety.get("clinical_use_allowed") is not False:
        raise ConfidenceConfigError("clinical_use_allowed phải false")
    return config


def load_confidence_config(path: Path | str) -> dict[str, Any]:
    target = Path(path)
    try:
        raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfidenceConfigError(str(exc)) from exc
    return validate_confidence_config(_mapping(raw, "confidence config"))
