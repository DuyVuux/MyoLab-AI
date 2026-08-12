"""DAY41 analytically verified research band-pass implementation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from typing import Any, Mapping

import numpy as np
from scipy import signal


class BandpassError(ValueError):
    """Base class for band-pass processing failures."""


class BandpassConfigurationError(BandpassError):
    """Raised when the declared filter configuration is invalid."""


class BandpassRuntimeError(BandpassError):
    """Raised when runtime signal context cannot support the filter."""


@dataclass(frozen=True)
class BandpassSpec:
    low_cut_hz: float
    high_cut_hz: float
    filter_order: int = 4
    method: str = "butterworth_sos"
    phase_mode: str = "ZERO_PHASE"
    version: str = "day41-bandpass.v0.1.0"

    def validate(self, fs_hz: float) -> None:
        if fs_hz <= 0:
            raise BandpassRuntimeError("SAMPLING_RATE_REQUIRED_POSITIVE")
        if self.method != "butterworth_sos":
            raise BandpassConfigurationError("UNSUPPORTED_BANDPASS_METHOD")
        if not 1 <= self.filter_order <= 12:
            raise BandpassConfigurationError("FILTER_ORDER_OUT_OF_RANGE")
        if not 0 < self.low_cut_hz < self.high_cut_hz:
            raise BandpassConfigurationError("INVALID_BANDPASS_CUTOFF_ORDER")
        if self.high_cut_hz >= 0.5 * fs_hz:
            raise BandpassRuntimeError("BANDPASS_HIGH_CUT_VIOLATES_NYQUIST")
        if self.phase_mode not in {"ZERO_PHASE", "CAUSAL"}:
            raise BandpassConfigurationError("UNSUPPORTED_PHASE_MODE")


@dataclass(frozen=True)
class BandpassResult:
    values: np.ndarray
    mask: np.ndarray
    metadata: Mapping[str, Any]


def _hash_array(values: np.ndarray) -> str:
    array = np.ascontiguousarray(values)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(str(array.shape).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def design_sos(spec: BandpassSpec, fs_hz: float) -> np.ndarray:
    spec.validate(fs_hz)
    return signal.butter(
        spec.filter_order,
        [spec.low_cut_hz, spec.high_cut_hz],
        btype="bandpass",
        fs=fs_hz,
        output="sos",
    )


def frequency_response(
    spec: BandpassSpec,
    fs_hz: float,
    worN: int = 32768,
) -> tuple[np.ndarray, np.ndarray]:
    sos = design_sos(spec, fs_hz)
    frequencies, response = signal.sosfreqz(sos, worN=worN, fs=fs_hz)
    return frequencies, np.abs(response)



def causal_group_delay_samples(
    spec: BandpassSpec,
    fs_hz: float,
    frequency_hz: float,
) -> float:
    """Return causal IIR group delay at one physical frequency in samples."""

    sos = design_sos(spec, fs_hz)
    numerator, denominator = signal.sos2tf(sos)
    angular_frequency = 2 * np.pi * frequency_hz / fs_hz
    _, delay = signal.group_delay(
        (numerator, denominator),
        w=[angular_frequency],
    )
    return float(delay[0])

def _valid_segments(valid: np.ndarray):
    indexes = np.flatnonzero(valid)
    if indexes.size == 0:
        return
    start = indexes[0]
    previous = indexes[0]
    for index in indexes[1:]:
        if index != previous + 1:
            yield start, previous + 1
            start = index
        previous = index
    yield start, previous + 1


def apply_bandpass(
    values: np.ndarray,
    fs_hz: float,
    spec: BandpassSpec,
    *,
    mask: np.ndarray | None = None,
    source_window_id: str,
    profile_id: str,
    profile_fingerprint: str,
) -> BandpassResult:
    signal_values = np.asarray(values, dtype=float)
    if signal_values.ndim != 1:
        raise BandpassRuntimeError("BANDPASS_REQUIRES_1D_SIGNAL")

    raw_hash = _hash_array(signal_values)
    if mask is None:
        processing_mask = np.zeros(signal_values.shape, dtype=bool)
    else:
        processing_mask = np.asarray(mask, dtype=bool).copy()
    if processing_mask.shape != signal_values.shape:
        raise BandpassRuntimeError("MASK_SHAPE_MISMATCH")

    sos = design_sos(spec, fs_hz)
    output = np.full(signal_values.shape, np.nan, dtype=float)
    valid = (~processing_mask) & np.isfinite(signal_values)
    short_segments = 0

    for start, end in _valid_segments(valid):
        segment = signal_values[start:end]
        minimum_samples = max(32, 6 * spec.filter_order + 3)
        if segment.size < minimum_samples:
            short_segments += 1
            continue
        if spec.phase_mode == "ZERO_PHASE":
            output[start:end] = signal.sosfiltfilt(sos, segment)
        else:
            output[start:end] = signal.sosfilt(sos, segment)

    if _hash_array(signal_values) != raw_hash:
        raise RuntimeError("RAW_MUTATION_DETECTED")

    timing_effect = (
        "ZERO_PHASE_ACAUSAL"
        if spec.phase_mode == "ZERO_PHASE"
        else "CAUSAL_GROUP_DELAY"
    )
    metadata = {
        "processor": "DAY41_BANDPASS",
        "processor_version": spec.version,
        "source_window_id": source_window_id,
        "profile_id": profile_id,
        "profile_fingerprint": profile_fingerprint,
        "native_fs_hz": float(fs_hz),
        "processed_fs_hz": float(fs_hz),
        "phase_mode": spec.phase_mode,
        "filter_config": asdict(spec),
        "input_hash": raw_hash,
        "output_hash": _hash_array(output),
        "mask_preserved": True,
        "short_unprocessed_segments": short_segments,
        "effect": {
            "sampling_grid": "UNCHANGED",
            "spectral_content": "BAND_LIMITED",
            "timing": timing_effect,
            "mask": "PRESERVED",
        },
    }
    return BandpassResult(output, processing_mask, metadata)
