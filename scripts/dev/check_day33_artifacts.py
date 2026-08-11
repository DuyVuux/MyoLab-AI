from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    manifest_path = root / "qa-validation/evidence/day33-artifact-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for item in manifest["artifacts"]:
        path = root / item["path"]
        if not path.exists():
            failures.append(f"MISSING:{item['path']}")
            continue
        actual = sha256_file(path)
        if actual != item["sha256"]:
            failures.append(f"HASH_MISMATCH:{item['path']}")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print(f"DAY33 ARTIFACTS PASS {len(manifest['artifacts'])}/{len(manifest['artifacts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
