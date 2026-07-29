from __future__ import annotations

import itertools
from collections import defaultdict
from typing import Any, Iterable

import numpy as np

from .descriptive_stats import mad


def robust_shift(values_a: Iterable[float], values_b: Iterable[float]) -> float:
    a = np.asarray(list(values_a), dtype=float)
    b = np.asarray(list(values_b), dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if a.size == 0 or b.size == 0:
        return float("nan")
    pooled_mad = (mad(a) + mad(b)) / 2.0
    scale = 1.4826 * pooled_mad
    return float((np.median(b) - np.median(a)) / (scale + 1e-12))


def build_drift_summary(
    feature_rows: Iterable[dict[str, Any]],
    feature_name: str,
    minimum_records_per_day: int = 2,
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in feature_rows:
        key = (str(row["subject_id"]), str(row["canonical_label"]), str(row["channel_id"]))
        groups[key][str(row["day_id"])].append(float(row[feature_name]))

    output: list[dict[str, Any]] = []
    for (subject, label, channel), by_day in sorted(groups.items()):
        for day_a, day_b in itertools.combinations(sorted(by_day), 2):
            values_a = np.asarray(by_day[day_a], dtype=float)
            values_b = np.asarray(by_day[day_b], dtype=float)
            if len(values_a) < minimum_records_per_day or len(values_b) < minimum_records_per_day:
                continue
            med_a = float(np.median(values_a))
            med_b = float(np.median(values_b))
            output.append(
                {
                    "subject_id": subject,
                    "canonical_label": label,
                    "channel_id": channel,
                    "feature": feature_name,
                    "day_a": day_a,
                    "day_b": day_b,
                    "n_a": int(len(values_a)),
                    "n_b": int(len(values_b)),
                    "median_a": med_a,
                    "median_b": med_b,
                    "mad_a": mad(values_a),
                    "mad_b": mad(values_b),
                    "ratio_b_over_a": float(med_b / (med_a + 1e-12)),
                    "robust_shift_z": robust_shift(values_a, values_b),
                    "interpretation": "DISTRIBUTION_SHIFT_DESCRIPTIVE_ONLY",
                    "fatigue_inference_allowed": False,
                }
            )
    return output
