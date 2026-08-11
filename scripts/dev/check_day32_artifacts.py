from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


FORBIDDEN_SUFFIXES = {
    ".pyc", ".pkl", ".pickle", ".joblib", ".onnx", ".pt", ".pth"
}
FORBIDDEN_DIRS = {"__pycache__", ".pytest_cache"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    manifest_path = root / "qa-validation/evidence/day32-artifact-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for rel, expected in manifest["artifacts"].items():
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"missing managed artifact: {rel}")
        if any(part in FORBIDDEN_DIRS for part in Path(rel).parts):
            raise SystemExit(f"forbidden managed cache path: {rel}")
        if path.suffix in FORBIDDEN_SUFFIXES:
            raise SystemExit(f"forbidden managed binary/model artifact: {rel}")
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"hash mismatch: {rel}: {actual} != {expected}")
    result = {
        "status": "PASS",
        "managed_artifacts": len(manifest["artifacts"]),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
