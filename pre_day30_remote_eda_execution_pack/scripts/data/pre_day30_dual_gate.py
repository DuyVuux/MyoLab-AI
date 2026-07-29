from __future__ import annotations

import argparse
from pathlib import Path

from _common import load_yaml, write_json

REQUIRED_COMMON = [
    'real_eda_executed',
    'test_set_opened',
    'test_signal_rows_read',
]


def evaluate_dataset(name: str, cfg: dict) -> tuple[dict, list[str]]:
    blockers = []
    p = Path(cfg['readiness_file'])
    if not p.exists():
        return {'status': 'MISSING', 'path': str(p)}, [f'{name.upper()}_READINESS_FILE_MISSING']
    data = load_yaml(p)
    status = data.get('status') or data.get('decision') or data.get('readiness')
    if status != cfg['expected_go_state']:
        blockers.append(f'{name.upper()}_NOT_GO:{status}')
    if data.get('real_eda_executed') is not True:
        blockers.append(f'{name.upper()}_REAL_EDA_NOT_CONFIRMED')
    if data.get('test_set_opened') is not False:
        blockers.append(f'{name.upper()}_TEST_SET_NOT_CONFIRMED_CLOSED')
    if int(data.get('test_signal_rows_read', -1)) != 0:
        blockers.append(f'{name.upper()}_TEST_SIGNAL_ROWS_NONZERO_OR_UNKNOWN')
    if name == 'grabmyo' and data.get('cross_day_audit_completed') is not True:
        blockers.append('GRABMYO_CROSS_DAY_AUDIT_NOT_CONFIRMED')
    return {'status': status, 'path': str(p), 'content': data}, blockers


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    all_blockers = []
    datasets = {}
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
        'decision': 'GO_FOR_DAY30_HARMONIZATION' if go else 'BLOCKED_WITH_EVIDENCE',
        'day30_full_execution_allowed': go,
        'training_allowed': False,
        'pooled_training_allowed': False,
        'datasets': datasets,
        'blockers': all_blockers,
    }
    write_json(args.output, output)
    print(output['decision'], all_blockers)
    return 0 if go else 1


if __name__ == '__main__':
    raise SystemExit(main())
