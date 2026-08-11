from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

SCHEMA_VERSION = "0.1"
AGGREGATION_ALGORITHM_VERSION = "day30-hierarchical-aggregation.v0.1.0"
QC_CONTRACT_VERSION = "DAY30-v0.1"


class EvaluationStatus(StrEnum):
    EVALUATED = "EVALUATED"
    NOT_EVALUATED = "NOT_EVALUATED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class SignalQuality(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class Supportability(StrEnum):
    SUPPORTABLE = "SUPPORTABLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
    NOT_EVALUATED = "NOT_EVALUATED"


class LabelCandidate(StrEnum):
    PASS = "PASS_CANDIDATE"
    WARNING = "WARNING_CANDIDATE"
    FAIL = "FAIL_CANDIDATE"
    ABSTAIN = "ABSTAIN"
    UNKNOWN = "UNKNOWN"


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    SOURCE_REPORTED = "SOURCE_REPORTED"
    UNKNOWN = "UNKNOWN"
    NOT_VERIFIED = "NOT_VERIFIED"
    DISCOVERY_REQUIRED = "DISCOVERY_REQUIRED"


class ThresholdStatus(StrEnum):
    VERIFIED_FOR_SYNTHETIC = "VERIFIED_FOR_SYNTHETIC"
    NOT_VERIFIED = "NOT_VERIFIED"


class SemanticContradictionError(ValueError):
    """Raised when a result combines logically impossible QC semantics."""


class WeakLabelContractError(ValueError):
    """Raised when a weak label tries to exceed its evidence authority."""


class AggregationPolicyError(ValueError):
    """Raised when a configured aggregation policy is internally invalid."""


@dataclass(frozen=True)
class RawDetectorEvidence:
    detector_id: str
    target_id: str
    reason_code: str
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...]
    measurements: tuple[tuple[str, float | int | str | None], ...] = ()

    def __post_init__(self) -> None:
        if not self.detector_id or not self.target_id or not self.reason_code:
            raise ValueError("raw evidence identifiers must be non-empty")
        if not self.evidence_refs:
            raise ValueError("raw evidence must keep provenance refs")


@dataclass(frozen=True)
class WeakLabelCandidate:
    lf_id: str
    target_id: str
    reason_code: str
    label_candidate: LabelCandidate
    severity: str
    qc_supportability: Supportability
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...]
    ground_truth_claim: bool = False
    expert_label_claim: bool = False
    clinical_label: str | None = None

    def __post_init__(self) -> None:
        if not self.lf_id or not self.target_id or not self.reason_code:
            raise WeakLabelContractError("weak label identifiers must be non-empty")
        if not self.evidence_refs:
            raise WeakLabelContractError("weak label requires evidence refs")
        if self.ground_truth_claim or self.expert_label_claim:
            raise WeakLabelContractError(
                "weak supervision output cannot claim ground truth or expert truth"
            )
        if self.clinical_label is not None:
            raise WeakLabelContractError(
                "weak supervision output cannot carry a clinical diagnosis label"
            )


@dataclass(frozen=True)
class IntegrityFinding:
    scope: str
    target_id: str
    reason_code: str
    blocking: bool
    evidence_status: EvidenceStatus
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.scope not in {"SESSION", "CHANNEL", "WINDOW"}:
            raise ValueError("integrity scope must be SESSION, CHANNEL, or WINDOW")
        if not self.evidence_refs:
            raise ValueError("integrity finding requires evidence refs")


@dataclass(frozen=True)
class AggregationPolicy:
    profile_id: str
    version: str
    threshold_status: ThresholdStatus
    required_lf_ids: tuple[str, ...]
    optional_lf_ids: tuple[str, ...]
    window_fail_reason_codes: tuple[str, ...]
    physiology_protection_reason_codes: tuple[str, ...]
    ambiguous_reason_codes: tuple[str, ...]
    channel_min_usable_window_ratio: float | None
    session_max_allowed_bad_channels: int | None
    require_complete_window_evidence: bool

    def __post_init__(self) -> None:
        overlap = set(self.required_lf_ids) & set(self.optional_lf_ids)
        if overlap:
            raise AggregationPolicyError(
                f"LF cannot be required and optional simultaneously: {sorted(overlap)}"
            )
        if self.threshold_status == ThresholdStatus.VERIFIED_FOR_SYNTHETIC:
            if self.channel_min_usable_window_ratio is None:
                raise AggregationPolicyError("verified profile requires channel threshold")
            if self.session_max_allowed_bad_channels is None:
                raise AggregationPolicyError("verified profile requires session threshold")
        if self.channel_min_usable_window_ratio is not None:
            if not 0.0 <= self.channel_min_usable_window_ratio <= 1.0:
                raise AggregationPolicyError("usable-window ratio must be within [0,1]")
        if self.session_max_allowed_bad_channels is not None:
            if self.session_max_allowed_bad_channels < 0:
                raise AggregationPolicyError("bad-channel threshold cannot be negative")


