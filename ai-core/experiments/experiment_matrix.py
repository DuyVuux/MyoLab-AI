from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = {
    "id", "task", "hypothesis", "feature_group", "model", "regime",
    "personalization", "fatigue_architecture", "primary_metric", "result_status"
}


def load_matrix(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data.get("trainingAllowed") is not False:
        raise ValueError("Day 26 matrix must block training")
    if data.get("outer_test_opened") is not False:
        raise ValueError("Outer test must remain sealed")
    seen: set[str] = set()
    for row in data.get("experiments", []):
        missing = REQUIRED_FIELDS - set(row)
        if missing:
            raise ValueError(f"Experiment missing fields: {sorted(missing)}")
        if row["id"] in seen:
            raise ValueError(f"Duplicate experiment id: {row['id']}")
        seen.add(row["id"])
        if row["result_status"] != "NOT_RUN":
            raise ValueError(f"Day 26 result must be NOT_RUN: {row['id']}")
    return data
