#!/usr/bin/env python3
"""Kiểm tra artifact và invariant an toàn của Day 7."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "docs/06-ai-signal-processing/windowing-math-primer.md",
    "docs/06-ai-signal-processing/segmentation-windowing-spec.md",
    "docs/05-data/windowing-result-contract.md",
    "docs/08-validation-qa/day7-windowing-test-plan.md",
    "docs/03-architecture/adr/ADR-0009-fixed-half-open-window-plan-v0.1.md",
    "services/feature-extraction-service/README.md",
    "services/feature-extraction-service/configs/windowing_v0.1.yaml",
    "services/feature-extraction-service/src/window_config.py",
    "services/feature-extraction-service/src/window_result_models.py",
    "services/feature-extraction-service/src/windowing.py",
    "packages/semg-core/semg_core/windowing.py",
    "packages/common-schemas/json/windowing-result.schema.json",
    "scripts/data/run_signal_windowing.py",
    "scripts/data/verify_window_geometry.py",
    "scripts/dev/run_day7_checks.sh",
    "qa-validation/requirements/day7-acceptance-criteria.md",
]

NOTE_FILES = [
    f"docs/notes/day07/{index:02d}-{name}.md"
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
            "todo-day08",
        ),
        start=1,
    )
]


def _profile_map(plan: dict) -> dict[str, dict]:
    return {
        item["profile_id"]: item
        for item in plan.get("profiles", [])
        if isinstance(item, dict) and "profile_id" in item
    }


def main() -> int:
    errors: list[str] = []
    for relative in [*REQUIRED, *NOTE_FILES]:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"Thiếu file: {relative}")
        elif path.stat().st_size == 0:
            errors.append(f"File rỗng: {relative}")

    config_path = (
        ROOT
        / "services"
        / "feature-extraction-service"
        / "configs"
        / "windowing_v0.1.yaml"
    )
    if config_path.is_file():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        profiles = config.get("profiles", {})
        invariants = {
            "clinical_validation_status_not_validated": (
                config.get("clinical_validation_status") == "not_validated"
            ),
            "half_open": (
                config.get("segmentation", {}).get("phase_boundary_convention")
                == "half_open"
            ),
            "protocol_alignment_enabled": (
                config.get("protocol_alignment", {}).get(
                    "validate_default_windowing"
                )
                is True
            ),
            "two_profiles_exact": set(profiles) == {
                "time_domain",
                "frequency_domain",
            },
            "time_profile_500ms": (
                profiles.get("time_domain", {}).get("duration_ms") == 500
            ),
            "frequency_profile_1000ms": (
                profiles.get("frequency_domain", {}).get("duration_ms") == 1000
            ),
            "both_partial_windows_disabled": all(
                item.get("allow_partial_final_window") is False
                for item in profiles.values()
            ) if profiles else False,
            "taper_not_applied": (
                config.get("feature_preparation", {}).get(
                    "apply_taper_during_windowing"
                )
                is False
            ),
            "raw_samples_not_in_json": (
                config.get("output_contract", {}).get(
                    "include_raw_samples_in_json"
                )
                is False
            ),
        }
        for name, ok in invariants.items():
            if not ok:
                errors.append(f"Invariant fail: {name}")

    evidence = ROOT / "qa-validation/evidence/day7-windowing-result.json"
    if evidence.is_file():
        payload = json.loads(evidence.read_text(encoding="utf-8"))
        serialized = json.dumps(payload, ensure_ascii=False)
        if "samples_uV" in serialized:
            errors.append("Windowing JSON chứa raw samples_uV")
        plan = payload.get("plan")
        if payload.get("status") == "completed" and not plan:
            errors.append("Completed output thiếu plan")
        if isinstance(plan, dict):
            profiles = _profile_map(plan)
            expected = {
                "time_domain": (500, 250, 239),
                "frequency_domain": (1000, 500, 119),
            }
            if set(profiles) != set(expected):
                errors.append(f"Sai profile set: {sorted(profiles)}")
            for profile_id, (window, hop, count) in expected.items():
                profile = profiles.get(profile_id, {})
                observed = profile.get("windowing", {})
                if observed.get("window_size_samples") != window:
                    errors.append(f"{profile_id}: sai window_size_samples")
                if observed.get("hop_size_samples") != hop:
                    errors.append(f"{profile_id}: sai hop_size_samples")
                if observed.get("window_count") != count:
                    errors.append(f"{profile_id}: sai window_count")

    geometry = ROOT / "qa-validation/evidence/day7-window-geometry.json"
    if geometry.is_file():
        payload = json.loads(geometry.read_text(encoding="utf-8"))
        if payload.get("status") != "pass":
            errors.append("Geometry verification không PASS")

    if errors:
        print("DAY 7 ARTIFACT CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("DAY 7 ARTIFACT CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
