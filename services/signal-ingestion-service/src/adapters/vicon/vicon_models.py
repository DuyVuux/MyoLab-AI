from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


from adapters.common.provenance import (
    ParserProvenance,
    SourceLinkage,
    sha256_file,
    source_linkage,
    stable_run_id,
)
class ViconParseError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        source_path: Path | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.source_path = str(source_path) if source_path else None
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "source_path": self.source_path,
            "details": self.details,
        }


@dataclass(frozen=True)
class MultimodalAlignmentContext:
    modality_id: str = "vicon_context"
    time_base: str = "VICON_SECTION_NATIVE"
    sync_source: str = "NOT_VERIFIED"
    offset_seconds: float | None = None
    drift_ppm: float | None = None
    sync_status: str = "NOT_VERIFIED"
    availability: str = "AVAILABLE"
    quality: str = "NOT_VERIFIED"
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ViconColumnDescriptor:
    index: int
    group_label_raw: str
    column_label_raw: str
    unit_raw: str | None
    component_label: str | None
    anatomical_plane: str | None
    anatomical_plane_evidence: str


@dataclass(frozen=True)
class ViconSection:
    section_name: str
    sampling_rate_hz: float
    raw_header_rows: tuple[tuple[str, ...], ...]
    columns: tuple[ViconColumnDescriptor, ...]
    raw_rows: tuple[tuple[str, ...], ...]
    values: tuple[tuple[str | None, ...], ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class UnsupportedSectionEvidence:
    section_name: str
    raw_rows: tuple[tuple[str, ...], ...]
    reason: str


@dataclass(frozen=True)
class ViconStackedRecord:
    source: SourceLinkage
    provenance: ParserProvenance
    sections: tuple[ViconSection, ...]
    evidence_only_sections: tuple[UnsupportedSectionEvidence, ...]
    alignment: MultimodalAlignmentContext
    warnings: tuple[str, ...]

    def section(self, name: str) -> ViconSection | None:
        return next(
            (item for item in self.sections if item.section_name == name),
            None,
        )



