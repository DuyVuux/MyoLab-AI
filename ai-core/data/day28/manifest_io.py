from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
PLACEHOLDER_MARKERS = ("<REQUIRED", "PENDING", "NOT_VERIFIED")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be object: {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not lines:
        return []
    return list(csv.DictReader(lines))


def archive_hash_entries(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and HEX64.match(parts[0]):
            entries.append((parts[0].lower(), parts[1].strip().lstrip("*")))
    return entries


def find_placeholders(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            found.extend(find_placeholders(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(find_placeholders(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        upper = value.upper()
        if any(marker in upper for marker in PLACEHOLDER_MARKERS):
            found.append(path)
    return found
