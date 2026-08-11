from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("qa-validation/evidence/day21-artifact-manifest.json"),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for entry in data["artifacts"]:
        path = root / entry["path"]
        if not path.is_file():
            failures.append(f"missing:{entry['path']}")
            continue
        if sha256(path) != entry["sha256"]:
            failures.append(f"hash:{entry['path']}")
    report = {
        "status": "PASS" if not failures else "FAIL",
        "checked": len(data["artifacts"]),
        "failures": failures,
    }
    print(json.dumps(report))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
