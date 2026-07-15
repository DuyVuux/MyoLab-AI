#!/usr/bin/env python3
"""Generate a deterministic, full-protocol synthetic sEMG fixture.

The fixture exists only to test ingestion, provenance, phase mapping, and later
DSP regression. It is not patient data and is not evidence of clinical validity.

Signal design (active phase):
- a sum of chirped sinusoidal components with random phases;
- an amplitude envelope that increases over time;
- component frequencies that trend downward over time;
- low-level Gaussian and 50 Hz contamination.

No downstream fatigue conclusion should be made from this synthetic fixture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


FILE_STEM = "golden_signal_01"
DEFAULT_FS_HZ = 1000
DEFAULT_SEED = 20260714
BASELINE_DURATION_S = 5.0
ACTIVE_DURATION_S = 60.0
RECOVERY_DURATION_S = 5.0


def compute_sha256(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _unit_rms(values: np.ndarray) -> np.ndarray:
    rms = float(np.sqrt(np.mean(np.square(values))))
    if not math.isfinite(rms) or rms <= 0:
        raise ValueError("Cannot RMS-normalize a zero or invalid signal")
    return values / rms


def _active_semg_like(
    sample_count: int,
    sampling_rate_hz: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Create a smooth nonstationary, fatigue-like synthetic active segment."""

    t = np.arange(sample_count, dtype=np.float64) / sampling_rate_hz
    duration_s = sample_count / sampling_rate_hz
    progress = np.clip(t / max(duration_s, np.finfo(float).eps), 0.0, 1.0)

    component_count = 24
    start_frequencies = rng.uniform(65.0, 190.0, size=component_count)
    end_frequencies = np.maximum(
        rng.uniform(35.0, 105.0, size=component_count),
        22.0,
    )
    random_phases = rng.uniform(0.0, 2.0 * np.pi, size=component_count)
    weights = rng.lognormal(mean=0.0, sigma=0.25, size=component_count)
    weights /= np.sqrt(np.sum(np.square(weights)))

    signal = np.zeros(sample_count, dtype=np.float64)
    for f_start, f_end, phase0, weight in zip(
        start_frequencies,
        end_frequencies,
        random_phases,
        weights,
    ):
        chirp_rate = (f_end - f_start) / duration_s
        phase = 2.0 * np.pi * (f_start * t + 0.5 * chirp_rate * np.square(t)) + phase0
        signal += weight * np.sin(phase)

    signal = _unit_rms(signal)

    # Amplitude envelope in microvolts. This is a demo trend, not a clinical model.
    envelope_uV = 55.0 + 40.0 * progress
    envelope_uV *= 1.0 + 0.08 * np.sin(2.0 * np.pi * 0.35 * t)

    gaussian_noise_uV = rng.normal(loc=0.0, scale=5.0, size=sample_count)
    line_noise_uV = 1.5 * np.sin(2.0 * np.pi * 50.0 * t + 0.2)
    slow_modulation = 1.0 + 0.04 * np.sin(2.0 * np.pi * 0.08 * t)
    return envelope_uV * slow_modulation * signal + gaussian_noise_uV + line_noise_uV


