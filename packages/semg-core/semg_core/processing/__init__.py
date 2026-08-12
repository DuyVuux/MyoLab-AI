"""Versioned sEMG processing contracts and later DSP implementations."""

from semg_core.processing.bandpass import (
    BandpassConfigurationError,
    BandpassError,
    BandpassResult,
    BandpassRuntimeError,
    BandpassSpec,
    apply_bandpass,
    causal_group_delay_samples,
    design_sos,
    frequency_response,
)
from semg_core.processing.envelope import (
    EnvelopeError,
    EnvelopeResult,
    build_envelope,
    rectify,
    smooth,
)
from semg_core.processing.masking import (
    MaskApplication,
    MaskingError,
    apply_metadata_mask,
    freeze_window_identity,
    hash_array,
    metric_mask_eligibility,
)
from semg_core.processing.notch import (
    NotchConfigurationError,
    NotchError,
    NotchResult,
    NotchSpec,
    apply_notch,
)

__all__ = [
    "BandpassConfigurationError",
    "BandpassError",
    "BandpassResult",
    "BandpassRuntimeError",
    "BandpassSpec",
    "apply_bandpass",
    "causal_group_delay_samples",
    "design_sos",
    "frequency_response",
    "NotchConfigurationError",
    "NotchError",
    "NotchResult",
    "NotchSpec",
    "apply_notch",
    "EnvelopeError",
    "EnvelopeResult",
    "build_envelope",
    "rectify",
    "smooth",
    "MaskApplication",
    "MaskingError",
    "apply_metadata_mask",
    "freeze_window_identity",
    "hash_array",
    "metric_mask_eligibility",
]



