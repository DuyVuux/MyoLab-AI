from __future__ import annotations

import hashlib
import json
from typing import Any

PLACEHOLDER_MARKERS = ("<REQUIRED", "TO_VERIFY", "NOT_VERIFIED")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def find_placeholders(value: Any, path: str = "$", *, include_none: bool = True) -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            findings.extend(find_placeholders(child, f"{path}.{key}", include_none=include_none))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_placeholders(child, f"{path}[{index}]", include_none=include_none))
    elif isinstance(value, str):
        upper = value.upper()
        if any(marker in upper for marker in PLACEHOLDER_MARKERS):
            findings.append(path)
    elif value is None and include_none:
        findings.append(path)
    return findings


def is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(char in "0123456789abcdefABCDEF" for char in value)
