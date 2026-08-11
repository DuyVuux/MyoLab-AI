from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

EVALUATOR_VERSION = "day29-data-integrity.v0.1.0"
SCHEMA_VERSION = "0.1"


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    SOURCE_REPORTED = "SOURCE_REPORTED"
    UNKNOWN = "UNKNOWN"
    NOT_VERIFIED = "NOT_VERIFIED"
    DISCOVERY_REQUIRED = "DISCOVERY_REQUIRED"


class Severity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class Supportability(StrEnum):
    SUPPORTABLE = "SUPPORTABLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class EvaluationStatus(StrEnum):
    EVALUATED = "EVALUATED"
    NOT_EVALUATED = "NOT_EVALUATED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class SignalQuality(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class DataQualityCode(StrEnum):
    TIMESTAMP_NON_MONOTONIC = "TIMESTAMP_NON_MONOTONIC"
    TIMESTAMP_DUPLICATE = "TIMESTAMP_DUPLICATE"
    SAMPLING_INTERVAL_MISMATCH = "SAMPLING_INTERVAL_MISMATCH"
    SAMPLING_RATE_NOT_VERIFIED = "SAMPLING_RATE_NOT_VERIFIED"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    UNIT_NOT_VERIFIED = "UNIT_NOT_VERIFIED"
    COORDINATE_CONVENTION_NOT_VERIFIED = (
        "COORDINATE_CONVENTION_NOT_VERIFIED"
    )
    MULTIMODAL_SYNC_NOT_VERIFIED = "MULTIMODAL_SYNC_NOT_VERIFIED"
    SYNC_OFFSET_EXCEEDED = "SYNC_OFFSET_EXCEEDED"
    SYNC_DRIFT_EXCEEDED = "SYNC_DRIFT_EXCEEDED"
    SYNC_THRESHOLD_NOT_VERIFIED = "SYNC_THRESHOLD_NOT_VERIFIED"
    MISSING_REQUIRED_MODALITY = "MISSING_REQUIRED_MODALITY"
    MISSING_OPTIONAL_MODALITY = "MISSING_OPTIONAL_MODALITY"
    DATA_INTEGRITY_VALIDATED = "DATA_INTEGRITY_VALIDATED"


BLOCKING_CODES = {
    DataQualityCode.TIMESTAMP_NON_MONOTONIC,
    DataQualityCode.TIMESTAMP_DUPLICATE,
    DataQualityCode.SAMPLING_INTERVAL_MISMATCH,
    DataQualityCode.UNIT_MISMATCH,
    DataQualityCode.SYNC_OFFSET_EXCEEDED,
    DataQualityCode.SYNC_DRIFT_EXCEEDED,
    DataQualityCode.MISSING_REQUIRED_MODALITY,
}


@dataclass(frozen=True)
class IngestValidationAnomaly:
    code: DataQualityCode
    severity: Severity
    evidence_status: EvidenceStatus
    source_refs: tuple[str, ...]
    modality_id: str | None = None
    required_for_downstream: bool = True

    def __post_init__(self) -> None:
        if not self.source_refs:
            raise ValueError("source_refs must not be empty")


@dataclass(frozen=True)
class AlignmentContext:
    modality_id: str
    time_base: str
    sync_source: str | None
    sync_status: EvidenceStatus
    offset_seconds: float | None
    drift_ppm: float | None
    quality: EvidenceStatus
    source_refs: tuple[str, ...]
    required_for_downstream: bool = False

    def __post_init__(self) -> None:
        if not self.modality_id:
            raise ValueError("modality_id is required")
        if not self.time_base:
            raise ValueError("time_base is required")
        if not self.source_refs:
            raise ValueError("source_refs must not be empty")


@dataclass(frozen=True)
class DistributionContext:
    session_id: str
    session_day: str | None
    protocol_id: str | None
    protocol_status: EvidenceStatus
    layout_id: str | None
    layout_status: EvidenceStatus
    mapping_version: str | None
    sampling_rates_hz: tuple[float, ...]
    sampling_status: EvidenceStatus
    unit_tokens: tuple[str, ...]
    unit_status: EvidenceStatus
    modalities_present: tuple[str, ...]
    modalities_expected: tuple[str, ...]
    modalities_required: tuple[str, ...]
    coordinate_convention_status: EvidenceStatus

    def __post_init__(self) -> None:
        if not self.session_id:
            raise ValueError("session_id is required")
        if any(rate <= 0 for rate in self.sampling_rates_hz):
            raise ValueError("sampling rates must be positive")


