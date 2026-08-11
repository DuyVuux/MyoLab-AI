#!/usr/bin/env python3
"""Deterministic adversarial and throughput stress test for Day 31."""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import time
import tracemalloc
from hashlib import sha256
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.pipeline import PartitionAccessError, assert_window_visible
from semg_core.day31_features import (
    FEATURE_ORDER,
    FeatureExtractionError,
    extract_feature_set_14,
)


def _guard_row(partition: str, signal_path: str) -> dict[str, str]:
    return {"partition": partition, "signal_path": signal_path}


def run_stress(windows: int, channels: int = 28) -> dict[str, object]:
    """Run deterministic numerical, memory, and fail-closed stress lanes."""

    if isinstance(windows, bool) or not isinstance(windows, int) or windows <= 0:
        raise ValueError("windows must be a positive integer")
    if (
        isinstance(channels, bool)
        or not isinstance(channels, int)
        or not 1 <= channels <= 28
    ):
        raise ValueError("channels must be an integer in [1, 28]")

    random = np.random.default_rng(31)
    digest = sha256()
    feature_rows = 0
    infinite_features = 0
    started = time.perf_counter()
    tracemalloc.start()
    for window_index in range(windows):
        sampling_rate = 2_000.0 if window_index % 2 == 0 else 2_048.0
        sample_count = 400 if sampling_rate == 2_000.0 else 410
        time_axis = np.arange(sample_count) / sampling_rate
        for channel_index in range(channels):
            frequency = 35.0 + 5.0 * (channel_index % 16)
            amplitude = 0.25 + 0.05 * (channel_index + 1)
            signal = amplitude * np.sin(2 * np.pi * frequency * time_axis)
            signal += 0.02 * random.normal(size=sample_count)
            result = extract_feature_set_14(signal, sampling_rate)
            for feature_id in FEATURE_ORDER:
                value = result.features[feature_id]
                if math.isinf(value):
                    infinite_features += 1
                digest.update(feature_id.encode("ascii"))
                digest.update(struct.pack(">d", value))
                feature_rows += 1

    partition_attacks = (
        ("test", "/zone2/test/a.npy"),
        ("sealed_test", "/zone2/data/a.npy"),
        ("outer_test", "/zone2/data/a.npy"),
        ("unknown", "/zone2/data/a.npy"),
        ("validation", "/zone2/sealed-test/a.npy"),
        ("validation", r"C:\zone2\outer_test\a.npy"),
        ("TRAIN", "/zone2/train/a.npy"),
    )
    partition_attacks_blocked = 0
    for partition, signal_path in partition_attacks:
        try:
            assert_window_visible(_guard_row(partition, signal_path))
        except PartitionAccessError:
            partition_attacks_blocked += 1

    malformed_signals = (
        np.array([]),
        np.ones((4, 2)),
        np.array(["not-a-number"], dtype=object),
    )
    malformed_blocked = 0
    for signal in malformed_signals:
        try:
            extract_feature_set_14(signal, 2_000.0)
        except FeatureExtractionError:
            malformed_blocked += 1

    nonfinite_signals = (
        np.array([1.0, math.nan, 2.0, 3.0]),
        np.array([1.0, math.inf, 2.0, 3.0]),
        np.array([1.0, -math.inf, 2.0, 3.0]),
    )
    nonfinite_blocked = 0
    for signal in nonfinite_signals:
        try:
            extract_feature_set_14(signal, 2_000.0)
        except FeatureExtractionError:
            nonfinite_blocked += 1

    extreme = extract_feature_set_14(
        np.array([1e308, -1e308, 1e308, -1e308]),
        2_000.0,
    )
    infinite_features += sum(
        math.isinf(value) for value in extreme.features.values()
    )
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed_seconds = time.perf_counter() - started
    max_elapsed_seconds = max(60.0, windows * channels * 0.01)
    max_peak_memory_mib = 512.0
    passed = (
        feature_rows == windows * channels * len(FEATURE_ORDER)
        and partition_attacks_blocked == len(partition_attacks)
        and malformed_blocked == len(malformed_signals)
        and nonfinite_blocked == len(nonfinite_signals)
        and infinite_features == 0
        and elapsed_seconds < max_elapsed_seconds
        and peak_bytes < max_peak_memory_mib * 1024 * 1024
    )
    return {
        "schema_version": "day31-stress-test.v1",
        "seed": 31,
        "windows": windows,
        "channels": channels,
        "feature_rows_generated": feature_rows,
        "feature_digest_sha256": digest.hexdigest(),
        "forbidden_partition_attacks": len(partition_attacks),
        "forbidden_partition_attacks_blocked": partition_attacks_blocked,
        "malformed_signal_attacks": len(malformed_signals),
        "malformed_signal_attacks_blocked": malformed_blocked,
        "nonfinite_attacks": len(nonfinite_signals),
        "nonfinite_attacks_blocked": nonfinite_blocked,
        "infinite_features_emitted": infinite_features,
        "elapsed_seconds": round(elapsed_seconds, 6),
        "peak_memory_mib": round(peak_bytes / (1024 * 1024), 3),
        "thresholds": {
            "max_elapsed_seconds": max_elapsed_seconds,
            "max_peak_memory_mib": max_peak_memory_mib,
        },
        "test_signal_rows_read": 0,
        "training_executed": False,
        "model_fitting_executed": False,
        "pooled_training_executed": False,
        "pass": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=int, default=1_500)
    parser.add_argument("--channels", type=int, default=28)
    parser.add_argument(
        "--output",
        default="qa-validation/evidence/day31/day31-stress-test.json",
    )
    arguments = parser.parse_args()
    try:
        result = run_stress(arguments.windows, arguments.channels)
        output = Path(arguments.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
            + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["pass"] else 2
    except (OSError, TypeError, ValueError, AssertionError) as error:
        print(f"day31 stress test failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
