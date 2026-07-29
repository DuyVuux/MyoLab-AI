from __future__ import annotations

from typing import Any
import pandas as pd
import yaml


def load_rules(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("rules", {})


def apply_rules(channel_stats: pd.DataFrame, rules: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for rule_id, rule in rules.items():
        metric = rule["metric"]
        if metric not in channel_stats.columns:
            continue
        threshold = float(rule["threshold"])
        comparison = rule["comparison"]
        values = pd.to_numeric(channel_stats[metric], errors="coerce")
        if comparison == "greater_than":
            mask = values > threshold
        elif comparison == "equal_to":
            mask = values == threshold
        else:
            raise ValueError(f"Unsupported comparison: {comparison}")
        for _, row in channel_stats.loc[mask].iterrows():
            rows.append({
                "relative_path": row.get("relative_path"),
                "subject_id": row.get("subject_id"),
                "canonical_channel_id": row.get("canonical_channel_id"),
                "rule_id": rule_id,
                "severity": rule["severity"],
                "metric": metric,
                "observed_value": row.get(metric),
                "provisional_threshold": threshold,
                "human_review_required": True,
                "clinical_threshold": False,
            })
    return pd.DataFrame(rows)
