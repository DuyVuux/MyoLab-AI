from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


BASELINE_COLUMNS = [
    "baseline_row_id",
    "observation_id",
    "analysis_case_id",
    "observation_mode",
    "evidence_status",
    "governance_approval_reference",
    "source_observation_ref",
    "source_sha256",
    "partial_case",
    "observed_start_boundary",
    "observed_end_boundary",
    "elapsed_time_sec",
    "doctor_data_hands_on_union_sec",
    "technician_data_hands_on_union_sec",
    "acquisition_hands_on_union_sec",
    "system_active_union_sec",
    "waiting_blocked_union_sec",
    "remeasurement_union_sec",
    "clinical_interpretation_union_sec",
    "parallel_time_union_sec",
    "remeasurement_occurred",
    "remeasurement_episode_count",
    "full_manual_review_required",
    "protocol_label",
    "task_label",
    "workflow_variant",
    "reported_bottleneck_summary_non_phi",
    "reported_remeasurement_reason_non_phi",
    "measurement_fact_summary_non_phi",
    "baseline_eligible",
    "baseline_exclusion_reason",
    "reviewer_status",
    "reviewer_role",
    "review_date",
    "evidence_limitations",
    "oq_links",
]

BASELINE_ELIGIBLE_MODES = {
    "DIRECT_OBSERVATION",
    "RETROSPECTIVE_WORKFLOW_RECONSTRUCTION",
}

BASELINE_ELIGIBLE_REVIEW_STATUS = "ACCEPTED_FOR_ROUND1_BASELINE"


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML object in {path}")
    return data


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def interval_union_seconds(intervals: Iterable[tuple[datetime, datetime]]) -> float:
    ordered = sorted(intervals, key=lambda item: item[0])
    if not ordered:
        return 0.0

    total = 0.0
    current_start, current_end = ordered[0]
    if current_end < current_start:
        raise ValueError("Interval end precedes start")

    for start, end in ordered[1:]:
        if end < start:
            raise ValueError("Interval end precedes start")
        if start <= current_end:
            current_end = max(current_end, end)
            continue
        total += (current_end - current_start).total_seconds()
        current_start, current_end = start, end

    total += (current_end - current_start).total_seconds()
    return total


def event_intervals(
    observation: dict[str, Any],
    *,
    time_class: str | None = None,
) -> list[tuple[datetime, datetime]]:
    intervals: list[tuple[datetime, datetime]] = []
    for event in observation.get("events", []):
        if time_class is not None and event.get("time_class") != time_class:
            continue
        start_value = event.get("start_timestamp")
        end_value = event.get("end_timestamp")
        if not start_value or not end_value:
            continue
        intervals.append(
            (
                parse_timestamp(start_value),
                parse_timestamp(end_value),
            )
        )
    return intervals


def calculate_observation_summary(observation: dict[str, Any]) -> dict[str, float | int | bool]:
    meta = observation.get("observation", {})
    start_value = meta.get("observation_start")
    end_value = meta.get("observation_end")
    if not start_value or not end_value:
        raise ValueError("Observation start/end are required for a calculated summary")

    start = parse_timestamp(start_value)
    end = parse_timestamp(end_value)
    if end < start:
        raise ValueError("Observation end precedes start")

    classes = {
        "doctor_data_hands_on_union_sec": "CLINICIAN_DATA_HANDS_ON",
        "technician_data_hands_on_union_sec": "TECHNICIAN_DATA_HANDS_ON",
        "acquisition_hands_on_union_sec": "ACQUISITION_HANDS_ON",
        "system_active_union_sec": "SYSTEM_ACTIVE",
        "waiting_blocked_union_sec": "WAITING_BLOCKED",
        "remeasurement_union_sec": "REMEASUREMENT",
        "clinical_interpretation_union_sec": "CLINICAL_INTERPRETATION",
    }

    summary: dict[str, float | int | bool] = {
        "elapsed_time_sec": (end - start).total_seconds(),
    }
    for output_name, time_class in classes.items():
        summary[output_name] = interval_union_seconds(
            event_intervals(observation, time_class=time_class)
        )

    all_intervals = event_intervals(observation)
    naive_sum = sum((end_i - start_i).total_seconds() for start_i, end_i in all_intervals)
    union_all = interval_union_seconds(all_intervals)
    summary["parallel_time_union_sec"] = max(0.0, naive_sum - union_all)

    remeasure_events = [
        event
        for event in observation.get("events", [])
        if event.get("remeasurement") is True
    ]
    episode_ids = {
        event.get("remeasurement_episode_id")
        for event in remeasure_events
        if event.get("remeasurement_episode_id")
    }
    summary["remeasurement_occurred"] = bool(remeasure_events)
    summary["remeasurement_episode_count"] = len(episode_ids)
    return summary


def read_baseline_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        if reader.fieldnames != BASELINE_COLUMNS:
            raise ValueError("DAY03 baseline CSV header does not match the frozen contract")
        return list(reader)


def baseline_eligible_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("baseline_eligible", "").lower() == "true"
        and row.get("observation_mode") in BASELINE_ELIGIBLE_MODES
        and row.get("reviewer_status") == BASELINE_ELIGIBLE_REVIEW_STATUS
    ]


def determine_gate_status(rows: Iterable[dict[str, str]]) -> str:
    rows_list = list(rows)
    if not baseline_eligible_rows(rows_list):
        return "BLOCKED_WITH_EVIDENCE"
    return "GO_FOR_DAY_04"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data
