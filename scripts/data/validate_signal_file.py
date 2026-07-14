#!/usr/bin/env python3
"""Validate the Day 2 generic CSV + manifest contract.

This is an ingestion/protocol validator, not the full spectral quality gate.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


SUPPORTED_UNITS = {"uV", "mV", "V"}
FORBIDDEN_KEYS = {
    "patient_name",
    "full_name",
    "mrn",
    "medical_record_number",
    "date_of_birth",
    "dob",
    "phone",
    "email",
}
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


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    blocking: bool = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=("format", "protocol"),
        default="format",
        help="format checks the file contract; protocol also checks protocol compatibility",
    )
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path("clinical/protocols/quad-isometric-60s.v0.1.yaml"),
    )
    parser.add_argument(
        "--sampling-rate-tolerance",
        type=float,
        default=0.01,
    )
    parser.add_argument(
        "--expect-error",
        action="append",
        default=[],
        help="Expected blocking code. The command passes when every expected code is present.",
    )
    parser.add_argument("--json-output", action="store_true")
    return parser.parse_args()


def collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(collect_keys(child))
    return keys


def load_manifest(path: Path) -> tuple[dict[str, Any] | None, list[Issue]]:
    if not path.is_file():
        return None, [Issue("MANIFEST_NOT_FOUND", f"Manifest not found: {path}")]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, [Issue("MANIFEST_JSON_INVALID", str(exc))]
    if not isinstance(value, dict):
        return None, [Issue("MANIFEST_JSON_INVALID", "Manifest root must be an object")]
    return value, []


def validate_manifest(manifest: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        issues.append(
            Issue(
                "REQUIRED_METADATA_MISSING",
                f"Missing manifest fields: {', '.join(missing)}",
            )
        )

    present_forbidden = sorted(FORBIDDEN_KEYS & collect_keys(manifest))
    if present_forbidden:
        issues.append(
            Issue(
                "FORBIDDEN_PHI_KEY_PRESENT",
                f"Forbidden direct-identifier keys: {', '.join(present_forbidden)}",
            )
        )

    channels = manifest.get("channels")
    if not isinstance(channels, list) or not channels:
        issues.append(Issue("NO_USABLE_SIGNAL_CHANNEL", "At least one channel is required"))
        return issues

    for index, channel in enumerate(channels):
        if not isinstance(channel, dict):
            issues.append(
                Issue("REQUIRED_METADATA_MISSING", f"Channel {index} must be an object")
            )
            continue
        required = {"column", "channel_id", "muscle", "side", "unit", "role"}
        channel_missing = sorted(required - set(channel))
        if channel_missing:
            issues.append(
                Issue(
                    "REQUIRED_METADATA_MISSING",
                    f"Channel {index} missing: {', '.join(channel_missing)}",
                )
            )
        if channel.get("unit") not in SUPPORTED_UNITS:
            issues.append(
                Issue(
                    "UNSUPPORTED_SIGNAL_UNIT",
                    f"Channel {index} unit {channel.get('unit')!r} is unsupported",
                )
            )

    try:
        declared_fs = float(manifest.get("sampling_rate_hz"))
        if not math.isfinite(declared_fs) or declared_fs <= 0:
            raise ValueError
    except (TypeError, ValueError):
        issues.append(
            Issue("REQUIRED_METADATA_MISSING", "sampling_rate_hz must be positive")
        )

    protocol = manifest.get("protocol")
    if not isinstance(protocol, dict) or not {"id", "version"} <= set(protocol):
        issues.append(
            Issue(
                "REQUIRED_METADATA_MISSING",
                "protocol must contain id and version",
            )
        )
    return issues


def parse_csv(
    csv_path: Path,
    time_column: str,
    channel_columns: list[str],
) -> tuple[dict[str, Any] | None, list[Issue]]:
    issues: list[Issue] = []
    if not csv_path.is_file():
        return None, [Issue("SIGNAL_FILE_NOT_FOUND", f"Signal file not found: {csv_path}")]

    times: list[float] = []
    nonfinite_count = 0
    sample_count = 0

    try:
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            if time_column not in headers:
                return None, [
                    Issue(
                        "CSV_HEADER_INVALID",
                        f"Time column {time_column!r} not found; headers={headers}",
                    )
                ]
            missing_channels = [column for column in channel_columns if column not in headers]
            if missing_channels:
                return None, [
                    Issue(
                        "CHANNEL_COLUMN_MISSING",
                        f"Missing channel columns: {', '.join(missing_channels)}",
                    )
                ]

            for row_number, row in enumerate(reader, start=2):
                try:
                    time_value = float(row[time_column])
                except (TypeError, ValueError):
                    return None, [
                        Issue(
                            "CSV_PARSE_ERROR",
                            f"Non-numeric time at row {row_number}: {row.get(time_column)!r}",
                        )
                    ]
                if not math.isfinite(time_value):
                    return None, [
                        Issue(
                            "TIME_VALUE_NONFINITE",
                            f"Non-finite time at row {row_number}",
                        )
                    ]
                times.append(time_value)

                for column in channel_columns:
                    raw = row.get(column, "")
                    try:
                        value = float(raw)
                    except (TypeError, ValueError):
                        nonfinite_count += 1
                    else:
                        if not math.isfinite(value):
                            nonfinite_count += 1
                sample_count += 1
    except (OSError, csv.Error) as exc:
        return None, [Issue("CSV_PARSE_ERROR", str(exc))]

    if sample_count < 2:
        return None, [Issue("CSV_PARSE_ERROR", "At least two samples are required")]

    dt = [b - a for a, b in zip(times, times[1:])]
    if any(delta <= 0 for delta in dt):
        issues.append(Issue("TIME_NOT_MONOTONIC", "Timestamps must be strictly increasing"))

    median_dt = statistics.median(dt)
    inferred_fs = 1.0 / median_dt if median_dt > 0 else float("nan")
    abs_deviation = [abs(delta - median_dt) for delta in dt]
    relative_jitter = (
        statistics.median(abs_deviation) / median_dt if median_dt > 0 else float("inf")
    )
    duration_s = times[-1] - times[0]
    denominator = sample_count * max(len(channel_columns), 1)
    nonfinite_ratio = nonfinite_count / denominator

    return {
        "sample_count": sample_count,
        "channel_count": len(channel_columns),
        "duration_s": duration_s,
        "inferred_sampling_rate_hz": inferred_fs,
        "relative_jitter": relative_jitter,
        "nonfinite_ratio": nonfinite_ratio,
    }, issues


def protocol_checks(
    manifest: dict[str, Any],
    summary: dict[str, Any],
    protocol_path: Path,
) -> list[Issue]:
    if not protocol_path.is_file():
        return [Issue("PROTOCOL_NOT_FOUND", f"Protocol not found: {protocol_path}")]

    try:
        protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [Issue("PROTOCOL_NOT_FOUND", f"Cannot parse protocol: {exc}")]

    issues: list[Issue] = []
    manifest_ref = manifest["protocol"]
    if manifest_ref["id"] != protocol["protocol_id"]:
        issues.append(
            Issue(
                "PROTOCOL_VERSION_MISMATCH",
                f"Manifest protocol id {manifest_ref['id']!r} != {protocol['protocol_id']!r}",
            )
        )
    if manifest_ref["version"] != protocol["version"]:
        issues.append(
            Issue(
                "PROTOCOL_VERSION_MISMATCH",
                f"Manifest version {manifest_ref['version']!r} != {protocol['version']!r}",
            )
        )

    declared_fs = float(manifest["sampling_rate_hz"])
    minimum_fs = float(protocol["acquisition"]["minimum_sampling_rate_hz"])
    if declared_fs < minimum_fs:
        issues.append(
            Issue(
                "SAMPLING_RATE_BELOW_PROTOCOL_MIN",
                f"Declared Fs={declared_fs:g} Hz < protocol minimum {minimum_fs:g} Hz",
            )
        )

    active_phase_id = protocol["analysis"]["active_phase_id"]
    markers = manifest.get("phase_markers", [])
    active = next(
        (
            marker
            for marker in markers
            if isinstance(marker, dict) and marker.get("phase_id") == active_phase_id
        ),
        None,
    )
    if active is None:
        issues.append(
            Issue("ACTIVE_PHASE_MISSING", f"Missing phase marker {active_phase_id!r}")
        )
    else:
        try:
            active_duration = float(active["end_s"]) - float(active["start_s"])
        except (KeyError, TypeError, ValueError):
            issues.append(
                Issue("ACTIVE_PHASE_MISSING", "Active phase marker is malformed")
            )
        else:
            expected_duration = float(protocol["task"]["active_duration_s"])
            minimum_duration = 0.90 * expected_duration
            if active_duration < minimum_duration:
                issues.append(
                    Issue(
                        "ACTIVE_DURATION_TOO_SHORT",
                        f"Active duration={active_duration:.3f}s; "
                        f"minimum={minimum_duration:.3f}s",
                    )
                )

    if summary["nonfinite_ratio"] > 0.01:
        issues.append(
            Issue(
                "NONFINITE_RATIO_EXCESSIVE",
                f"Non-finite ratio={summary['nonfinite_ratio']:.6f} > 0.01",
            )
        )
    elif summary["nonfinite_ratio"] > 0.001:
        issues.append(
            Issue(
                "NONFINITE_RATIO_WARNING",
                f"Non-finite ratio={summary['nonfinite_ratio']:.6f} > 0.001",
                blocking=False,
            )
        )

    return issues


def main() -> int:
    args = parse_args()
    manifest, issues = load_manifest(args.manifest)
    if manifest is not None:
        issues.extend(validate_manifest(manifest))

    summary: dict[str, Any] | None = None
    if manifest is not None and not any(issue.blocking for issue in issues):
        csv_path = args.manifest.parent / str(manifest["signal_file"])
        channel_columns = [str(channel["column"]) for channel in manifest["channels"]]
        summary, csv_issues = parse_csv(
            csv_path,
            str(manifest["time_column"]),
            channel_columns,
        )
        issues.extend(csv_issues)

        if summary is not None:
            declared_fs = float(manifest["sampling_rate_hz"])
            relative_error = abs(
                summary["inferred_sampling_rate_hz"] - declared_fs
            ) / declared_fs
            if relative_error > args.sampling_rate_tolerance:
                issues.append(
                    Issue(
                        "SAMPLING_RATE_MISMATCH",
                        f"Inferred Fs={summary['inferred_sampling_rate_hz']:.6f} Hz; "
                        f"declared Fs={declared_fs:.6f} Hz; relative error={relative_error:.6f}",
                    )
                )

            if args.mode == "protocol":
                issues.extend(protocol_checks(manifest, summary, args.protocol))

    blocking_codes = {issue.code for issue in issues if issue.blocking}
    expected = set(args.expect_error)

    result = {
        "mode": args.mode,
        "manifest": str(args.manifest),
        "summary": summary,
        "issues": [
            {"code": issue.code, "message": issue.message, "blocking": issue.blocking}
            for issue in issues
        ],
        "blocking_codes": sorted(blocking_codes),
    }

    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Validation mode: {args.mode}")
        if summary:
            print(
                f"samples={summary['sample_count']} "
                f"channels={summary['channel_count']} "
                f"duration={summary['duration_s']:.6f}s "
                f"Fs_inferred={summary['inferred_sampling_rate_hz']:.6f}Hz "
                f"jitter={summary['relative_jitter']:.6g} "
                f"nonfinite_ratio={summary['nonfinite_ratio']:.6g}"
            )
        for issue in issues:
            level = "BLOCK" if issue.blocking else "WARN"
            print(f"{level}: {issue.code}: {issue.message}")

    if expected:
        missing_expected = expected - blocking_codes
        unexpected = blocking_codes - expected
        if missing_expected:
            print(
                f"FAIL: expected blocking codes not observed: {sorted(missing_expected)}",
                file=sys.stderr,
            )
            return 1
        if unexpected:
            print(
                f"FAIL: unexpected blocking codes: {sorted(unexpected)}",
                file=sys.stderr,
            )
            return 1
        print(f"PASS: expected blocking code(s) observed: {sorted(expected)}")
        return 0

    if blocking_codes:
        print(f"FAIL: blocking codes: {sorted(blocking_codes)}", file=sys.stderr)
        return 1

    print("PASS: validation completed without blocking errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())