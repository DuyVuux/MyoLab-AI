"""DAY12 canonical MotionLab session contracts.

This module intentionally does not parse MR4 files and does not infer muscle, side,
protocol, or channel mapping from vendor names. It provides strict runtime models for
canonical Session/Signal/ProtocolContext plus DomainContext and process correlation.

Python: 3.11+
Pydantic: v2
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SCHEMA_VERSION = "1.0.0"


class ContractError(ValueError):
    """Raised when a cross-object DAY12 contract invariant is violated."""


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    SOURCE_REPORTED = "SOURCE_REPORTED"
    UNKNOWN = "UNKNOWN"
    NOT_VERIFIED = "NOT_VERIFIED"
    DISCOVERY_REQUIRED = "DISCOVERY_REQUIRED"


class StrictFrozenModel(BaseModel):
    """Base model that rejects undeclared fields and never silently trims source text."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=False,
        validate_assignment=True,
    )


class EvidenceString(StrictFrozenModel):
    value: str | None
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_evidence(self) -> "EvidenceString":
        _validate_evidence_semantics(
            value=self.value,
            status=self.evidence_status,
            refs=self.evidence_refs,
        )
        return self


class EvidencePositiveNumber(StrictFrozenModel):
    value: float | None = Field(default=None, gt=0)
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_evidence(self) -> "EvidencePositiveNumber":
        _validate_evidence_semantics(
            value=self.value,
            status=self.evidence_status,
            refs=self.evidence_refs,
        )
        return self


class EvidenceInteger(StrictFrozenModel):
    value: int | None = Field(default=None, ge=0)
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_evidence(self) -> "EvidenceInteger":
        _validate_evidence_semantics(
            value=self.value,
            status=self.evidence_status,
            refs=self.evidence_refs,
        )
        return self


class EvidenceTimestamp(StrictFrozenModel):
    value: str | None
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_evidence(self) -> "EvidenceTimestamp":
        _validate_evidence_semantics(
            value=self.value,
            status=self.evidence_status,
            refs=self.evidence_refs,
        )
        return self


class EvidenceQuantity(StrictFrozenModel):
    value: float | None
    unit: str | None
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_quantity(self) -> "EvidenceQuantity":
        _validate_evidence_semantics(
            value=self.value,
            status=self.evidence_status,
            refs=self.evidence_refs,
        )
        if self.value is None and self.unit is not None:
            raise ContractError("unit cannot be supplied when quantity value is absent")
        return self


def _validate_evidence_semantics(
    *, value: object | None, status: EvidenceStatus, refs: tuple[str, ...]
) -> None:
    if status is EvidenceStatus.VERIFIED and not refs:
        raise ContractError("VERIFIED values require at least one evidence reference")
    if status is EvidenceStatus.SOURCE_REPORTED and value is None:
        raise ContractError("SOURCE_REPORTED requires a source value")
    if status is EvidenceStatus.UNKNOWN and value is not None:
        raise ContractError("UNKNOWN must not carry an invented value")
    if any(not ref for ref in refs):
        raise ContractError("evidence references must be non-empty strings")
    if len(set(refs)) != len(refs):
        raise ContractError("evidence references must be unique")


