from __future__ import annotations

from typing import Any


def evaluate_quality(stats: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    config = rules["rules"]
    reasons: list[str] = []

    nonfinite = float(stats["nonfinite_ratio"])
    if nonfinite > float(config["nonfinite_ratio"]["warning"]):
        reasons.append("NONFINITE_PRESENT")

    flatline = float(stats["flatline_ratio"])
    if flatline > float(config["flatline_ratio"]["warning"]):
        reasons.append("FLATLINE_CANDIDATE")
    if flatline >= 0.999:
        reasons.append("CONSTANT_CHANNEL")

    clipping = float(stats["clipping_candidate_ratio"])
    if clipping > float(config["clipping_candidate_ratio"]["warning"]):
        reasons.append("CLIPPING_CANDIDATE")

    if int(stats["sample_count"]) < int(config["minimum_samples"]["warning"]):
        reasons.append("SHORT_RECORD")
    return sorted(set(reasons))
