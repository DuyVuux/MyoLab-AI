#!/usr/bin/env python3
"""Kiểm tra artifact, contract và safety invariants của Day 8."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "docs/plans/DAY8_EXECUTION_PLAN.md",
    "docs/06-ai-signal-processing/time-domain-feature-math-primer.md",
    "docs/06-ai-signal-processing/feature-extraction-spec.md",
    "docs/05-data/time-domain-feature-result-contract.md",
    "docs/08-validation-qa/day8-time-domain-feature-test-plan.md",
    "docs/03-architecture/adr/ADR-0010-time-domain-features-before-spectral-and-inference.md",
    "docs/00-executive/day8-decision-log-append.md",
    "docs/01-product/backlog/day8-backlog.md",
    "services/feature-extraction-service/configs/features_semg_v0.1.yaml",
    "services/feature-extraction-service/src/feature_config.py",
    "services/feature-extraction-service/src/time_domain.py",
    "services/feature-extraction-service/src/feature_result_models.py",
    "services/feature-extraction-service/src/extractor.py",
    "services/feature-extraction-service/tests/test_feature_config.py",
    "packages/semg-core/semg_core/features.py",
    "packages/common-schemas/json/feature-row.schema.json",
    "packages/common-schemas/json/time-domain-feature-result.schema.json",
    "packages/common-schemas/json/time-domain-feature-verification.schema.json",
    "scripts/data/run_time_domain_features.py",
    "scripts/data/verify_time_domain_features.py",
    "scripts/dev/register_feature_extractor_v0_1.py",
    "scripts/dev/run_day8_checks.sh",
    "qa-validation/requirements/day8-acceptance-criteria.md",
    "qa-validation/evidence/day8-time-domain-feature-verification.json",
    "qa-validation/evidence/day8-time-domain-features.json",
    "ai-core/validation-reports/analytical_validation_time_domain_features_v0.1.md",
    "mlops/registry/feature_extractors.yaml",
]

# Skeleton hiện tại của người dùng dùng docs/note/ (số ít).
NOTE_FILES = [
    f"docs/note/day08/{index:02d}-{name}.md"
    for index, name in enumerate(
        (
            "learning-objectives",
            "reading-notes",
            "math-notes",
            "signal-processing-notes",
            "clinical-notes",
            "questions",
            "decisions",
            "daily-summary",
            "todo-day09",
        ),
        start=1,
    )
]


def _load_json(relative: str) -> dict:
    payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON phải là object: {relative}")
    return payload


def main() -> int:
    errors: list[str] = []
    for relative in [*REQUIRED, *NOTE_FILES]:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"Thiếu file: {relative}")
        elif path.stat().st_size == 0:
            errors.append(f"File rỗng: {relative}")

    config_path = ROOT / "services/feature-extraction-service/configs/features_semg_v0.1.yaml"
    if config_path.is_file():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        features = config.get("features", {}) if isinstance(config, dict) else {}
        contract = config.get("input_contract", {}) if isinstance(config, dict) else {}
        semantics = config.get("preprocessing_semantics", {}) if isinstance(config, dict) else {}
        normalization = config.get("normalization", {}) if isinstance(config, dict) else {}
        aggregation = config.get("aggregation", {}) if isinstance(config, dict) else {}
        output = config.get("output_contract", {}) if isinstance(config, dict) else {}
        safety = config.get("safety", {}) if isinstance(config, dict) else {}
        invariants = {
            "clinical_not_validated": config.get("clinical_validation_status") == "not_validated",
            "time_domain_profile_only": contract.get("required_profile_id") == "time_domain",
            "only_rms_mav": set(features) == {"rms", "mav"},
            "compute_only_valid_windows": contract.get("compute_only_valid_windows") is True,
            "untapered_samples": contract.get("require_untapered_samples") is True,
            "unrectified_rms": semantics.get("apply_rectification_before_rms") is False,
            "unrectified_mav": semantics.get("apply_rectification_before_mav") is False,
            "no_taper": semantics.get("apply_taper") is False,
            "no_mvc_normalization": normalization.get("mode") == "none" and normalization.get("mvc_normalized") is False,
            "cross_session_comparison_disabled": normalization.get("allow_cross_session_amplitude_comparison") is False,
            "no_cross_channel_aggregate": aggregation.get("emit_cross_channel_aggregate") is False,
            "no_trend_yet": aggregation.get("trend_features_in_scope") is False,
            "raw_samples_excluded": output.get("include_raw_samples") is False,
            "no_fatigue_interpretation": safety.get("do_not_interpret_fatigue") is True,
            "no_ml": safety.get("do_not_train_ml") is True,
        }
        for name, ok in invariants.items():
            if not ok:
                errors.append(f"Invariant fail: {name}")

    verification_path = ROOT / "qa-validation/evidence/day8-time-domain-feature-verification.json"
    if verification_path.is_file():
        verification = _load_json("qa-validation/evidence/day8-time-domain-feature-verification.json")
        if verification.get("verification_status") != "passed":
            errors.append("RMS/MAV analytical verification không PASSED")
        if verification.get("scope") != "software_dsp_analytical_verification_only":
            errors.append("Verification scope không đúng")

    evidence_path = ROOT / "qa-validation/evidence/day8-time-domain-features.json"
    if evidence_path.is_file():
        payload = _load_json("qa-validation/evidence/day8-time-domain-features.json")
        serialized = json.dumps(payload, ensure_ascii=False)
        if payload.get("status") != "completed":
            errors.append("Golden feature extraction không completed")
        if payload.get("downstream_allowed") is not True:
            errors.append("Golden feature extraction không downstream_allowed")
        if "samples_uV" in serialized or "raw_samples" in serialized:
            errors.append("Feature output chứa raw samples")
        summary = payload.get("summary", {})
        if summary.get("total_row_count") != 239:
            errors.append(
                f"Golden total_row_count phải là 239, quan sát={summary.get('total_row_count')}"
            )
        if summary.get("computed_row_count") != 239:
            errors.append("Golden computed_row_count phải là 239")
        if summary.get("not_computed_row_count") != 0:
            errors.append("Golden không được có not_computed row")
        if payload.get("config", {}).get("normalization") != "none":
            errors.append("Golden output sai normalization state")
        rows = payload.get("rows", [])
        if len(rows) != 239:
            errors.append("Số row thực tế không bằng 239")
        for index, row in enumerate(rows):
            if row.get("status") != "computed":
                errors.append(f"Golden row {index} không computed")
                break
            features = row.get("features") or {}
            rms = (features.get("rms") or {}).get("value")
            mav = (features.get("mav") or {}).get("value")
            if not isinstance(rms, (int, float)) or not isinstance(mav, (int, float)):
                errors.append(f"Row {index} thiếu RMS/MAV số")
                break
            if rms < 0 or mav < 0 or rms + 1e-10 < mav:
                errors.append(f"Row {index} vi phạm RMS/MAV invariant")
                break

    registry_path = ROOT / "mlops/registry/feature_extractors.yaml"
    if registry_path.is_file():
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        entries = registry.get("feature_extractors", []) if isinstance(registry, dict) else []
        matches = [
            item
            for item in entries
            if isinstance(item, dict) and item.get("config_id") == "features_semg_v0.1"
        ]
        if len(matches) != 1:
            errors.append("Registry cần đúng một entry features_semg_v0.1")
        else:
            entry = matches[0]
            if entry.get("clinical_validation_status") != "not_validated":
                errors.append("Registry overclaim clinical validation")
            if entry.get("implemented_features") != ["rms", "mav"]:
                errors.append("Registry implemented_features không đúng RMS/MAV")
            if entry.get("cross_session_amplitude_comparison_allowed") is not False:
                errors.append("Registry cho phép cross-session amplitude comparison")
            if entry.get("fatigue_inference_in_scope") is not False:
                errors.append("Registry đưa fatigue inference vào Day 8")

    extractor_path = ROOT / "services/feature-extraction-service/src/extractor.py"
    if extractor_path.is_file():
        code = extractor_path.read_text(encoding="utf-8").lower()
        for token in ("sklearn", "tensorflow", "torch", "fatigue_resistance_score"):
            if token in code:
                errors.append(f"Extractor chứa token ngoài scope: {token}")

    if errors:
        print("DAY 8 ARTIFACT CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DAY 8 ARTIFACT CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
