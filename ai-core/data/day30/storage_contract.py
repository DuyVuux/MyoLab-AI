from __future__ import annotations

from collections import defaultdict

from .contracts import ALLOWED_PARTITIONS, PROTECTED_LABELS

REQUIRED_WINDOW_COLUMNS = frozenset(
    {
        "window_id",
        "dataset_id",
        "record_id",
        "subject_id",
        "canonical_label",
        "partition",
        "signal_path",
        "source_file_sha256",
        "split_version",
        "label_mapping_version",
        "start_sample",
        "end_sample_exclusive",
        "record_n_samples",
        "sampling_rate_hz",
        "window_ms",
        "hop_ms",
        "channel_policy_id",
        "preprocessing_policy_id",
    }
)


def validate_window_rows(rows: list[dict]) -> dict:
    if not isinstance(rows, list):
        raise TypeError("rows must be a list")
    errors: list[str] = []
    window_ids: set[str] = set()
    subject_partitions: dict[str, set[str]] = defaultdict(set)

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"row_{index}_not_object")
            continue
        missing = sorted(REQUIRED_WINDOW_COLUMNS - set(row))
        if missing:
            errors.append(f"row_{index}_missing:{missing}")
            continue
        partition = row["partition"]
        if partition not in ALLOWED_PARTITIONS:
            errors.append(f"row_{index}_forbidden_partition")
        window_id = str(row["window_id"])
        if not window_id:
            errors.append(f"row_{index}_empty_window_id")
        elif window_id in window_ids:
            errors.append(f"row_{index}_duplicate_window_id")
        window_ids.add(window_id)
        subject_partitions[str(row["subject_id"])].add(str(partition))
        try:
            start = int(row["start_sample"])
            end = int(row["end_sample_exclusive"])
            record_n_samples = int(row["record_n_samples"])
            sampling_rate = float(row["sampling_rate_hz"])
        except (TypeError, ValueError):
            errors.append(f"row_{index}_invalid_numeric_value")
            continue
        if start < 0 or end <= start:
            errors.append(f"row_{index}_invalid_bounds")
        if end > record_n_samples:
            errors.append(f"row_{index}_exceeds_record")
        if record_n_samples < 0 or sampling_rate <= 0:
            errors.append(f"row_{index}_invalid_record_contract")
        if str(row["canonical_label"]).lower() in PROTECTED_LABELS:
            errors.append(f"row_{index}_protected_label")

    for subject_id, partitions in sorted(subject_partitions.items()):
        if len(partitions) > 1:
            errors.append(f"subject_partition_overlap:{subject_id}")
    return {"pass": not errors, "errors": errors, "row_count": len(rows)}