@dataclass(frozen=True)
class AlignmentPolicy:
    policy_id: str
    version: str
    threshold_status: EvidenceStatus
    max_abs_offset_seconds: float | None
    max_abs_drift_ppm: float | None

    def __post_init__(self) -> None:
        if self.threshold_status == EvidenceStatus.VERIFIED:
            if self.max_abs_offset_seconds is None:
                raise ValueError("verified policy requires offset threshold")
            if self.max_abs_drift_ppm is None:
                raise ValueError("verified policy requires drift threshold")
            if self.max_abs_offset_seconds < 0 or self.max_abs_drift_ppm < 0:
                raise ValueError("alignment thresholds must be non-negative")


@dataclass(frozen=True)
class DataQualityReason:
    code: DataQualityCode
    severity: Severity
    qc_supportability: Supportability
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...]
    modality_id: str | None = None


@dataclass(frozen=True)
class DistributionSupportInputs:
    readiness_level: str
    session_id: str
    session_day: str | None
    protocol_id: str | None
    protocol_status: EvidenceStatus
    layout_id: str | None
    layout_status: EvidenceStatus
    mapping_version: str | None
    sampling_rates_hz: tuple[float, ...]
    sampling_status: EvidenceStatus
    unit_tokens: tuple[str, ...]
    unit_status: EvidenceStatus
    sync_status_by_modality: tuple[tuple[str, str], ...]
    missing_modalities: tuple[str, ...]
    coordinate_convention_status: EvidenceStatus


@dataclass(frozen=True)
class DataIntegrityQcResult:
    schema_version: str
    evaluator_version: str
    config_version: str
    scope: str
    evaluation_status: EvaluationStatus
    signal_quality: SignalQuality | None
    integrity_gate_status: Supportability
    downstream_supportable: bool
    final_policy_status: str
    reasons: tuple[DataQualityReason, ...]
    distribution_support_inputs: DistributionSupportInputs

    def to_dict(self) -> dict[str, Any]:
        return _to_plain_dict(asdict(self))


def _to_plain_dict(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _to_plain_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain_dict(item) for item in value]
    if isinstance(value, StrEnum):
        return value.value
    return value


def load_alignment_policy(path: str | Path, profile_id: str) -> AlignmentPolicy:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    profile = raw["profiles"][profile_id]
    return AlignmentPolicy(
        policy_id=profile_id,
        version=str(profile["version"]),
        threshold_status=EvidenceStatus(profile["threshold_status"]),
        max_abs_offset_seconds=profile.get("max_abs_offset_seconds"),
        max_abs_drift_ppm=profile.get("max_abs_drift_ppm"),
    )


def _reason_from_anomaly(anomaly: IngestValidationAnomaly) -> DataQualityReason:
    blocking = (
        anomaly.code in BLOCKING_CODES and anomaly.required_for_downstream
    )
    if blocking:
        support = Supportability.BLOCKED
    elif anomaly.evidence_status in {
        EvidenceStatus.UNKNOWN,
        EvidenceStatus.NOT_VERIFIED,
        EvidenceStatus.DISCOVERY_REQUIRED,
    }:
        support = (
            Supportability.BLOCKED
            if anomaly.required_for_downstream
            else Supportability.REVIEW_REQUIRED
        )
    else:
        support = Supportability.REVIEW_REQUIRED
    return DataQualityReason(
        code=anomaly.code,
        severity=anomaly.severity,
        qc_supportability=support,
        evidence_status=anomaly.evidence_status,
        evidence_refs=anomaly.source_refs,
        modality_id=anomaly.modality_id,
    )


