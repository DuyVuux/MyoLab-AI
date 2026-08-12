"""DAY43 rectification and deterministic smoothing primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
from scipy import signal

from .masking import apply_metadata_mask, hash_array


class EnvelopeError(ValueError):
    """Raised when envelope configuration/runtime context is invalid."""


@dataclass(frozen=True)
class EnvelopeResult:
    values: np.ndarray
    mask: np.ndarray
    window_identity: Mapping[str, Any]
    metadata: Mapping[str, Any]


def rectify(values: np.ndarray, method: str = "FULL_WAVE") -> np.ndarray:
    signal_values = np.asarray(values, dtype=float)
    if method == "FULL_WAVE":
        return np.abs(signal_values)
    if method == "HALF_WAVE":
        return np.maximum(signal_values, 0.0)
    if method == "NONE":
        return signal_values.copy()
    raise EnvelopeError("UNSUPPORTED_RECTIFICATION_METHOD")


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


def smooth(
    values: np.ndarray,
    fs_hz: float,
    *,
    method: str = "MOVING_AVERAGE",
    window_ms: float | None = None,
    cutoff_hz: float | None = None,
    filter_order: int = 2,
    mask: np.ndarray | None = None,
) -> np.ndarray:
    signal_values = np.asarray(values, dtype=float)
    if mask is None:
        processing_mask = np.zeros_like(signal_values, dtype=bool)
    else:
        processing_mask = np.asarray(mask, dtype=bool)
    if processing_mask.shape != signal_values.shape:
        raise EnvelopeError("MASK_SHAPE_MISMATCH")

    output = np.full_like(signal_values, np.nan, dtype=float)
    valid = (~processing_mask) & np.isfinite(signal_values)
    for start, end in _valid_segments(valid):
        segment = signal_values[start:end]
        if method == "MOVING_AVERAGE":
            if window_ms is None or window_ms <= 0:
                raise EnvelopeError("WINDOW_MS_REQUIRED")
            window_samples = max(1, int(round(window_ms * fs_hz / 1000)))
            if len(segment) < window_samples:
                continue
            kernel = np.ones(window_samples) / window_samples
            output[start:end] = np.convolve(segment, kernel, mode="same")
        elif method == "BUTTERWORTH_LOWPASS":
            if cutoff_hz is None or not 0 < cutoff_hz < fs_hz / 2:
                raise EnvelopeError("VALID_CUTOFF_HZ_REQUIRED")
            sos = signal.butter(
                filter_order,
                cutoff_hz,
                btype="lowpass",
                fs=fs_hz,
                output="sos",
            )
            minimum_samples = max(32, 6 * filter_order + 3)
            if len(segment) < minimum_samples:
                continue
            output[start:end] = signal.sosfiltfilt(sos, segment)
        elif method == "NONE":
            output[start:end] = segment
        else:
            raise EnvelopeError("UNSUPPORTED_SMOOTHING_METHOD")
    return output


def build_envelope(
    values: np.ndarray,
    fs_hz: float,
    window_identity: Mapping[str, Any],
    *,
    mask: np.ndarray,
    rectification: str = "FULL_WAVE",
    smoothing: str = "MOVING_AVERAGE",
    window_ms: float | None = 50.0,
    cutoff_hz: float | None = None,
    filter_order: int = 2,
) -> EnvelopeResult:
    signal_values = np.asarray(values, dtype=float)
    raw_hash = hash_array(signal_values)
    masked = apply_metadata_mask(signal_values, mask, window_identity)
    rectified = rectify(masked.values, rectification)
    output = smooth(
        rectified,
        fs_hz,
        method=smoothing,
        window_ms=window_ms,
        cutoff_hz=cutoff_hz,
        filter_order=filter_order,
        mask=masked.mask,
    )
    if hash_array(signal_values) != raw_hash:
        raise RuntimeError("RAW_MUTATION_DETECTED")

    metadata = {
        "processor": "DAY43_ENVELOPE",
        "source_window_id": masked.window_identity["window_id"],
        "native_fs_hz": float(fs_hz),
        "processed_fs_hz": float(fs_hz),
        "rectification": rectification,
        "smoothing": {
            "method": smoothing,
            "window_ms": window_ms,
            "cutoff_hz": cutoff_hz,
            "filter_order": filter_order,
        },
        "input_hash": raw_hash,
        "output_hash": hash_array(output),
        "mask_preserved": True,
        "sample_count_preserved": len(output) == len(signal_values),
    }
    return EnvelopeResult(
        output,
        masked.mask,
        masked.window_identity,
        metadata,
    )
