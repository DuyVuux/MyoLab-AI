#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
MAN = ROOT / "qa-validation/evidence/day35-artifact-manifest.json"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    data = json.loads(MAN.read_text(encoding="utf-8"))
    bad = []
    for row in data["artifacts"]:
        path = ROOT / row["path"]
        if not path.exists() or sha(path) != row["sha256"]:
            bad.append(row["path"])
    if bad:
        raise SystemExit("DAY35 ARTIFACT HASH FAILURE: " + ",".join(bad))
    count = len(data["artifacts"])
    print(f"DAY35 ARTIFACTS PASS {count}/{count}")


if __name__ == "__main__":
    main()
