"""Canonical long-format serialization for Day 31 features."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

from .feature_set_14_v1 import FeatureResult

ALLOWED_PARTITIONS = frozenset({"train", "validation"})
REQUIRED_METADATA = (
    "dataset_id",
    "dataset_view_id",
    "split_name",
    "subject_id",
    "day_id",
    "session_id",
    "repetition_id",
    "record_id",
    "window_id",
    "channel_id",
    "canonical_label",
    "sampling_rate_hz",
    "window_ms",
    "hop_ms",
    "preprocessing_policy_id",
    "channel_policy_id",
    "source_file_sha256",
    "split_version",
    "label_mapping_version",
)
_OPTIONAL_PROVENANCE = frozenset({"day_id", "session_id", "repetition_id"})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def validate_feature_metadata(metadata: Mapping[str, Any]) -> None:
    """Validate one window-channel provenance record before serialization."""

    missing = [name for name in REQUIRED_METADATA if name not in metadata]
    if missing:
        raise ValueError(f"missing metadata: {missing}")
    if metadata["split_name"] not in ALLOWED_PARTITIONS:
        raise PermissionError("source_partition_forbidden")

    for name in REQUIRED_METADATA:
        if name in {"sampling_rate_hz", "window_ms", "hop_ms"}:
            continue
        value = metadata[name]
        if name in _OPTIONAL_PROVENANCE and value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    source_hash = str(metadata["source_file_sha256"])
    if _SHA256.fullmatch(source_hash) is None:
        raise ValueError("source_file_sha256 must be lowercase SHA-256")
    for name in ("sampling_rate_hz", "window_ms", "hop_ms"):
        value = metadata[name]
        if isinstance(value, bool):
            raise TypeError(f"{name} must be positive and finite")
        try:
            numeric = float(value)
        except (TypeError, ValueError, OverflowError) as error:
            raise TypeError(f"{name} must be positive and finite") from error
        if not math.isfinite(numeric) or numeric <= 0.0:
            raise ValueError(f"{name} must be positive and finite")
    if not isinstance(metadata["window_ms"], int) or not isinstance(
        metadata["hop_ms"], int
    ):
        raise TypeError("window_ms and hop_ms must be integers")


def to_long_rows(
    metadata: Mapping[str, Any],
    result: FeatureResult,
) -> list[dict[str, Any]]:
    """Convert an extractor result to JSON-safe canonical long rows."""

    validate_feature_metadata(metadata)
    base = {name: metadata[name] for name in REQUIRED_METADATA}
    flags = list(result.qc_flags)
    rows: list[dict[str, Any]] = []
    for feature_id, value in result.features.items():
        rows.append(
            {
                **base,
                "feature_id": feature_id,
                "feature_value": float(value)
                if math.isfinite(value)
                else None,
                "feature_version": result.contract_version,
                "qc_flags": flags.copy(),
            }
        )
    return rows
