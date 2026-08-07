from __future__ import annotations

import json
import sys
from pathlib import Path

from day03_time_motion_utils import sha256_file


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day03-artifact-manifest.json"

FORBIDDEN_DAY03_SUFFIXES = {
    ".npz",
    ".npy",
    ".mat",
    ".c3d",
    ".joblib",
    ".pkl",
    ".pickle",
    ".pt",
    ".pth",
    ".onnx",
}


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []

    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            failures.append(f"Missing managed DAY03 artifact: {item['path']}")
            continue
        actual_hash = sha256_file(path)
        if actual_hash != item["sha256"]:
            failures.append(f"Hash mismatch: {item['path']}")
        if path.suffix.lower() in FORBIDDEN_DAY03_SUFFIXES:
            failures.append(f"DAY03 introduced forbidden binary/model/data artifact: {item['path']}")

    if failures:
        print("\n".join(failures))
        return 1

    print(f"Managed DAY03 artifacts verified: {len(manifest['files'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
