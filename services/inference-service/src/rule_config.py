"""Nạp và kiểm tra fatigue_rule_v0.1.yaml."""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from semg_core.fatigue_rules import build_pattern_rules


class RuleConfigError(ValueError):
    pass


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RuleConfigError(f"{name} phải là object/map")
    return value


def validate_rule_config(raw: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(_mapping(raw, "rule config"))
    if config.get("schema_version") != "fatigue-rule-config.v0.1":
        raise RuleConfigError("Sai schema_version")
    if config.get("config_id") != "fatigue_rule_v0.1":
        raise RuleConfigError("Sai config_id")
    if config.get("clinical_validation_status") != "not_validated":
        raise RuleConfigError("clinical_validation_status phải là not_validated")

    contract = _mapping(config.get("input_contract"), "input_contract")
    expected = {
        "require_evidence_downstream_allowed": True,
        "required_evidence_config_id": "fatigue_evidence_v0.1",
        "required_evidence_schema_version": "fatigue-evidence-result.v0.1",
        "upstream_block_policy": "abstain",
        "require_at_least_one_evaluated_channel": True,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            raise RuleConfigError(f"input_contract.{key} phải bằng {value!r}")

    rules = _mapping(config.get("pattern_rules"), "pattern_rules")
    required_patterns = {
        "multi_domain_change_pattern_observed",
        "frequency_decline_pattern_observed",
        "amplitude_increase_pattern_observed",
        "partial_change_pattern_observed",
        "evidence_mixed_or_opposite",
        "insufficient_evidence",
        "no_predefined_change_pattern_observed",
    }
    if set(rules) != required_patterns:
        raise RuleConfigError("pattern_rules không đủ hoặc có pattern ngoài contract")
    build_pattern_rules(rules)

    aggregation = _mapping(config.get("aggregation"), "aggregation")
    if aggregation.get("multiple_channel_policy") != "require_consensus_else_inconclusive":
        raise RuleConfigError("multiple_channel_policy không đúng")
    for key in ("output_probability", "output_frs", "output_diagnosis"):
        if aggregation.get(key) is not False:
            raise RuleConfigError(f"aggregation.{key} phải false")

    safety = _mapping(config.get("safety"), "safety")
    required_true = (
        "abstention_is_first_class_output",
        "supported_pattern_is_not_diagnosis",
        "no_supported_pattern_is_not_no_fatigue",
        "inconclusive_requires_review",
        "do_not_output_probability",
        "do_not_generate_frs",
        "do_not_generate_treatment_recommendation",
        "do_not_generate_return_to_play_decision",
        "require_human_review_for_future_clinical_use",
        "synthetic_data_is_not_clinical_evidence",
    )
    for key in required_true:
        if safety.get(key) is not True:
            raise RuleConfigError(f"safety.{key} phải true")
    return config


def load_rule_config(path: Path | str) -> dict[str, Any]:
    target = Path(path)
    try:
        raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RuleConfigError(f"Không đọc được rule config: {exc}") from exc
    return validate_rule_config(_mapping(raw, "rule config"))