def generate_signal(
    *,
    sampling_rate_hz: int = DEFAULT_FS_HZ,
    seed: int = DEFAULT_SEED,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    if sampling_rate_hz < 1000:
        raise ValueError("This Day 3 fixture requires Fs >= 1000 Hz")

    rng = np.random.default_rng(seed)
    n_baseline = int(round(BASELINE_DURATION_S * sampling_rate_hz))
    n_active = int(round(ACTIVE_DURATION_S * sampling_rate_hz))
    n_recovery = int(round(RECOVERY_DURATION_S * sampling_rate_hz))
    total_samples = n_baseline + n_active + n_recovery

    # Correct discrete-time construction: t[n] = n / Fs, endpoint excluded.
    time_s = np.arange(total_samples, dtype=np.float64) / sampling_rate_hz

    baseline_t = np.arange(n_baseline, dtype=np.float64) / sampling_rate_hz
    baseline = rng.normal(0.0, 2.5, size=n_baseline)
    baseline += 0.6 * np.sin(2.0 * np.pi * 50.0 * baseline_t)

    active = _active_semg_like(n_active, sampling_rate_hz, rng)

    recovery_t = np.arange(n_recovery, dtype=np.float64) / sampling_rate_hz
    recovery = rng.normal(0.0, 3.0, size=n_recovery)
    recovery += 7.0 * np.exp(-recovery_t / 0.7) * np.sin(
        2.0 * np.pi * 75.0 * recovery_t + 0.4
    )
    recovery += 0.6 * np.sin(2.0 * np.pi * 50.0 * recovery_t)

    signal_uV = np.concatenate([baseline, active, recovery]).astype(np.float64)
    metadata = {
        "seed": seed,
        "sampling_rate_hz": sampling_rate_hz,
        "sample_count": total_samples,
        "phase_sample_counts": {
            "baseline_rest": n_baseline,
            "active_contraction": n_active,
            "recovery": n_recovery,
        },
        "phase_durations_s": {
            "baseline_rest": BASELINE_DURATION_S,
            "active_contraction": ACTIVE_DURATION_S,
            "recovery": RECOVERY_DURATION_S,
        },
        "generator_version": "synthetic-semglike.v0.1",
    }
    return time_s, signal_uV, metadata


def build_manifest(
    *,
    csv_name: str,
    csv_hash: str,
    sampling_rate_hz: int,
    seed: int,
) -> dict[str, Any]:
    active_start = BASELINE_DURATION_S
    active_end = BASELINE_DURATION_S + ACTIVE_DURATION_S
    total_end = active_end + RECOVERY_DURATION_S
    return {
        "schema_version": "semg-session-manifest.v0.1",
        "session_id": "SYNTH_D3_GOLDEN_001",
        "fixture_type": "full_protocol_ingestion_golden",
        "analysis_ready": True,
        "clinical_use_allowed": False,
        "data_source": "synthetic",
        "signal_file": csv_name,
        "source_hash_sha256": csv_hash,
        "sampling_rate_hz": sampling_rate_hz,
        "time_column": "time_s",
        "protocol": {"id": "quad-isometric-60s", "version": "0.1.0"},
        "session_parameters": {
            "target_mvc_percent": 30,
            "parameter_status": "synthetic_demo_only_not_prescription",
        },
        "channels": [
            {
                "column": "VL_R_01",
                "channel_id": "VL_R_01",
                "muscle": "vastus_lateralis",
                "side": "right",
                "unit": "uV",
                "role": "bipolar_semg",
            }
        ],
        "phase_markers": [
            {"phase_id": "baseline_rest", "start_s": 0.0, "end_s": active_start},
            {
                "phase_id": "active_contraction",
                "start_s": active_start,
                "end_s": active_end,
            },
            {"phase_id": "recovery", "start_s": active_end, "end_s": total_end},
        ],
        "electrode_config": {
            "configuration": "single_bipolar_synthetic",
            "linear_array_confirmed": False,
            "interelectrode_distance_mm": None,
            "orientation_along_fibres_confirmed": False,
            "mfcv_candidate": False,
        },
        "processing_history": {
            "raw_export": True,
            "hardware_filter_known": False,
            "software_filter_applied": False,
            "synthetic_generator": "synthetic-semglike.v0.1",
            "generator_seed": seed,
        },
        "limitations": [
            "Synthetic signal; not physiological ground truth",
            "Not valid for clinical thresholds or model-performance claims",
            "MFCV is not eligible because no linear electrode array is represented",
        ],
    }


def write_fixture(output_dir: Path, *, sampling_rate_hz: int, seed: int, overwrite: bool) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{FILE_STEM}.csv"
    manifest_path = output_dir / f"{FILE_STEM}.manifest.json"
    generation_path = output_dir / f"{FILE_STEM}.generation.json"
    expected_path = output_dir / f"{FILE_STEM}.expected_ingestion_summary.json"
    targets = [csv_path, manifest_path, generation_path, expected_path]

    existing = [path for path in targets if path.exists()]
    if existing and not overwrite:
        names = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"Refusing to overwrite existing files: {names}")

    time_s, signal_uV, metadata = generate_signal(
        sampling_rate_hz=sampling_rate_hz,
        seed=seed,
    )
    matrix = np.column_stack([time_s, signal_uV])
    np.savetxt(
        csv_path,
        matrix,
        delimiter=",",
        header="time_s,VL_R_01",
        comments="",
        fmt=("%.6f", "%.9f"),
    )
    csv_hash = compute_sha256(csv_path)

    manifest = build_manifest(
        csv_name=csv_path.name,
        csv_hash=csv_hash,
        sampling_rate_hz=sampling_rate_hz,
        seed=seed,
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    generation_report = {
        **metadata,
        "csv_file": csv_path.name,
        "manifest_file": manifest_path.name,
        "source_hash_sha256": csv_hash,
        "signal_unit": "uV",
        "signal_min_uV": float(np.min(signal_uV)),
        "signal_max_uV": float(np.max(signal_uV)),
        "signal_finite_ratio": float(np.isfinite(signal_uV).mean()),
        "disclaimer": "Synthetic engineering fixture only; no clinical validity claim.",
    }
    generation_path.write_text(
        json.dumps(generation_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    expected_summary = {
        "schema_version": "normalized-signal.v0.1",
        "session_id": "SYNTH_D3_GOLDEN_001",
        "sampling_rate_hz": float(sampling_rate_hz),
        "sample_count": metadata["sample_count"],
        "channel_count": 1,
        "active_phase_sample_count": metadata["phase_sample_counts"]["active_contraction"],
        "canonical_unit": "uV",
        "source_hash_sha256": csv_hash,
        "mfcv_expected_eligible": False,
    }
    expected_path.write_text(
        json.dumps(expected_summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return generation_report


def verify_existing(output_dir: Path) -> dict[str, Any]:
    csv_path = output_dir / f"{FILE_STEM}.csv"
    manifest_path = output_dir / f"{FILE_STEM}.manifest.json"
    if not csv_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("Generated CSV and manifest are required for verification")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    computed_hash = compute_sha256(csv_path)
    declared_hash = manifest.get("source_hash_sha256")
    if declared_hash != computed_hash:
        raise ValueError(
            f"Hash mismatch: declared={declared_hash!r}, computed={computed_hash!r}"
        )
    return {
        "verified": True,
        "csv_file": str(csv_path),
        "manifest_file": str(manifest_path),
        "source_hash_sha256": computed_hash,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data-platform/synthetic-data"),
    )
    parser.add_argument("--sampling-rate-hz", type=int, default=DEFAULT_FS_HZ)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--verify-existing", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.verify_existing:
            result = verify_existing(args.output_dir)
        else:
            result = write_fixture(
                args.output_dir,
                sampling_rate_hz=args.sampling_rate_hz,
                seed=args.seed,
                overwrite=args.overwrite,
            )
    except (FileExistsError, FileNotFoundError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
