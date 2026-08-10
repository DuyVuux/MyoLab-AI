from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day11-artifact-manifest.json"


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    forbidden_parts = {".pytest_cache", "__pycache__", ".git", ".venv", "node_modules"}
    for item in payload["managed_files"]:
        rel_path = Path(item["path"])
        if any(part in forbidden_parts for part in rel_path.parts):
            failures.append(f"forbidden-manifest-path:{item['path']}")
            continue
        path = ROOT / rel_path
        if not path.is_file():
            failures.append(f"missing:{item['path']}")
            continue
        digest = sha256_file(path)
        if digest != item["sha256"]:
            failures.append(f"hash-mismatch:{item['path']}")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print(f"DAY11 artifact manifest: PASS ({len(payload['managed_files'])} managed files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
