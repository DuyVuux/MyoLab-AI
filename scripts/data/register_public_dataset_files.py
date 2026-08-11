"""Register locally acquired public files without moving raw payload into the repo."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.root.exists() or not args.root.is_dir():
        raise SystemExit("public dataset root does not exist")
    files = []
    for path in sorted(p for p in args.root.rglob("*") if p.is_file()):
        files.append(
            {
                "relative_path": path.relative_to(args.root).as_posix(),
                "sha256": file_sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    payload = {
        "schema_version": "external-public-payload-ledger.v0.1",
        "dataset_id": args.dataset_id,
        "raw_payload_in_repo": False,
        "external_root_redacted": True,
        "file_count": len(files),
        "files": files,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "files": len(files)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
