from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

import pandas as pd

CORE_CLASSES = ["rest", "hand_close", "wrist_flexion", "wrist_extension"]


@dataclass
class LabelAuditSummary:
    row_count: int
    subject_count: int
    source_labels: list[str]
    canonical_labels: list[str]
    core_classes_present: list[str]
    core_classes_missing: list[str]
    hand_open_supported: bool
    unknown_row_count: int
    test_rows_loaded: int
    subjects_missing_core_classes: dict[str, list[str]]


def audit_labels(metadata: pd.DataFrame, allowed_partitions: Iterable[str]) -> LabelAuditSummary:
    required = {"subject_id", "source_label", "canonical_label", "partition"}
    missing = sorted(required - set(metadata.columns))
    if missing:
        raise ValueError(f"Metadata missing columns: {missing}")
    allowed = set(allowed_partitions)
    test_rows = int((metadata["partition"] == "test").sum())
    if test_rows:
        raise ValueError("Sealed test rows are present in EDA input")
    invalid_partitions = sorted(set(metadata["partition"].dropna().astype(str)) - allowed)
    if invalid_partitions:
        raise ValueError(f"Unexpected partitions in EDA input: {invalid_partitions}")

    source_labels = sorted(metadata["source_label"].dropna().astype(str).unique().tolist())
    canonical_labels = sorted(metadata["canonical_label"].dropna().astype(str).unique().tolist())
    present = sorted(set(CORE_CLASSES) & set(canonical_labels))
    missing_core = sorted(set(CORE_CLASSES) - set(canonical_labels))
    missing_by_subject: dict[str, list[str]] = {}
    for subject_id, group in metadata.groupby("subject_id", dropna=False):
        subject_classes = set(group["canonical_label"].dropna().astype(str))
        missing_for_subject = sorted(set(CORE_CLASSES) - subject_classes)
        if missing_for_subject:
            missing_by_subject[str(subject_id)] = missing_for_subject

    return LabelAuditSummary(
        row_count=int(len(metadata)),
        subject_count=int(metadata["subject_id"].nunique(dropna=True)),
        source_labels=source_labels,
        canonical_labels=canonical_labels,
        core_classes_present=present,
        core_classes_missing=missing_core,
        hand_open_supported="hand_open" in canonical_labels,
        unknown_row_count=int((metadata["canonical_label"] == "unknown").sum()),
        test_rows_loaded=test_rows,
        subjects_missing_core_classes=missing_by_subject,
    )


def summary_to_dict(summary: LabelAuditSummary) -> dict[str, object]:
    return asdict(summary)
