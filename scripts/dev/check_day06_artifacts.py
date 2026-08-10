from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day06-artifact-manifest.json"


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []

    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            failures.append(item["path"])

    if failures:
        print("DAY06 manifest failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"DAY06 manifest PASS: {len(manifest['files'])} managed files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
