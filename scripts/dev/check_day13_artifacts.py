#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def find_pack_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "INTEGRATION_MANIFEST.json").exists():
            return parent
    raise SystemExit("DAY13 package root not found")


def main() -> int:
    pack_root = find_pack_root(Path(__file__).resolve())
    repo_root = pack_root / "repo_patch"
    manifest = json.loads((pack_root / "INTEGRATION_MANIFEST.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    for item in manifest["managed_artifacts"]:
        path = repo_root / item["path"]
        if not path.is_file():
            failures.append(f"missing: {item['path']}")
            continue
        if sha256_file(path) != item["sha256"]:
            failures.append(f"hash mismatch: {item['path']}")
    forbidden = {".npz", ".npy", ".mat", ".c3d", ".joblib", ".pkl", ".pickle", ".pt", ".pth", ".onnx"}
    for item in manifest["managed_artifacts"]:
        if Path(item["path"]).suffix.lower() in forbidden:
            failures.append(f"DAY13 introduced forbidden artifact: {item['path']}")
    print(json.dumps({"managed": len(manifest["managed_artifacts"]), "failures": failures, "status": "PASS" if not failures else "FAIL"}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
