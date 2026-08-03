from __future__ import annotations

import csv
import json
from pathlib import Path


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["outer_fold"] = int(row["outer_fold"])
    return rows


def write_json(path, obj):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows, fieldnames=None):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output.write_text("", encoding="utf-8")
        return
    normalized = []
    for row in rows:
        normalized.append({
            key: json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (list, dict)) else value
            for key, value in row.items()
        })
    if fieldnames is None:
        fieldnames = []
        for row in normalized:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(normalized)