@dataclass(frozen=True)
class AggregationMetrics:
    usable_window_ratio: float | None
    total_evaluated_windows: int
    usable_windows_count: int
    bad_window_count: int
    bad_channel_count: int
    total_channels_count: int


@dataclass(frozen=True)
class ScopeHierarchy:
    session_id: str
    target_scope: str
    channel_id: str | None = None
    window_id: str | None = None


@dataclass(frozen=True)
class QcAggregationResult:
    schema_version: str
    taxonomy_version: str
    evaluation_status: EvaluationStatus
    scope_hierarchy: ScopeHierarchy
    signal_quality: SignalQuality | None
    qc_supportability: Supportability
    metrics: AggregationMetrics
    evidence_reasons: tuple[str, ...]
    disposition_reasons: tuple[str, ...]
    source_refs: tuple[str, ...]
    policy_profile_id: str
    config_version: str
    aggregation_algorithm_version: str = AGGREGATION_ALGORITHM_VERSION
    qc_contract_version: str = QC_CONTRACT_VERSION
    critical_failure: bool = False

    def __post_init__(self) -> None:
        validate_result_semantics(self)

    def to_dict(self) -> dict[str, Any]:
        raw = _plain(asdict(self))
        raw["reasons"] = {
            "evidence_reasons": raw.pop("evidence_reasons"),
            "disposition_reasons": raw.pop("disposition_reasons"),
        }
        raw["provenance"] = {
            "qc_contract_version": raw.pop("qc_contract_version"),
            "aggregation_algorithm_version": raw.pop(
                "aggregation_algorithm_version"
            ),
            "config_version": raw.pop("config_version"),
            "policy_profile_id": raw.pop("policy_profile_id"),
            "source_refs": raw.pop("source_refs"),
        }
        raw.pop("critical_failure")
        return raw


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, StrEnum):
        return value.value
    return value


def load_aggregation_policy(path: str | Path, profile_id: str) -> AggregationPolicy:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    profile = raw["profiles"][profile_id]
    return AggregationPolicy(
        profile_id=profile_id,
        version=str(profile["version"]),
        threshold_status=ThresholdStatus(profile["threshold_status"]),
        required_lf_ids=tuple(profile["required_lf_ids"]),
        optional_lf_ids=tuple(profile.get("optional_lf_ids", [])),
        window_fail_reason_codes=tuple(profile["window_fail_reason_codes"]),
        physiology_protection_reason_codes=tuple(
            profile["physiology_protection_reason_codes"]
        ),
        ambiguous_reason_codes=tuple(profile["ambiguous_reason_codes"]),
        channel_min_usable_window_ratio=profile.get(
            "channel_min_usable_window_ratio"
        ),
        session_max_allowed_bad_channels=profile.get(
            "session_max_allowed_bad_channels"
        ),
        require_complete_window_evidence=bool(
            profile["require_complete_window_evidence"]
        ),
    )


def _sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _source_refs(
    raw_evidence: Iterable[RawDetectorEvidence],
    labels: Iterable[WeakLabelCandidate],
    integrity: Iterable[IntegrityFinding],
    child_results: Iterable[QcAggregationResult] = (),
) -> tuple[str, ...]:
    refs: list[str] = []
    for item in raw_evidence:
        refs.extend(item.evidence_refs)
    for item in labels:
        refs.extend(item.evidence_refs)
    for item in integrity:
        refs.extend(item.evidence_refs)
    for result in child_results:
        refs.extend(result.source_refs)
    return _sorted_unique(refs or ("evidence://day30/no-source-ref",))


def _empty_metrics() -> AggregationMetrics:
    return AggregationMetrics(
        usable_window_ratio=None,
        total_evaluated_windows=0,
        usable_windows_count=0,
        bad_window_count=0,
        bad_channel_count=0,
        total_channels_count=0,
    )


