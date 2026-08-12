from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
MANIFEST = ROOT / "qa-validation/evidence/day40-artifact-manifest.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    for item in manifest["artifacts"]:
        path = ROOT / item["path"]
        if not path.exists():
            failures.append(f"missing:{item['path']}")
            continue
        actual = digest(path)
        if actual != item["sha256"]:
            failures.append(f"hash:{item['path']}")
    if failures:
        raise SystemExit("DAY40 ARTIFACTS FAIL " + ",".join(failures))
    print(f"DAY40 ARTIFACTS PASS {len(manifest['artifacts'])}/{len(manifest['artifacts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
