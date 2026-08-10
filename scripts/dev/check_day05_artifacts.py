from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day05-artifact-manifest.json"

def sha(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()

def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(item["path"])
    if failures:
        print("DAY05 manifest failures:", *failures, sep="\n- ")
        return 1
    print(f"DAY05 manifest PASS: {len(manifest['files'])} managed files")
    return 0
if __name__ == "__main__": raise SystemExit(main())
