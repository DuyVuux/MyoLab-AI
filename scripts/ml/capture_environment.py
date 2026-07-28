#!/usr/bin/env python3
"""Capture a non-PHI runtime fingerprint for reproducibility."""
from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import subprocess
import sys
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


def package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return 'NOT_INSTALLED'


def command_output(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True, timeout=10).strip()
    except Exception as exc:  # noqa: BLE001 - fingerprint must continue on partial systems
        return f'NOT_AVAILABLE: {type(exc).__name__}: {exc}'


def file_hash(path: Path) -> str:
    h = sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--lock-file', type=Path)
    args = parser.parse_args()

    thread_vars = [
        'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
        'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'
    ]

    fingerprint: dict[str, Any] = {
        'schema_version': '1.0',
        'status': 'CAPTURED',
        'rationale': 'Non-PHI runtime fingerprint for experiment reproducibility.',
        'evidence_ids': ['EXT-SK-PARALLEL', 'EXT-UV-LOCK'],
        'open_questions': [],
        'training_allowed': False,
        'python': {
            'version': sys.version,
            'executable': sys.executable,
            'implementation': platform.python_implementation(),
        },
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'libc': platform.libc_ver(),
        },
        'host_pseudonym': sha256(socket.gethostname().encode('utf-8')).hexdigest()[:16],
        'cpu': {
            'logical_count': os.cpu_count(),
            'lscpu': command_output(['lscpu']),
        },
        'packages': {
            name: package_version(name)
            for name in [
                'numpy', 'scipy', 'scikit-learn', 'joblib', 'threadpoolctl',
                'mlflow', 'pydantic', 'jsonschema', 'PyYAML', 'psutil', 'packaging'
            ]
        },
        'thread_environment': {name: os.environ.get(name) for name in thread_vars},
        'git': {
            'commit': command_output(['git', 'rev-parse', 'HEAD']),
            'branch': command_output(['git', 'branch', '--show-current']),
            'status_porcelain': command_output(['git', 'status', '--porcelain']),
        },
        'threadpoolctl': 'NOT_INSTALLED',
        'numpy_config': 'NOT_CAPTURED',
        'lock': None,
    }

    try:
        from threadpoolctl import threadpool_info
        fingerprint['threadpoolctl'] = threadpool_info()
    except Exception as exc:  # noqa: BLE001
        fingerprint['threadpoolctl'] = f'NOT_AVAILABLE: {exc}'

    try:
        import numpy as np
        fingerprint['numpy_config'] = command_output([sys.executable, '-c', 'import numpy as np; np.show_config()'])
    except Exception as exc:  # noqa: BLE001
        fingerprint['numpy_config'] = f'NOT_AVAILABLE: {exc}'

    if args.lock_file:
        lock = args.lock_file.resolve()
        fingerprint['lock'] = {
            'path': str(lock),
            'exists': lock.exists(),
            'sha256': file_hash(lock) if lock.exists() else None,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fingerprint, indent=2), encoding='utf-8')
    print(args.output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
