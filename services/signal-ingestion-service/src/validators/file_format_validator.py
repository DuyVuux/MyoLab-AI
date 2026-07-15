"""Strict Generic CSV v0.1 parser and source-integrity helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
from typing import Iterable

import numpy as np

from semg_core.validation import ValidationIssue


@dataclass(frozen=True, slots=True)
class ParsedCSV:
    time_s: np.ndarray
    channels: dict[str, np.ndarray]
    source_hash_sha256: str


def compute_sha256(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_signal_value(raw: str) -> float:
    value = raw.strip()
    if value == "":
        return float("nan")
    return float(value)


def parse_generic_csv(
    csv_path: Path,
    *,
    time_column: str,
    channel_columns: Iterable[str],
) -> tuple[ParsedCSV | None, list[ValidationIssue]]:
    if not csv_path.is_file():
        return None, [
            ValidationIssue("SIGNAL_FILE_NOT_FOUND", f"Signal file not found: {csv_path}")
        ]

    channels_requested = list(channel_columns)
    times: list[float] = []
    channel_values: dict[str, list[float]] = {
        column: [] for column in channels_requested
    }
    issues: list[ValidationIssue] = []

    try:
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration:
                return None, [ValidationIssue("CSV_PARSE_ERROR", "CSV file is empty")]

            if len(header) != len(set(header)):
                return None, [
                    ValidationIssue("CSV_HEADER_INVALID", "CSV header contains duplicates")
                ]
            if time_column not in header:
                return None, [
                    ValidationIssue(
                        "CSV_HEADER_INVALID",
                        f"Time column {time_column!r} not found; headers={header}",
                    )
                ]
            missing = [column for column in channels_requested if column not in header]
            if missing:
                return None, [
                    ValidationIssue(
                        "CHANNEL_COLUMN_MISSING",
                        f"Missing channel columns: {', '.join(missing)}",
                    )
                ]

            indexes = {name: header.index(name) for name in [time_column, *channels_requested]}
            expected_width = len(header)
            for row_number, row in enumerate(reader, start=2):
                if len(row) != expected_width:
                    return None, [
                        ValidationIssue(
                            "CSV_PARSE_ERROR",
                            f"Row {row_number} has {len(row)} columns; expected {expected_width}",
                        )
                    ]
                try:
                    time_value = float(row[indexes[time_column]])
                except (TypeError, ValueError):
                    return None, [
                        ValidationIssue(
                            "CSV_PARSE_ERROR",
                            f"Non-numeric timestamp at row {row_number}",
                        )
                    ]
                if not math.isfinite(time_value):
                    return None, [
                        ValidationIssue(
                            "TIME_VALUE_NONFINITE",
                            f"Timestamp at row {row_number} is non-finite",
                        )
                    ]
                times.append(time_value)

                for column in channels_requested:
                    try:
                        parsed = _parse_signal_value(row[indexes[column]])
                    except ValueError:
                        parsed = float("nan")
                        issues.append(
                            ValidationIssue(
                                "SIGNAL_VALUE_NONNUMERIC",
                                f"Non-numeric signal value in {column} at row {row_number}; converted to NaN",
                                blocking=False,
                            )
                        )
                    channel_values[column].append(parsed)
    except (OSError, csv.Error) as exc:
        return None, [ValidationIssue("CSV_PARSE_ERROR", str(exc))]

    if len(times) < 2:
        return None, [
            ValidationIssue("CSV_PARSE_ERROR", "At least two rows of samples are required")
        ]

    time_array = np.asarray(times, dtype=np.float64)
    parsed_channels = {
        column: np.asarray(values, dtype=np.float64)
        for column, values in channel_values.items()
    }
    for column, values in parsed_channels.items():
        if not np.any(np.isfinite(values)):
            issues.append(
                ValidationIssue(
                    "NO_USABLE_SIGNAL_CHANNEL",
                    f"Column {column} contains no finite samples",
                )
            )

    try:
        source_hash = compute_sha256(csv_path)
    except OSError as exc:
        return None, [ValidationIssue("FILE_NOT_READABLE", str(exc))]

    return (
        ParsedCSV(
            time_s=time_array,
            channels=parsed_channels,
            source_hash_sha256=source_hash,
        ),
        issues,
    )
