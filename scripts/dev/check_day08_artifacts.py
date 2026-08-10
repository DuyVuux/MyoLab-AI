from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    manifest_path = args.root / "qa-validation/evidence/day08-artifact-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for item in manifest["files"]:
        path = args.root / item["path"]
        if not path.is_file():
            failures.append(f"missing: {item['path']}")
            continue
        digest = sha256(path)
        if digest != item["sha256"]:
            failures.append(f"hash mismatch: {item['path']}")
    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1
    print(f"[PASS] verified {len(manifest['files'])} DAY08-managed artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