def _alignment_reasons(
    contexts: Iterable[AlignmentContext],
    policy: AlignmentPolicy,
) -> list[DataQualityReason]:
    reasons: list[DataQualityReason] = []
    for ctx in contexts:
        if ctx.sync_status != EvidenceStatus.VERIFIED:
            support = (
                Supportability.BLOCKED
                if ctx.required_for_downstream
                else Supportability.REVIEW_REQUIRED
            )
            reasons.append(
                DataQualityReason(
                    code=DataQualityCode.MULTIMODAL_SYNC_NOT_VERIFIED,
                    severity=(
                        Severity.HIGH
                        if ctx.required_for_downstream
                        else Severity.MODERATE
                    ),
                    qc_supportability=support,
                    evidence_status=ctx.sync_status,
                    evidence_refs=ctx.source_refs,
                    modality_id=ctx.modality_id,
                )
            )
            continue
        if policy.threshold_status != EvidenceStatus.VERIFIED:
            support = (
                Supportability.BLOCKED
                if ctx.required_for_downstream
                else Supportability.REVIEW_REQUIRED
            )
            reasons.append(
                DataQualityReason(
                    code=DataQualityCode.SYNC_THRESHOLD_NOT_VERIFIED,
                    severity=(
                        Severity.HIGH
                        if ctx.required_for_downstream
                        else Severity.MODERATE
                    ),
                    qc_supportability=support,
                    evidence_status=policy.threshold_status,
                    evidence_refs=ctx.source_refs,
                    modality_id=ctx.modality_id,
                )
            )
            continue
        assert policy.max_abs_offset_seconds is not None
        assert policy.max_abs_drift_ppm is not None
        if ctx.offset_seconds is None or ctx.drift_ppm is None:
            support = (
                Supportability.BLOCKED
                if ctx.required_for_downstream
                else Supportability.REVIEW_REQUIRED
            )
            reasons.append(
                DataQualityReason(
                    code=DataQualityCode.MULTIMODAL_SYNC_NOT_VERIFIED,
                    severity=Severity.HIGH,
                    qc_supportability=support,
                    evidence_status=EvidenceStatus.NOT_VERIFIED,
                    evidence_refs=ctx.source_refs,
                    modality_id=ctx.modality_id,
                )
            )
            continue
        if abs(ctx.offset_seconds) > policy.max_abs_offset_seconds:
            reasons.append(
                DataQualityReason(
                    code=DataQualityCode.SYNC_OFFSET_EXCEEDED,
                    severity=Severity.HIGH,
                    qc_supportability=(
                        Supportability.BLOCKED
                        if ctx.required_for_downstream
                        else Supportability.REVIEW_REQUIRED
                    ),
                    evidence_status=EvidenceStatus.VERIFIED,
                    evidence_refs=ctx.source_refs,
                    modality_id=ctx.modality_id,
                )
            )
        if abs(ctx.drift_ppm) > policy.max_abs_drift_ppm:
            reasons.append(
                DataQualityReason(
                    code=DataQualityCode.SYNC_DRIFT_EXCEEDED,
                    severity=Severity.HIGH,
                    qc_supportability=(
                        Supportability.BLOCKED
                        if ctx.required_for_downstream
                        else Supportability.REVIEW_REQUIRED
                    ),
                    evidence_status=EvidenceStatus.VERIFIED,
                    evidence_refs=ctx.source_refs,
                    modality_id=ctx.modality_id,
                )
            )
    return reasons


def build_distribution_support_inputs(
    context: DistributionContext,
    alignments: Iterable[AlignmentContext],
) -> DistributionSupportInputs:
    alignments_tuple = tuple(alignments)
    sync_status = tuple(
        sorted((item.modality_id, item.sync_status.value) for item in alignments_tuple)
    )
    missing = tuple(
        sorted(set(context.modalities_expected) - set(context.modalities_present))
    )
    return DistributionSupportInputs(
        readiness_level="CONTEXT_ONLY_NO_OOD_SCORE",
        session_id=context.session_id,
        session_day=context.session_day,
        protocol_id=context.protocol_id,
        protocol_status=context.protocol_status,
        layout_id=context.layout_id,
        layout_status=context.layout_status,
        mapping_version=context.mapping_version,
        sampling_rates_hz=tuple(sorted(set(context.sampling_rates_hz))),
        sampling_status=context.sampling_status,
        unit_tokens=tuple(sorted(set(context.unit_tokens))),
        unit_status=context.unit_status,
        sync_status_by_modality=sync_status,
        missing_modalities=missing,
        coordinate_convention_status=context.coordinate_convention_status,
    )


