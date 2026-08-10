"""Immutable-source provenance ledger for MotionLab ingestion.

DAY11 scope:
- hash source bytes without modifying them;
- derive a deterministic content-addressed source_id;
- append a first-seen SourceRecord to an append-only JSONL ledger;
- detect byte-identical re-ingestion as DUPLICATE without overwrite;
- verify later that a source still matches its recorded byte size/hash.

This module deliberately does NOT parse MR4, canonicalize sessions, resample,
filter, de-identify, or decide clinical usability. Those responsibilities belong
to later contracts/days.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field, field_validator
from filelock import FileLock


SCHEMA_VERSION: Final[str] = "1.0.0"
HASH_ALGORITHM: Final[str] = "sha256"
SOURCE_ID_PREFIX: Final[str] = "src_sha256_"


class SourceLedgerError(RuntimeError):
    """Base typed error for DAY11 ledger operations."""


class InvalidSourcePathError(SourceLedgerError):
    """Raised when the candidate source is not a readable regular file."""


class LedgerCorruptionError(SourceLedgerError):
    """Raised when the persisted ledger violates append-only identity invariants."""


class SourceIntegrityError(SourceLedgerError):
    """Raised when bytes no longer match a previously recorded source."""


class RegistrationStatus(str, Enum):
    REGISTERED = "REGISTERED"
    DUPLICATE = "DUPLICATE"


class SourceMetadata(BaseModel):
    """Source-level metadata captured without interpreting signal semantics.

    Unknown values remain ``None`` and must be paired with an explicit
    evidence_status in the SourceRecord. DAY12+ owns richer DomainContext.
    """
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    original_filename: str
    device_vendor: str | None = None
    device_family: str | None = None
    device_model: str | None = None
    software_name: str | None = None
    software_version: str | None = None
    export_family: str | None = None


class GovernanceMetadata(BaseModel):
    """Governance facts relevant to retention/research reuse.

    ``research_reuse_eligible`` is intentionally tri-state. ``None`` means
    UNKNOWN/NOT_VERIFIED and MUST NOT be treated as permission.
    """
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    deidentification_status: str
    governance_status: str
    research_reuse_eligible: bool | None = None
    retention_class: str | None = None


class SourceRecord(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    schema_version: str
    source_id: str
    content_hash_algorithm: str
    content_hash_digest: str
    byte_size: int = Field(ge=0)
    original_filename: str
    storage_reference: str
    ingestion_timestamp: str
    evidence_status: str
    device_vendor: str | None
    device_family: str | None
    device_model: str | None
    software_name: str | None
    software_version: str | None
    export_family: str | None
    deidentification_status: str
    governance_status: str
    research_reuse_eligible: bool | None
    retention_class: str | None
    immutable_raw: bool

    @field_validator("content_hash_digest")
    @classmethod
    def _validate_digest(cls, v: str) -> str:
        if len(v) != 64 or any(ch not in "0123456789abcdef" for ch in v):
            raise ValueError("Expected a lowercase 64-character SHA-256 digest")
        return v

    @field_validator("source_id")
    @classmethod
    def _validate_source_id(cls, v: str) -> str:
        if not v.startswith(SOURCE_ID_PREFIX):
            raise ValueError(f"source_id must start with {SOURCE_ID_PREFIX}")
        return v


class RegistrationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: RegistrationStatus
    source_record: SourceRecord
    appended: bool


def _ensure_regular_file(path: Path) -> None:
    if not path.exists():
        raise InvalidSourcePathError(f"Source does not exist: {path}")
    if not path.is_file():
        raise InvalidSourcePathError(f"Source is not a regular file: {path}")


def sha256_file(path: Path) -> str:
    """Return lowercase SHA-256 for exact source bytes without mutation."""
    _ensure_regular_file(path)
    try:
        with path.open("rb") as file_obj:
            return hashlib.file_digest(file_obj, HASH_ALGORITHM).hexdigest()
    except PermissionError as exc:
        raise InvalidSourcePathError(f"Source is not readable: {path}") from exc


def source_id_from_digest(digest: str) -> str:
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise ValueError("Expected a lowercase 64-character SHA-256 digest")
    return f"{SOURCE_ID_PREFIX}{digest}"


def _normalize_timestamp(value: datetime | None) -> str:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("ingestion_timestamp must be timezone-aware")
    return timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _json_line(record: SourceRecord) -> bytes:
    payload = json.dumps(
        record.model_dump(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (payload + "\n").encode("utf-8")


class JsonlSourceLedger:
    """Small append-only JSONL ledger for source identity/provenance.
    
    Enhanced with FileLock for thread-safe/process-safe concurrent appends.
    """

    def __init__(self, ledger_path: Path) -> None:
        self.ledger_path = ledger_path
        self.lock_path = self.ledger_path.with_suffix(".jsonl.lock")

    def _load_records(self) -> dict[str, SourceRecord]:
        if not self.ledger_path.exists():
            return {}
        if not self.ledger_path.is_file():
            raise LedgerCorruptionError(
                f"Ledger path is not a regular file: {self.ledger_path}"
            )

        records_by_digest: dict[str, SourceRecord] = {}
        source_ids: set[str] = set()

        with self.ledger_path.open("r", encoding="utf-8") as file_obj:
            for line_number, line in enumerate(file_obj, start=1):
                if not line.strip():
                    raise LedgerCorruptionError(
                        f"Blank ledger line is not allowed at line {line_number}"
                    )
                try:
                    payload: dict[str, Any] = json.loads(line)
                    record = SourceRecord(**payload)
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    raise LedgerCorruptionError(
                        f"Invalid ledger record at line {line_number}: {exc}"
                    ) from exc

                expected_id = source_id_from_digest(record.content_hash_digest)
                if record.source_id != expected_id:
                    raise LedgerCorruptionError(
                        f"source_id/hash mismatch at line {line_number}"
                    )
                if record.content_hash_algorithm != HASH_ALGORITHM:
                    raise LedgerCorruptionError(
                        f"Unsupported hash algorithm at line {line_number}"
                    )
                if record.source_id in source_ids:
                    raise LedgerCorruptionError(
                        f"Duplicate source_id in ledger at line {line_number}"
                    )
                if record.content_hash_digest in records_by_digest:
                    raise LedgerCorruptionError(
                        f"Duplicate digest appended at line {line_number}"
                    )

                source_ids.add(record.source_id)
                records_by_digest[record.content_hash_digest] = record

        return records_by_digest

    def register_source(
        self,
        source_path: Path,
        *,
        storage_reference: str,
        metadata: SourceMetadata,
        governance: GovernanceMetadata,
        evidence_status: str,
        ingestion_timestamp: datetime | None = None,
    ) -> RegistrationResult:
        """Register source bytes once; identical bytes are duplicate/idempotent.

        The method never writes to ``source_path``. The ledger is append-only:
        re-ingesting identical bytes returns the first immutable record and does
        not replace original filename/device/software/governance metadata.
        Thread-safe appending is ensured via FileLock.
        """

        _ensure_regular_file(source_path)
        digest = sha256_file(source_path)
        
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Lock for concurrent environments
        with FileLock(str(self.lock_path)):
            records = self._load_records()

            existing = records.get(digest)
            if existing is not None:
                return RegistrationResult(
                    status=RegistrationStatus.DUPLICATE,
                    source_record=existing,
                    appended=False,
                )

            record = SourceRecord(
                schema_version=SCHEMA_VERSION,
                source_id=source_id_from_digest(digest),
                content_hash_algorithm=HASH_ALGORITHM,
                content_hash_digest=digest,
                byte_size=source_path.stat().st_size,
                original_filename=metadata.original_filename,
                storage_reference=storage_reference,
                ingestion_timestamp=_normalize_timestamp(ingestion_timestamp),
                evidence_status=evidence_status,
                device_vendor=metadata.device_vendor,
                device_family=metadata.device_family,
                device_model=metadata.device_model,
                software_name=metadata.software_name,
                software_version=metadata.software_version,
                export_family=metadata.export_family,
                deidentification_status=governance.deidentification_status,
                governance_status=governance.governance_status,
                research_reuse_eligible=governance.research_reuse_eligible,
                retention_class=governance.retention_class,
                immutable_raw=True,
            )

            line = _json_line(record)
            fd = os.open(
                self.ledger_path,
                os.O_WRONLY | os.O_CREAT | os.O_APPEND,
                0o600,
            )
            try:
                with os.fdopen(fd, "ab", closefd=True) as file_obj:
                    file_obj.write(line)
                    file_obj.flush()
                    os.fsync(file_obj.fileno())
            except Exception:
                raise

        return RegistrationResult(
            status=RegistrationStatus.REGISTERED,
            source_record=record,
            appended=True,
        )

    def get_by_source_id(self, source_id: str) -> SourceRecord | None:
        for record in self._load_records().values():
            if record.source_id == source_id:
                return record
        return None

    def verify_source(self, source_path: Path, record: SourceRecord) -> None:
        """Raise SourceIntegrityError if source bytes differ from recorded truth."""

        _ensure_regular_file(source_path)
        current_size = source_path.stat().st_size
        if current_size != record.byte_size:
            raise SourceIntegrityError(
                f"Byte-size mismatch for {record.source_id}: "
                f"expected {record.byte_size}, got {current_size}"
            )

        current_digest = sha256_file(source_path)
        if current_digest != record.content_hash_digest:
            raise SourceIntegrityError(
                f"SHA-256 mismatch for {record.source_id}: source bytes changed"
            )