def _unknown_result(
    *,
    hierarchy: ScopeHierarchy,
    policy: AggregationPolicy,
    reasons: Iterable[str],
    source_refs: Iterable[str],
    evaluation_status: EvaluationStatus = EvaluationStatus.INSUFFICIENT_EVIDENCE,
    metrics: AggregationMetrics | None = None,
) -> QcAggregationResult:
    return QcAggregationResult(
        schema_version=SCHEMA_VERSION,
        taxonomy_version="0.2",
        evaluation_status=evaluation_status,
        scope_hierarchy=hierarchy,
        signal_quality=None,
        qc_supportability=Supportability.NOT_EVALUATED,
        metrics=metrics or _empty_metrics(),
        evidence_reasons=_sorted_unique(reasons),
        disposition_reasons=("QC_NOT_EVALUATED",),
        source_refs=_sorted_unique(source_refs),
        policy_profile_id=policy.profile_id,
        config_version=policy.version,
    )


def aggregate_window(
    *,
    session_id: str,
    channel_id: str,
    window_id: str,
    raw_evidence: Sequence[RawDetectorEvidence],
    weak_labels: Sequence[WeakLabelCandidate],
    integrity_findings: Sequence[IntegrityFinding],
    policy: AggregationPolicy,
) -> QcAggregationResult:
    """Aggregate one WindowIdentity without mutating detector evidence or raw data."""
    for item in raw_evidence:
        if item.target_id != window_id:
            raise ValueError("raw evidence target_id does not match window_id")
    for item in weak_labels:
        if item.target_id != window_id:
            raise WeakLabelContractError(
                "weak-label target_id must equal canonical DAY22 window_id"
            )
    for item in integrity_findings:
        if item.scope == "WINDOW" and item.target_id != window_id:
            raise ValueError("window integrity target_id mismatch")

    refs = _source_refs(raw_evidence, weak_labels, integrity_findings)
    hierarchy = ScopeHierarchy(
        session_id=session_id,
        channel_id=channel_id,
        window_id=window_id,
        target_scope="WINDOW",
    )

    hard_blocks = [item for item in integrity_findings if item.blocking]
    if hard_blocks:
        return QcAggregationResult(
            schema_version=SCHEMA_VERSION,
            taxonomy_version="0.2",
            evaluation_status=EvaluationStatus.EVALUATED,
            scope_hierarchy=hierarchy,
            signal_quality=SignalQuality.FAIL,
            qc_supportability=Supportability.BLOCKED,
            metrics=AggregationMetrics(0.0, 1, 0, 1, 0, 0),
            evidence_reasons=_sorted_unique(item.reason_code for item in hard_blocks),
            disposition_reasons=("QUALITY_BLOCKED",),
            source_refs=refs,
            policy_profile_id=policy.profile_id,
            config_version=policy.version,
            critical_failure=True,
        )

    allowed_lf_ids = set(policy.required_lf_ids) | set(policy.optional_lf_ids)
    unknown_lf_ids = sorted({item.lf_id for item in weak_labels} - allowed_lf_ids)
    if unknown_lf_ids:
        raise WeakLabelContractError(
            f"unregistered LF IDs for policy {policy.profile_id}: {unknown_lf_ids}"
        )
    lf_ids = [item.lf_id for item in weak_labels]
    duplicate_lf_ids = sorted(
        {lf_id for lf_id in lf_ids if lf_ids.count(lf_id) > 1}
    )
    if duplicate_lf_ids:
        raise WeakLabelContractError(
            f"duplicate LF candidates for one window: {duplicate_lf_ids}"
        )
    labels_by_lf = {item.lf_id: item for item in weak_labels}
    missing_required = [
        lf_id for lf_id in policy.required_lf_ids if lf_id not in labels_by_lf
    ]
    unresolved_required = [
        lf_id
        for lf_id in policy.required_lf_ids
        if lf_id in labels_by_lf
        and labels_by_lf[lf_id].label_candidate
        in {LabelCandidate.ABSTAIN, LabelCandidate.UNKNOWN}
    ]
    if missing_required or unresolved_required:
        reasons = ["QC_NOT_EVALUATED", "INSUFFICIENT_QC_EVIDENCE"]
        return _unknown_result(
            hierarchy=hierarchy,
            policy=policy,
            reasons=reasons,
            source_refs=refs,
        )

    reason_codes = {item.reason_code for item in weak_labels}
    fail_candidates = [
        item
        for item in weak_labels
        if item.label_candidate == LabelCandidate.FAIL
        and item.reason_code in set(policy.window_fail_reason_codes)
    ]
    if fail_candidates:
        return QcAggregationResult(
            schema_version=SCHEMA_VERSION,
            taxonomy_version="0.2",
            evaluation_status=EvaluationStatus.EVALUATED,
            scope_hierarchy=hierarchy,
            signal_quality=SignalQuality.FAIL,
            qc_supportability=Supportability.BLOCKED,
            metrics=AggregationMetrics(0.0, 1, 0, 1, 0, 0),
            evidence_reasons=_sorted_unique(reason_codes),
            disposition_reasons=("QUALITY_BLOCKED",),
            source_refs=refs,
            policy_profile_id=policy.profile_id,
            config_version=policy.version,
            critical_failure=False,
        )

    has_warning = any(
        item.label_candidate == LabelCandidate.WARNING for item in weak_labels
    )
    has_ambiguous = bool(reason_codes & set(policy.ambiguous_reason_codes))
    has_physiology = bool(
        reason_codes & set(policy.physiology_protection_reason_codes)
    )
    if has_warning or has_ambiguous or has_physiology:
        return QcAggregationResult(
            schema_version=SCHEMA_VERSION,
            taxonomy_version="0.2",
            evaluation_status=EvaluationStatus.EVALUATED,
            scope_hierarchy=hierarchy,
            signal_quality=SignalQuality.WARNING,
            qc_supportability=Supportability.REVIEW_REQUIRED,
            metrics=AggregationMetrics(1.0, 1, 1, 0, 0, 0),
            evidence_reasons=_sorted_unique(reason_codes),
            disposition_reasons=("CLINICIAN_REVIEW_REQUIRED",),
            source_refs=refs,
            policy_profile_id=policy.profile_id,
            config_version=policy.version,
        )

    return QcAggregationResult(
        schema_version=SCHEMA_VERSION,
        taxonomy_version="0.2",
        evaluation_status=EvaluationStatus.EVALUATED,
        scope_hierarchy=hierarchy,
        signal_quality=SignalQuality.PASS,
        qc_supportability=Supportability.SUPPORTABLE,
        metrics=AggregationMetrics(1.0, 1, 1, 0, 0, 0),
        evidence_reasons=_sorted_unique(reason_codes or ("DATA_INTEGRITY_VALIDATED",)),
        disposition_reasons=(),
        source_refs=refs,
        policy_profile_id=policy.profile_id,
        config_version=policy.version,
    )


