#!/usr/bin/env python3
"""Compute SHA-256 for a file or deterministic directory ledger."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def directory_ledger(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in sorted((p for p in path.rglob('*') if p.is_file()), key=lambda p: p.relative_to(path).as_posix()):
        rows.append({
            'path': item.relative_to(path).as_posix(),
            'size_bytes': item.stat().st_size,
            'sha256': sha256_file(item),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path)
    parser.add_argument('--json', action='store_true', dest='as_json')
    args = parser.parse_args()

    path = args.path.resolve()
    if not path.exists():
        raise SystemExit(f'Path does not exist: {path}')

    if path.is_file():
        result = {'path': str(path), 'size_bytes': path.stat().st_size, 'sha256': sha256_file(path)}
    else:
        ledger = directory_ledger(path)
        canonical = json.dumps(ledger, sort_keys=True, separators=(',', ':')).encode('utf-8')
        result = {
            'path': str(path),
            'file_count': len(ledger),
            'ledger_sha256': hashlib.sha256(canonical).hexdigest(),
            'files': ledger,
        }

    if args.as_json:
        print(json.dumps(result, indent=2))
    elif path.is_file():
        print(result['sha256'])
    else:
        print(result['ledger_sha256'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
