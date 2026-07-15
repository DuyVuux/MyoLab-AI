"""Manifest and privacy validation for Generic CSV v0.1."""

from __future__ import annotations

import json
import math
from pathlib import Path
import re
from typing import Any, Mapping

from semg_core.validation import ValidationIssue

from normalizers.unit_normalizer import supported_units


REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "session_id",
    "data_source",
    "signal_file",
    "sampling_rate_hz",
    "time_column",
    "protocol",
    "channels",
    "processing_history",
}

FORBIDDEN_DIRECT_IDENTIFIER_KEYS = {
    "patient_name",
    "full_name",
    "mrn",
    "medical_record_number",
    "date_of_birth",
    "dob",
    "phone",
    "email",
}

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(_collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_collect_keys(child))
    return keys


def load_manifest(path: Path) -> tuple[dict[str, Any] | None, list[ValidationIssue]]:
    if not path.is_file():
        return None, [ValidationIssue("MANIFEST_NOT_FOUND", f"Manifest not found: {path}")]
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [ValidationIssue("MANIFEST_JSON_INVALID", str(exc))]
    if not isinstance(raw, dict):
        return None, [
            ValidationIssue("MANIFEST_JSON_INVALID", "Manifest root must be a JSON object")
        ]
    return raw, []


def validate_manifest(manifest: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        issues.append(
            ValidationIssue(
                "REQUIRED_METADATA_MISSING",
                f"Missing manifest fields: {', '.join(missing)}",
            )
        )

    forbidden = sorted(FORBIDDEN_DIRECT_IDENTIFIER_KEYS & _collect_keys(manifest))
    if forbidden:
        issues.append(
            ValidationIssue(
                "FORBIDDEN_PHI_KEY_PRESENT",
                f"Forbidden direct-identifier keys: {', '.join(forbidden)}",
            )
        )

    if manifest.get("schema_version") != "semg-session-manifest.v0.1":
        issues.append(
            ValidationIssue(
                "MANIFEST_SCHEMA_VERSION_UNSUPPORTED",
                f"Unsupported schema_version: {manifest.get('schema_version')!r}",
            )
        )

    try:
        fs = float(manifest.get("sampling_rate_hz"))
        if not math.isfinite(fs) or fs <= 0:
            raise ValueError
    except (TypeError, ValueError):
        issues.append(
            ValidationIssue(
                "REQUIRED_METADATA_MISSING",
                "sampling_rate_hz must be positive and finite",
            )
        )

    for key in ("session_id", "signal_file", "time_column", "data_source"):
        if not isinstance(manifest.get(key), str) or not str(manifest.get(key)).strip():
            issues.append(
                ValidationIssue(
                    "REQUIRED_METADATA_MISSING",
                    f"{key} must be a non-empty string",
                )
            )

    protocol = manifest.get("protocol")
    if not isinstance(protocol, Mapping) or not {"id", "version"} <= set(protocol):
        issues.append(
            ValidationIssue(
                "REQUIRED_METADATA_MISSING",
                "protocol must contain id and version",
            )
        )

    channels = manifest.get("channels")
    if not isinstance(channels, list) or not channels:
        issues.append(
            ValidationIssue("NO_USABLE_SIGNAL_CHANNEL", "At least one channel is required")
        )
    else:
        seen_ids: set[str] = set()
        seen_columns: set[str] = set()
        for index, channel in enumerate(channels):
            if not isinstance(channel, Mapping):
                issues.append(
                    ValidationIssue(
                        "REQUIRED_METADATA_MISSING",
                        f"Channel {index} must be an object",
                    )
                )
                continue
            required = {"column", "channel_id", "muscle", "side", "unit", "role"}
            missing_channel = sorted(required - set(channel))
            if missing_channel:
                issues.append(
                    ValidationIssue(
                        "REQUIRED_METADATA_MISSING",
                        f"Channel {index} missing: {', '.join(missing_channel)}",
                    )
                )
                continue
            channel_id = str(channel["channel_id"])
            column = str(channel["column"])
            if channel_id in seen_ids:
                issues.append(
                    ValidationIssue(
                        "DUPLICATE_CHANNEL_ID",
                        f"Duplicate channel_id: {channel_id}",
                    )
                )
            if column in seen_columns:
                issues.append(
                    ValidationIssue(
                        "DUPLICATE_CHANNEL_COLUMN",
                        f"Duplicate channel column mapping: {column}",
                    )
                )
            seen_ids.add(channel_id)
            seen_columns.add(column)
            if channel.get("unit") not in supported_units():
                issues.append(
                    ValidationIssue(
                        "UNSUPPORTED_SIGNAL_UNIT",
                        f"Channel {index} uses unsupported unit {channel.get('unit')!r}",
                    )
                )

    processing_history = manifest.get("processing_history")
    if not isinstance(processing_history, Mapping):
        issues.append(
            ValidationIssue(
                "REQUIRED_METADATA_MISSING",
                "processing_history must be an object",
            )
        )

    markers = manifest.get("phase_markers", [])
    if not isinstance(markers, list):
        issues.append(
            ValidationIssue("PHASE_MARKER_INVALID", "phase_markers must be an array")
        )
    else:
        for index, marker in enumerate(markers):
            if not isinstance(marker, Mapping) or not {
                "phase_id",
                "start_s",
                "end_s",
            } <= set(marker):
                issues.append(
                    ValidationIssue(
                        "PHASE_MARKER_INVALID",
                        f"Phase marker {index} is malformed",
                    )
                )

    declared_hash = manifest.get("source_hash_sha256")
    if declared_hash is not None and not _SHA256_RE.fullmatch(str(declared_hash)):
        issues.append(
            ValidationIssue(
                "SOURCE_HASH_INVALID",
                "source_hash_sha256 must be 64 lowercase hexadecimal characters",
            )
        )
    return issues
