"""Production MR4 single-CSV parser.

The parser is read-only, deterministic, fail-closed, and does not perform DSP, AI,
clinical interpretation, preprocessing, resampling, interpolation, or unit conversion.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from adapters.mr4.contracts import SingleCsvContract, MR4_SINGLE_CSV_V0_1
from adapters.common.provenance import (
    ParserProvenance,
    SourceLinkage,
    source_linkage,
    stable_run_id,
)
from adapters.mr4.models import (
    FieldValue,
    Mr4ParseError,
    SignalDescriptor,
    stable_signal_id,
)

PARSER_ID = "noraxon-mr4-single-csv"
PARSER_VERSION = "0.1.0"


@dataclass(frozen=True)
class SingleCsvRecord:
    source: SourceLinkage
    provenance: ParserProvenance
    metadata: tuple[FieldValue, ...]
    unknown_metadata: tuple[FieldValue, ...]
    data_header: tuple[str, ...]
    raw_rows: tuple[tuple[str, ...], ...]
    timestamps_seconds: tuple[float, ...]
    signals: tuple[SignalDescriptor, ...]

    def metadata_value(self, name: str) -> str | None:
        for item in self.metadata:
            if item.name == name:
                return item.raw_value
        return None


def parse_single_csv(path: Path, contract: SingleCsvContract = MR4_SINGLE_CSV_V0_1) -> SingleCsvRecord:
    """Parse one MR4 single CSV according to the provided contract."""
    path = Path(path)
    before = source_linkage(path)
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "source is not valid UTF-8/UTF-8-BOM text",
            source_path=path,
        ) from exc

    try:
        rows = list(csv.reader(StringIO(text)))
    except csv.Error as exc:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "CSV tokenization failed",
            source_path=path,
        ) from exc

    if len(rows) < 5:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "single CSV requires metadata, blank separator, header and data",
            source_path=path,
        )

    metadata_header = rows[0]
    metadata_values = rows[1]
    if not metadata_header or len(metadata_header) != len(metadata_values):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "metadata header/value arity mismatch",
            source_path=path,
        )
    if len(metadata_header) != len(set(metadata_header)):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "duplicate metadata header is not contractually defined",
            source_path=path,
        )
    if not _is_blank(rows[2]):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "required blank separator row is missing",
            source_path=path,
        )

    data_header = rows[3]
    if not data_header or data_header[0] != "time":
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "data header must begin with time",
            source_path=path,
        )
    if len(data_header) != len(set(data_header)):
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "duplicate data columns are not contractually defined",
            source_path=path,
        )

    data_rows = rows[4:]
    if not data_rows:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "time-series contains no rows",
            source_path=path,
        )
    for index, row in enumerate(data_rows, start=5):
        if len(row) != len(data_header):
            raise Mr4ParseError(
                "INGEST_SCHEMA_ERROR",
                "data row arity does not match header",
                source_path=path,
                details={"row_number": index},
            )

    metadata_map = dict(zip(metadata_header, metadata_values))
    _validate_declared_count(metadata_map, len(data_rows), path)
    timestamps = _parse_timestamps(data_rows, path)
    _validate_frequency(metadata_map, timestamps, path)

    metadata = tuple(
        FieldValue(name=name, raw_value=value)
        for name, value in zip(metadata_header, metadata_values)
        if name in contract.known_metadata
    )
    unknown_metadata = tuple(
        FieldValue(name=name, raw_value=value, evidence_status="UNKNOWN")
        for name, value in zip(metadata_header, metadata_values)
        if name not in contract.known_metadata
    )

    source = before
    signals = tuple(
        _build_signal_descriptor(
            source.source_id,
            column,
            column_index,
            data_rows,
            _optional_positive_float(metadata_map.get("frequency"), "frequency", path),
            contract,
        )
        for column_index, column in enumerate(data_header[1:], start=1)
    )
    provenance = ParserProvenance(
        parser_id=PARSER_ID,
        parser_version=PARSER_VERSION,
        contract_id=contract.contract_id,
        contract_version=contract.contract_version,
        source_id=source.source_id,
        run_id=stable_run_id(
            source_id=source.source_id,
            parser_version=PARSER_VERSION,
            contract_version=contract.contract_version,
        ),
    )

    after = source_linkage(path)
    if before.sha256 != after.sha256 or before.source_path != after.source_path:
        raise Mr4ParseError(
            "RAW_MUTATION_DETECTED",
            "source bytes/path changed during parsing",
            source_path=path,
        )

    return SingleCsvRecord(
        source=source,
        provenance=provenance,
        metadata=metadata,
        unknown_metadata=unknown_metadata,
        data_header=tuple(data_header),
        raw_rows=tuple(tuple(cell for cell in row) for row in data_rows),
        timestamps_seconds=timestamps,
        signals=signals,
    )


def _is_blank(row: list[str]) -> bool:
    return not row or all(cell == "" for cell in row)


def _validate_declared_count(metadata: dict[str, str], observed: int, path: Path) -> None:
    raw_count = metadata.get("count")
    if raw_count in {None, ""}:
        return
    try:
        expected = int(raw_count)
    except ValueError as exc:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            "count metadata is not an integer",
            source_path=path,
        ) from exc
    if expected != observed:
        raise Mr4ParseError(
            "COUNT_MISMATCH",
            "declared count differs from observed rows",
            source_path=path,
            details={"expected": expected, "observed": observed},
        )


def _parse_timestamps(rows: list[list[str]], path: Path) -> tuple[float, ...]:
    values: list[float] = []
    for index, row in enumerate(rows, start=5):
        try:
            value = float(row[0])
        except ValueError as exc:
            raise Mr4ParseError(
                "TIMESTAMP_INVALID",
                "timestamp is not numeric",
                source_path=path,
                details={"row_number": index},
            ) from exc
        values.append(value)
    if any(current <= previous for previous, current in zip(values, values[1:])):
        raise Mr4ParseError(
            "TIMESTAMP_INVALID",
            "timestamps must be strictly increasing",
            source_path=path,
        )
    return tuple(values)


def _validate_frequency(
    metadata: dict[str, str], timestamps: tuple[float, ...], path: Path
) -> None:
    frequency = _optional_positive_float(metadata.get("frequency"), "frequency", path)
    if frequency is None or len(timestamps) < 2:
        return
    expected = 1.0 / frequency
    observed = timestamps[1] - timestamps[0]
    tolerance = max(1e-9, expected * 1e-3)
    if abs(observed - expected) > tolerance:
        raise Mr4ParseError(
            "SAMPLING_INTERVAL_MISMATCH",
            "timestamp interval is inconsistent with declared table frequency",
            source_path=path,
            details={"expected_dt": expected, "observed_dt": observed},
        )


def _optional_positive_float(raw: str | None, field: str, path: Path) -> float | None:
    if raw in {None, ""}:
        return None
    try:
        value = float(raw)
    except ValueError as exc:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            f"{field} metadata is not numeric",
            source_path=path,
        ) from exc
    if value <= 0:
        raise Mr4ParseError(
            "INGEST_SCHEMA_ERROR",
            f"{field} metadata must be positive",
            source_path=path,
        )
    return value


def _build_signal_descriptor(
    source_id: str,
    column: str,
    column_index: int,
    rows: list[list[str]],
    frequency: float | None,
    contract: SingleCsvContract,
) -> SignalDescriptor:
    role, unit, evidence, unknown = contract.get_column_semantics(column)
    values: list[tuple[str | None, ...]] = []
    for row in rows:
        raw = row[column_index]
        values.append((None if raw == "" else raw,))
    return SignalDescriptor(
        signal_id=stable_signal_id(source_id, column),
        vendor_name=column,
        semantic_role=role,
        unit=unit,
        unit_evidence=evidence,
        sampling_rate_hz=frequency,
        columns=(column,),
        raw_values=tuple(values),
        unknown_semantics=unknown,
    )