def evaluate_data_integrity(
    *,
    anomalies: Iterable[IngestValidationAnomaly],
    distribution_context: DistributionContext,
    alignment_contexts: Iterable[AlignmentContext],
    alignment_policy: AlignmentPolicy,
    config_version: str,
) -> DataIntegrityQcResult:
    anomalies_tuple = tuple(anomalies)
    alignments_tuple = tuple(alignment_contexts)
    reasons = [_reason_from_anomaly(item) for item in anomalies_tuple]
    reasons.extend(_alignment_reasons(alignments_tuple, alignment_policy))

    expected = set(distribution_context.modalities_expected)
    required = set(distribution_context.modalities_required)
    present = set(distribution_context.modalities_present)
    for modality in sorted(expected - present):
        is_required = modality in required
        reasons.append(
            DataQualityReason(
                code=(
                    DataQualityCode.MISSING_REQUIRED_MODALITY
                    if is_required
                    else DataQualityCode.MISSING_OPTIONAL_MODALITY
                ),
                severity=Severity.HIGH if is_required else Severity.INFO,
                qc_supportability=(
                    Supportability.BLOCKED
                    if is_required
                    else Supportability.REVIEW_REQUIRED
                ),
                evidence_status=EvidenceStatus.VERIFIED,
                evidence_refs=(f"modality://{modality}",),
                modality_id=modality,
            )
        )

    if distribution_context.sampling_status != EvidenceStatus.VERIFIED:
        reasons.append(
            DataQualityReason(
                code=DataQualityCode.SAMPLING_RATE_NOT_VERIFIED,
                severity=Severity.HIGH,
                qc_supportability=Supportability.BLOCKED,
                evidence_status=distribution_context.sampling_status,
                evidence_refs=(f"session://{distribution_context.session_id}",),
            )
        )
    if distribution_context.unit_status != EvidenceStatus.VERIFIED:
        reasons.append(
            DataQualityReason(
                code=DataQualityCode.UNIT_NOT_VERIFIED,
                severity=Severity.HIGH,
                qc_supportability=Supportability.BLOCKED,
                evidence_status=distribution_context.unit_status,
                evidence_refs=(f"session://{distribution_context.session_id}",),
            )
        )

    if not reasons:
        reasons.append(
            DataQualityReason(
                code=DataQualityCode.DATA_INTEGRITY_VALIDATED,
                severity=Severity.INFO,
                qc_supportability=Supportability.SUPPORTABLE,
                evidence_status=EvidenceStatus.VERIFIED,
                evidence_refs=(f"session://{distribution_context.session_id}",),
            )
        )

    has_block = any(
        item.qc_supportability == Supportability.BLOCKED for item in reasons
    )
    has_review = any(
        item.qc_supportability == Supportability.REVIEW_REQUIRED
        for item in reasons
    )
    if has_block:
        quality = SignalQuality.FAIL
        gate = Supportability.BLOCKED
    elif has_review:
        quality = SignalQuality.WARNING
        gate = Supportability.REVIEW_REQUIRED
    else:
        quality = SignalQuality.PASS
        gate = Supportability.SUPPORTABLE

    return DataIntegrityQcResult(
        schema_version=SCHEMA_VERSION,
        evaluator_version=EVALUATOR_VERSION,
        config_version=config_version,
        scope="SESSION",
        evaluation_status=EvaluationStatus.EVALUATED,
        signal_quality=quality,
        integrity_gate_status=gate,
        downstream_supportable=gate == Supportability.SUPPORTABLE,
        final_policy_status="DATA_INTEGRITY_GATE_ONLY_DAY30_QC_AGGREGATION_DEFERRED",
        reasons=tuple(reasons),
        distribution_support_inputs=build_distribution_support_inputs(
            distribution_context, alignments_tuple
        ),
    )


def stable_result_digest(result: DataIntegrityQcResult) -> str:
    payload = json.dumps(
        result.to_dict(), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def forbidden_ood_fields(payload: Mapping[str, Any]) -> set[str]:
    forbidden = {
        "ood_score",
        "ood_probability",
        "shift_threshold",
        "reference_distribution_fit",
        "automatic_domain_adaptation",
        "test_time_adaptation",
        "shared_embedding",
    }
    return forbidden.intersection(payload.keys())
