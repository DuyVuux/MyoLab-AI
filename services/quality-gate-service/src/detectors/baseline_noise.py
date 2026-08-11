"""DAY25 protocol-aware baseline/noise indicator and weak-label candidate.

A low-amplitude window is never inferred to be rest/reference. Reference eligibility must
come from protocol evidence supplied by the caller. Robust descriptors can be computed
when reference evidence is eligible; label thresholds remain protocol/version specific.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal
import numpy as np
from semg_core.qc_windowing import WindowIdentity

class BaselineNoiseError(ValueError):
    pass

ReferenceStatus = Literal['VERIFIED_ELIGIBLE', 'NOT_VERIFIED', 'INELIGIBLE']
ThresholdStatus = Literal['APPROVED', 'SYNTHETIC_ENGINEERING_ONLY', 'NOT_VERIFIED']

@dataclass(frozen=True)
class ReferenceRegionEvidence:
    protocol_ref: str
    reference_role: str
    eligibility_status: ReferenceStatus
    marker_evidence_ref: str | None = None

    def __post_init__(self):
        if not self.protocol_ref.strip():
            raise BaselineNoiseError('protocol_ref required')
        if not self.reference_role.strip():
            raise BaselineNoiseError('reference_role required')
        if self.eligibility_status == 'VERIFIED_ELIGIBLE' and (not self.marker_evidence_ref):
            raise BaselineNoiseError('verified reference requires marker evidence ref')

@dataclass(frozen=True)
class ProtocolNoiseProfile:
    protocol_ref: str
    config_version: str
    rule_version: str = '0.1.0'
    registry_version: str = '0.1'
    allowed_reference_roles: tuple[str, ...] = ('REST', 'BASELINE_REFERENCE')
    threshold_status: ThresholdStatus = 'NOT_VERIFIED'
    rms_warning_threshold: float | None = None
    mad_warning_threshold: float | None = None
    min_samples: int = 16

    def __post_init__(self):
        if not self.protocol_ref.strip():
            raise BaselineNoiseError('protocol_ref required')
        if self.min_samples < 4:
            raise BaselineNoiseError('min_samples must be >= 4')
        if self.threshold_status in {'APPROVED', 'SYNTHETIC_ENGINEERING_ONLY'}:
            if self.rms_warning_threshold is None or self.mad_warning_threshold is None:
                raise BaselineNoiseError('verified/engineering threshold profile requires thresholds')
        if self.threshold_status == 'NOT_VERIFIED' and (
            self.rms_warning_threshold is not None or self.mad_warning_threshold is not None
        ):
            raise BaselineNoiseError('NOT_VERIFIED profile cannot carry operative thresholds')
        for x in (self.rms_warning_threshold, self.mad_warning_threshold):
            if x is not None and x < 0:
                raise BaselineNoiseError('noise thresholds cannot be negative')

@dataclass(frozen=True)
class BaselineNoiseDescriptors:
    sample_count: int
    median: float
    mad: float
    rms: float
    p05: float
    p95: float

def compute_descriptors(
    signal_array: np.ndarray, window: WindowIdentity, min_samples: int = 16
) -> BaselineNoiseDescriptors:
    values = np.asarray(signal_array)
    if values.ndim != 1:
        raise BaselineNoiseError('baseline/noise expects 1-D samples')
    if window.end_sample_exclusive > values.shape[0]:
        raise BaselineNoiseError('WindowIdentity exceeds raw channel length')
    core = values[window.start_sample:window.end_sample_exclusive]
    if core.size < min_samples or not np.all(np.isfinite(core)):
        raise BaselineNoiseError('INSUFFICIENT_REFERENCE_SAMPLES')
    x = core.astype(float, copy=False)
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med)))
    rms = float(np.sqrt(np.mean(np.square(x))))
    p05, p95 = (float(v) for v in np.percentile(x, [5, 95]))
    return BaselineNoiseDescriptors(core.size, med, mad, rms, p05, p95)

def _lf(
    window: WindowIdentity,
    profile: ProtocolNoiseProfile,
    *,
    reason: str,
    candidate: str,
    severity: str,
    supportability: str,
    strength: str,
    evidence_types: tuple[str, ...],
) -> dict[str, Any]:
    return {
        'schema_version': '0.1',
        'lf_id': 'LF_BASELINE_NOISE',
        'lf_version': profile.rule_version,
        'reason_code': reason,
        'label_candidate': candidate,
        'evidence_type': list(evidence_types),
        'severity': severity,
        'qc_supportability': supportability,
        'evidence_strength': strength,
        'evidence_refs': [window.window_id, profile.protocol_ref],
        'ground_truth_claim': False,
        'expert_label_claim': False,
        'provenance': {
            'registry_version': profile.registry_version,
            'rule_version': profile.rule_version,
            'config_version': profile.config_version,
        },
    }

def evaluate_baseline_noise(
    signal_array: np.ndarray,
    window: WindowIdentity,
    reference: ReferenceRegionEvidence,
    profile: ProtocolNoiseProfile,
) -> tuple[BaselineNoiseDescriptors | None, dict[str, Any]]:
    if reference.protocol_ref != profile.protocol_ref:
        raise BaselineNoiseError('reference protocol does not match noise profile')
    if (
        reference.reference_role not in profile.allowed_reference_roles
        or reference.eligibility_status != 'VERIFIED_ELIGIBLE'
    ):
        return (
            None,
            _lf(
                window,
                profile,
                reason='INSUFFICIENT_REFERENCE',
                candidate='ABSTAIN',
                severity='UNKNOWN',
                supportability='NOT_EVALUATED',
                strength='UNKNOWN',
                evidence_types=('PROTOCOL_CONTEXT',),
            ),
        )
    try:
        desc = compute_descriptors(signal_array, window, profile.min_samples)
    except BaselineNoiseError as exc:
        if str(exc) == 'INSUFFICIENT_REFERENCE_SAMPLES':
            return (
                None,
                _lf(
                    window,
                    profile,
                    reason='INSUFFICIENT_REFERENCE',
                    candidate='ABSTAIN',
                    severity='UNKNOWN',
                    supportability='NOT_EVALUATED',
                    strength='UNKNOWN',
                    evidence_types=('PROTOCOL_CONTEXT', 'RAW_STRUCTURAL'),
                ),
            )
        raise
    if profile.threshold_status == 'NOT_VERIFIED':
        return (
            desc,
            _lf(
                window,
                profile,
                reason='BASELINE_NOISE_THRESHOLD_NOT_VERIFIED',
                candidate='UNKNOWN',
                severity='UNKNOWN',
                supportability='REVIEW_REQUIRED',
                strength='UNKNOWN',
                evidence_types=('AMPLITUDE', 'PROTOCOL_CONTEXT'),
            ),
        )
    assert profile.rms_warning_threshold is not None and profile.mad_warning_threshold is not None
    elevated = (
        desc.rms > profile.rms_warning_threshold or desc.mad > profile.mad_warning_threshold
    )
    if elevated:
        return (
            desc,
            _lf(
                window,
                profile,
                reason='BASELINE_NOISE_ELEVATED',
                candidate='WARNING_CANDIDATE',
                severity='MODERATE',
                supportability='REVIEW_REQUIRED',
                strength='MODERATE',
                evidence_types=('AMPLITUDE', 'PROTOCOL_CONTEXT'),
            ),
        )
    return (
        desc,
        _lf(
            window,
            profile,
            reason='BASELINE_NOISE_WITHIN_REFERENCE',
            candidate='PASS_CANDIDATE',
            severity='INFO',
            supportability='SUPPORTABLE',
            strength='MODERATE',
            evidence_types=('AMPLITUDE', 'PROTOCOL_CONTEXT'),
        ),
    )
