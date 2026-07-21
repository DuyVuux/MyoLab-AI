#!/usr/bin/env python3
"""Kiểm tra artifact, contract và safety invariants của Day 9."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "packages/semg-core/semg_core/spectral.py",
    "packages/semg-core/tests/test_spectral.py",
    "services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml",
    "services/feature-extraction-service/src/spectral_config.py",
    "services/feature-extraction-service/src/frequency_domain.py",
    "services/feature-extraction-service/src/spectral_result_models.py",
    "services/feature-extraction-service/src/spectral_estimator.py",
    "services/feature-extraction-service/src/spectral_extractor.py",
    "services/feature-extraction-service/tests/test_spectral_config.py",
    "services/feature-extraction-service/tests/test_frequency_domain.py",
    "services/feature-extraction-service/tests/test_spectral_estimator.py",
    "packages/common-schemas/json/spectral-window-row.schema.json",
    "packages/common-schemas/json/spectral-estimation-result.schema.json",
    "packages/common-schemas/json/spectral-verification.schema.json",
    "scripts/data/run_spectral_estimation.py",
    "scripts/data/verify_spectral_estimation.py",
    "scripts/dev/register_spectral_estimator_v0_1.py",
    "scripts/dev/validate_day9_outputs.py",
    "scripts/dev/run_day9_checks.sh",
    "qa-validation/automated-tests/test_spectral_estimation_analytical.py",
    "qa-validation/evidence/day9-spectral-verification.json",
    "qa-validation/evidence/day9-spectral-verification.md",
    "qa-validation/evidence/day9-spectral-estimation.json",
    "qa-validation/evidence/day9-spectral-estimation-rerun.json",
    "qa-validation/evidence/day9-spectral-estimation.csv",
    "qa-validation/evidence/day9-spectral-blocked.json",
    "qa-validation/requirements/day9-acceptance-criteria.md",
    "ai-core/validation-reports/analytical_validation_spectral_estimation_v0.1.md",
    "docs/06-ai-signal-processing/frequency-domain-math-primer.md",
    "docs/06-ai-signal-processing/spectral-estimation-spec.md",
    "docs/05-data/spectral-estimation-result-contract.md",
    "docs/08-validation-qa/day9-spectral-estimation-test-plan.md",
    "docs/03-architecture/adr/ADR-0011-hann-welch-spectral-foundation-before-mdf-mnf.md",
    "docs/01-product/backlog/day9-backlog.md",
    "docs/00-executive/day9-decision-log-append.md",
    "docs/plans/DAY9_EXECUTION_PLAN.md",
    "DAY9_STARTER_PACK_README.md",
)

NOTE_FILES = tuple(
    f"docs/note/day09/{name}"
    for name in (
        "01-learning-objectives.md",
        "02-reading-notes.md",
        "03-math-notes.md",
        "04-signal-processing-notes.md",
        "05-clinical-notes.md",
        "06-questions.md",
        "07-decisions.md",
        "08-daily-summary.md",
        "09-todo-day10.md",
    )
)


def _load_json(relative: str) -> dict[str, Any]:
    payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root phải là object: {relative}")
    return payload


def _contains_vietnamese(text: str) -> bool:
    return bool(re.search(r"[ăâđêôơưÁÀẢÃẠáàảãạĂÂĐÊÔƠƯ]", text))


def main() -> int:
    errors: list[str] = []

    for relative in (*REQUIRED_FILES, *NOTE_FILES):
        path = ROOT / relative
        if not path.exists():
            errors.append(f"Thiếu file: {relative}")
        elif path.is_file() and path.stat().st_size == 0:
            errors.append(f"File rỗng: {relative}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    config = yaml.safe_load(
        (ROOT / "services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml").read_text(
            encoding="utf-8"
        )
    )
    if config.get("clinical_validation_status") != "not_validated":
        errors.append("Spectral config phải giữ clinical_validation_status=not_validated")
    if config.get("future_features", {}).get("mdf", {}).get("enabled") is not False:
        errors.append("MDF phải disabled trong Day 9")
    if config.get("future_features", {}).get("mnf", {}).get("enabled") is not False:
        errors.append("MNF phải disabled trong Day 9")
    if config.get("safety", {}).get("do_not_interpret_fatigue") is not True:
        errors.append("Day 9 phải cấm fatigue interpretation")
    if config.get("output_contract", {}).get("include_raw_samples") is not False:
        errors.append("Spectral output không được chứa raw samples")

    verification = _load_json(
        "qa-validation/evidence/day9-spectral-verification.json"
    )
    if verification.get("verification_status") != "passed":
        errors.append("Analytical spectral verification chưa passed")
    checks = verification.get("checks", [])
    if not isinstance(checks, list) or len(checks) < 8:
        errors.append("Analytical spectral verification phải có ít nhất 8 kiểm tra")
    elif any(item.get("status") != "passed" for item in checks if isinstance(item, dict)):
        errors.append("Có analytical spectral check chưa passed")
    if verification.get("clinical_validation_status") != "not_validated":
        errors.append("Verification không được tuyên bố clinical validation")

    first = _load_json("qa-validation/evidence/day9-spectral-estimation.json")
    second = _load_json(
        "qa-validation/evidence/day9-spectral-estimation-rerun.json"
    )

    blocked = _load_json("qa-validation/evidence/day9-spectral-blocked.json")
    if blocked.get("status") != "blocked":
        errors.append("Fixture QC fail phải trả spectral status=blocked")
    if blocked.get("downstream_allowed") is not False:
        errors.append("Fixture QC fail phải downstream_allowed=false")
    if blocked.get("rows") not in ([], None):
        errors.append("Fixture QC fail không được tạo spectral rows")
    if "SPECTRAL_ESTIMATION_BLOCKED_BY_WINDOWING" not in blocked.get("reason_codes", []):
        errors.append("Fixture QC fail thiếu reason code block từ windowing")
    if first.get("status") != "completed":
        errors.append(f"Golden spectral status không phải completed: {first.get('status')}")
    if first.get("downstream_allowed") is not True:
        errors.append("Golden spectral phải downstream_allowed=true")
    if first.get("result_hash_sha256") != second.get("result_hash_sha256"):
        errors.append("Golden spectral result hash không deterministic")
    summary = first.get("summary", {})
    expected_summary = {
        "total_row_count": 119,
        "computed_row_count": 119,
        "not_computed_row_count": 0,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            errors.append(f"Golden {key} phải bằng {expected}; nhận {summary.get(key)}")
    if first.get("config", {}).get("mdf_mnf_computed") is not False:
        errors.append("Golden Day 9 không được có MDF/MNF")

    axis = first.get("frequency_axis") or {}
    if axis.get("bin_count") != 381:
        errors.append(f"Frequency bin count phải 381; nhận {axis.get('bin_count')}")
    if axis.get("lower_hz") != 20.0 or axis.get("upper_hz") != 400.0:
        errors.append("Golden analysis band phải là 20--400 Hz")
    if axis.get("bin_spacing_hz") != 1.0:
        errors.append("Golden bin spacing phải 1 Hz")

    rows = first.get("rows", [])
    if len(rows) != 119:
        errors.append("Golden phải có 119 spectral rows")
    for index, row in enumerate(rows):
        if row.get("status") != "computed":
            errors.append(f"Golden row {index} không computed")
            break
        spectral = row.get("spectral") or {}
        psd = spectral.get("psd", {})
        if psd.get("unit") != "uV^2/Hz":
            errors.append(f"Golden row {index} sai PSD unit")
            break
        if len(psd.get("values", [])) != 381:
            errors.append(f"Golden row {index} sai PSD length")
            break
        band = spectral.get("band_power", {}).get("value")
        full = spectral.get("full_power", {}).get("value")
        if not isinstance(band, (int, float)) or not isinstance(full, (int, float)):
            errors.append(f"Golden row {index} thiếu power values")
            break
        if band > full + max(1e-9, abs(full) * 1e-9):
            errors.append(f"Golden row {index}: band power > full power")
            break

    serialized = json.dumps(first, ensure_ascii=False)
    for forbidden in ("samples_uV", "raw_samples", "fatigue_status", "frs"):
        if forbidden in serialized:
            errors.append(f"Forbidden field/text trong spectral JSON: {forbidden}")

    registry = yaml.safe_load(
        (ROOT / "mlops/registry/feature_extractors.yaml").read_text(
            encoding="utf-8"
        )
    )
    entries = registry.get("feature_extractors", []) if isinstance(registry, dict) else []
    spectral_entries = [
        item
        for item in entries
        if isinstance(item, dict)
        and item.get("config_id") == "spectral_estimation_v0.1"
    ]
    if len(spectral_entries) != 1:
        errors.append("Registry phải có đúng một spectral_estimation_v0.1 entry")
    else:
        entry = spectral_entries[0]
        if entry.get("clinical_validation_status") != "not_validated":
            errors.append("Registry spectral entry không được clinical validated")
        if entry.get("implemented_features") != ["welch_psd"]:
            errors.append("Registry implemented_features phải chỉ có welch_psd")

    markdown_paths = [
        ROOT / relative
        for relative in REQUIRED_FILES + NOTE_FILES
        if relative.endswith(".md")
    ]
    for path in markdown_paths:
        text = path.read_text(encoding="utf-8")
        if not _contains_vietnamese(text):
            errors.append(f"Markdown chưa thể hiện nội dung tiếng Việt: {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Day 9 artifact/safety check passed.")
    print(f"Golden spectral hash: {first['result_hash_sha256']}")
    print("Golden rows/bins: 119 / 381")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
