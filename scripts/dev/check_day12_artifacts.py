from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day12-artifact-manifest.json"


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"missing: {item['path']}")
            continue
        digest = sha256_file(path)
        if digest != item["sha256"]:
            errors.append(f"hash mismatch: {item['path']}")
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    print(f"[PASS] DAY12 managed artifacts: {len(manifest['files'])}/{len(manifest['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
