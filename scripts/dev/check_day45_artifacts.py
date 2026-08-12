#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day45-artifact-manifest.json"


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for item in payload["artifacts"]:
        path = ROOT / item["path"]
        if not path.is_file():
            failures.append(f"MISSING:{item['path']}")
            continue
        digest = sha256_file(path)
        if digest != item["sha256"]:
            failures.append(f"HASH_MISMATCH:{item['path']}")
    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": "PASS",
                "verified": len(payload["artifacts"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
