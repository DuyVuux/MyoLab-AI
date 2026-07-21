"""Analytical tests bổ sung cho preprocessing v0.1."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
from scipy.signal import sosfreqz
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMGC_CORE = ROOT / "packages" / "semg-core"
if str(SEMGC_CORE) not in sys.path:
    sys.path.insert(0, str(SEMGC_CORE))

from semg_core.preprocessing import (  # noqa: E402
    design_butterworth_bandpass_sos,
    preprocess_channel,
)


def config() -> dict:
    return yaml.safe_load((ROOT / "services/preprocessing-service/configs/preprocess_v0.1.yaml").read_text(encoding="utf-8"))


def kwargs(cfg: dict, notch: bool = False) -> dict:
    steps = cfg["steps"]
    return {
        "mean_center_enabled": bool(steps["mean_center"]["enabled"]),
        "bandpass_low_hz": float(steps["bandpass"]["low_cut_hz"]),
        "bandpass_high_hz": float(steps["bandpass"]["high_cut_hz"]),
        "bandpass_order": int(steps["bandpass"]["order"]),
        "nyquist_margin_ratio": float(steps["bandpass"]["nyquist_margin_ratio"]),
        "notch_enabled": notch,
        "notch_frequency_hz": float(steps["notch"]["line_frequency_hz"]),
        "notch_q_factor": float(steps["notch"]["q_factor"]),
    }


def zero_phase_gain_db(sos: np.ndarray, frequency: float, fs: float) -> float:
    _, h = sosfreqz(sos, worN=np.asarray([frequency]), fs=fs)
    return float(20.0 * np.log10(max(abs(h[0]) ** 2, 1e-15)))


def test_theoretical_passband_and_stopband() -> None:
    cfg = config()
    fs = 1000.0
    bp = cfg["steps"]["bandpass"]
    sos = design_butterworth_bandpass_sos(
        sampling_rate_hz=fs,
        low_cut_hz=float(bp["low_cut_hz"]),
        high_cut_hz=float(bp["high_cut_hz"]),
        order=int(bp["order"]),
        nyquist_margin_ratio=float(bp["nyquist_margin_ratio"]),
    )
    assert zero_phase_gain_db(sos, 5.0, fs) <= -40.0
    assert -0.5 <= zero_phase_gain_db(sos, 80.0, fs) <= 0.5
    assert -0.5 <= zero_phase_gain_db(sos, 200.0, fs) <= 0.5
    assert zero_phase_gain_db(sos, 450.0, fs) <= -30.0


def test_zero_phase_impulse_is_centered_and_symmetric() -> None:
    cfg = config()
    fs = 1000.0
    sample_count = 20001
    center = sample_count // 2
    impulse = np.zeros(sample_count)
    impulse[center] = 1.0
    result = preprocess_channel(impulse, sampling_rate_hz=fs, **kwargs(cfg))
    output = result.samples_uV
    assert int(np.argmax(np.abs(output))) == center
    symmetry = np.max(np.abs(output[:center][::-1] - output[center + 1 :])) / np.max(np.abs(output))
    assert symmetry <= 1e-10


def test_same_input_same_hash_in_same_process() -> None:
    cfg = config()
    fs = 1000.0
    time_s = np.arange(20500, dtype=np.float64) / fs
    signal = 30.0 * np.sin(2 * np.pi * 80.0 * time_s) + 10.0 * np.sin(2 * np.pi * 5.0 * time_s)
    hashes = {
        preprocess_channel(signal, sampling_rate_hz=fs, **kwargs(cfg)).diagnostics.output_hash_sha256
        for _ in range(3)
    }
    assert len(hashes) == 1