def aggregate_channel(
    *,
    session_id: str,
    channel_id: str,
    windows: Sequence[QcAggregationResult],
    integrity_findings: Sequence[IntegrityFinding],
    policy: AggregationPolicy,
) -> QcAggregationResult:
    hierarchy = ScopeHierarchy(
        session_id=session_id,
        channel_id=channel_id,
        target_scope="CHANNEL",
    )
    for item in windows:
        if item.scope_hierarchy.target_scope != "WINDOW":
            raise ValueError("channel aggregation accepts WINDOW child results only")
        if item.scope_hierarchy.channel_id != channel_id:
            raise ValueError("window channel_id mismatch")
    for item in integrity_findings:
        if item.scope == "CHANNEL" and item.target_id != channel_id:
            raise ValueError("channel integrity target_id mismatch")
        if item.scope not in {"CHANNEL", "WINDOW"}:
            raise ValueError("channel aggregation cannot consume SESSION integrity")
    refs = _source_refs((), (), integrity_findings, windows)

    hard_blocks = [item for item in integrity_findings if item.blocking]
    if hard_blocks or any(item.critical_failure for item in windows):
        evaluated = [
            item for item in windows if item.evaluation_status == EvaluationStatus.EVALUATED
        ]
        bad_count = sum(item.signal_quality == SignalQuality.FAIL for item in evaluated)
        usable = sum(
            item.signal_quality in {SignalQuality.PASS, SignalQuality.WARNING}
            for item in evaluated
        )
        ratio = usable / len(evaluated) if evaluated else None
        return QcAggregationResult(
            schema_version=SCHEMA_VERSION,
            taxonomy_version="0.2",
            evaluation_status=EvaluationStatus.EVALUATED,
            scope_hierarchy=hierarchy,
            signal_quality=SignalQuality.FAIL,
            qc_supportability=Supportability.BLOCKED,
            metrics=AggregationMetrics(ratio, len(evaluated), usable, bad_count, 1, 1),
            evidence_reasons=_sorted_unique(
                [item.reason_code for item in hard_blocks]
                + [reason for item in windows for reason in item.evidence_reasons]
            ),
            disposition_reasons=("QUALITY_BLOCKED",),
            source_refs=refs,
            policy_profile_id=policy.profile_id,
            config_version=policy.version,
            critical_failure=True,
        )

    if not windows:
        return _unknown_result(
            hierarchy=hierarchy,
            policy=policy,
            reasons=("QC_NOT_EVALUATED",),
            source_refs=refs,
        )
    incomplete = [
        item for item in windows if item.evaluation_status != EvaluationStatus.EVALUATED
    ]
    evaluated = [
        item for item in windows if item.evaluation_status == EvaluationStatus.EVALUATED
    ]
    usable = sum(
        item.signal_quality in {SignalQuality.PASS, SignalQuality.WARNING}
        for item in evaluated
    )
    bad_count = sum(item.signal_quality == SignalQuality.FAIL for item in evaluated)
    ratio = usable / len(evaluated) if evaluated else None
    metrics = AggregationMetrics(ratio, len(evaluated), usable, bad_count, 0, 1)

    if incomplete and policy.require_complete_window_evidence:
        return _unknown_result(
            hierarchy=hierarchy,
            policy=policy,
            reasons=("INSUFFICIENT_QC_EVIDENCE",),
            source_refs=refs,
            metrics=metrics,
        )
    if not evaluated:
        return _unknown_result(
            hierarchy=hierarchy,
            policy=policy,
            reasons=("QC_NOT_EVALUATED",),
            source_refs=refs,
            metrics=metrics,
        )

    evidence_reasons = _sorted_unique(
        reason for item in windows for reason in item.evidence_reasons
    )
    if bad_count:
        threshold = policy.channel_min_usable_window_ratio
        if threshold is None:
            return _unknown_result(
                hierarchy=hierarchy,
                policy=policy,
                reasons=("AGGREGATION_THRESHOLD_NOT_VERIFIED",),
                source_refs=refs,
                metrics=metrics,
            )
        if ratio is not None and ratio < threshold:
            return QcAggregationResult(
                schema_version=SCHEMA_VERSION,
                taxonomy_version="0.2",
                evaluation_status=EvaluationStatus.EVALUATED,
                scope_hierarchy=hierarchy,
                signal_quality=SignalQuality.FAIL,
                qc_supportability=Supportability.BLOCKED,
                metrics=AggregationMetrics(
                    ratio, len(evaluated), usable, bad_count, 1, 1
                ),
                evidence_reasons=evidence_reasons,
                disposition_reasons=("QUALITY_BLOCKED",),
                source_refs=refs,
                policy_profile_id=policy.profile_id,
                config_version=policy.version,
            )

    has_warning = any(item.signal_quality == SignalQuality.WARNING for item in evaluated)
    if has_warning or bad_count:
        return QcAggregationResult(
            schema_version=SCHEMA_VERSION,
            taxonomy_version="0.2",
            evaluation_status=EvaluationStatus.EVALUATED,
            scope_hierarchy=hierarchy,
            signal_quality=SignalQuality.WARNING,
            qc_supportability=Supportability.REVIEW_REQUIRED,
            metrics=metrics,
            evidence_reasons=evidence_reasons,
            disposition_reasons=("CHANNEL_WARNING",),
            source_refs=refs,
            policy_profile_id=policy.profile_id,
            config_version=policy.version,
        )

    return QcAggregationResult(
        schema_version=SCHEMA_VERSION,
        taxonomy_version="0.2",
        evaluation_status=EvaluationStatus.EVALUATED,
        scope_hierarchy=hierarchy,
        signal_quality=SignalQuality.PASS,
        qc_supportability=Supportability.SUPPORTABLE,
        metrics=metrics,
        evidence_reasons=evidence_reasons,
        disposition_reasons=(),
        source_refs=refs,
        policy_profile_id=policy.profile_id,
        config_version=policy.version,
    )


