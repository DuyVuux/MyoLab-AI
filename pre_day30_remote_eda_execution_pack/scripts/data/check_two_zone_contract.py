from __future__ import annotations

import argparse
import os
from pathlib import Path

from _common import load_yaml, write_json


def is_relative_to(a: Path, b: Path) -> bool:
    try:
        a.resolve().relative_to(b.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--output')
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    repo = Path(cfg['repo_root']).expanduser()
    data = Path(cfg['data_root']).expanduser()

    errors: list[str] = []
    warnings: list[str] = []

    if repo.resolve() == data.resolve():
        errors.append('ZONE_ROOTS_IDENTICAL')
    if is_relative_to(data, repo):
        errors.append('DATA_ROOT_INSIDE_REPO')
    if is_relative_to(repo, data):
        errors.append('REPO_ROOT_INSIDE_DATA_ROOT')
    if not repo.exists():
        warnings.append('REPO_ROOT_NOT_PRESENT_ON_THIS_MACHINE')
    if not data.exists():
        warnings.append('DATA_ROOT_NOT_BOOTSTRAPPED')

    result = {
        'schema_version': 'two-zone-contract-check.v1',
        'repo_root': str(repo),
        'data_root': str(data),
        'same_root': repo.resolve() == data.resolve(),
        'data_inside_repo': is_relative_to(data, repo),
        'repo_inside_data': is_relative_to(repo, data),
        'repo_exists': repo.exists(),
        'data_exists': data.exists(),
        'errors': errors,
        'warnings': warnings,
        'status': 'PASS' if not errors else 'FAIL',
    }
    if args.output:
        write_json(args.output, result)
    print(result)
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
