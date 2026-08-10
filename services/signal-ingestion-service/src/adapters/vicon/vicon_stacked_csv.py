"""DAY18 minimal Vicon stacked-section parser.

The adapter is contract-driven and context-only. It does not perform biomechanics,
coordinate interpretation, resampling, interpolation, or representation learning.
"""
from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from .vicon_contracts import ViconStackedContract, load_vicon_contract
from src.adapters.common.provenance import (
    ParserProvenance,
    source_linkage,
    stable_run_id,
)
from .vicon_models import (
    MultimodalAlignmentContext,
    UnsupportedSectionEvidence,
    ViconColumnDescriptor,
    ViconParseError,
    ViconSection,
    ViconStackedRecord,
)

PARSER_ID = "vicon-stacked-csv-context"
PARSER_VERSION = "0.1.0"


def parse_vicon_stacked_csv(
    path: Path,
    *,
    contract: ViconStackedContract | None = None,
    alignment: MultimodalAlignmentContext | None = None,
) -> ViconStackedRecord:
    path = Path(path)
    contract = contract or load_vicon_contract()
    alignment = alignment or MultimodalAlignmentContext()
    _validate_alignment(alignment, path)

    before = source_linkage(path)
    rows = _read_rows(path)
    known = set(contract.supported_sections) | set(
        contract.evidence_only_sections
    )

    sections: list[ViconSection] = []
    evidence: list[UnsupportedSectionEvidence] = []
    warnings: list[str] = []
    seen: set[str] = set()
    index = 0

    while index < len(rows):
        if _blank(rows[index]):
            index += 1
            continue

        marker = _marker(rows[index], known)
        if marker is None:
            raise ViconParseError(
                "VICON_SECTION_NOT_IN_CONTRACT",
                "unexpected row outside declared section",
                source_path=path,
                details={"row_number": index + 1, "row": rows[index]},
            )
        if marker in seen:
            raise ViconParseError(
                "INGEST_SCHEMA_ERROR",
                "duplicate Vicon section not defined",
                source_path=path,
                details={"section": marker},
            )
        seen.add(marker)

        next_index = _next_marker(rows, index + 1, known)
        block = rows[index:next_index]
        if marker in contract.evidence_only_sections:
            evidence.append(
                UnsupportedSectionEvidence(
                    section_name=marker,
                    raw_rows=tuple(
                        tuple(cell for cell in row) for row in block
                    ),
                    reason=(
                        "SECTION_PRESERVED_NOT_PARSED_IN_DAY18_SCOPE"
                    ),
                )
            )
            warnings.append("EVIDENCE_ONLY_SECTION:" + marker)
        else:
            sections.append(_parse_block(marker, block, contract, path))
        index = next_index

    if not sections:
        raise ViconParseError(
            "INGEST_SCHEMA_ERROR",
            "no supported Vicon context sections found",
            source_path=path,
        )

    after = source_linkage(path)
    if before.sha256 != after.sha256 or before.source_path != after.source_path:
        raise ViconParseError(
            "RAW_MUTATION_DETECTED",
            "source changed while parsing",
            source_path=path,
        )

    provenance = ParserProvenance(
        parser_id=PARSER_ID,
        parser_version=PARSER_VERSION,
        contract_id=contract.contract_id,
        contract_version=contract.version,
        source_id=before.source_id,
        run_id=stable_run_id(
            source_id=before.source_id,
            parser_version=PARSER_VERSION,
            contract_version=contract.version,
        ),
    )
    return ViconStackedRecord(
        source=before,
        provenance=provenance,
        sections=tuple(sections),
        evidence_only_sections=tuple(evidence),
        alignment=alignment,
        warnings=tuple(warnings),
    )


def _read_rows(path: Path) -> list[list[str]]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ViconParseError(
            "INGEST_SCHEMA_ERROR",
            "invalid UTF-8 Vicon source",
            source_path=path,
        ) from exc
    try:
        return list(csv.reader(StringIO(text)))
    except csv.Error as exc:
        raise ViconParseError(
            "INGEST_SCHEMA_ERROR",
            "Vicon CSV tokenization failed",
            source_path=path,
        ) from exc


def _marker(row: list[str], known: set[str]) -> str | None:
    cells = [cell for cell in row if cell != ""]
    if len(cells) == 1 and cells[0] in known:
        return cells[0]
    return None


def _next_marker(
    rows: list[list[str]],
    start: int,
    known: set[str],
) -> int:
    for index in range(start, len(rows)):
        if _marker(rows[index], known) is not None:
            return index
    return len(rows)


