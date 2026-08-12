import numpy as np
import pytest

from semg_core.processing.envelope import build_envelope, rectify, smooth
from semg_core.processing.masking import (
    apply_metadata_mask,
    metric_mask_eligibility,
)


WINDOW_IDENTITY = {
    "window_id": "qcw_x",
    "session_id": "s",
    "channel_id": "c",
    "start_sample": 0,
    "end_sample_exclusive": 1000,
}


def test_mask_not_delete_and_raw_immutable():
    values = np.linspace(-1, 1, 1000)
    before = values.copy()
    mask = np.zeros(1000, dtype=bool)
    mask[100:200] = True
    result = apply_metadata_mask(values, mask, WINDOW_IDENTITY)
    assert len(result.values) == len(values)
    assert np.array_equal(values, before)
    assert np.isnan(result.values[mask]).all()
    assert result.metadata["raw_deleted"] is False


def test_masked_window_metric_blocked():
    mask = np.zeros(1000, dtype=bool)
    mask[10] = True
    eligibility = metric_mask_eligibility(
        mask,
        qc_signal_quality="PASS",
        processing_permission="ALLOW_PROFILED_PROCESSING",
    )
    assert not eligibility["eligible"]
    assert eligibility["metric_value"] is None


def test_qc_fail_blocked_even_without_mask():
    eligibility = metric_mask_eligibility(
        np.zeros(10, dtype=bool),
        qc_signal_quality="FAIL",
        processing_permission="ALLOW_PROFILED_PROCESSING",
    )
    assert not eligibility["eligible"]
    assert "QC_FAIL_BLOCKS_METRIC" in eligibility["reason_codes"]


def test_full_wave_and_half_wave():
    values = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    assert np.array_equal(rectify(values), [2, 1, 0, 1, 2])
    assert np.array_equal(rectify(values, "HALF_WAVE"), [0, 0, 0, 1, 2])


def test_smoothing_deterministic_and_boundary_shape():
    fs_hz = 1000
    time = np.arange(1000) / fs_hz
    values = np.abs(np.sin(2 * np.pi * 40 * time))
    mask = np.zeros(1000, dtype=bool)
    mask[400:450] = True
    first = smooth(
        values,
        fs_hz,
        method="MOVING_AVERAGE",
        window_ms=50,
        mask=mask,
    )
    second = smooth(
        values,
        fs_hz,
        method="MOVING_AVERAGE",
        window_ms=50,
        mask=mask,
    )
    assert np.array_equal(first, second, equal_nan=True)
    assert len(first) == len(values)
    assert np.isnan(first[mask]).all()


def test_lowpass_nyquist_validation():
    with pytest.raises(ValueError):
        smooth(
            np.ones(500),
            1000,
            method="BUTTERWORTH_LOWPASS",
            cutoff_hz=600,
        )


def test_window_identity_lineage_preserved():
    fs_hz = 1000
    time = np.arange(1000) / fs_hz
    values = np.sin(2 * np.pi * 40 * time)
    mask = np.zeros(1000, dtype=bool)
    result = build_envelope(
        values,
        fs_hz,
        WINDOW_IDENTITY,
        mask=mask,
    )
    assert dict(result.window_identity) == WINDOW_IDENTITY
    assert result.metadata["source_window_id"] == WINDOW_IDENTITY["window_id"]
    assert result.metadata["sample_count_preserved"]


def test_short_segment_is_not_silently_adapted_to_smaller_kernel():
    values = np.ones(20)
    result = smooth(
        values,
        1000,
        method="MOVING_AVERAGE",
        window_ms=50,
        mask=np.zeros(20, dtype=bool),
    )
    assert np.isnan(result).all()
