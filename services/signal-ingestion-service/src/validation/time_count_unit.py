"""DAY13 deterministic validation for time, count, sampling rate, and units.

This module validates already-typed canonical inputs. It intentionally does NOT parse
MR4 CSV files (DAY16/DAY17), infer channel semantics (DAY14), perform signal QC
(DAY21+), or mutate raw data.

Python: 3.11+
Pydantic: v2
"""
from __future__ import annotations

import hashlib
import json
import math
from enum import StrEnum
from pathlib import Path
from typing import Iterable, Literal, Sequence

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALIDATOR_VERSION = "day13-time-count-unit.v0.1.0"
DEFAULT_CONFIG_VERSION = "day13-validation-profile.v0.1.0"


class ValidationContractError(ValueError):
    """Raised when validation inputs/config are structurally invalid."""


class UnitRegistryError(ValueError):
    """Raised when the unit registry is malformed or inconsistent."""


class UnsupportedUnitConversionError(ValueError):
    """Raised when a requested conversion is not explicitly authorized."""


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class CheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_EVALUATED = "NOT_EVALUATED"


class FindingCode(StrEnum):
    TIME_OK = "TIME_OK"
    TIME_SERIES_EMPTY = "TIME_SERIES_EMPTY"
    TIME_DUPLICATE = "TIME_DUPLICATE"
    TIME_NON_MONOTONIC = "TIME_NON_MONOTONIC"
    COUNT_MATCH = "COUNT_MATCH"
    COUNT_MISMATCH = "COUNT_MISMATCH"
    COUNT_METADATA_UNAVAILABLE = "COUNT_METADATA_UNAVAILABLE"
    BEGIN_TIME_MATCH = "BEGIN_TIME_MATCH"
    BEGIN_TIME_MISMATCH = "BEGIN_TIME_MISMATCH"
    BEGIN_TIME_METADATA_UNAVAILABLE = "BEGIN_TIME_METADATA_UNAVAILABLE"
    SAMPLING_RATE_VALID = "SAMPLING_RATE_VALID"
    SAMPLING_RATE_INVALID = "SAMPLING_RATE_INVALID"
    SAMPLING_RATE_METADATA_UNAVAILABLE = "SAMPLING_RATE_METADATA_UNAVAILABLE"
    SAMPLING_INTERVAL_MATCH = "SAMPLING_INTERVAL_MATCH"
    SAMPLING_INTERVAL_MISMATCH = "SAMPLING_INTERVAL_MISMATCH"
    UNIT_KNOWN = "UNIT_KNOWN"
    UNIT_UNKNOWN = "UNIT_UNKNOWN"
    UNIT_METADATA_UNAVAILABLE = "UNIT_METADATA_UNAVAILABLE"


