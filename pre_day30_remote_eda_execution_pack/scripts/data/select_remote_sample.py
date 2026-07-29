from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

from _common import load_yaml, write_json


def stable_key(record: dict) -> tuple:
    return tuple(str(record.get(k) or '') for k in ('subject_id', 'day_id', 'source_label', 'repetition_id', 'record_id'))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding='utf-8'))
    cfg = load_yaml(args.config)
    allowed = set(cfg['partition_policy']['allowed_signal_partitions'])
    forbidden = set(cfg['partition_policy']['forbidden_signal_partitions'])
    budget_n = int(cfg['budgets']['max_sample_records'])
    budget_b = int(cfg['budgets']['max_sample_total_bytes'])
    seed = int(cfg['sampling_policy']['seed'])

    candidates = []
    blockers = []
    for r in catalog.get('records', []):
        partition = str(r.get('partition') or '').lower()
        if partition in forbidden:
            continue
        if partition not in allowed:
            blockers.append(f"UNKNOWN_OR_FORBIDDEN_PARTITION:{r.get('record_id')}:{partition}")
            continue
        if not r.get('official_source'):
            blockers.append(f"NON_OFFICIAL_SOURCE:{r.get('record_id')}")
            continue
        candidates.append(r)

    rng = random.Random(seed)
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in candidates:
        groups[(r.get('subject_id'), r.get('day_id'), r.get('source_label'))].append(r)
    for rows in groups.values():
        rows.sort(key=stable_key)
        rng.shuffle(rows)

    selected = []
    total = 0
    group_keys = sorted(groups, key=lambda x: tuple('' if v is None else str(v) for v in x))
    progress = True
    idx = 0
    while progress and len(selected) < budget_n:
        progress = False
        for key in group_keys:
            rows = groups[key]
            if idx >= len(rows):
                continue
            r = rows[idx]
            size = int(r.get('size_bytes') or 0)
            if total + size > budget_b and selected:
                continue
            selected.append(r)
            total += size
            progress = True
            if len(selected) >= budget_n:
                break
        idx += 1

    payload = {
        'schema_version': 'remote-sample-plan.v1',
        'mode': cfg['execution_mode'],
        'seed': seed,
        'budget_records': budget_n,
        'budget_bytes': budget_b,
        'selected_record_count': len(selected),
        'selected_known_bytes': total,
        'test_signal_records_selected': sum(str(r.get('partition')).lower() in forbidden for r in selected),
        'blockers': blockers,
        'records': selected,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
    payload['plan_sha256'] = hashlib.sha256(canonical).hexdigest()
    write_json(args.output, payload)
    print({'selected': len(selected), 'known_bytes': total, 'blockers': len(blockers)})
    return 1 if blockers or payload['test_signal_records_selected'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
