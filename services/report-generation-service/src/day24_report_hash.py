from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_report_bytes(payload: dict[str, Any]) -> bytes:
    cleaned = {key: value for key, value in payload.items() if key != "reportHashSha256"}
    return json.dumps(
        cleaned,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def compute_report_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_report_bytes(payload)).hexdigest()


def verify_report_hash(payload: dict[str, Any]) -> bool:
    expected = payload.get("reportHashSha256")
    return isinstance(expected, str) and expected == compute_report_hash(payload)
