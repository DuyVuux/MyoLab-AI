#!/usr/bin/env python3
"""Kiểm tra đáp ứng tần số lý thuyết của preprocess_v0.1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from scipy.signal import sosfreqz


ROOT = Path(__file__).resolve().parents[2]
SEMGC_PATH = ROOT / "packages" / "semg-core"
PREPROCESS_PATH = ROOT / "services" / "preprocessing-service" / "src"
for path in (SEMGC_PATH, PREPROCESS_PATH):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from semg_core.preprocessing import (  # noqa: E402
    design_butterworth_bandpass_sos,
    design_notch_sos,
)
from preprocess_config import load_preprocess_config  # noqa: E402


def db(value: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.asarray(value), 1e-15))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("services/preprocessing-service/configs/preprocess_v0.1.yaml"),
    )
    parser.add_argument("--sampling-rate-hz", type=float, default=1000.0)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_preprocess_config(args.config)
    band = config["steps"]["bandpass"]
    notch = config["steps"]["notch"]
    frequencies = np.array([5.0, 20.0, 50.0, 80.0, 400.0, 450.0])
    omega = 2.0 * np.pi * frequencies / args.sampling_rate_hz

    band_sos = design_butterworth_bandpass_sos(
        sampling_rate_hz=args.sampling_rate_hz,
        low_cut_hz=float(band["low_cut_hz"]),
        high_cut_hz=float(band["high_cut_hz"]),
        order=int(band["order"]),
        nyquist_margin_ratio=float(band["nyquist_margin_ratio"]),
    )
    _, band_h = sosfreqz(band_sos, worN=omega)
    band_effective_db = db(np.abs(band_h) ** 2)

    notch_sos = design_notch_sos(
        sampling_rate_hz=args.sampling_rate_hz,
        line_frequency_hz=float(notch["line_frequency_hz"]),
        q_factor=float(notch["q_factor"]),
    )
    _, notch_h = sosfreqz(notch_sos, worN=omega)
    notch_effective_db = db(np.abs(notch_h) ** 2)

    by_frequency = {
        str(int(f) if f.is_integer() else f): {
            "bandpass_zero_phase_gain_db": float(g1),
            "notch_zero_phase_gain_db": float(g2),
            "combined_if_notch_applied_db": float(g1 + g2),
        }
        for f, g1, g2 in zip(frequencies, band_effective_db, notch_effective_db)
    }
    acceptance = {
        "5_hz_attenuated_below_minus_20_db": by_frequency["5"]["bandpass_zero_phase_gain_db"] < -20.0,
        "80_hz_preserved_above_minus_1_db": by_frequency["80"]["bandpass_zero_phase_gain_db"] > -1.0,
        "450_hz_attenuated_below_minus_20_db": by_frequency["450"]["bandpass_zero_phase_gain_db"] < -20.0,
        "50_hz_notch_below_minus_20_db": by_frequency["50"]["notch_zero_phase_gain_db"] < -20.0,
    }
    payload = {
        "config_id": config["config_id"],
        "sampling_rate_hz": args.sampling_rate_hz,
        "frequency_response": by_frequency,
        "acceptance": acceptance,
        "all_passed": all(acceptance.values()),
        "note": "Gain zero-phase được tính bằng bình phương biên độ one-pass; đây là verification kỹ thuật, không phải clinical validation.",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
