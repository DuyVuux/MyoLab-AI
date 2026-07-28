from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_hash_ledger(paths: Iterable[Path], root: Path) -> dict[str, object]:
    rows = []
    for path in sorted(paths, key=lambda item: str(item)):
        if not path.is_file():
            continue
        rows.append({
            "relativePath": str(path.relative_to(root)).replace("\\", "/"),
            "sizeBytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schemaVersion": "hash-ledger.v1",
        "entries": rows,
        "ledgerSha256": hashlib.sha256(canonical).hexdigest(),
    }
