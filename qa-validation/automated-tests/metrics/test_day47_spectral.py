"""DAY47 automated unit tests for Welch PSD, MDF, and MNF spectral metrics."""

import sys
from pathlib import Path
import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SEMG_ROOT = REPO_ROOT / "packages" / "semg-core"
if str(SEMG_ROOT) not in sys.path:
    sys.path.insert(0, str(SEMG_ROOT))

from semg_core.metrics.spectral import PsdSpec, compute_mdf_mnf, fingerprint


def tone(fs: float, f: float, n: int = 4096) -> np.ndarray:
    t = np.arange(n) / fs
    return np.sin(2 * np.pi * f * t)


def test_tone_mnf_mdf():
    spec = PsdSpec(2048.0, 1024, 512, fmin_hz=20.0, fmax_hz=500.0)
    r = compute_mdf_mnf(tone(2048.0, 128.0), spec)
    assert r.status == "AVAILABLE"
    assert r.mnf_hz is not None and abs(r.mnf_hz - 128.0) < 2.0
    assert r.mdf_hz is not None and abs(r.mdf_hz - 128.0) < 2.0


def test_fs_variation():
    for fs in (1000.0, 2000.0, 4000.0):
        spec = PsdSpec(
            fs,
            min(1000, int(fs)),
            0,
            fmin_hz=20.0,
            fmax_hz=min(450.0, fs / 2.0 - 1.0),
        )
        r = compute_mdf_mnf(tone(fs, 100.0), spec)
        assert r.status == "AVAILABLE"
        assert r.mnf_hz is not None and abs(r.mnf_hz - 100.0) < 3.0


def test_insufficient_returns_null():
    r = compute_mdf_mnf(np.ones(10), PsdSpec(2000.0, 256))
    assert r.status == "UNAVAILABLE"
    assert r.mdf_hz is None
    assert "INSUFFICIENT_SAMPLES" in r.reason_codes


def test_alias_range_rejected():
    r = compute_mdf_mnf(np.ones(512), PsdSpec(1000.0, 256, fmax_hz=600.0))
    assert r.status == "UNAVAILABLE"
    assert "FREQUENCY_RANGE_INVALID" in r.reason_codes


def test_nonfinite_returns_null():
    x = np.ones(512)
    x[2] = np.nan
    r = compute_mdf_mnf(x, PsdSpec(2000.0, 256))
    assert r.status == "UNAVAILABLE"
    assert "NONFINITE_INPUT" in r.reason_codes


def test_fingerprint_deterministic():
    spec = PsdSpec(2000.0, 256, 128)
    assert fingerprint(spec) == fingerprint(spec)
