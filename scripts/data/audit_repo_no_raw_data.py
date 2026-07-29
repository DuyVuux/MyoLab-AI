"""Scan the repository for raw data, archives, or model artifacts.

Returns PASS if no blocked files are found, FAIL otherwise.
Excludes virtual environments, node_modules, and other common
development directories that may contain blocked extensions innocuously.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from _common import write_json

BLOCKED_EXTENSIONS = {
    '.zip', '.7z', '.rar', '.tar', '.gz', '.tgz', '.mat', '.h5', '.hdf5',
    '.dat', '.npy', '.npz', '.joblib', '.pkl', '.pickle', '.onnx',
}
BLOCKED_PATH_PARTS = {
    'acquired', 'extracted', 'normalized', 'cache', 'raw-signals',
}
# Directories to skip entirely — these are dev/build artifacts, not data
SKIP_DIRS = {
    '.git', '.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache',
    'node_modules', '.next', 'dist', 'build',
}
# Virtual environment prefixes
VENV_PREFIXES = ('.venv', 'venv', '.env-', 'env-')

# Small test fixtures are expected and should not trigger FAIL
FIXTURE_EXEMPTION_BYTES = 1_048_576  # 1 MiB
FIXTURE_PATH_PARTS = {'fixtures', 'test-data', 'test_data'}


def _should_skip_dir(name: str) -> bool:
    """Check if a directory name should be skipped."""
    if name in SKIP_DIRS:
        return True
    for prefix in VENV_PREFIXES:
        if name.startswith(prefix):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', required=True)
    ap.add_argument('--output')
    ap.add_argument(
        '--large-file-bytes', type=int, default=50 * 1024 * 1024,
    )
    args = ap.parse_args()

    root = Path(args.repo_root)
    findings = []
    if root.exists():
        for p in root.rglob('*'):
            if not p.is_file():
                continue
            # Skip excluded directories
            if any(_should_skip_dir(part) for part in p.parts):
                continue
            rel = p.relative_to(root)
            reasons = []

            is_fixture = any(
                part.lower() in FIXTURE_PATH_PARTS for part in rel.parts
            )
            size = p.stat().st_size

            if p.suffix.lower() in BLOCKED_EXTENSIONS:
                # Small test fixtures with blocked extensions are OK
                if is_fixture and size <= FIXTURE_EXEMPTION_BYTES:
                    continue
                reasons.append('BLOCKED_EXTENSION')
            if any(
                part.lower() in BLOCKED_PATH_PARTS for part in rel.parts
            ):
                reasons.append('BLOCKED_PATH_PATTERN')
            if size > args.large_file_bytes:
                reasons.append('LARGE_FILE')
            if reasons:
                findings.append({
                    'path': str(rel),
                    'size_bytes': size,
                    'reasons': reasons,
                })

    result = {
        'schema_version': 'repo-raw-scan.v1',
        'repo_root': str(root),
        'status': 'PASS' if not findings else 'FAIL',
        'findings_count': len(findings),
        'findings': findings,
    }
    if args.output:
        write_json(args.output, result)
    print(result['status'], f'({len(findings)} findings)')
    return 0 if not findings else 1


if __name__ == '__main__':
    raise SystemExit(main())
