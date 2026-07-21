#!/usr/bin/env python3
"""Kiểm tra artifact và safety invariants Day 6."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Mapping

import yaml

ROOT = Path(__file__).resolve().parents[2]

STATIC_FILES = [
    "docs/plans/DAY6_EXECUTION_PLAN.md",
    "docs/03-architecture/adr/ADR-0008-freeze-preprocess-v0.1-after-analytical-verification.md",
    "docs/06-ai-signal-processing/preprocessing-verification-spec.md",
    "docs/06-ai-signal-processing/filter-response-math-primer.md",
    "docs/08-validation-qa/day6-preprocessing-verification-test-plan.md",
    "docs/09-mlops-devops/dsp-reproducibility-policy.md",
    "qa-validation/configs/preprocess_verification_v0.1.yaml",
    "packages/common-schemas/json/preprocessing-verification-report.schema.json",
    "qa-validation/requirements/day6-acceptance-criteria.md",
    "qa-validation/automated-tests/test_preprocessing_analytical.py",
    "scripts/data/verify_preprocess_v0_1.py",
    "scripts/dev/capture_dsp_environment.py",
    "scripts/dev/freeze_preprocess_v0_1.py",
]
GENERATED_FILES = [
    "qa-validation/evidence/day6-preprocessing-verification.json",
    "qa-validation/evidence/day6-filter-verification.md",
    "qa-validation/evidence/day6-dsp-environment.json",
    "ai-core/validation-reports/analytical_validation_preprocessing_v0.1.md",
    "mlops/registry/preprocessing_configs.yaml",
]


def fail(message: str) -> None:
    raise SystemExit(f"DAY 6 ARTIFACT CHECK FAILED: {message}")


def main() -> int:
    missing = [path for path in STATIC_FILES + GENERATED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail(f"Thiếu file: {missing}")

    config = yaml.safe_load((ROOT / "services/preprocessing-service/configs/preprocess_v0.1.yaml").read_text(encoding="utf-8"))
    if config.get("clinical_validation_status") != "not_validated":
        fail("preprocess_v0.1 không được claim clinical validation")
    if config.get("mode", {}).get("execution") != "offline":
        fail("preprocess_v0.1 phải giữ offline execution")
    if config.get("mode", {}).get("realtime_compatible") is not False:
        fail("preprocess_v0.1 không được claim realtime compatible")

    verification = json.loads((ROOT / GENERATED_FILES[0]).read_text(encoding="utf-8"))
    if verification.get("overall", {}).get("all_passed") is not True:
        fail("Verification overall chưa pass")
    if verification.get("overall", {}).get("clinical_validation_status") != "not_validated":
        fail("Verification report có clinical claim sai")

    registry = yaml.safe_load((ROOT / GENERATED_FILES[-1]).read_text(encoding="utf-8"))
    if not isinstance(registry, Mapping):
        fail("Registry root không phải object")
    entries = [item for item in registry.get("preprocessing_configs", []) if isinstance(item, Mapping) and item.get("config_id") == "preprocess_v0.1"]
    if len(entries) != 1:
        fail("Registry phải có đúng một entry preprocess_v0.1")
    entry = entries[0]
    if entry.get("lifecycle_status") != "frozen_for_mvp0":
        fail("Lifecycle status không đúng")
    if entry.get("analytically_verified_for_mvp0") is not True:
        fail("Registry chưa ghi analytical pass")
    if entry.get("clinical_validation_status") != "not_validated":
        fail("Registry có clinical claim sai")
    if entry.get("realtime_compatible") is not False:
        fail("Registry có realtime claim sai")

    required_phrase = "không phải xác nhận lâm sàng"
    evidence_text = (ROOT / "qa-validation/evidence/day6-filter-verification.md").read_text(encoding="utf-8").lower()
    if required_phrase not in evidence_text:
        fail("Evidence Markdown thiếu safety statement tiếng Việt")

    note_files = sorted((ROOT / "docs/note/day06").glob("*.md"))
    if len(note_files) < 9:
        fail("Thiếu bộ notes Day 6")

    print("DAY 6 ARTIFACT CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
