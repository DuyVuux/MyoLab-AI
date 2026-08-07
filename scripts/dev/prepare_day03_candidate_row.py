from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

from day03_time_motion_utils import (
    BASELINE_COLUMNS,
    calculate_observation_summary,
    load_yaml,
    sha256_file,
)


def text_value(block: object) -> str:
    if isinstance(block, dict):
        value = block.get("value")
        return "UNKNOWN" if value in {None, ""} else str(value)
    if block in {None, ""}:
        return "UNKNOWN"
    return str(block)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare one DAY03 candidate baseline row from a de-identified DAY02-style "
            "observation YAML. The generated row is always PENDING_REVIEW and not baseline "
            "eligible until an independent review accepts it."
        )
    )
    parser.add_argument("observation_yaml", type=Path)
    parser.add_argument("--row-id", required=True)
    parser.add_argument("--partial-case", choices=["true", "false"], required=True)
    parser.add_argument("--start-boundary", required=True)
    parser.add_argument("--end-boundary", required=True)
    parser.add_argument("--reviewer-role", default="UNASSIGNED")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    observation_path = args.observation_yaml.resolve()
    observation = load_yaml(observation_path)
    summary = calculate_observation_summary(observation)

    meta = observation.get("observation", {})
    context = observation.get("context", {})
    events = observation.get("events", [])

    remeasurement_reasons = [
        str(event.get("reason_reported_by_operator"))
        for event in events
        if event.get("remeasurement") is True
        and event.get("reason_reported_by_operator")
    ]

    observed_actions = [
        str(event.get("observed_action"))
        for event in events
        if event.get("observed_action")
    ]

    row = {
        "baseline_row_id": args.row_id,
        "observation_id": str(meta.get("observation_id") or "UNKNOWN"),
        "analysis_case_id": str(meta.get("analysis_case_id") or "UNKNOWN"),
        "observation_mode": str(meta.get("observation_mode") or "UNKNOWN"),
        "evidence_status": str(meta.get("evidence_status") or "UNKNOWN"),
        "governance_approval_reference": str(
            meta.get("governance_approval_reference") or "UNKNOWN"
        ),
        "source_observation_ref": observation_path.name,
        "source_sha256": sha256_file(observation_path),
        "partial_case": args.partial_case,
        "observed_start_boundary": args.start_boundary,
        "observed_end_boundary": args.end_boundary,
        "elapsed_time_sec": str(summary["elapsed_time_sec"]),
        "doctor_data_hands_on_union_sec": str(
            summary["doctor_data_hands_on_union_sec"]
        ),
        "technician_data_hands_on_union_sec": str(
            summary["technician_data_hands_on_union_sec"]
        ),
        "acquisition_hands_on_union_sec": str(
            summary["acquisition_hands_on_union_sec"]
        ),
        "system_active_union_sec": str(summary["system_active_union_sec"]),
        "waiting_blocked_union_sec": str(summary["waiting_blocked_union_sec"]),
        "remeasurement_union_sec": str(summary["remeasurement_union_sec"]),
        "clinical_interpretation_union_sec": str(
            summary["clinical_interpretation_union_sec"]
        ),
        "parallel_time_union_sec": str(summary["parallel_time_union_sec"]),
        "remeasurement_occurred": str(summary["remeasurement_occurred"]).lower(),
        "remeasurement_episode_count": str(summary["remeasurement_episode_count"]),
        "full_manual_review_required": "unknown",
        "protocol_label": text_value(context.get("protocol_label")),
        "task_label": text_value(context.get("task_label")),
        "workflow_variant": text_value(context.get("workflow_variant")),
        "reported_bottleneck_summary_non_phi": "PENDING_REVIEW",
        "reported_remeasurement_reason_non_phi": (
            " | ".join(remeasurement_reasons) if remeasurement_reasons else "NONE_OBSERVED"
        ),
        "measurement_fact_summary_non_phi": (
            " | ".join(observed_actions) if observed_actions else "NO_ACTION_TEXT_RECORDED"
        ),
        "baseline_eligible": "false",
        "baseline_exclusion_reason": "PENDING_INDEPENDENT_REVIEW",
        "reviewer_status": "PENDING_REVIEW",
        "reviewer_role": args.reviewer_role,
        "review_date": date.today().isoformat(),
        "evidence_limitations": "PENDING_INDEPENDENT_REVIEW",
        "oq_links": "OQ-001|OQ-002|OQ-003|OQ-005",
    }

    output_stream = sys.stdout
    should_close = False
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output_stream = args.output.open("w", encoding="utf-8", newline="")
        should_close = True

    try:
        writer = csv.DictWriter(output_stream, fieldnames=BASELINE_COLUMNS)
        writer.writeheader()
        writer.writerow(row)
    finally:
        if should_close:
            output_stream.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
