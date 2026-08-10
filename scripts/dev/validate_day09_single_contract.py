from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "data-platform/contracts/noraxon/mr4-single-csv.schema.yaml"
FIXTURES = ROOT / "qa-validation/test-data/golden/noraxon/single_csv"


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for *path*."""
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def read_contract() -> dict[str, Any]:
    """Load the DAY09 YAML contract."""
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def inspect_csv(path: Path) -> dict[str, Any]:
    """Perform a minimal contract-only inspection of a synthetic single CSV."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < 4:
        return {"ok": False, "reason": "TOO_SHORT"}

    if lines[2].strip() != "":
        return {"ok": False, "reason": "MISSING_BLANK_SEPARATOR"}

    metadata_header = next(csv.reader([lines[0]]))
    metadata_values = next(csv.reader([lines[1]]))
    data_header = next(csv.reader([lines[3]]))

    if len(metadata_header) != len(metadata_values):
        return {"ok": False, "reason": "METADATA_ARITY_MISMATCH"}

    if "time" not in data_header:
        return {"ok": False, "reason": "TIME_COLUMN_MISSING"}

    return {
        "ok": True,
        "metadata": dict(zip(metadata_header, metadata_values, strict=True)),
        "columns": data_header,
    }


def main() -> int:
    """Run deterministic contract checks without implementing the DAY16 parser."""
    contract = read_contract()
    issues: list[str] = []

    if contract["layout"]["row_3"] != "blank_separator":
        issues.append("contract_row3")

    manifest_path = FIXTURES / "fixture-manifest.json"
    fixture_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, entry in fixture_manifest.items():
        if sha256_file(FIXTURES / name) != entry["sha256"]:
            issues.append(f"hash:{name}")

    if not inspect_csv(FIXTURES / "valid_minimal.csv")["ok"]:
        issues.append("valid_minimal")

    if not inspect_csv(FIXTURES / "valid_unknown_fields.csv")["ok"]:
        issues.append("valid_unknown")

    if inspect_csv(FIXTURES / "invalid_missing_blank_separator.csv")["ok"]:
        issues.append("negative_not_rejected")

    result = {
        "day": "DAY09",
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
