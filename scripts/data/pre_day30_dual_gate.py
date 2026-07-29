"""Pre-Day30 Dual Gate — evaluate readiness of both Mendeley and GRABMyo.

Validates readiness files against expected state, checks safety flags,
validates output against JSON Schema, and includes provenance hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from _common import load_yaml, write_json


REQUIRED_COMMON = [
    'real_eda_executed',
    'test_set_opened',
    'test_signal_rows_read',
]


def hash_file(path: Path) -> str | None:
    """SHA-256 hash of a file for provenance tracking."""
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_dataset(
    name: str, cfg: dict,
) -> tuple[dict, list[str]]:
    blockers: list[str] = []
    p = Path(cfg['readiness_file'])
    if not p.exists():
        return (
            {'status': 'MISSING', 'path': str(p), 'file_hash': None},
            [f'{name.upper()}_READINESS_FILE_MISSING'],
        )

    data = load_yaml(p)
    file_hash = hash_file(p)
    status = (
        data.get('status')
        or data.get('decision')
        or data.get('readiness')
    )

    if status != cfg['expected_go_state']:
        blockers.append(f'{name.upper()}_NOT_GO:{status}')
    if data.get('real_eda_executed') is not True:
        blockers.append(f'{name.upper()}_REAL_EDA_NOT_CONFIRMED')
    if data.get('test_set_opened') is not False:
        blockers.append(f'{name.upper()}_TEST_SET_NOT_CONFIRMED_CLOSED')
    if int(data.get('test_signal_rows_read', -1)) != 0:
        blockers.append(
            f'{name.upper()}_TEST_SIGNAL_ROWS_NONZERO_OR_UNKNOWN'
        )
    if name == 'grabmyo' and data.get('cross_day_audit_completed') is not True:
        blockers.append('GRABMYO_CROSS_DAY_AUDIT_NOT_CONFIRMED')

    return (
        {
            'status': status,
            'path': str(p),
            'file_hash': file_hash,
            'content': data,
        },
        blockers,
    )


def validate_output_schema(output: dict) -> list[str]:
    """Basic structural validation against the dual-gate schema contract."""
    issues: list[str] = []
    required = [
        'schema_version', 'decision', 'day30_full_execution_allowed',
        'training_allowed', 'datasets', 'blockers',
    ]
    for key in required:
        if key not in output:
            issues.append(f'MISSING_REQUIRED_FIELD:{key}')
    if output.get('schema_version') != 'pre-day30-dual-gate.v1':
        issues.append('INVALID_SCHEMA_VERSION')
    if output.get('decision') not in {
        'GO_FOR_DAY30_HARMONIZATION', 'BLOCKED_WITH_EVIDENCE',
    }:
        issues.append(f"INVALID_DECISION:{output.get('decision')}")
    if output.get('training_allowed') is not False:
        issues.append('TRAINING_ALLOWED_MUST_BE_FALSE')
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(
        description='Pre-Day30 Dual Gate — evaluate both datasets',
    )
    ap.add_argument('--config', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--operator', default='auto')
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    all_blockers: list[str] = []
    datasets: dict = {}
    for name in ('mendeley', 'grabmyo'):
        result, blockers = evaluate_dataset(name, cfg['datasets'][name])
        datasets[name] = result
        all_blockers.extend(blockers)

    safety = cfg.get('safety', {})
    if safety.get('training_allowed') is not False:
        all_blockers.append('TRAINING_FLAG_NOT_FALSE')
    if safety.get('test_signal_access_allowed') is not False:
        all_blockers.append('TEST_SIGNAL_ACCESS_FLAG_NOT_FALSE')

    go = not all_blockers
    output = {
        'schema_version': 'pre-day30-dual-gate.v1',
        'decision': (
            'GO_FOR_DAY30_HARMONIZATION' if go
            else 'BLOCKED_WITH_EVIDENCE'
        ),
        'day30_full_execution_allowed': go,
        'training_allowed': False,
        'pooled_training_allowed': False,
        'datasets': datasets,
        'blockers': all_blockers,
        'operator': args.operator,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }

    # Self-validate output
    schema_issues = validate_output_schema(output)
    if schema_issues:
        output['schema_validation_issues'] = schema_issues

    write_json(args.output, output)
    print(output['decision'], all_blockers)
    return 0 if go else 1


if __name__ == '__main__':
    raise SystemExit(main())
