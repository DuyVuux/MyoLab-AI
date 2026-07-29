from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable

from .contracts import RecordMeta


def audit_hierarchy(records: Iterable[RecordMeta]) -> dict[str, Any]:
    rows = list(records)
    record_ids = [row.record_id for row in rows]
    natural_keys = [
        (row.subject_id, row.day_id, row.session_id, row.repetition_id, row.canonical_label)
        for row in rows
    ]
    subjects = sorted({row.subject_id for row in rows})
    days = sorted({row.day_id for row in rows})
    labels = sorted({row.canonical_label for row in rows})

    subject_days: dict[str, set[str]] = defaultdict(set)
    subject_day_labels: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        subject_days[row.subject_id].add(row.day_id)
        subject_day_labels[(row.subject_id, row.day_id)].add(row.canonical_label)

    duplicate_record_ids = sorted(key for key, count in Counter(record_ids).items() if count > 1)
    duplicate_natural_keys = [
        {"subject_id": key[0], "day_id": key[1], "session_id": key[2], "repetition_id": key[3], "canonical_label": key[4]}
        for key, count in Counter(natural_keys).items()
        if count > 1
    ]

    missing_required_ids = [
        row.record_id
        for row in rows
        if not all([row.subject_id, row.day_id, row.session_id, row.repetition_id])
    ]

    status = "VERIFIED"
    if duplicate_record_ids or duplicate_natural_keys or missing_required_ids:
        status = "CONFLICTING"
    elif any(len(value) < 2 for value in subject_days.values()):
        status = "PARTIAL"

    return {
        "status": status,
        "record_count": len(rows),
        "subject_count": len(subjects),
        "day_count": len(days),
        "canonical_labels": labels,
        "duplicate_record_ids": duplicate_record_ids,
        "duplicate_natural_keys": duplicate_natural_keys,
        "missing_required_ids": missing_required_ids,
        "days_per_subject": {key: sorted(value) for key, value in sorted(subject_days.items())},
        "labels_per_subject_day": {
            f"{subject}|{day}": sorted(value)
            for (subject, day), value in sorted(subject_day_labels.items())
        },
    }