def aggregate_session(
    *,
    session_id: str,
    channels: Sequence[QcAggregationResult],
    integrity_findings: Sequence[IntegrityFinding],
    policy: AggregationPolicy,
) -> QcAggregationResult:
    hierarchy = ScopeHierarchy(session_id=session_id, target_scope="SESSION")
    for item in channels:
        if item.scope_hierarchy.target_scope != "CHANNEL":
            raise ValueError("session aggregation accepts CHANNEL child results only")
        if item.scope_hierarchy.session_id != session_id:
            raise ValueError("channel session_id mismatch")
    for item in integrity_findings:
        if item.scope != "SESSION":
            raise ValueError("session aggregation accepts SESSION integrity only")
        if item.target_id != session_id:
            raise ValueError("session integrity target_id mismatch")
    refs = _source_refs((), (), integrity_findings, channels)

    hard_blocks = [item for item in integrity_findings if item.blocking]
    critical_channel = [item for item in channels if item.critical_failure]
    if hard_blocks or critical_channel:
        return _session_fail(
            session_id=session_id,
            channels=channels,
            evidence_reasons=_sorted_unique(
                [item.reason_code for item in hard_blocks]
                + [reason for item in critical_channel for reason in item.evidence_reasons]
            ),
            refs=refs,
            policy=policy,
            critical_failure=True,
        )

    if not channels:
        return _unknown_result(
            hierarchy=hierarchy,
            policy=policy,
            reasons=("QC_NOT_EVALUATED",),
            source_refs=refs,
        )
    if any(item.evaluation_status != EvaluationStatus.EVALUATED for item in channels):
        return _unknown_result(
            hierarchy=hierarchy,
            policy=policy,
            reasons=("INSUFFICIENT_QC_EVIDENCE",),
            source_refs=refs,
            metrics=_session_metrics(channels),
        )

    bad_channels = [item for item in channels if item.signal_quality == SignalQuality.FAIL]
    warning_channels = [
        item for item in channels if item.signal_quality == SignalQuality.WARNING
    ]
    if bad_channels:
        threshold = policy.session_max_allowed_bad_channels
        if threshold is None:
            return _unknown_result(
                hierarchy=hierarchy,
                policy=policy,
                reasons=("AGGREGATION_THRESHOLD_NOT_VERIFIED",),
                source_refs=refs,
                metrics=_session_metrics(channels),
            )
        if len(bad_channels) > threshold:
            return _session_fail(
                session_id=session_id,
                channels=channels,
                evidence_reasons=_sorted_unique(
                    reason for item in bad_channels for reason in item.evidence_reasons
                ),
                refs=refs,
                policy=policy,
                critical_failure=False,
            )

    if bad_channels or warning_channels:
        return QcAggregationResult(
            schema_version=SCHEMA_VERSION,
            taxonomy_version="0.2",
            evaluation_status=EvaluationStatus.EVALUATED,
            scope_hierarchy=hierarchy,
            signal_quality=SignalQuality.WARNING,
            qc_supportability=Supportability.REVIEW_REQUIRED,
            metrics=_session_metrics(channels),
            evidence_reasons=_sorted_unique(
                reason for item in channels for reason in item.evidence_reasons
            ),
            disposition_reasons=("CLINICIAN_REVIEW_REQUIRED",),
            source_refs=refs,
            policy_profile_id=policy.profile_id,
            config_version=policy.version,
        )

    return QcAggregationResult(
        schema_version=SCHEMA_VERSION,
        taxonomy_version="0.2",
        evaluation_status=EvaluationStatus.EVALUATED,
        scope_hierarchy=hierarchy,
        signal_quality=SignalQuality.PASS,
        qc_supportability=Supportability.SUPPORTABLE,
        metrics=_session_metrics(channels),
        evidence_reasons=_sorted_unique(
            reason for item in channels for reason in item.evidence_reasons
        ),
        disposition_reasons=(),
        source_refs=refs,
        policy_profile_id=policy.profile_id,
        config_version=policy.version,
    )


