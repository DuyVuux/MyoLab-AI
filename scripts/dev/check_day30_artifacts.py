from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", "--root", dest="repo_root", default=".")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    manifest_path = root / "qa-validation/evidence/day30-artifact-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    mismatches = []
    for item in manifest["artifacts"]:
        path = root / item["path"]
        if not path.exists():
            mismatches.append(f"missing: {item['path']}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"]:
            mismatches.append(f"hash mismatch: {item['path']}")
    if mismatches:
        raise SystemExit("\n".join(mismatches))
    count = len(manifest["artifacts"])
    print(f"DAY30 artifact manifest: PASS ({count}/{count})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
