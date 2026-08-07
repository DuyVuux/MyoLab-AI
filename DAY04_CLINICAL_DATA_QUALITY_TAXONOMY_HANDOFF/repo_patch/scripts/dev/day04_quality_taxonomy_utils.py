from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


VALID_QUALITY = {"PASS", "WARNING", "FAIL"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj)
    if not isinstance(data, dict):
        raise TypeError(f"Expected mapping in {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    if not isinstance(data, dict):
        raise TypeError(f"Expected object in {path}")
    return data


def validate_reason_record(record: dict[str, Any], schema: dict[str, Any]) -> None:
    jsonschema.Draft202012Validator(schema).validate(record)


def taxonomy_by_code(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = taxonomy.get("reason_codes", [])
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        code = item["code"]
        if code in result:
            raise ValueError(f"Duplicate reason code: {code}")
        result[code] = item
    return result


def aggregate_signal_quality(
    reasons: list[dict[str, Any]],
    taxonomy: dict[str, Any],
) -> str:
    """Aggregate only typed, policy-resolved reasons.

    POLICY_DEPENDENT taxonomy items do not automatically become WARNING/FAIL.
    The supplied reason record's signal_quality is accepted only for a concrete
    reason instance. Physiology-only reasons must have quality_effect NONE and
    cannot downgrade signal quality by themselves.
    """
    by_code = taxonomy_by_code(taxonomy)
    qualities: list[str] = []

    for reason in reasons:
        code = reason["reason_code"]
        if code not in by_code:
            raise ValueError(f"Unknown reason code: {code}")

        definition = by_code[code]
        quality = reason["signal_quality"]
        if quality not in VALID_QUALITY:
            raise ValueError(f"Invalid signal quality: {quality}")

        if definition["quality_effect"] == "NONE" and quality != "PASS":
            raise ValueError(
                f"Reason {code} has quality_effect NONE and cannot downgrade quality"
            )
        qualities.append(quality)

    if "FAIL" in qualities:
        return "FAIL"
    if "WARNING" in qualities:
        return "WARNING"
    return "PASS"