def _parse_block(
    name: str,
    block: list[list[str]],
    contract: ViconStackedContract,
    path: Path,
) -> ViconSection:
    layout = contract.layouts[name]
    if len(block) < 2 + layout.header_rows:
        raise ViconParseError(
            "INGEST_SCHEMA_ERROR",
            "section shorter than contract framing",
            source_path=path,
            details={"section": name},
        )

    rate = _positive_float(block[1], name, path)
    headers = block[2 : 2 + layout.header_rows]
    data = [
        row
        for row in block[2 + layout.header_rows :]
        if not _blank(row)
    ]
    column_header = headers[layout.column_header_index]
    units = (
        headers[layout.units_index]
        if layout.units_index is not None
        else None
    )
    group_header = (
        headers[0]
        if layout.header_rows > 1
        else [""] * len(column_header)
    )
    width = len(column_header)
    if width == 0:
        raise ViconParseError(
            "INGEST_SCHEMA_ERROR",
            "empty Vicon column header",
            source_path=path,
            details={"section": name},
        )

    for header_number, row in enumerate(headers, start=1):
        if len(row) != width:
            raise ViconParseError(
                "INGEST_SCHEMA_ERROR",
                "multi-row header width mismatch",
                source_path=path,
                details={
                    "section": name,
                    "header_row": header_number,
                },
            )
    for data_number, row in enumerate(data, start=1):
        if len(row) != width:
            raise ViconParseError(
                "INGEST_SCHEMA_ERROR",
                "data row width mismatch",
                source_path=path,
                details={"section": name, "data_row": data_number},
            )

    columns = tuple(
        _column_descriptor(
            index=index,
            group=(
                group_header[index]
                if index < len(group_header)
                else ""
            ),
            column=column_header[index],
            unit=(units[index] if units is not None else None),
        )
        for index in range(width)
    )
    values = tuple(
        tuple(cell if cell != "" else None for cell in row)
        for row in data
    )
    warnings = ("SECTION_PRESENT_WITHOUT_DATA",) if not data else ()
    return ViconSection(
        section_name=name,
        sampling_rate_hz=rate,
        raw_header_rows=tuple(
            tuple(cell for cell in row) for row in headers
        ),
        columns=columns,
        raw_rows=tuple(tuple(cell for cell in row) for row in data),
        values=values,
        warnings=warnings,
    )


def _column_descriptor(
    *,
    index: int,
    group: str,
    column: str,
    unit: str | None,
) -> ViconColumnDescriptor:
    component = column if column in {"X", "Y", "Z"} else None
    return ViconColumnDescriptor(
        index=index,
        group_label_raw=group,
        column_label_raw=column,
        unit_raw=unit if unit not in {None, ""} else None,
        component_label=component,
        anatomical_plane=None,
        anatomical_plane_evidence="NOT_VERIFIED",
    )


def _positive_float(
    row: list[str],
    name: str,
    path: Path,
) -> float:
    cells = [cell for cell in row if cell != ""]
    if len(cells) != 1:
        raise ViconParseError(
            "INGEST_SCHEMA_ERROR",
            "sampling-rate row must contain one value",
            source_path=path,
            details={"section": name},
        )
    try:
        value = float(cells[0])
    except ValueError as exc:
        raise ViconParseError(
            "INGEST_SCHEMA_ERROR",
            "section sampling rate is not numeric",
            source_path=path,
            details={"section": name},
        ) from exc
    if value <= 0:
        raise ViconParseError(
            "INGEST_SCHEMA_ERROR",
            "section sampling rate must be positive",
            source_path=path,
            details={"section": name},
        )
    return value


def _validate_alignment(
    context: MultimodalAlignmentContext,
    path: Path,
) -> None:
    if (
        context.sync_status not in {"NOT_VERIFIED", "VERIFIED", "UNAVAILABLE"}
        or context.quality
        not in {"NOT_VERIFIED", "GOOD", "WARNING", "UNUSABLE"}
        or context.availability not in {"AVAILABLE", "UNAVAILABLE", "PARTIAL"}
    ):
        raise ViconParseError(
            "MULTIMODAL_ALIGNMENT_INVALID",
            "unsupported alignment enum",
            source_path=path,
        )
    if context.sync_status != "VERIFIED" and (
        context.offset_seconds is not None
        or context.drift_ppm is not None
    ):
        raise ViconParseError(
            "MULTIMODAL_ALIGNMENT_INVALID",
            "offset/drift require VERIFIED synchronization",
            source_path=path,
        )
    if context.sync_status == "VERIFIED" and not context.evidence_refs:
        raise ViconParseError(
            "MULTIMODAL_ALIGNMENT_INVALID",
            "VERIFIED synchronization requires evidence refs",
            source_path=path,
        )


def _blank(row: list[str]) -> bool:
    return not row or all(cell == "" for cell in row)