class StrictFrozenModel(BaseModel):
    """Strict immutable runtime contract; source/vendor strings are not normalized."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=False,
        validate_assignment=True,
        allow_inf_nan=False,
    )


class ValidationConfig(StrictFrozenModel):
    version: str = DEFAULT_CONFIG_VERSION
    strict_monotonic_time: Literal[True] = True
    begin_time_abs_tolerance_seconds: float = Field(default=1e-9, ge=0)
    sampling_interval_abs_tolerance_seconds: float = Field(default=1e-6, ge=0)

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        if not value:
            raise ValueError("config version must be non-empty")
        return value


class SignalValidationInput(StrictFrozenModel):
    source_record_id: str
    signal_id: str
    timestamps_seconds: tuple[float, ...]
    metadata_count: int | None = Field(default=None, ge=0)
    begin_time_seconds: float | None = None
    sampling_rate_hz: float | None = None
    unit: str | None = None
    evidence_status: Literal[
        "VERIFIED",
        "SOURCE_REPORTED",
        "UNKNOWN",
        "NOT_VERIFIED",
        "DISCOVERY_REQUIRED",
    ] = "SOURCE_REPORTED"

    @field_validator("source_record_id")
    @classmethod
    def validate_source_record_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "src_sha256_", 64)
        return value

    @field_validator("signal_id")
    @classmethod
    def validate_signal_id(cls, value: str) -> str:
        _validate_prefixed_hex_id(value, "sig_", 32)
        return value


class ValidationProvenance(StrictFrozenModel):
    validator_version: str
    config_version: str
    unit_registry_version: str
    source_record_id: str
    signal_id: str
    evidence_status: str


class ValidationFinding(StrictFrozenModel):
    code: FindingCode
    status: CheckStatus
    severity: Severity
    message: str
    observed: str | int | float | None = None
    expected: str | int | float | None = None


class ValidationReport(StrictFrozenModel):
    validation_id: str
    overall_status: CheckStatus
    findings: tuple[ValidationFinding, ...]
    provenance: ValidationProvenance

    @model_validator(mode="after")
    def validate_overall_status(self) -> "ValidationReport":
        has_error = any(
            finding.status is CheckStatus.FAIL and finding.severity is Severity.ERROR
            for finding in self.findings
        )
        expected = CheckStatus.FAIL if has_error else CheckStatus.PASS
        if self.overall_status is not expected:
            raise ValidationContractError(
                f"overall_status must be {expected.value} for supplied findings"
            )
        return self


class UnitDefinition(StrictFrozenModel):
    symbol: str
    dimension: str
    canonical_unit: str
    observed_in_project: bool


class UnitConversion(StrictFrozenModel):
    source_unit: str
    target_unit: str
    factor: float = Field(gt=0)
    operation: Literal["multiply"] = "multiply"
    evidence_basis: str


class UnitRegistry(StrictFrozenModel):
    schema_version: str
    registry_id: str
    registry_version: str
    units: tuple[UnitDefinition, ...]
    conversions: tuple[UnitConversion, ...]

    @model_validator(mode="after")
    def validate_registry(self) -> "UnitRegistry":
        symbols = [unit.symbol for unit in self.units]
        if len(symbols) != len(set(symbols)):
            raise UnitRegistryError("unit symbols must be unique")
        known = set(symbols)
        for conversion in self.conversions:
            if conversion.source_unit not in known or conversion.target_unit not in known:
                raise UnitRegistryError("conversion references unknown unit")
        return self

    def has_unit(self, symbol: str) -> bool:
        return any(unit.symbol == symbol for unit in self.units)

    def conversion_factor(self, source_unit: str, target_unit: str) -> float:
        if source_unit == target_unit:
            if not self.has_unit(source_unit):
                raise UnsupportedUnitConversionError(f"unknown unit: {source_unit}")
            return 1.0
        for conversion in self.conversions:
            if (
                conversion.source_unit == source_unit
                and conversion.target_unit == target_unit
            ):
                return conversion.factor
        raise UnsupportedUnitConversionError(
            f"conversion not authorized: {source_unit} -> {target_unit}"
        )


class ConversionProvenance(StrictFrozenModel):
    registry_id: str
    registry_version: str
    source_record_id: str
    signal_id: str
    source_unit: str
    target_unit: str
    factor: float
    operation: Literal["multiply"] = "multiply"


class ConversionResult(StrictFrozenModel):
    values: tuple[float, ...]
    provenance: ConversionProvenance


def load_unit_registry(path: Path) -> UnitRegistry:
    """Load and validate the versioned YAML unit registry."""
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise UnitRegistryError(f"cannot read unit registry: {path}") from exc
    if not isinstance(payload, dict):
        raise UnitRegistryError("unit registry root must be a mapping")
    try:
        return UnitRegistry.model_validate(payload)
    except Exception as exc:  # Pydantic gives rich typed detail to caller.
        raise UnitRegistryError("unit registry validation failed") from exc


def validate_signal(
    signal: SignalValidationInput,
    *,
    registry: UnitRegistry,
    config: ValidationConfig | None = None,
) -> ValidationReport:
    """Validate one signal independently; no same-Fs assumption across signals."""
    cfg = config or ValidationConfig()
    findings: list[ValidationFinding] = []
    findings.extend(_validate_time(signal, cfg))
    findings.extend(_validate_count(signal))
    findings.extend(_validate_begin_time(signal, cfg))
    findings.extend(_validate_sampling(signal, cfg))
    findings.extend(_validate_unit(signal, registry))

    overall = (
        CheckStatus.FAIL
        if any(
            item.status is CheckStatus.FAIL and item.severity is Severity.ERROR
            for item in findings
        )
        else CheckStatus.PASS
    )
    provenance = ValidationProvenance(
        validator_version=VALIDATOR_VERSION,
        config_version=cfg.version,
        unit_registry_version=registry.registry_version,
        source_record_id=signal.source_record_id,
        signal_id=signal.signal_id,
        evidence_status=signal.evidence_status,
    )
    validation_id = _validation_id(signal, cfg, registry)
    return ValidationReport(
        validation_id=validation_id,
        overall_status=overall,
        findings=tuple(findings),
        provenance=provenance,
    )


def validate_signals(
    signals: Sequence[SignalValidationInput],
    *,
    registry: UnitRegistry,
    config: ValidationConfig | None = None,
) -> tuple[ValidationReport, ...]:
    """Validate heterogeneous-rate signals independently and deterministically."""
    return tuple(
        validate_signal(signal, registry=registry, config=config)
        for signal in signals
    )


def convert_values(
    values: Iterable[float],
    *,
    source_unit: str,
    target_unit: str,
    registry: UnitRegistry,
    source_record_id: str,
    signal_id: str,
) -> ConversionResult:
    """Return converted copies plus explicit provenance; input values are never mutated."""
    _validate_prefixed_hex_id(source_record_id, "src_sha256_", 64)
    _validate_prefixed_hex_id(signal_id, "sig_", 32)
    factor = registry.conversion_factor(source_unit, target_unit)
    materialized = tuple(float(value) for value in values)
    if any(not math.isfinite(value) for value in materialized):
        raise ValidationContractError("conversion input values must be finite")
    converted = tuple(value * factor for value in materialized)
    provenance = ConversionProvenance(
        registry_id=registry.registry_id,
        registry_version=registry.registry_version,
        source_record_id=source_record_id,
        signal_id=signal_id,
        source_unit=source_unit,
        target_unit=target_unit,
        factor=factor,
    )
    return ConversionResult(values=converted, provenance=provenance)


def _validate_time(
    signal: SignalValidationInput, config: ValidationConfig
) -> list[ValidationFinding]:
    timestamps = signal.timestamps_seconds
    if not timestamps:
        return [
            ValidationFinding(
                code=FindingCode.TIME_SERIES_EMPTY,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message="time series contains no samples",
                observed=0,
                expected=">=1 sample",
            )
        ]
    duplicate = any(curr == prev for prev, curr in zip(timestamps, timestamps[1:]))
    if duplicate and config.strict_monotonic_time:
        return [
            ValidationFinding(
                code=FindingCode.TIME_DUPLICATE,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message="duplicate timestamp violates strict monotonicity",
            )
        ]
    non_monotonic = any(curr < prev for prev, curr in zip(timestamps, timestamps[1:]))
    if non_monotonic:
        return [
            ValidationFinding(
                code=FindingCode.TIME_NON_MONOTONIC,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message="timestamp sequence decreases",
            )
        ]
    return [
        ValidationFinding(
            code=FindingCode.TIME_OK,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="timestamps are strictly increasing",
        )
    ]


def _validate_count(signal: SignalValidationInput) -> list[ValidationFinding]:
    if signal.metadata_count is None:
        return [
            ValidationFinding(
                code=FindingCode.COUNT_METADATA_UNAVAILABLE,
                status=CheckStatus.NOT_EVALUATED,
                severity=Severity.INFO,
                message="metadata count unavailable; no value was inferred",
            )
        ]
    observed = len(signal.timestamps_seconds)
    if signal.metadata_count != observed:
        return [
            ValidationFinding(
                code=FindingCode.COUNT_MISMATCH,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message="metadata count differs from observed sample count",
                observed=observed,
                expected=signal.metadata_count,
            )
        ]
    return [
        ValidationFinding(
            code=FindingCode.COUNT_MATCH,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="metadata count matches observed sample count",
            observed=observed,
            expected=signal.metadata_count,
        )
    ]


def _validate_begin_time(
    signal: SignalValidationInput, config: ValidationConfig
) -> list[ValidationFinding]:
    if signal.begin_time_seconds is None:
        return [
            ValidationFinding(
                code=FindingCode.BEGIN_TIME_METADATA_UNAVAILABLE,
                status=CheckStatus.NOT_EVALUATED,
                severity=Severity.INFO,
                message="begin_time unavailable; first timestamp was not promoted as metadata",
            )
        ]
    if not signal.timestamps_seconds:
        return [
            ValidationFinding(
                code=FindingCode.BEGIN_TIME_MISMATCH,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message="begin_time cannot be checked because the time series is empty",
                expected=signal.begin_time_seconds,
            )
        ]
    first = signal.timestamps_seconds[0]
    if not math.isclose(
        first,
        signal.begin_time_seconds,
        rel_tol=0.0,
        abs_tol=config.begin_time_abs_tolerance_seconds,
    ):
        return [
            ValidationFinding(
                code=FindingCode.BEGIN_TIME_MISMATCH,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message=(
                    "first timestamp does not match declared begin_time "
                    "within config tolerance"
                ),
                observed=first,
                expected=signal.begin_time_seconds,
            )
        ]
    return [
        ValidationFinding(
            code=FindingCode.BEGIN_TIME_MATCH,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="first timestamp matches declared begin_time",
            observed=first,
            expected=signal.begin_time_seconds,
        )
    ]


def _validate_sampling(
    signal: SignalValidationInput, config: ValidationConfig
) -> list[ValidationFinding]:
    fs = signal.sampling_rate_hz
    if fs is None:
        return [
            ValidationFinding(
                code=FindingCode.SAMPLING_RATE_METADATA_UNAVAILABLE,
                status=CheckStatus.NOT_EVALUATED,
                severity=Severity.INFO,
                message="sampling rate unavailable; no common/default Fs was assumed",
            )
        ]
    if fs <= 0:
        return [
            ValidationFinding(
                code=FindingCode.SAMPLING_RATE_INVALID,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message="sampling rate must be greater than zero",
                observed=fs,
                expected=">0 Hz",
            )
        ]
    findings = [
        ValidationFinding(
            code=FindingCode.SAMPLING_RATE_VALID,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="declared per-signal sampling rate is positive",
            observed=fs,
        )
    ]
    timestamps = signal.timestamps_seconds
    if len(timestamps) < 2:
        return findings
    expected_dt = 1.0 / fs
    mismatches = [
        abs((curr - prev) - expected_dt)
        for prev, curr in zip(timestamps, timestamps[1:])
        if abs((curr - prev) - expected_dt)
        > config.sampling_interval_abs_tolerance_seconds
    ]
    if mismatches:
        findings.append(
            ValidationFinding(
                code=FindingCode.SAMPLING_INTERVAL_MISMATCH,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message="timestamp interval is inconsistent with this signal's declared Fs",
                observed=max(mismatches),
                expected=expected_dt,
            )
        )
    else:
        findings.append(
            ValidationFinding(
                code=FindingCode.SAMPLING_INTERVAL_MATCH,
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="timestamp intervals are consistent with this signal's declared Fs",
                expected=expected_dt,
            )
        )
    return findings


def _validate_unit(
    signal: SignalValidationInput, registry: UnitRegistry
) -> list[ValidationFinding]:
    if signal.unit is None:
        return [
            ValidationFinding(
                code=FindingCode.UNIT_METADATA_UNAVAILABLE,
                status=CheckStatus.NOT_EVALUATED,
                severity=Severity.WARNING,
                message="unit unavailable; no default unit was inferred",
            )
        ]
    if not registry.has_unit(signal.unit):
        return [
            ValidationFinding(
                code=FindingCode.UNIT_UNKNOWN,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message="unit is not present in the versioned unit registry",
                observed=signal.unit,
            )
        ]
    return [
        ValidationFinding(
            code=FindingCode.UNIT_KNOWN,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="unit is present in the versioned unit registry",
            observed=signal.unit,
        )
    ]


def _validation_id(
    signal: SignalValidationInput,
    config: ValidationConfig,
    registry: UnitRegistry,
) -> str:
    payload = {
        "validator_version": VALIDATOR_VERSION,
        "config": config.model_dump(mode="json"),
        "registry_version": registry.registry_version,
        "signal": signal.model_dump(mode="json"),
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "val_sha256_" + hashlib.sha256(encoded).hexdigest()


def _validate_prefixed_hex_id(value: str, prefix: str, length: int) -> None:
    if not value.startswith(prefix):
        raise ValidationContractError(f"identifier must start with {prefix}")
    digest = value[len(prefix) :]
    if len(digest) != length:
        raise ValidationContractError(f"identifier digest must have {length} hex chars")
    if any(char not in "0123456789abcdef" for char in digest):
        raise ValidationContractError("identifier digest must be lowercase hexadecimal")
