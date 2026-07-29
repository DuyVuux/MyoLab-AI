from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from .contracts import RecordMeta


def audit_labels(records: Iterable[RecordMeta]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, set[str] | int]] = defaultdict(
        lambda: {"records": 0, "subjects": set(), "days": set()}
    )
    for row in records:
        if row.canonical_label.strip().lower() == "rest" and row.source_label.strip().lower() in {"unknown", "unsupported"}:
            raise ValueError("Không được map unknown/unsupported thành rest")
        key = (row.source_label, row.canonical_label)
        grouped[key]["records"] = int(grouped[key]["records"]) + 1
        grouped[key]["subjects"].add(row.subject_id)  # type: ignore[union-attr]
        grouped[key]["days"].add(row.day_id)  # type: ignore[union-attr]

    output: list[dict[str, Any]] = []
    for (source_label, canonical_label), values in sorted(grouped.items()):
        output.append(
            {
                "source_label": source_label,
                "canonical_label": canonical_label,
                "record_count": values["records"],
                "subject_count": len(values["subjects"]),
                "day_count": len(values["days"]),
                "analysis_eligibility": "SUPPORTED_TASK_A" if canonical_label != "unknown" else "UNKNOWN_GESTURE_AUDIT",
            }
        )
    return output