def _session_metrics(channels: Sequence[QcAggregationResult]) -> AggregationMetrics:
    total_evaluated_windows = sum(
        item.metrics.total_evaluated_windows for item in channels
    )
    usable = sum(item.metrics.usable_windows_count for item in channels)
    bad_windows = sum(item.metrics.bad_window_count for item in channels)
    ratio = usable / total_evaluated_windows if total_evaluated_windows else None
    bad_channels = sum(item.signal_quality == SignalQuality.FAIL for item in channels)
    return AggregationMetrics(
        usable_window_ratio=ratio,
        total_evaluated_windows=total_evaluated_windows,
        usable_windows_count=usable,
        bad_window_count=bad_windows,
        bad_channel_count=bad_channels,
        total_channels_count=len(channels),
    )


def _session_fail(
    *,
    session_id: str,
    channels: Sequence[QcAggregationResult],
    evidence_reasons: tuple[str, ...],
    refs: tuple[str, ...],
    policy: AggregationPolicy,
    critical_failure: bool,
) -> QcAggregationResult:
    return QcAggregationResult(
        schema_version=SCHEMA_VERSION,
        taxonomy_version="0.2",
        evaluation_status=EvaluationStatus.EVALUATED,
        scope_hierarchy=ScopeHierarchy(
            session_id=session_id,
            target_scope="SESSION",
        ),
        signal_quality=SignalQuality.FAIL,
        qc_supportability=Supportability.BLOCKED,
        metrics=_session_metrics(channels),
        evidence_reasons=evidence_reasons,
        disposition_reasons=("QUALITY_BLOCKED",),
        source_refs=refs,
        policy_profile_id=policy.profile_id,
        config_version=policy.version,
        critical_failure=critical_failure,
    )


