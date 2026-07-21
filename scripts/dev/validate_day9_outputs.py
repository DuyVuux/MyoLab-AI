#!/usr/bin/env python3
"""Validate Day 9 schemas, deterministic hashes và safety invariants."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def load_json(relative: str) -> dict[str, Any]:
    payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"JSON root phải là object: {relative}")
    return payload


def main() -> int:
    row_schema = load_json(
        "packages/common-schemas/json/spectral-window-row.schema.json"
    )
    result_schema = load_json(
        "packages/common-schemas/json/spectral-estimation-result.schema.json"
    )
    verification_schema = load_json(
        "packages/common-schemas/json/spectral-verification.schema.json"
    )

    for schema in (row_schema, result_schema, verification_schema):
        Draft202012Validator.check_schema(schema)

    first = load_json("qa-validation/evidence/day9-spectral-estimation.json")
    second = load_json(
        "qa-validation/evidence/day9-spectral-estimation-rerun.json"
    )
    blocked = load_json("qa-validation/evidence/day9-spectral-blocked.json")
    verification = load_json(
        "qa-validation/evidence/day9-spectral-verification.json"
    )

    result_validator = Draft202012Validator(result_schema)
    result_validator.validate(first)
    result_validator.validate(second)
    result_validator.validate(blocked)
    Draft202012Validator(verification_schema).validate(verification)

    row_validator = Draft202012Validator(row_schema)
    for row in first.get("rows", []):
        row_validator.validate(row)

    first_hash = first.get("result_hash_sha256")
    second_hash = second.get("result_hash_sha256")
    if first_hash != second_hash:
        raise SystemExit(
            "Spectral result hash không deterministic: "
            f"{first_hash} != {second_hash}"
        )

    if blocked.get("status") != "blocked" or blocked.get("rows"):
        raise SystemExit(
            "Fixture QC fail phải block spectral stage và không tạo row"
        )

    axis = first.get("frequency_axis") or {}
    if (
        axis.get("bin_count") != 381
        or axis.get("lower_hz") != 20.0
        or axis.get("upper_hz") != 400.0
        or axis.get("bin_spacing_hz") != 1.0
    ):
        raise SystemExit("Frequency axis không đúng 20–400 Hz / 381 bins / 1 Hz")

    config = first.get("config") or {}
    if config.get("mdf_mnf_computed") is not False:
        raise SystemExit("Day 9 không được tính MDF/MNF")

    rows = first.get("rows", [])
    if len(rows) != 119:
        raise SystemExit(f"Golden phải có 119 rows; nhận {len(rows)}")

    qa_rows = 0
    for index, row in enumerate(rows):
        if row.get("status") != "computed":
            raise SystemExit(f"Golden row {index} không computed")
        spectral = row.get("spectral") or {}
        psd = spectral.get("psd") or {}
        values = psd.get("values") or []
        if len(values) != 381:
            raise SystemExit(
                f"PSD vector row {index} không khớp 381-bin shared axis"
            )
        band_power = (spectral.get("band_power") or {}).get("value")
        full_power = (spectral.get("full_power") or {}).get("value")
        if not isinstance(band_power, (int, float)) or not isinstance(
            full_power, (int, float)
        ):
            raise SystemExit(f"Golden row {index} thiếu power values")
        if band_power > full_power + max(1e-9, abs(full_power) * 1e-9):
            raise SystemExit(f"Golden row {index}: band power > full power")
        qa_rows += bool(spectral.get("qa_flags"))

    serialized = json.dumps(first, ensure_ascii=False)
    for forbidden in (
        "samples_uV",
        "raw_samples",
        "fatigue_status",
        "fatigue_resistance_score",
    ):
        if forbidden in serialized:
            raise SystemExit(f"Forbidden field trong spectral output: {forbidden}")

    print(f"JSON Schema PASS; deterministic spectral hash={first_hash}")
    print(f"Spectral invariants PASS; QA-flagged rows={qa_rows}/119")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
