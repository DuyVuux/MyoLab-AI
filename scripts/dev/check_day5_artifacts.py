#!/usr/bin/env python3
"""Kiểm tra sự hiện diện và một số guardrail của artifact Day 5."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
REQUIRED = (
    "docs/06-ai-signal-processing/preprocessing-spec.md",
    "docs/05-data/preprocessing-result-contract.md",
    "docs/08-validation-qa/day5-preprocessing-test-plan.md",
    "services/preprocessing-service/configs/preprocess_v0.1.yaml",
    "services/preprocessing-service/src/preprocess_config.py",
    "services/preprocessing-service/src/filters.py",
    "services/preprocessing-service/src/pipeline.py",
    "services/preprocessing-service/src/preprocess_result_models.py",
    "packages/semg-core/semg_core/preprocessing.py",
    "packages/semg-core/tests/test_preprocessing.py",
    "packages/common-schemas/json/preprocessing-result.schema.json",
    "scripts/data/run_signal_preprocessing.py",
    "scripts/data/verify_preprocessing_response.py",
    "qa-validation/requirements/day5-acceptance-criteria.md",
)


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED:
        path = ROOT / rel
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"Thiếu hoặc rỗng: {rel}")

    config_text = (ROOT / "services/preprocessing-service/configs/preprocess_v0.1.yaml").read_text(encoding="utf-8")
    required_fragments = (
        "execution: offline",
        "phase_behavior: zero_phase",
        "low_cut_hz: 20.0",
        "high_cut_hz: 400.0",
        "conditional_on_qc_reason_code",
        "resampling:\n    enabled: false",
        "rectification:\n    enabled: false",
        "envelope:\n    enabled: false",
    )
    for fragment in required_fragments:
        if fragment not in config_text:
            errors.append(f"Config thiếu guardrail: {fragment!r}")

    schema = json.loads((ROOT / "packages/common-schemas/json/preprocessing-result.schema.json").read_text(encoding="utf-8"))
    if schema.get("properties", {}).get("schema_version", {}).get("const") != "preprocessing-result.v0.1":
        errors.append("Schema version không đúng")

    notes = ROOT / "docs" / "note" / "day05"
    expected_notes = [
        "01-learning-objectives.md", "02-reading-notes.md", "03-math-notes.md",
        "04-signal-processing-notes.md", "05-clinical-notes.md", "06-questions.md",
        "07-decisions.md", "08-daily-summary.md", "09-todo-day06.md",
    ]
    for name in expected_notes:
        if not (notes / name).is_file():
            errors.append(f"Thiếu notes Day 5: {name}")

    if errors:
        print("DAY 5 ARTIFACT CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DAY 5 ARTIFACT CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
