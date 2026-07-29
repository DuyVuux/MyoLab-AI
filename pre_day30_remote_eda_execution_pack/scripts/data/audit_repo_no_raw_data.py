from __future__ import annotations

import argparse
from pathlib import Path

from _common import write_json

BLOCKED_EXTENSIONS = {
    '.zip', '.7z', '.rar', '.tar', '.gz', '.tgz', '.mat', '.h5', '.hdf5',
    '.dat', '.npy', '.npz', '.joblib', '.pkl', '.pickle', '.onnx'
}
BLOCKED_PATH_PARTS = {'acquired', 'extracted', 'normalized', 'cache', 'raw-signals'}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', required=True)
    ap.add_argument('--output')
    ap.add_argument('--large-file-bytes', type=int, default=50 * 1024 * 1024)
    args = ap.parse_args()

    root = Path(args.repo_root)
    findings = []
    if root.exists():
        for p in root.rglob('*'):
            if not p.is_file() or '.git' in p.parts:
                continue
            if any(part in {'.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache'} for part in p.parts):
                continue
            rel = p.relative_to(root)
            reasons = []
            if p.suffix.lower() in BLOCKED_EXTENSIONS:
                reasons.append('BLOCKED_EXTENSION')
            if any(part.lower() in BLOCKED_PATH_PARTS for part in rel.parts):
                reasons.append('BLOCKED_PATH_PATTERN')
            size = p.stat().st_size
            if size > args.large_file_bytes:
                reasons.append('LARGE_FILE')
            if reasons:
                findings.append({'path': str(rel), 'size_bytes': size, 'reasons': reasons})

    result = {
        'schema_version': 'repo-raw-scan.v1',
        'repo_root': str(root),
        'status': 'PASS' if not findings else 'FAIL',
        'findings': findings,
    }
    if args.output:
        write_json(args.output, result)
    print(result)
    return 0 if not findings else 1


if __name__ == '__main__':
    raise SystemExit(main())