class Side(StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BILATERAL = "BILATERAL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class EvidenceSide(StrictFrozenModel):
    value: Side | None
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_evidence(self) -> "EvidenceSide":
        _validate_evidence_semantics(
            value=self.value,
            status=self.evidence_status,
            refs=self.evidence_refs,
        )
        return self


class ProtocolContext(StrictFrozenModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    protocol_id: EvidenceString
    protocol_version: EvidenceString
    task: EvidenceString
    muscle_context: tuple[EvidenceString, ...]
    side: EvidenceSide
    load: EvidenceQuantity
    speed: EvidenceQuantity
    markers: tuple[EvidenceString, ...]
    clinical_context_ref: EvidenceString
    normalization_reference: EvidenceString


class ContextCategory(StrEnum):
    CLINICAL_PATIENT = "CLINICAL_PATIENT"
    HEALTHY_VOLUNTEER = "HEALTHY_VOLUNTEER"
    PUBLIC_DATASET = "PUBLIC_DATASET"
    VENDOR_SAMPLE = "VENDOR_SAMPLE"
    SYNTHETIC = "SYNTHETIC"
    UNKNOWN = "UNKNOWN"


class DomainContext(StrictFrozenModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    acquisition_site_id: EvidenceString
    device_manufacturer: EvidenceString
    device_model: EvidenceString
    device_revision: EvidenceString
    software_name: EvidenceString
    software_version: EvidenceString
    protocol_version: EvidenceString
    electrode_layout_id: EvidenceString
    channel_layout_id: EvidenceString
    session_day_index: EvidenceInteger
    task: EvidenceString
    load_context: EvidenceString
    speed_context: EvidenceString
    context_category: ContextCategory


class CanonicalChannelRef(StrictFrozenModel):
    channel_id: str | None
    mapping_version: str | None
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_mapping(self) -> "CanonicalChannelRef":
        if self.evidence_status is EvidenceStatus.UNKNOWN:
            if self.channel_id is not None or self.mapping_version is not None:
                raise ContractError("UNKNOWN channel mapping cannot carry mapped values")
        if self.channel_id is not None and self.mapping_version is None:
            raise ContractError("mapped channel requires mapping_version")
        if self.evidence_status is EvidenceStatus.VERIFIED and not self.evidence_refs:
            raise ContractError("VERIFIED channel mapping requires evidence")
        return self


class SignalType(StrEnum):
    EMG = "EMG"
    PRESSURE = "PRESSURE"
    COP = "COP"
    FORCE = "FORCE"
    EVENT = "EVENT"
    KINEMATIC = "KINEMATIC"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class SignalShape(StrEnum):
    SIGNAL_1D = "SIGNAL_1D"
    SIGNAL_2D = "SIGNAL_2D"
    TABLE = "TABLE"
    UNKNOWN = "UNKNOWN"


class CanonicalSignal(StrictFrozenModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    signal_id: str
    source_record_id: str
    source_signal_name: EvidenceString
    signal_type: SignalType
    shape: SignalShape
    sampling_rate_hz: EvidencePositiveNumber
    units: EvidenceString
    canonical_channel_ref: CanonicalChannelRef | None

    @field_validator("signal_id")
    @classmethod
    def validate_signal_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "sig_", 32)
        return value

    @field_validator("source_record_id")
    @classmethod
    def validate_source_record_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "src_sha256_", 64)
        return value


class ProcessCorrelation(StrictFrozenModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    case_id: str
    correlation_id: str
    session_id: str
    parent_correlation_id: str | None = None
    correlation_scope: Literal["INGESTION_TO_REVIEW"] = "INGESTION_TO_REVIEW"
    raw_payload_included: Literal[False] = False

    @field_validator("case_id")
    @classmethod
    def validate_case_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "case_", 32)
        return value

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "corr_", 32)
        return value

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "ses_", 32)
        return value

    @field_validator("parent_correlation_id")
    @classmethod
    def validate_parent_correlation_id(cls, value: str | None) -> str | None:
        if value is not None:
            _validate_prefixed_hex_id(value, "corr_", 32)
        return value


class RecordNameRef(StrictFrozenModel):
    source_record_id: str
    field_path: Literal["record_name"] = "record_name"
    exposure_policy: Literal["RESTRICTED_SOURCE_METADATA"] = "RESTRICTED_SOURCE_METADATA"

    @field_validator("source_record_id")
    @classmethod
    def validate_source_record_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "src_sha256_", 64)
        return value


class DeidentificationStatus(StrEnum):
    VERIFIED_DEIDENTIFIED = "VERIFIED_DEIDENTIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class GovernanceStatus(StrEnum):
    APPROVED = "APPROVED"
    RESTRICTED = "RESTRICTED"
    NOT_VERIFIED = "NOT_VERIFIED"
    UNKNOWN = "UNKNOWN"


class CanonicalizationReason(StrEnum):
    MISSING_PROTOCOL_METADATA = "MISSING_PROTOCOL_METADATA"
    UNKNOWN_SIDE = "UNKNOWN_SIDE"
    UNKNOWN_MUSCLE_CONTEXT = "UNKNOWN_MUSCLE_CONTEXT"
    UNKNOWN_CHANNEL_MAPPING = "UNKNOWN_CHANNEL_MAPPING"
    UNKNOWN_LAYOUT = "UNKNOWN_LAYOUT"
    UNKNOWN_SITE_CONFIGURATION = "UNKNOWN_SITE_CONFIGURATION"
    GOVERNANCE_NOT_VERIFIED = "GOVERNANCE_NOT_VERIFIED"
    DEIDENTIFICATION_NOT_VERIFIED = "DEIDENTIFICATION_NOT_VERIFIED"


