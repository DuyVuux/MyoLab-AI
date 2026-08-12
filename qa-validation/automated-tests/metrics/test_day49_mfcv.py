"""DAY49 automated unit tests for MFCV feasibility and gate estimator."""

import sys
from pathlib import Path
import numpy as np
import pytest
from scipy import signal

REPO_ROOT = Path(__file__).resolve().parents[3]
QG_SERVICE_ROOT = REPO_ROOT / "services" / "quality-gate-service" / "src"
if str(QG_SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(QG_SERVICE_ROOT))

from application.mfcv_eligibility import (
    MfcvRequest,
    estimate_mfcv,
    evaluate_mfcv_eligibility,
)


def req(**k) -> MfcvRequest:
    d = dict(
        channel_ids=("c1", "c2", "c3"),
        spacing_m=(0.004, 0.004),
        channel_order_known=True,
        same_muscle_region=True,
        orientation_evidence="VERIFIED",
        synchronization_status="VERIFIED",
        sampling_resolution_status="VERIFIED",
        signal_representation="RAW_UNRECTIFIED",
        qc_pass=True,
    )
    d.update(k)
    return MfcvRequest(**d)


def test_unknown_ied_null():
    r = estimate_mfcv(
        np.zeros((3, 100)),
        2000.0,
        req(spacing_m=None),
        min_peak_ncc=0.5,
        max_pair_cv=0.35,
        physical_sanity_range_m_per_s=(0.5, 20.0),
    )
    assert r.status == "MFCV_UNSUPPORTED"
    assert "IED_UNKNOWN" in r.reason_codes


def test_unknown_orientation_null():
    r = estimate_mfcv(
        np.zeros((3, 100)),
        2000.0,
        req(orientation_evidence="UNKNOWN"),
        min_peak_ncc=0.5,
        max_pair_cv=0.35,
        physical_sanity_range_m_per_s=(0.5, 20.0),
    )
    assert r.status == "MFCV_UNSUPPORTED"
    assert "ORIENTATION_UNVERIFIED" in r.reason_codes


def test_insufficient_channels():
    r = estimate_mfcv(
        np.zeros((1, 100)),
        2000.0,
        req(channel_ids=("c1",), spacing_m=()),
        min_peak_ncc=0.5,
        max_pair_cv=0.35,
        physical_sanity_range_m_per_s=(0.5, 20.0),
    )
    assert r.status == "MFCV_UNSUPPORTED"
    assert "INSUFFICIENT_SPATIAL_OBSERVATIONS" in r.reason_codes


def test_rectified_rejected():
    r = estimate_mfcv(
        np.zeros((3, 100)),
        2000.0,
        req(signal_representation="RECTIFIED"),
        min_peak_ncc=0.5,
        max_pair_cv=0.35,
        physical_sanity_range_m_per_s=(0.5, 20.0),
    )
    assert r.status == "MFCV_UNSUPPORTED"
    assert "SIGNAL_REPRESENTATION_UNSUPPORTED" in r.reason_codes


def test_known_delay_mechanics():
    fs = 2000.0
    rng = np.random.default_rng(49)
    base = rng.normal(size=4096)
    # Band-limit for stable NCC correlation
    sos = signal.butter(4, [20.0, 400.0], btype="bandpass", fs=fs, output="sos")
    base = signal.sosfiltfilt(sos, base)

    # 2 samples delay at 2000 Hz = 1 ms delay. Distance = 4 mm = 0.004 m -> 4.0 m/s
    x = np.vstack(
        [
            base,
            np.concatenate([np.zeros(2), base[:-2]]),
            np.concatenate([np.zeros(4), base[:-4]]),
        ]
    )

    r = estimate_mfcv(
        x,
        fs,
        req(),
        min_peak_ncc=0.5,
        max_pair_cv=0.35,
        physical_sanity_range_m_per_s=(0.5, 20.0),
    )
    assert r.status == "MFCV_RESEARCH_SUPPORTED"
    assert r.value_m_per_s is not None
    assert abs(r.value_m_per_s - 4.0) < 0.15


def test_two_channels_allowed_with_warning():
    r, w = evaluate_mfcv_eligibility(req(channel_ids=("c1", "c2"), spacing_m=(0.004,)))
    assert not r
    assert "PAIRWISE_MINIMUM_LOW_REDUNDANCY" in w


def test_2d_grid_path_can_feed_reference_estimator():
    r, w = evaluate_mfcv_eligibility(req(geometry_type="ORDERED_PATH_FROM_2D_GRID"))
    assert not r
