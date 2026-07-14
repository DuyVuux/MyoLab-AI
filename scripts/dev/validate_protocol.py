#!/usr/bin/env python3
"""Validate protocol YAML structurally and semantically.

Structural validation uses JSON Schema Draft 2020-12.
Semantic validation handles cross-field constraints that JSON Schema cannot
reliably express without non-standard extensions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise SystemExit("jsonschema is required: pip install jsonschema") from exc

FILE_PATTERN = re.compile(
    r"^(?P<protocol_id>[a-z0-9]+(?:-[a-z0-9]+)*)\.v"
    r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.yaml$"
)

CORE_METADATA_FIELDS = {
    "session_id",
    "data_source",
    "sampling_rate_hz",
    "protocol_id",
    "protocol_version",
    "target_muscle",
    "side",
    "channel_map",
    "signal_unit",
    "phase_markers",
    "processing_history",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path("clinical/protocols/quad-isometric-60s.v0.1.yaml"),
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("clinical/protocols/protocol-schema.json"),
    )
    parser.add_argument(
        "--check-references",
        action="store_true",
        help="Check that repository-local references exist relative to repo root.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
    )
    return parser.parse_args()


def load_inputs(protocol_path: Path, schema_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot parse input: {exc}") from exc

    if not isinstance(protocol, dict):
        raise ValueError("protocol root must be a YAML mapping/object")
    if not isinstance(schema, dict):
        raise ValueError("schema root must be a JSON object")
    return protocol, schema


def structural_errors(protocol: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(protocol), key=lambda e: list(e.absolute_path))
    rendered: list[str] = []
    for error in errors:
        path = ".".join(str(p) for p in error.absolute_path) or "<root>"
        rendered.append(f"{path}: {error.message}")
    return rendered


def semantic_errors(protocol: dict[str, Any], protocol_path: Path) -> list[str]:
    errors: list[str] = []

    # File name and semantic version consistency.
    match = FILE_PATTERN.match(protocol_path.name)
    if not match:
        errors.append("filename must follow {protocol-id}.v{major}.{minor}.yaml")
    else:
        file_id = match.group("protocol_id")
        file_mm = f"{match.group('major')}.{match.group('minor')}"
        protocol_id = str(protocol.get("protocol_id", ""))
        protocol_version = str(protocol.get("version", ""))
        protocol_mm = ".".join(protocol_version.split(".")[:2])
        if file_id != protocol_id:
            errors.append(f"filename protocol id {file_id!r} != YAML id {protocol_id!r}")
        if file_mm != protocol_mm:
            errors.append(f"filename version v{file_mm} != YAML version {protocol_version}")

    acquisition = protocol["acquisition"]
    if acquisition["preferred_sampling_rate_hz"] < acquisition["minimum_sampling_rate_hz"]:
        errors.append(
            "acquisition.preferred_sampling_rate_hz must be >= minimum_sampling_rate_hz"
        )

    phases = protocol["phases"]
    phase_ids = [phase["id"] for phase in phases]
    duplicate_phase_ids = sorted({pid for pid in phase_ids if phase_ids.count(pid) > 1})
    if duplicate_phase_ids:
        errors.append(f"phase ids must be unique: {duplicate_phase_ids}")

    active_phase_id = protocol["analysis"]["active_phase_id"]
    matching = [phase for phase in phases if phase["id"] == active_phase_id]
    if len(matching) != 1:
        errors.append(
            "analysis.active_phase_id must reference exactly one phase in phases"
        )
    else:
        active_phase = matching[0]
        if not active_phase["required"]:
            errors.append("analysis active phase must be required=true")
        if active_phase["duration_s"] != protocol["task"]["active_duration_s"]:
            errors.append(
                "task.active_duration_s must equal the duration_s of analysis.active_phase_id"
            )

    required_fields = set(protocol["metadata"]["required_fields"])
    missing_core = sorted(CORE_METADATA_FIELDS - required_fields)
    if missing_core:
        errors.append(f"metadata.required_fields is missing core fields: {missing_core}")

    effort = protocol["task"]["effort"]
    if effort["parameter"] == "target_mvc_percent" and effort["required_at_session_level"]:
        if "target_mvc_percent" not in required_fields:
            errors.append(
                "metadata.required_fields must include target_mvc_percent when effort requires it"
            )

    windowing = protocol["analysis"]["default_windowing"]
    active_duration_ms = protocol["task"]["active_duration_s"] * 1000
    for field in ("time_domain_window_ms", "frequency_domain_window_ms"):
        if windowing[field] > active_duration_ms:
            errors.append(f"analysis.default_windowing.{field} exceeds active duration")

    mfcv = protocol["mfcv"]
    if mfcv["required_for_basic_analysis"]:
        if "mfcv" not in protocol["analysis"]["required_features"]:
            errors.append(
                "analysis.required_features must include mfcv when it is required for basic analysis"
            )
        if acquisition["minimum_basic_semg_channels"] < mfcv["eligibility"]["minimum_adjacent_channels"]:
            errors.append(
                "minimum_basic_semg_channels is insufficient for required MFCV analysis"
            )

    if protocol["safety"]["clinical_use_allowed"]:
        if protocol["clinical_approval"]["status"] != "approved":
            errors.append("clinical use requires clinical_approval.status=approved")

    return errors


def reference_warnings(protocol: dict[str, Any], repo_root: Path) -> list[str]:
    warnings: list[str] = []
    for ref in protocol.get("references", []):
        if "://" in ref or ref.startswith("doi:"):
            continue
        path = repo_root / ref
        if not path.exists():
            warnings.append(f"reference does not exist in repository: {ref}")
    return warnings


def main() -> int:
    args = parse_args()
    if not args.protocol.is_file():
        print(f"FAIL: protocol not found: {args.protocol}", file=sys.stderr)
        return 2
    if not args.schema.is_file():
        print(f"FAIL: schema not found: {args.schema}", file=sys.stderr)
        return 2

    try:
        protocol, schema = load_inputs(args.protocol, args.schema)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    errors = structural_errors(protocol, schema)
    if errors:
        print("FAIL: structural schema errors:", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
        return 1

    errors = semantic_errors(protocol, args.protocol)
    if errors:
        print("FAIL: semantic protocol errors:", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
        return 1

    if args.check_references:
        warnings = reference_warnings(protocol, args.repo_root)
        for item in warnings:
            print(f"WARNING: {item}", file=sys.stderr)

    print(
        "PASS: protocol is structurally and semantically valid\n"
        f"  schema_id={schema.get('$id', '<missing>')}\n"
        f"  protocol_id={protocol['protocol_id']}\n"
        f"  version={protocol['version']}\n"
        f"  status={protocol['status']}\n"
        f"  clinical_use_allowed={protocol['safety']['clinical_use_allowed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
