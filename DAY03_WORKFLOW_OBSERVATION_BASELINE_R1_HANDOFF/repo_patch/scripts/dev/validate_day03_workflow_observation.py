from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import jsonschema

from day03_time_motion_utils import (
    BASELINE_COLUMNS,
    baseline_eligible_rows,
    determine_gate_status,
    read_baseline_rows,
)


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "clinical/studies/time-motion-baseline-round1.csv"
EVIDENCE_LOG = ROOT / "clinical/workflows/current-workflow-evidence-log.md"
BURNDOWN = ROOT / "docs/02-clinical/discovery/open-questions-burndown.md"
TRACE = ROOT / "docs/03-architecture/traceability/day03-workflow-observation-traceability.v0.1.csv"
SCHEMA = ROOT / "packages/common-schemas/json/day03-time-motion-baseline-row.schema.json"
REPORT = ROOT / "qa-validation/evidence/day03-validation-report.json"


def parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def parse_number(value: str) -> float:
    return float(value)


def parse_integer(value: str) -> int:
    return int(value)


def normalized_row(row: dict[str, str]) -> dict[str, object]:
    data: dict[str, object] = dict(row)
    numeric_fields = {
        "elapsed_time_sec",
        "doctor_data_hands_on_union_sec",
        "technician_data_hands_on_union_sec",
        "acquisition_hands_on_union_sec",
        "system_active_union_sec",
        "waiting_blocked_union_sec",
        "remeasurement_union_sec",
        "clinical_interpretation_union_sec",
        "parallel_time_union_sec",
    }
    for field in numeric_fields:
        data[field] = parse_number(row[field])
    data["remeasurement_episode_count"] = parse_integer(row["remeasurement_episode_count"])
    return data


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    direct_phi_field_tokens = {
        "patient_name",
        "mrn",
        "date_of_birth",
        "email",
        "phone",
        "address",
    }
    if direct_phi_field_tokens.intersection(BASELINE_COLUMNS):
        failures.append("Baseline contract contains direct-PHI field names")

    seen_row_ids: set[str] = set()
    seen_observation_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        if not all(row.get(column, "") != "" for column in BASELINE_COLUMNS):
            failures.append(f"Row {index} contains blank required fields")
            continue

        try:
            validator.validate(normalized_row(row))
        except Exception as exc:  # noqa: BLE001 - preserve validation details
            failures.append(f"Row {index} schema validation failed: {exc}")
            continue

        row_id = row["baseline_row_id"]
        obs_id = row["observation_id"]
        if row_id in seen_row_ids:
            failures.append(f"Duplicate baseline_row_id: {row_id}")
        if obs_id in seen_observation_ids:
            failures.append(f"Duplicate observation_id: {obs_id}")
        seen_row_ids.add(row_id)
        seen_observation_ids.add(obs_id)

        elapsed = float(row["elapsed_time_sec"])
        class_fields = [
            "doctor_data_hands_on_union_sec",
            "technician_data_hands_on_union_sec",
            "acquisition_hands_on_union_sec",
            "system_active_union_sec",
            "waiting_blocked_union_sec",
            "remeasurement_union_sec",
            "clinical_interpretation_union_sec",
        ]
        for field in class_fields:
            if float(row[field]) > elapsed:
                failures.append(f"Row {index}: {field} exceeds elapsed time")

        eligible = row["baseline_eligible"].lower() == "true"
        if eligible:
            if row["observation_mode"] not in {
                "DIRECT_OBSERVATION",
                "RETROSPECTIVE_WORKFLOW_RECONSTRUCTION",
            }:
                failures.append(f"Row {index}: ineligible observation mode marked baseline eligible")
            if row["reviewer_status"] != "ACCEPTED_FOR_ROUND1_BASELINE":
                failures.append(f"Row {index}: baseline eligible without accepted review")
            if row["source_sha256"] == "0" * 64:
                failures.append(f"Row {index}: placeholder source hash is not acceptable")

    return failures


def main() -> int:
    failures: list[str] = []
    for required_path in [BASELINE, EVIDENCE_LOG, BURNDOWN, TRACE, SCHEMA]:
        if not required_path.is_file():
            failures.append(f"Missing required artifact: {required_path.relative_to(ROOT)}")

    rows: list[dict[str, str]] = []
    if BASELINE.is_file():
        try:
            rows = read_baseline_rows(BASELINE)
        except Exception as exc:  # noqa: BLE001
            failures.append(str(exc))

    if not failures:
        failures.extend(validate_rows(rows))

    gate_status = "VALIDATION_FAILED"
    if not failures:
        gate_status = determine_gate_status(rows)

    eligible_count = len(baseline_eligible_rows(rows)) if not failures else 0
    report = {
        "version": "0.1",
        "day": "DAY03",
        "status": gate_status,
        "meaning": (
            "Round-1 observation evidence is sufficient to proceed to DAY04."
            if gate_status == "GO_FOR_DAY_04"
            else "DAY03 tooling/contracts are valid but no reviewed baseline-eligible site evidence is present."
            if gate_status == "BLOCKED_WITH_EVIDENCE"
            else "DAY03 validation failed."
        ),
        "baseline_rows_total": len(rows),
        "baseline_eligible_rows": eligible_count,
        "baseline_measured": eligible_count > 0,
        "representativeness_claimed": False,
        "sixty_minute_value_status": "TEAM_ESTIMATE_NOT_BASELINE",
        "fifty_percent_target_status": "RESEARCH_TARGET_NOT_COMMITTED",
        "training_executed": False,
        "raw_patient_data_required_by_pack": False,
        "mfcv_site_eligibility": "NOT_VERIFIED",
        "knee_algorithm_authorized": False,
        "validation_failures": failures,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
