from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    manifest_path = root / "qa-validation/evidence/day34-artifact-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checked = 0
    for item in manifest["artifacts"]:
        path = root / item["path"]
        if not path.is_file():
            raise SystemExit(f"MISSING {item['path']}")
        if sha256(path) != item["sha256"]:
            raise SystemExit(f"HASH_MISMATCH {item['path']}")
        checked += 1
    print(f"DAY34 ARTIFACTS PASS {checked}/{checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
