"""Production MR4 separated-CSV record assembler — DAY17.

DAY10 explicitly left physical info.csv framing NOT_VERIFIED. This module therefore
requires an explicit, versioned layout profile and never auto-detects an info layout.
Synthetic profiles are valid for engineering tests only and are not site evidence.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

import yaml

from adapters.mr4.models import (
    FieldValue,
    Mr4ParseError,
    ParserProvenance,
    SourceLinkage,
    source_linkage,
    stable_run_id,
    stable_signal_id,
    SeparatedLayoutProfile,
    SeparatedSignal,
    UnknownSignalEvidence,
    SeparatedRecord,
)
from adapters.mr4.contracts import SeparatedCsvContract, MR4_SEPARATED_RECORD_V0_1

PARSER_ID = "noraxon-mr4-separated-csv"
PARSER_VERSION = "0.1.0"
CONTRACT_ID = "MR4_SEPARATED_RECORD_V0_1+MR4_SIGNAL_FILE_V0_1"
CONTRACT_VERSION = "0.1.0"









def load_layout_profile(path: Path) -> SeparatedLayoutProfile:
    try:
        payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Mr4ParseError("LAYOUT_PROFILE_INVALID", "cannot read layout profile") from exc
    if not isinstance(payload, dict):
        raise Mr4ParseError("LAYOUT_PROFILE_INVALID", "layout profile root must be a mapping")
    required = {
        "profile_id",
        "version",
        "status",
        "evidence_status",
        "info_layout",
        "signal_layout",
        "site_verified",
    }
    if any(payload.get(key) in {None, ""} for key in required - {"site_verified"}):
        raise Mr4ParseError("INFO_LAYOUT_NOT_VERIFIED", "layout profile is incomplete")
    layout_unverified = (
        payload.get("info_layout") == "NOT_VERIFIED"
        or payload.get("signal_layout") == "NOT_VERIFIED"
    )
    if layout_unverified:
        raise Mr4ParseError(
            "INFO_LAYOUT_NOT_VERIFIED",
            "physical separated layout is not verified",
        )
    return SeparatedLayoutProfile(
        profile_id=str(payload["profile_id"]),
        version=str(payload["version"]),
        status=str(payload["status"]),
        evidence_status=str(payload["evidence_status"]),
        info_layout=str(payload["info_layout"]),
        signal_layout=str(payload["signal_layout"]),
        site_verified=bool(payload["site_verified"]),
    )


def assemble_separated_export(
    directory: Path,
    *,
    layout_profile: SeparatedLayoutProfile | None,
    contract: SeparatedCsvContract = MR4_SEPARATED_RECORD_V0_1,
) -> SeparatedRecord:
    directory = Path(directory)
    if layout_profile is None:
        raise Mr4ParseError(
            "INFO_LAYOUT_NOT_VERIFIED",
            "separated export requires an explicit physical layout profile",
            source_path=directory,
        )
    if not directory.is_dir():
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "separated source is not a directory",
        )
    info_path = directory / "info.csv"
    if not info_path.is_file():
        raise Mr4ParseError(
            "MISSING_REQUIRED_METADATA",
            "separated export requires info.csv",
            source_path=directory,
        )

    info_fields = _parse_info(info_path, layout_profile, contract.known_info_fields)
    known_info = tuple(item for item in info_fields if item.name in contract.known_info_fields)
    unknown_info = tuple(item for item in info_fields if item.name not in contract.known_info_fields)

    signals: list[SeparatedSignal] = []
    unknown_signals: list[UnknownSignalEvidence] = []
    warnings: list[str] = []
    source_files: list[SourceLinkage] = [source_linkage(info_path)]

    signal_paths = sorted(
        path for path in directory.glob("*.csv") if path.name != "info.csv"
    )
    if not signal_paths:
        raise Mr4ParseError(
            "MISSING_REQUIRED_METADATA",
            "separated export contains no signal files",
            source_path=directory,
        )

    for path in signal_paths:
        parsed = _parse_signal_file(path, layout_profile, contract.known_units)
        source_files.append(parsed.source)
        if isinstance(parsed, UnknownSignalEvidence):
            unknown_signals.append(parsed)
            warnings.append(parsed.reason_code)
        else:
            signals.append(parsed)
            warnings.extend(parsed.warnings)

    assembly_id = _assembly_id(source_files, layout_profile)
    aggregate_source_id = "srcset_sha256_" + assembly_id.rsplit("_", 1)[-1]
    provenance = ParserProvenance(
        parser_id=PARSER_ID,
        parser_version=PARSER_VERSION,
        contract_id=CONTRACT_ID,
        contract_version=CONTRACT_VERSION,
        source_id=aggregate_source_id,
        run_id=stable_run_id(
            source_id=aggregate_source_id,
            parser_version=PARSER_VERSION,
            contract_version=CONTRACT_VERSION + "+" + layout_profile.version,
        ),
    )

    _verify_sources_unchanged(source_files)
    return SeparatedRecord(
        directory=str(directory.resolve()),
        info_source=source_files[0],
        source_files=tuple(source_files),
        provenance=provenance,
        layout_profile_id=layout_profile.profile_id,
        layout_profile_version=layout_profile.version,
        info_metadata=known_info,
        unknown_info_metadata=unknown_info,
        signals=tuple(signals),
        unknown_signals=tuple(unknown_signals),
        warnings=tuple(sorted(set(warnings))),
        assembly_id=assembly_id,
    )


def _parse_info(path: Path, profile: SeparatedLayoutProfile, known_info_fields: frozenset[str]) -> tuple[FieldValue, ...]:
    if profile.info_layout != "HORIZONTAL_HEADER_VALUE":
        raise Mr4ParseError(
            "INFO_LAYOUT_NOT_VERIFIED",
            f"unsupported explicit info layout: {profile.info_layout}",
            source_path=path,
        )
    rows = _read_csv_rows(path)
    nonblank = [row for row in rows if not _is_blank(row)]
    if len(nonblank) != 2 or len(nonblank[0]) != len(nonblank[1]):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "info.csv does not match explicit horizontal header/value profile",
            source_path=path,
        )
    header, values = nonblank
    if len(header) != len(set(header)):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "duplicate info metadata header",
            source_path=path,
        )
    return tuple(
        FieldValue(
            name=name,
            raw_value=value,
            evidence_status="SOURCE_REPORTED" if name in known_info_fields else "UNKNOWN",
        )
        for name, value in zip(header, values)
    )


def _parse_signal_file(
    path: Path,
    profile: SeparatedLayoutProfile,
    known_units: frozenset[str],
) -> SeparatedSignal | UnknownSignalEvidence:
    if profile.signal_layout != "HORIZONTAL_HEADER_VALUE_BLANK_DATA_HEADER":
        raise Mr4ParseError(
            "INFO_LAYOUT_NOT_VERIFIED",
            f"unsupported explicit signal layout: {profile.signal_layout}",
            source_path=path,
        )
    rows = _read_csv_rows(path)
    if len(rows) < 5 or len(rows[0]) != len(rows[1]) or not _is_blank(rows[2]):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "signal file framing mismatch",
            source_path=path,
        )
    if len(rows[0]) != len(set(rows[0])):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "duplicate signal metadata header",
            source_path=path,
        )
    metadata = dict(zip(rows[0], rows[1]))
    data_header = rows[3]
    data_rows = rows[4:]
    source = source_linkage(path)
    signal_type = metadata.get("type")
    vendor_name = metadata.get("name") or None

    if signal_type not in {"signal", "signal_2d"}:
        return UnknownSignalEvidence(
            source=source,
            vendor_name=vendor_name,
            declared_type=signal_type,
            metadata=tuple(
                FieldValue(name=k, raw_value=v, evidence_status="UNKNOWN")
                for k, v in metadata.items()
            ),
            data_header=tuple(data_header),
            raw_rows=tuple(tuple(cell for cell in row) for row in data_rows),
            reason_code="UNSUPPORTED_SIGNAL_TYPE_PRESERVED",
        )

    expected_header = (
        ["time", "value"]
        if signal_type == "signal"
        else ["time", "x", "y"]
    )
    if data_header != expected_header:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            f"{signal_type} data shape does not match contract",
            source_path=path,
        )
    if not data_rows:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "signal contains no rows",
            source_path=path,
        )
    if any(len(row) != len(expected_header) for row in data_rows):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "signal row arity mismatch",
            source_path=path,
        )

    count = _optional_nonnegative_int(metadata.get("count"), "count", path)
    if count is not None and count != len(data_rows):
        raise Mr4ParseError(
            "COUNT_MISMATCH",
            "signal declared count differs from source rows",
            source_path=path,
            details={"expected": count, "observed": len(data_rows)},
        )
    timestamps = _timestamps(data_rows, path)
    frequency = _optional_positive_float(
        metadata.get("frequency"),
        "frequency",
        path,
    )
    _validate_interval(frequency, timestamps, path)
    unit = metadata.get("units") or None
    if unit is not None and unit not in known_units:
        raise Mr4ParseError(
            "UNIT_MISMATCH",
            "signal unit is unknown/unverified; no inference performed",
            source_path=path,
            details={"unit": unit},
        )
    begin_time = _optional_float(metadata.get("begin_time"), "begin_time", path)
    warnings: list[str] = []
    if vendor_name is None:
        warnings.append("ORPHAN_SIGNAL_MISSING_NAME_PRESERVED")
    if frequency is None:
        warnings.append("SAMPLING_RATE_METADATA_UNAVAILABLE")
    if unit is None:
        warnings.append("UNIT_METADATA_UNAVAILABLE")

    values = tuple(
        tuple(None if cell == "" else cell for cell in row[1:])
        for row in data_rows
    )
    signal_id = stable_signal_id(source.source_id, vendor_name or path.name)
    return SeparatedSignal(
        source=source,
        signal_id=signal_id,
        vendor_name=vendor_name,
        signal_type=signal_type,
        frequency_hz=frequency,
        count=count,
        unit=unit,
        begin_time_seconds=begin_time,
        time_unit=metadata.get("time_units") or None,
        columns=tuple(expected_header),
        raw_rows=tuple(tuple(cell for cell in row) for row in data_rows),
        timestamps_seconds=timestamps,
        values=values,
        warnings=tuple(warnings),
    )


def _read_csv_rows(path: Path) -> list[list[str]]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "invalid UTF-8 signal source",
            source_path=path,
        ) from exc
    try:
        return list(csv.reader(StringIO(text)))
    except csv.Error as exc:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "CSV tokenization failed",
            source_path=path,
        ) from exc


def _is_blank(row: list[str]) -> bool:
    return not row or all(cell == "" for cell in row)


def _timestamps(rows: list[list[str]], path: Path) -> tuple[float, ...]:
    values: list[float] = []
    for row in rows:
        try:
            values.append(float(row[0]))
        except ValueError as exc:
            raise Mr4ParseError(
            "TIMESTAMP_INVALID",
            "timestamp is not numeric",
            source_path=path,
        ) from exc
    if any(current <= previous for previous, current in zip(values, values[1:])):
        raise Mr4ParseError(
            "TIMESTAMP_INVALID",
            "timestamps must be strictly increasing",
            source_path=path,
        )
    return tuple(values)


def _validate_interval(frequency: float | None, timestamps: tuple[float, ...], path: Path) -> None:
    if frequency is None or len(timestamps) < 2:
        return
    expected = 1.0 / frequency
    observed = timestamps[1] - timestamps[0]
    tolerance = max(1e-9, expected * 1e-3)
    if abs(observed - expected) > tolerance:
        raise Mr4ParseError(
            "SAMPLING_INTERVAL_MISMATCH",
            "per-signal time interval contradicts declared frequency",
            source_path=path,
        )


def _optional_positive_float(raw: str | None, field: str, path: Path) -> float | None:
    if raw in {None, ""}:
        return None
    value = _optional_float(raw, field, path)
    assert value is not None
    if value <= 0:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            f"{field} must be positive",
            source_path=path,
        )
    return value


def _optional_float(raw: str | None, field: str, path: Path) -> float | None:
    if raw in {None, ""}:
        return None
    try:
        return float(raw)
    except ValueError as exc:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            f"{field} is not numeric",
            source_path=path,
        ) from exc


def _optional_nonnegative_int(raw: str | None, field: str, path: Path) -> int | None:
    if raw in {None, ""}:
        return None
    try:
        value = int(raw)
    except ValueError as exc:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            f"{field} is not an integer",
            source_path=path,
        ) from exc
    if value < 0:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            f"{field} must be nonnegative",
            source_path=path,
        )
    return value


def _assembly_id(sources: list[SourceLinkage], profile: SeparatedLayoutProfile) -> str:
    payload = {
        "source_ids": sorted(item.source_id for item in sources),
        "profile_id": profile.profile_id,
        "profile_version": profile.version,
        "parser_version": PARSER_VERSION,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return "assembly_sha256_" + digest


def _verify_sources_unchanged(sources: list[SourceLinkage]) -> None:
    for source in sources:
        current = source_linkage(Path(source.source_path))
        if current.sha256 != source.sha256 or current.source_path != source.source_path:
            raise Mr4ParseError(
                "RAW_MUTATION_DETECTED",
                "source changed during separated assembly",
                source_path=Path(source.source_path),
            )
