#!/usr/bin/env python3
"""Verify the Day 4 artifact inventory and safety-critical markers."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "docs/00-executive/day4-decision-log-append.md",
    "docs/01-product/backlog/day4-backlog.md",
    "docs/05-data/qc-result-contract.md",
    "docs/06-ai-signal-processing/signal-quality-gate-spec.md",
    "docs/08-validation-qa/day4-qc-test-plan.md",
    "packages/semg-core/semg_core/qc.py",
    "packages/semg-core/tests/test_qc.py",
    "services/quality-gate-service/src/result_models.py",
    "services/quality-gate-service/src/config_loader.py",
    "services/quality-gate-service/src/quality_gate.py",
    "services/quality-gate-service/src/checks/protocol_compatibility_check.py",
    "services/quality-gate-service/src/checks/sampling_rate_check.py",
    "services/quality-gate-service/src/checks/duration_check.py",
    "services/quality-gate-service/src/checks/channel_completeness_check.py",
    "services/quality-gate-service/src/checks/nonfinite_check.py",
    "services/quality-gate-service/src/checks/flatline_check.py",
    "services/quality-gate-service/src/checks/clipping_saturation_check.py",
    "services/quality-gate-service/src/checks/powerline_noise_check.py",
    "services/quality-gate-service/src/checks/motion_artifact_check.py",
    "services/quality-gate-service/src/checks/baseline_noise_check.py",
    "services/quality-gate-service/src/checks/cv_eligibility_check.py",
    "services/quality-gate-service/tests/test_quality_gate.py",
    "qa-validation/test-data/synthetic/generate_qc_fixtures.py",
    "qa-validation/requirements/day4-acceptance-criteria.md",
    "qa-validation/evidence/day4-qc-evidence.template.md",
    "scripts/data/run_signal_qc.py",
    "scripts/dev/run_day4_checks.sh",
]

GENERATED_FIXTURE_STEMS = [
    "qc_fail_nonfinite",
    "qc_fail_flatline",
    "qc_warning_clipping",
    "qc_warning_powerline",
    "qc_warning_motion_artifact",
    "qc_fail_short_duration",
]

NOTE_FILES = [
    "01-learning-objectives.md",
    "02-reading-notes.md",
    "03-math-notes.md",
    "04-signal-processing-notes.md",
    "05-clinical-notes.md",
    "06-questions.md",
    "07-decisions.md",
    "08-daily-summary.md",
    "09-todo-day05.md",
]


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"Missing required file: {relative}")

    for name in NOTE_FILES:
        path = ROOT / "docs/note/day04" / name
        if not path.is_file():
            errors.append(f"Missing Day 4 note: {path.relative_to(ROOT)}")

    fixture_dir = ROOT / "qa-validation/test-data/synthetic"
    for stem in GENERATED_FIXTURE_STEMS:
        csv_path = fixture_dir / f"{stem}.csv"
        manifest_path = fixture_dir / f"{stem}.manifest.json"
        if not csv_path.is_file():
            errors.append(f"Missing generated fixture: {csv_path.relative_to(ROOT)}")
        if not manifest_path.is_file():
            errors.append(f"Missing generated manifest: {manifest_path.relative_to(ROOT)}")
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid fixture manifest {manifest_path}: {exc}")
            continue
        if manifest.get("clinical_use_allowed") is not False:
            errors.append(
                f"Fixture must set clinical_use_allowed=false: {manifest_path.relative_to(ROOT)}"
            )
        if manifest.get("data_source") != "synthetic":
            errors.append(f"Fixture must be synthetic: {manifest_path.relative_to(ROOT)}")

    gate_source = (ROOT / "services/quality-gate-service/src/quality_gate.py")
    if gate_source.is_file():
        text = gate_source.read_text(encoding="utf-8")
        for marker in (
            "signal_or_protocol_not_sufficient",
            "mfcv_ineligibility_blocks_basic_semg",
            "analysis_allowed = False",
        ):
            if marker not in text:
                errors.append(f"Safety marker missing from quality_gate.py: {marker}")

    config_path = ROOT / "services/quality-gate-service/configs/qc_v0.1.yaml"
    if config_path.is_file():
        config_text = config_path.read_text(encoding="utf-8")
        for marker in (
            "clinical_validation_status: not_validated",
            "critical_failure_blocks_analysis: true",
            "mfcv_ineligibility_blocks_basic_semg: false",
            "absolute_amplitude_thresholds_enabled: false",
        ):
            if marker not in config_text:
                errors.append(f"QC config safety marker missing: {marker}")

    if errors:
        print("DAY 4 ARTIFACT CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("DAY 4 ARTIFACT CHECK PASSED")
    print(f"Checked {len(REQUIRED_FILES)} required files, {len(NOTE_FILES)} notes, and {len(GENERATED_FIXTURE_STEMS)} fixtures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
