from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day10-artifact-manifest.json"


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for *path*."""
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def main() -> int:
    """Validate only DAY10-managed artifacts against the frozen manifest."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    issues: list[str] = []

    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        if not path.is_file():
            issues.append(f"missing:{entry['path']}")
            continue

        if sha256_file(path) != entry["sha256"]:
            issues.append(f"hash:{entry['path']}")

    result = {
        "managed_files": len(manifest["files"]),
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
