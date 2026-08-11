"""DAY24 clipping/saturation weak-label detector.

Verified device limits and heuristic plateau evidence are intentionally separated.
When ADC saturation semantics are not verified, heuristic evidence cannot be promoted
to device-truth clipping; candidate output remains UNKNOWN/review-oriented.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal
import numpy as np
from semg_core.qc_windowing import WindowIdentity, WindowMask


class ClippingDetectorError(ValueError):
    pass


AdcStatus = Literal['VERIFIED', 'NOT_VERIFIED']


@dataclass(frozen=True)
class ClippingDetectorConfig:
    config_version: str = '0.1.0'
    rule_version: str = '0.1.0'
    registry_version: str = '0.1'
    min_samples: int = 16
    repeated_extrema_fraction: float = 0.1
    plateau_run_min_samples: int = 4
    extrema_tolerance: float = 1e-12
    adc_semantics_status: AdcStatus = 'NOT_VERIFIED'
    adc_lower_limit: float | None = None
    adc_upper_limit: float | None = None
    mask_policy_version: str = 'day24-mask-v0.1'

    def __post_init__(self) -> None:
        if self.min_samples < 4:
            raise ClippingDetectorError('min_samples must be >= 4')
        if not 0 < self.repeated_extrema_fraction <= 1:
            raise ClippingDetectorError('repeated_extrema_fraction must be in (0,1]')
        if self.plateau_run_min_samples < 2:
            raise ClippingDetectorError('plateau_run_min_samples must be >= 2')
        if self.extrema_tolerance < 0:
            raise ClippingDetectorError('extrema_tolerance cannot be negative')
        if self.adc_semantics_status == 'VERIFIED':
            if self.adc_lower_limit is None or self.adc_upper_limit is None:
                raise ClippingDetectorError('verified ADC semantics require both limits')
            if self.adc_lower_limit >= self.adc_upper_limit:
                raise ClippingDetectorError('ADC lower limit must be < upper limit')
        elif self.adc_lower_limit is not None or self.adc_upper_limit is not None:
            raise ClippingDetectorError('unverified ADC semantics cannot carry trusted limits')


def _lf(
    window: WindowIdentity,
    config: ClippingDetectorConfig,
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
        'lf_id': 'LF_CLIPPING_SATURATION',
        'lf_version': config.rule_version,
        'reason_code': reason,
        'label_candidate': candidate,
        'evidence_type': list(evidence_types),
        'severity': severity,
        'qc_supportability': supportability,
        'evidence_strength': strength,
        'evidence_refs': [window.window_id],
        'ground_truth_claim': False,
        'expert_label_claim': False,
        'provenance': {
            'registry_version': config.registry_version,
            'rule_version': config.rule_version,
            'config_version': config.config_version,
        },
    }


def _max_run(values: np.ndarray, target: float, tol: float) -> int:
    mask = np.abs(values - target) <= tol
    if not np.any(mask):
        return 0
    padded = np.concatenate(([False], mask, [False]))
    diffs = np.diff(padded.astype(int))
    starts = np.flatnonzero(diffs == 1)
    ends = np.flatnonzero(diffs == -1)
    if len(starts) == 0:
        return 0
    return int(np.max(ends - starts))


def evaluate_clipping(
    signal_array: np.ndarray,
    window: WindowIdentity,
    config: ClippingDetectorConfig = ClippingDetectorConfig(),
) -> dict[str, Any]:
    values = np.asarray(signal_array)
    if values.ndim != 1:
        raise ClippingDetectorError('clipping detector expects 1-D channel samples')
    if window.end_sample_exclusive > values.shape[0]:
        raise ClippingDetectorError('WindowIdentity exceeds raw channel length')
    core = values[window.start_sample:window.end_sample_exclusive]
    if core.size < config.min_samples or not np.all(np.isfinite(core)):
        return _lf(
            window,
            config,
            reason='INSUFFICIENT_QC_EVIDENCE',
            candidate='ABSTAIN',
            severity='UNKNOWN',
            supportability='NOT_EVALUATED',
            strength='UNKNOWN',
            evidence_types=('RAW_STRUCTURAL',),
        )
    x = core.astype(float, copy=False)
    observed_min, observed_max = (float(np.min(x)), float(np.max(x)))
    max_count = int(np.count_nonzero(np.abs(x - observed_max) <= config.extrema_tolerance))
    min_count = int(np.count_nonzero(np.abs(x - observed_min) <= config.extrema_tolerance))
    extrema_fraction = max(max_count, min_count) / float(x.size)
    plateau_run = max(
        _max_run(x, observed_max, config.extrema_tolerance),
        _max_run(x, observed_min, config.extrema_tolerance),
    )
    heuristic_suspected = (
        extrema_fraction >= config.repeated_extrema_fraction
        and plateau_run >= config.plateau_run_min_samples
    )
    if config.adc_semantics_status == 'VERIFIED':
        assert config.adc_lower_limit is not None and config.adc_upper_limit is not None
        at_limit = bool(
            np.any(x <= config.adc_lower_limit + config.extrema_tolerance)
            or np.any(x >= config.adc_upper_limit - config.extrema_tolerance)
        )
        if at_limit and heuristic_suspected:
            return _lf(
                window,
                config,
                reason='CLIPPING_SATURATION_SUSPECTED',
                candidate='FAIL_CANDIDATE',
                severity='HIGH',
                supportability='BLOCKED',
                strength='HIGH',
                evidence_types=('AMPLITUDE', 'DEVICE_METADATA'),
            )
        return _lf(
            window,
            config,
            reason='CLIPPING_NOT_OBSERVED',
            candidate='PASS_CANDIDATE',
            severity='INFO',
            supportability='SUPPORTABLE',
            strength='HIGH',
            evidence_types=('AMPLITUDE', 'DEVICE_METADATA'),
        )
    if heuristic_suspected:
        return _lf(
            window,
            config,
            reason='CLIPPING_SATURATION_SUSPECTED',
            candidate='UNKNOWN',
            severity='MODERATE',
            supportability='REVIEW_REQUIRED',
            strength='LOW',
            evidence_types=('AMPLITUDE',),
        )
    return _lf(
        window,
        config,
        reason='CLIPPING_NOT_OBSERVED_BY_HEURISTIC',
        candidate='PASS_CANDIDATE',
        severity='INFO',
        supportability='SUPPORTABLE',
        strength='MODERATE',
        evidence_types=('AMPLITUDE',),
    )


def mask_from_candidate(
    output: dict[str, Any],
    window: WindowIdentity,
    config: ClippingDetectorConfig,
) -> WindowMask:
    masked = output['label_candidate'] == 'FAIL_CANDIDATE'
    return WindowMask(
        window_id=window.window_id,
        masked=masked,
        reason_codes=(str(output['reason_code']),) if masked else (),
        mask_policy_version=config.mask_policy_version,
        raw_deleted=False,
    )
