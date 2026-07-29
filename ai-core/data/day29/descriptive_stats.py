from __future__ import annotations

import math
from typing import Any

import numpy as np


def mad(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return math.nan
    center = np.median(finite)
    return float(np.median(np.abs(finite - center)))


def channel_statistics(values: np.ndarray) -> dict[str, Any]:
    x = np.asarray(values, dtype=float)
    finite_mask = np.isfinite(x)
    finite = x[finite_mask]
    n = int(x.size)
    nonfinite_ratio = float(1.0 - finite_mask.mean()) if n else 1.0
    if finite.size == 0:
        return {
            "sample_count": n,
            "finite_count": 0,
            "nonfinite_ratio": nonfinite_ratio,
            "mean": math.nan,
            "std": math.nan,
            "median": math.nan,
            "mad": math.nan,
            "rms": math.nan,
            "mav": math.nan,
            "minimum": math.nan,
            "maximum": math.nan,
            "zero_ratio": math.nan,
            "flatline_ratio": math.nan,
            "clipping_candidate_ratio": math.nan,
        }

    differences = np.diff(finite)
    flatline_ratio = float(np.mean(np.isclose(differences, 0.0, rtol=0.0, atol=1e-12))) if differences.size else 1.0
    minimum = float(np.min(finite))
    maximum = float(np.max(finite))
    extreme_hits = np.isclose(finite, minimum) | np.isclose(finite, maximum)

    return {
        "sample_count": n,
        "finite_count": int(finite.size),
        "nonfinite_ratio": nonfinite_ratio,
        "mean": float(np.mean(finite)),
        "std": float(np.std(finite, ddof=1)) if finite.size > 1 else 0.0,
        "median": float(np.median(finite)),
        "mad": mad(finite),
        "rms": float(np.sqrt(np.mean(np.square(finite)))),
        "mav": float(np.mean(np.abs(finite))),
        "minimum": minimum,
        "maximum": maximum,
        "zero_ratio": float(np.mean(np.isclose(finite, 0.0, rtol=0.0, atol=1e-12))),
        "flatline_ratio": flatline_ratio,
        "clipping_candidate_ratio": float(np.mean(extreme_hits)) if maximum > minimum else 1.0,
    }