class CanonicalSession(StrictFrozenModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    session_id: str
    subject_analysis_id: str
    source_record_ids: tuple[str, ...]
    record_name_ref: RecordNameRef | None
    measurement_time: EvidenceTimestamp
    deidentification_status: DeidentificationStatus
    governance_status: GovernanceStatus
    protocol_context: ProtocolContext
    domain_context: DomainContext
    process_correlation: ProcessCorrelation
    signals: tuple[CanonicalSignal, ...]
    canonicalization_reasons: tuple[CanonicalizationReason, ...] = ()

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "ses_", 32)
        return value

    @field_validator("subject_analysis_id")
    @classmethod
    def validate_subject_analysis_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "subj_", 32)
        return value

    @field_validator("source_record_ids")
    @classmethod
    def validate_source_record_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ContractError("canonical session requires at least one SourceRecord")
        for value in values:
            _validate_prefixed_hex_id(value, "src_sha256_", 64)
        if len(set(values)) != len(values):
            raise ContractError("source_record_ids must be unique")
        return values

    @model_validator(mode="after")
    def validate_cross_references(self) -> "CanonicalSession":
        source_ids = set(self.source_record_ids)
        if self.process_correlation.session_id != self.session_id:
            raise ContractError("process correlation must reference the same session_id")
        if self.record_name_ref is not None and self.record_name_ref.source_record_id not in source_ids:
            raise ContractError("record_name_ref must point to a session SourceRecord")
        for signal in self.signals:
            if signal.source_record_id not in source_ids:
                raise ContractError("every signal must reference a session SourceRecord")
        if len({signal.signal_id for signal in self.signals}) != len(self.signals):
            raise ContractError("signal_id values must be unique within a session")
        if len(set(self.canonicalization_reasons)) != len(self.canonicalization_reasons):
            raise ContractError("canonicalization reasons must be unique")
        return self


def new_session_id() -> str:
    """Return an opaque non-PHI session identifier.

    Random identity creation is intentionally not claimed deterministic. Reproducibility
    is achieved by persisting the created identity and replaying the same canonical record,
    not by re-deriving an identifier from PHI-bearing source metadata.
    """

    return f"ses_{uuid4().hex}"


def new_subject_analysis_id() -> str:
    """Return an opaque analysis subject identifier without embedding direct identifiers."""

    return f"subj_{uuid4().hex}"


def new_signal_id() -> str:
    return f"sig_{uuid4().hex}"


def new_case_id() -> str:
    return f"case_{uuid4().hex}"


def new_correlation_id() -> str:
    return f"corr_{uuid4().hex}"


def _validate_prefixed_hex_id(value: str, prefix: str, hex_length: int) -> None:
    if not value.startswith(prefix):
        raise ContractError(f"identifier must start with {prefix!r}")
    suffix = value[len(prefix) :]
    if len(suffix) != hex_length:
        raise ContractError(f"identifier suffix must have {hex_length} hexadecimal characters")
    try:
        int(suffix, 16)
    except ValueError as exc:
        raise ContractError("identifier suffix must be lowercase hexadecimal") from exc
    if suffix != suffix.lower():
        raise ContractError("identifier suffix must be lowercase hexadecimal")


__all__ = [
    "CanonicalSession",
    "CanonicalSignal",
    "ProtocolContext",
    "DomainContext",
    "ProcessCorrelation",
    "RecordNameRef",
    "EvidenceString",
    "EvidencePositiveNumber",
    "EvidenceInteger",
    "EvidenceTimestamp",
    "EvidenceQuantity",
    "EvidenceSide",
    "EvidenceStatus",
    "Side",
    "ContextCategory",
    "SignalType",
    "SignalShape",
    "CanonicalChannelRef",
    "DeidentificationStatus",
    "GovernanceStatus",
    "CanonicalizationReason",
    "ContractError",
    "new_session_id",
    "new_subject_analysis_id",
    "new_signal_id",
    "new_case_id",
    "new_correlation_id",
]
