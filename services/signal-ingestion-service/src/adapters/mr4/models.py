"""Shared MR4 parser primitives.

The module is deliberately small and dependency-light. It preserves source provenance,
provides stable typed failures, and never mutates source files.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from adapters.common.provenance import (
    ParserProvenance,
    SourceLinkage,
    sha256_file,
    source_linkage,
    stable_run_id,
)


class EvidenceStatus(StrEnum):
    OBSERVED = "OBSERVED"
    SOURCE_REPORTED = "SOURCE_REPORTED"
    UNKNOWN = "UNKNOWN"
    NOT_VERIFIED = "NOT_VERIFIED"


class ParseStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class Mr4ParseError(ValueError):
    """Typed fail-closed parser exception with stable reason code."""

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
class FieldValue:
    name: str
    raw_value: str
    evidence_status: str = EvidenceStatus.SOURCE_REPORTED.value


@dataclass(frozen=True)
class SignalDescriptor:
    signal_id: str
    vendor_name: str
    semantic_role: str
    unit: str | None
    unit_evidence: str
    sampling_rate_hz: float | None
    columns: tuple[str, ...]
    raw_values: tuple[tuple[str | None, ...], ...]
    unknown_semantics: bool


def stable_signal_id(source_id: str, vendor_name: str) -> str:
    payload = f"{source_id}\x1f{vendor_name}".encode("utf-8")
    return "sig_" + hashlib.sha256(payload).hexdigest()[:32]


def to_primitive(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {key: to_primitive(item) for key, item in value.items()}
    return value

@dataclass(frozen=True)
class SeparatedLayoutProfile:
    profile_id: str
    version: str
    status: str
    evidence_status: str
    info_layout: str
    signal_layout: str
    site_verified: bool

@dataclass(frozen=True)
class SeparatedSignal:
    source: SourceLinkage
    signal_id: str
    vendor_name: str | None
    signal_type: str
    frequency_hz: float | None
    count: int | None
    unit: str | None
    begin_time_seconds: float | None
    time_unit: str | None
    columns: tuple[str, ...]
    raw_rows: tuple[tuple[str, ...], ...]
    timestamps_seconds: tuple[float, ...]
    values: tuple[tuple[str | None, ...], ...]
    warnings: tuple[str, ...]

@dataclass(frozen=True)
class UnknownSignalEvidence:
    source: SourceLinkage
    vendor_name: str | None
    declared_type: str | None
    metadata: tuple[FieldValue, ...]
    data_header: tuple[str, ...]
    raw_rows: tuple[tuple[str, ...], ...]
    reason_code: str

@dataclass(frozen=True)
class SeparatedRecord:
    directory: str
    info_source: SourceLinkage
    source_files: tuple[SourceLinkage, ...]
    provenance: ParserProvenance
    layout_profile_id: str
    layout_profile_version: str
    info_metadata: tuple[FieldValue, ...]
    unknown_info_metadata: tuple[FieldValue, ...]
    signals: tuple[SeparatedSignal, ...]
    unknown_signals: tuple[UnknownSignalEvidence, ...]
    warnings: tuple[str, ...]
    assembly_id: str
