#!/usr/bin/env python3
"""Run golden mathematical and source-view synthetic extraction smoke tests."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import dump_json_strict
from day31.pipeline import extract_window_index
from semg_core.day31_features import (
    FEATURE_ORDER,
    FeatureExtractionError,
    extract_feature_set_14,
)


def _window_row(
    *,
    dataset_id: str,
    partition: str,
    sampling_rate_hz: float,
    sample_count: int,
    channel_policy_id: str,
    window_id: str,
) -> dict[str, Any]:
    return {
        "window_id": window_id,
        "dataset_id": dataset_id,
        "record_id": f"synthetic-{dataset_id}",
        "subject_id": "synthetic-subject",
        "day_id": "synthetic-day",
        "session_id": "synthetic-session",
        "repetition_id": "synthetic-repetition",
        "canonical_label": "rest",
        "partition": partition,
        "signal_path": f"/zone2/{partition}/synthetic.npy",
        "source_file_sha256": "a" * 64,
        "split_version": "synthetic-split-v1",
        "label_mapping_version": "synthetic-labels-v1",
        "start_sample": 0,
        "end_sample_exclusive": sample_count,
        "record_n_samples": sample_count,
        "sampling_rate_hz": sampling_rate_hz,
        "window_ms": 200,
        "hop_ms": 100,
        "channel_policy_id": channel_policy_id,
        "preprocessing_policy_id": "synthetic-dc-removed-v1",
    }


def _reader(row: Mapping[str, Any]) -> tuple[np.ndarray, tuple[str, ...]]:
    sampling_rate = float(row["sampling_rate_hz"])
    sample_count = int(row["end_sample_exclusive"]) - int(row["start_sample"])
    time_axis = np.arange(sample_count) / sampling_rate
    if row["dataset_id"] == "mendeley-4channel-hand-gesture-v2":
        channel_ids = (
            "EMG_Raw_CH1",
            "EMG_RAW_CH2",
            "EMG_RAW_CH3",
            "EMG_RAW_CH4",
        )
    else:
        channel_ids = tuple(
            [f"F{index}" for index in range(1, 17)]
            + [f"W{index}" for index in range(1, 13)]
            + [f"U{index}" for index in range(1, 5)]
        )
    signal = np.column_stack(
        [
            (1.0 + 0.01 * index)
            * np.sin(2 * np.pi * (40 + 5 * (index % 12)) * time_axis)
            for index in range(len(channel_ids))
        ]
    )
    return signal, channel_ids


def _json_features(features: Mapping[str, float]) -> dict[str, float | None]:
    return {
        name: float(value) if math.isfinite(value) else None
        for name, value in features.items()
    }


def _golden_tests() -> dict[str, Any]:
    sampling_rate = 2_000.0
    time_axis = np.arange(400) / sampling_rate
    sine = np.sin(2 * np.pi * 50 * time_axis)
    sine_result = extract_feature_set_14(sine, sampling_rate)
    scaled_result = extract_feature_set_14(10.0 * sine, sampling_rate)
    zero_result = extract_feature_set_14(np.zeros(400), sampling_rate)
    scale_checks = all(
        math.isclose(
            scaled_result.features[name],
            sine_result.features[name],
            rel_tol=1e-10,
            abs_tol=1e-10,
        )
        for name in (
            "skewness_unbiased",
            "kurtosis_fisher_unbiased",
            "mdf_hz",
            "mnf_hz",
            "spectral_entropy_bits",
        )
    )
    nonfinite_blocked = False
    try:
        extract_feature_set_14(
            np.array([1.0, math.nan, 2.0, 3.0]),
            sampling_rate,
        )
    except FeatureExtractionError:
        nonfinite_blocked = True
    passed = (
        tuple(sine_result.features) == FEATURE_ORDER
        and math.isclose(sine_result.features["mdf_hz"], 50.0, abs_tol=1e-10)
        and math.isclose(sine_result.features["mnf_hz"], 50.0, abs_tol=1e-10)
        and "zero_power_window" in zero_result.qc_flags
        and scale_checks
        and nonfinite_blocked
    )
    return {
        "pass": passed,
        "sine50_features": _json_features(sine_result.features),
        "zero_features": _json_features(zero_result.features),
        "zero_qc_flags": list(zero_result.qc_flags),
        "positive_scale_invariants_pass": scale_checks,
        "nonfinite_input_blocked": nonfinite_blocked,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    try:
        mendeley = extract_window_index(
            [
                _window_row(
                    dataset_id="mendeley-4channel-hand-gesture-v2",
                    partition="train",
                    sampling_rate_hz=2_000.0,
                    sample_count=400,
                    channel_policy_id="mendeley-ch123-primary-v1",
                    window_id="a" * 24,
                )
            ],
            dataset_view_id="mendeley_core4_primary_v1",
            source_reader=_reader,
        )
        grabmyo = extract_window_index(
            [
                _window_row(
                    dataset_id="grabmyo-v1.1.0",
                    partition="validation",
                    sampling_rate_hz=2_048.0,
                    sample_count=410,
                    channel_policy_id="grabmyo-fw28-primary-v1",
                    window_id="b" * 24,
                )
            ],
            dataset_view_id="grabmyo_project_subset_native28_v1",
            source_reader=_reader,
        )
        golden = _golden_tests()
        views = {
            "mendeley_core4_primary_v1": {
                "pass": len(mendeley.feature_rows) == 42,
                "feature_rows": len(mendeley.feature_rows),
                "feature_dimensions": 42,
                "channel_count": 3,
            },
            "grabmyo_project_subset_native28_v1": {
                "pass": len(grabmyo.feature_rows) == 392,
                "feature_rows": len(grabmyo.feature_rows),
                "feature_dimensions": 392,
                "channel_count": 28,
            },
        }
        passed = golden["pass"] and all(
            view["pass"] for view in views.values()
        )
        result = {
            "schema_version": "day31-smoke-extraction.v1",
            "pass": passed,
            "golden_tests": golden,
            "views": views,
            "real_data_signal_rows_read": 0,
            "test_signal_rows_read": 0,
            "training_executed": False,
            "model_fitting_executed": False,
            "pooled_training_executed": False,
        }
        dump_json_strict(arguments.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if passed else 2
    except (OSError, TypeError, ValueError, PermissionError) as error:
        print(f"day31 smoke extraction failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