def validate_result_semantics(result: QcAggregationResult) -> None:
    if result.evaluation_status == EvaluationStatus.EVALUATED:
        if result.signal_quality is None:
            raise SemanticContradictionError(
                "EVALUATED aggregation result requires signal_quality"
            )
    elif result.signal_quality is not None:
        raise SemanticContradictionError(
            "unevaluated aggregation result must use signal_quality=null"
        )
    if "QUALITY_BLOCKED" in result.disposition_reasons:
        if result.signal_quality != SignalQuality.FAIL:
            raise SemanticContradictionError(
                "QUALITY_BLOCKED requires signal_quality=FAIL"
            )
        if result.qc_supportability != Supportability.BLOCKED:
            raise SemanticContradictionError(
                "QUALITY_BLOCKED requires qc_supportability=BLOCKED"
            )
    if result.signal_quality == SignalQuality.PASS:
        if result.qc_supportability == Supportability.BLOCKED:
            raise SemanticContradictionError(
                "PASS cannot be combined with BLOCKED supportability"
            )
    metrics = result.metrics
    if metrics.total_evaluated_windows < 0:
        raise SemanticContradictionError("negative evaluated-window count")
    if metrics.usable_windows_count > metrics.total_evaluated_windows:
        raise SemanticContradictionError("usable windows exceed evaluated windows")
    if metrics.bad_window_count > metrics.total_evaluated_windows:
        raise SemanticContradictionError("bad windows exceed evaluated windows")
    if (
        metrics.usable_windows_count + metrics.bad_window_count
        > metrics.total_evaluated_windows
    ):
        raise SemanticContradictionError(
            "usable plus bad windows exceed evaluated windows"
        )
    if metrics.bad_channel_count > metrics.total_channels_count:
        raise SemanticContradictionError("bad channels exceed total channels")
    if metrics.usable_window_ratio is not None:
        if not 0.0 <= metrics.usable_window_ratio <= 1.0:
            raise SemanticContradictionError("usable-window ratio outside [0,1]")
        if metrics.total_evaluated_windows == 0:
            raise SemanticContradictionError(
                "non-null ratio requires evaluated windows"
            )
        expected_ratio = (
            metrics.usable_windows_count / metrics.total_evaluated_windows
        )
        if abs(metrics.usable_window_ratio - expected_ratio) > 1e-12:
            raise SemanticContradictionError(
                "usable-window ratio contradicts window counts"
            )
    elif metrics.total_evaluated_windows > 0:
        # Null ratio is allowed for some higher-level policy gaps only when there are
        # no usable/bad counts that claim a complete evaluated partition.
        if metrics.usable_windows_count + metrics.bad_window_count:
            raise SemanticContradictionError(
                "evaluated window counts require a non-null usable ratio"
            )


def stable_result_digest(result: QcAggregationResult) -> str:
    payload = json.dumps(
        result.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
