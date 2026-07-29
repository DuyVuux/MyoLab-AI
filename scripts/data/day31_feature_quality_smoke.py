#!/usr/bin/env python3
"""Run deterministic feature quality and redundancy smoke audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import dump_json_strict
from semg_core.day31_features import FEATURE_ORDER, extract_feature_set_14
from semg_core.day31_features.quality import correlation_pairs, summarize_feature


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--windows", type=int, default=256)
    arguments = parser.parse_args()
    try:
        if arguments.windows < 20:
            raise ValueError("quality smoke requires at least 20 windows")
        random = np.random.default_rng(31)
        time_axis = np.arange(400) / 2_000.0
        matrix: list[list[float]] = []
        for index in range(arguments.windows):
            signal = random.normal(scale=0.2, size=400)
            signal += (1.0 + index / arguments.windows) * np.sin(
                2 * np.pi * 50 * time_axis
            )
            features = extract_feature_set_14(signal, 2_000.0).features
            matrix.append([features[name] for name in FEATURE_ORDER])
        values = np.asarray(matrix)
        summaries = {
            name: summarize_feature(values[:, index])
            for index, name in enumerate(FEATURE_ORDER)
        }
        pairs = correlation_pairs(
            values,
            FEATURE_ORDER,
            threshold=0.95,
        )
        passed = (
            values.shape == (arguments.windows, 14)
            and all(
                summary["finite_ratio"] == 1.0
                for summary in summaries.values()
            )
        )
        result = {
            "schema_version": "day31-feature-quality-smoke.v1",
            "pass": passed,
            "partition": "synthetic_train",
            "window_count": arguments.windows,
            "feature_count": 14,
            "correlation_methods": ["pearson", "spearman"],
            "correlation_threshold": 0.95,
            "summaries": summaries,
            "redundancy_pairs": pairs,
            "automatic_feature_drop_executed": False,
            "test_signal_rows_read": 0,
            "training_executed": False,
        }
        dump_json_strict(arguments.output, result)
        print(
            json.dumps(
                {
                    "pass": passed,
                    "window_count": arguments.windows,
                    "redundancy_pair_count": len(pairs),
                },
                indent=2,
            )
        )
        return 0 if passed else 2
    except (OSError, TypeError, ValueError) as error:
        print(f"day31 quality smoke failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
