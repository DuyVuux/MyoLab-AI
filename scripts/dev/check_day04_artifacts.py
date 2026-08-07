from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day04-artifact-manifest.json"


def sha256(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("scope") != "DAY04_MANAGED_ARTIFACTS_ONLY":
        raise SystemExit("Invalid manifest scope")

    failures: list[str] = []
    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            failures.append(f"missing: {item['path']}")
            continue
        if item.get("sha256") and sha256(path) != item["sha256"]:
            failures.append(f"hash mismatch: {item['path']}")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print(f"[PASS] {len(manifest['files'])} DAY04-managed artifacts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
