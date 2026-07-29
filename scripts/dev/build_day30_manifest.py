#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEARCH_ROOTS = (
    ROOT / "ai-core",
    ROOT / "data-platform",
    ROOT / "docs",
    ROOT / "environment",
    ROOT / "packages",
    ROOT / "qa-validation",
    ROOT / "scripts",
)


def _digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assets(excluded: set[Path]) -> list[Path]:
    return sorted(
        path
        for root in SEARCH_ROOTS
        for path in root.rglob("*")
        if path.is_file()
        and path not in excluded
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
        and path.name not in {"input-working-tree.patch", "input-git-commit.txt"}
        and "day30" in path.relative_to(ROOT).as_posix().lower()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="qa-validation/evidence/day30/day30-final-manifest.json",
    )
    parser.add_argument(
        "--ledger",
        default="qa-validation/evidence/day30/day30-source-hash-ledger.json",
    )
    args = parser.parse_args()
    manifest_path = Path(args.manifest).resolve()
    ledger_path = Path(args.ledger).resolve()
    artifacts = [
        {
            "path": str(path.relative_to(ROOT)),
            "sha256": _digest(path),
            "bytes": path.stat().st_size,
        }
        for path in _assets({manifest_path, ledger_path})
    ]
    manifest_payload = {
        "schema_version": "day30-final-manifest.v1",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "raw_signal_included": False,
        "model_artifact_included": False,
        "training_executed": False,
        "pooled_training_executed": False,
        "test_signal_rows_read": 0,
    }
    manifest_id = sha256(
        json.dumps(
            manifest_payload, ensure_ascii=False, sort_keys=True
        ).encode("utf-8")
    ).hexdigest()
    manifest_payload["manifest_sha256"] = manifest_id
    ledger_payload = {
        "schema_version": "day30-source-hash-ledger.v1",
        "manifest_sha256": manifest_id,
        "entries": artifacts,
    }
    for path, document in (
        (manifest_path, manifest_payload),
        (ledger_path, ledger_payload),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(manifest_payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
