"""DAY23 dropout, missing-sample and flatline weak-label detectors.

The detector consumes DAY22 WindowIdentity coordinates and emits DAY21-compatible
LabelingFunctionOutput dictionaries. It never edits raw samples and never claims
ground truth. Synthetic fixture truth is maintained separately by the fixture factory.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Any, Literal
import numpy as np
from pydantic import BaseModel, Field
from semg_core.qc_windowing import WindowIdentity, WindowMask

class DropoutDetectorError(ValueError):
    """Typed DAY23 detector/configuration failure."""

class ProvenanceModel(BaseModel):
    registry_version: Literal['0.1'] = '0.1'
    rule_version: str = Field(..., min_length=1)
    config_version: str = Field(..., min_length=1)

class LabelingFunctionOutputModel(BaseModel):
    schema_version: Literal['0.1'] = '0.1'
    lf_id: str = Field(..., pattern=r'^LF_[A-Z0-9_]+$')
    lf_version: str = Field(..., min_length=1)
    reason_code: str = Field(..., pattern=r'^[A-Z][A-Z0-9_]+$')
    label_candidate: Literal['PASS_CANDIDATE', 'WARNING_CANDIDATE', 'FAIL_CANDIDATE', 'ABSTAIN', 'UNKNOWN']
    evidence_type: list[str] = Field(..., min_length=1)
    severity: Literal['INFO', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL', 'UNKNOWN']
    qc_supportability: Literal['SUPPORTABLE', 'REVIEW_REQUIRED', 'BLOCKED', 'UNKNOWN', 'NOT_EVALUATED']
    evidence_strength: Literal['LOW', 'MODERATE', 'HIGH', 'UNKNOWN', 'NOT_APPLICABLE']
    evidence_refs: list[str] = Field(..., min_length=1)
    ground_truth_claim: Literal[False] = False
    expert_label_claim: Literal[False] = False
    provenance: ProvenanceModel

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

@dataclass(frozen=True)
class DropoutDetectorConfig:
    config_version: str = '0.1.0'
    rule_version: str = '0.1.0'
    registry_version: str = '0.1'
    min_samples: int = 8
    missing_warning_fraction: float = 0.01
    missing_fail_fraction: float = 0.2
    zero_run_warning_fraction: float = 0.25
    zero_run_fail_fraction: float = 0.75
    flatline_peak_to_peak_epsilon: float = 1e-12
    mask_policy_version: str = 'day23-mask-v0.1'

    def __post_init__(self) -> None:
        if self.min_samples < 2:
            raise DropoutDetectorError('min_samples must be >= 2')
        for name, value in (('missing_warning_fraction', self.missing_warning_fraction), ('missing_fail_fraction', self.missing_fail_fraction), ('zero_run_warning_fraction', self.zero_run_warning_fraction), ('zero_run_fail_fraction', self.zero_run_fail_fraction)):
            if not 0 <= value <= 1:
                raise DropoutDetectorError(f'{name} must be within [0,1]')
        if self.missing_warning_fraction > self.missing_fail_fraction:
            raise DropoutDetectorError('missing warning threshold cannot exceed fail')
        if self.zero_run_warning_fraction > self.zero_run_fail_fraction:
            raise DropoutDetectorError('zero-run warning threshold cannot exceed fail')
        if self.flatline_peak_to_peak_epsilon < 0:
            raise DropoutDetectorError('flatline epsilon cannot be negative')

def _lf_output(*, lf_id: str, reason_code: str, label_candidate: str, severity: str, supportability: str, evidence_strength: str, window: WindowIdentity, config: DropoutDetectorConfig, evidence_types: tuple[str, ...]) -> dict[str, Any]:
    model = LabelingFunctionOutputModel(
        schema_version='0.1',
        lf_id=lf_id,
        lf_version=config.rule_version,
        reason_code=reason_code,
        label_candidate=label_candidate,
        evidence_type=list(evidence_types),
        severity=severity,
        qc_supportability=supportability,
        evidence_strength=evidence_strength,
        evidence_refs=[window.window_id],
        ground_truth_claim=False,
        expert_label_claim=False,
        provenance=ProvenanceModel(
            registry_version=config.registry_version,
            rule_version=config.rule_version,
            config_version=config.config_version,
        ),
    )
    return model.to_dict()

def _longest_zero_run(values: np.ndarray) -> int:
    best = current = 0
    for value in values:
        if value == 0.0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best

def evaluate_dropout_missing(signal_array: np.ndarray, window: WindowIdentity, config: DropoutDetectorConfig=DropoutDetectorConfig()) -> dict[str, Any]:
    """Evaluate missing/non-finite and explicit zero-run dropout evidence."""
    values = np.asarray(signal_array)
    if values.ndim != 1:
        raise DropoutDetectorError('DAY23 detector expects a 1-D channel array')
    if window.end_sample_exclusive > values.shape[0]:
        raise DropoutDetectorError('WindowIdentity exceeds raw channel length')
    core = values[window.start_sample:window.end_sample_exclusive]
    if core.size < config.min_samples:
        return _lf_output(lf_id='LF_MISSING_DROPOUT', reason_code='INSUFFICIENT_QC_EVIDENCE', label_candidate='ABSTAIN', severity='UNKNOWN', supportability='NOT_EVALUATED', evidence_strength='UNKNOWN', window=window, config=config, evidence_types=('RAW_STRUCTURAL',))
    finite = np.isfinite(core)
    missing_fraction = 1.0 - float(np.count_nonzero(finite)) / float(core.size)
    if missing_fraction >= config.missing_fail_fraction:
        return _lf_output(lf_id='LF_MISSING_DROPOUT', reason_code='MISSING_DROPOUT', label_candidate='FAIL_CANDIDATE', severity='HIGH', supportability='BLOCKED', evidence_strength='HIGH', window=window, config=config, evidence_types=('RAW_STRUCTURAL', 'TEMPORAL'))
    if missing_fraction >= config.missing_warning_fraction:
        return _lf_output(lf_id='LF_MISSING_DROPOUT', reason_code='MISSING_DROPOUT', label_candidate='WARNING_CANDIDATE', severity='MODERATE', supportability='REVIEW_REQUIRED', evidence_strength='HIGH', window=window, config=config, evidence_types=('RAW_STRUCTURAL', 'TEMPORAL'))
    finite_values = core[finite].astype(float, copy=False)
    zero_fraction = _longest_zero_run(finite_values) / float(core.size)
    if zero_fraction >= config.zero_run_fail_fraction:
        return _lf_output(lf_id='LF_MISSING_DROPOUT', reason_code='MISSING_DROPOUT', label_candidate='FAIL_CANDIDATE', severity='HIGH', supportability='BLOCKED', evidence_strength='MODERATE', window=window, config=config, evidence_types=('TEMPORAL', 'AMPLITUDE'))
    if zero_fraction >= config.zero_run_warning_fraction:
        return _lf_output(lf_id='LF_MISSING_DROPOUT', reason_code='MISSING_DROPOUT', label_candidate='WARNING_CANDIDATE', severity='MODERATE', supportability='REVIEW_REQUIRED', evidence_strength='MODERATE', window=window, config=config, evidence_types=('TEMPORAL', 'AMPLITUDE'))
    return _lf_output(lf_id='LF_MISSING_DROPOUT', reason_code='DROPOUT_NOT_DETECTED', label_candidate='PASS_CANDIDATE', severity='INFO', supportability='SUPPORTABLE', evidence_strength='MODERATE', window=window, config=config, evidence_types=('RAW_STRUCTURAL', 'TEMPORAL'))

def evaluate_flatline(signal_array: np.ndarray, window: WindowIdentity, config: DropoutDetectorConfig=DropoutDetectorConfig()) -> dict[str, Any]:
    """Evaluate constant/near-constant core samples without modifying raw evidence."""
    values = np.asarray(signal_array)
    if values.ndim != 1:
        raise DropoutDetectorError('DAY23 flatline detector expects 1-D input')
    if window.end_sample_exclusive > values.shape[0]:
        raise DropoutDetectorError('WindowIdentity exceeds raw channel length')
    core = values[window.start_sample:window.end_sample_exclusive]
    if core.size < config.min_samples or not np.all(np.isfinite(core)):
        return _lf_output(lf_id='LF_FLATLINE', reason_code='INSUFFICIENT_QC_EVIDENCE', label_candidate='ABSTAIN', severity='UNKNOWN', supportability='NOT_EVALUATED', evidence_strength='UNKNOWN', window=window, config=config, evidence_types=('RAW_STRUCTURAL',))
    peak_to_peak = float(np.ptp(core.astype(float, copy=False)))
    if math.isfinite(peak_to_peak) and peak_to_peak <= config.flatline_peak_to_peak_epsilon:
        return _lf_output(lf_id='LF_FLATLINE', reason_code='FLATLINE_DETECTED', label_candidate='FAIL_CANDIDATE', severity='HIGH', supportability='BLOCKED', evidence_strength='HIGH', window=window, config=config, evidence_types=('AMPLITUDE', 'TEMPORAL'))
    return _lf_output(lf_id='LF_FLATLINE', reason_code='FLATLINE_NOT_DETECTED', label_candidate='PASS_CANDIDATE', severity='INFO', supportability='SUPPORTABLE', evidence_strength='MODERATE', window=window, config=config, evidence_types=('AMPLITUDE', 'TEMPORAL'))

def mask_from_candidate(output: dict[str, Any], window: WindowIdentity, config: DropoutDetectorConfig) -> WindowMask:
    """Create mask metadata only for FAIL_CANDIDATE; never delete raw samples."""
    masked = output['label_candidate'] == 'FAIL_CANDIDATE'
    reasons = (str(output['reason_code']),) if masked else ()
    return WindowMask(window_id=window.window_id, masked=masked, reason_codes=reasons, mask_policy_version=config.mask_policy_version, raw_deleted=False)
