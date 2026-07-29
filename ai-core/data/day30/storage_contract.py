from __future__ import annotations

import re
from collections import defaultdict
from math import isfinite

from .contracts import ALLOWED_PARTITIONS, PROJECT_CLASS_ORDER
from .sample_rate import samples_for_ms
from .windowing import FORBIDDEN_PATH_COMPONENTS, SHA256_PATTERN

WINDOW_ID_PATTERN = re.compile(r"^[0-9a-f]{24}$")

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


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _contains_forbidden_path_component(path: object) -> bool:
    components = {
        component.lower()
        for component in re.split(r"[\\/]+", str(path))
        if component
    }
    return bool(components & FORBIDDEN_PATH_COMPONENTS)


def validate_window_rows(rows: list[dict]) -> dict:
    if not isinstance(rows, list):
        raise TypeError("rows must be a list")
    errors: list[str] = []
    window_ids: set[str] = set()
    subject_partitions: dict[tuple[str, str], set[str]] = defaultdict(set)

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
        if not WINDOW_ID_PATTERN.fullmatch(window_id):
            errors.append(f"row_{index}_invalid_window_id")
        elif window_id in window_ids:
            errors.append(f"row_{index}_duplicate_window_id")
        window_ids.add(window_id)

        for field in (
            "dataset_id",
            "record_id",
            "subject_id",
            "split_version",
            "label_mapping_version",
            "channel_policy_id",
            "preprocessing_policy_id",
        ):
            if not str(row[field]).strip():
                errors.append(f"row_{index}_empty_{field}")

        if not str(row["signal_path"]).strip():
            errors.append(f"row_{index}_empty_signal_path")
        elif _contains_forbidden_path_component(row["signal_path"]):
            errors.append(f"row_{index}_forbidden_signal_path")

        source_sha256 = str(row["source_file_sha256"])
        if not SHA256_PATTERN.fullmatch(source_sha256) or source_sha256.lower() != source_sha256:
            errors.append(f"row_{index}_invalid_source_file_sha256")

        canonical_label = str(row["canonical_label"]).strip().lower()
        if canonical_label not in PROJECT_CLASS_ORDER:
            errors.append(f"row_{index}_invalid_canonical_label")

        integer_fields = (
            "start_sample",
            "end_sample_exclusive",
            "record_n_samples",
            "window_ms",
            "hop_ms",
        )
        integer_values: dict[str, int] = {}
        for field in integer_fields:
            value = row[field]
            if not _is_integer(value):
                errors.append(f"row_{index}_invalid_{field}")
            else:
                integer_values[field] = value

        sampling_rate_value = row["sampling_rate_hz"]
        sampling_rate_valid = (
            isinstance(sampling_rate_value, (int, float))
            and not isinstance(sampling_rate_value, bool)
            and isfinite(float(sampling_rate_value))
            and float(sampling_rate_value) > 0
        )
        if not sampling_rate_valid:
            errors.append(f"row_{index}_invalid_sampling_rate_hz")

        for field in ("window_ms", "hop_ms"):
            if field in integer_values and integer_values[field] <= 0:
                errors.append(f"row_{index}_invalid_{field}")

        bounds_fields = {"start_sample", "end_sample_exclusive", "record_n_samples"}
        if bounds_fields <= integer_values.keys():
            start = integer_values["start_sample"]
            end = integer_values["end_sample_exclusive"]
            record_n_samples = integer_values["record_n_samples"]
            if start < 0 or end <= start or record_n_samples < 1:
                errors.append(f"row_{index}_invalid_bounds")
            if end > record_n_samples:
                errors.append(f"row_{index}_exceeds_record")
            if sampling_rate_valid and integer_values.get("window_ms", 0) > 0:
                expected_length = samples_for_ms(
                    float(sampling_rate_value), integer_values["window_ms"]
                )
                if end - start != expected_length:
                    errors.append(f"row_{index}_window_length_mismatch")

        dataset_id = str(row["dataset_id"]).strip()
        subject_id = str(row["subject_id"]).strip()
        if dataset_id and subject_id and partition in ALLOWED_PARTITIONS:
            subject_partitions[(dataset_id, subject_id)].add(str(partition))

    for (_, subject_id), partitions in sorted(subject_partitions.items()):
        if len(partitions) > 1:
            errors.append(f"subject_partition_overlap:{subject_id}")
    return {"pass": not errors, "errors": errors, "row_count": len(rows)}

