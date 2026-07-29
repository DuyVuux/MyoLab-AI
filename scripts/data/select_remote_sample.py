"""Select a bounded stratified sample from a remote catalog.

Enforces partition policy (test is ALWAYS forbidden),
validates gesture/day coverage, and embeds catalog hash
for reproducibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from _common import load_yaml, write_json


def stable_key(record: dict) -> tuple:
    return tuple(
        str(record.get(k) or '')
        for k in (
            'subject_id', 'day_id', 'source_label',
            'repetition_id', 'record_id',
        )
    )


def compute_coverage(selected: list[dict], cfg: dict) -> dict:
    """Compute coverage statistics and warnings for the selected sample."""
    subjects = set()
    days = set()
    labels = set()
    for r in selected:
        if r.get('subject_id'):
            subjects.add(r['subject_id'])
        if r.get('day_id'):
            days.add(r['day_id'])
        if r.get('source_label'):
            labels.add(r['source_label'])

    warnings = []
    stratify = cfg.get('sampling_policy', {}).get('stratify_fields', [])
    if 'source_label' in stratify and len(labels) < 2:
        warnings.append(
            f'LOW_LABEL_COVERAGE: only {len(labels)} unique label(s) selected'
        )
    if cfg.get('sampling_policy', {}).get('require_all_days_for_grabmyo'):
        if len(days) < 3 and any('grab' in str(r.get('record_id', '')).lower() for r in selected):
            warnings.append(
                f'INCOMPLETE_DAY_COVERAGE: only {len(days)} day(s) for GRABMyo'
            )

    return {
        'unique_subjects': len(subjects),
        'unique_days': len(days),
        'unique_labels': len(labels),
        'subjects': sorted(subjects),
        'days': sorted(days),
        'labels': sorted(labels),
        'warnings': warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description='Select bounded stratified sample from remote catalog',
    )
    ap.add_argument('--catalog', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    catalog_text = Path(args.catalog).read_text(encoding='utf-8')
    catalog = json.loads(catalog_text)
    catalog_hash = hashlib.sha256(catalog_text.encode('utf-8')).hexdigest()

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
            blockers.append(
                f"UNKNOWN_OR_FORBIDDEN_PARTITION:"
                f"{r.get('record_id')}:{partition}"
            )
            continue
        if not r.get('official_source'):
            blockers.append(f"NON_OFFICIAL_SOURCE:{r.get('record_id')}")
            continue
        candidates.append(r)

    rng = random.Random(seed)
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in candidates:
        groups[(
            r.get('subject_id'), r.get('day_id'), r.get('source_label'),
        )].append(r)
    for rows in groups.values():
        rows.sort(key=stable_key)
        rng.shuffle(rows)

    selected: list[dict] = []
    total = 0
    group_keys = sorted(
        groups,
        key=lambda x: tuple('' if v is None else str(v) for v in x),
    )
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

    coverage = compute_coverage(selected, cfg)

    payload = {
        'schema_version': 'remote-sample-plan.v1',
        'mode': cfg['execution_mode'],
        'seed': seed,
        'budget_records': budget_n,
        'budget_bytes': budget_b,
        'catalog_sha256': catalog_hash,
        'selected_record_count': len(selected),
        'selected_known_bytes': total,
        'test_signal_records_selected': sum(
            str(r.get('partition')).lower() in forbidden for r in selected
        ),
        'coverage': coverage,
        'blockers': blockers,
        'records': selected,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    canonical = json.dumps(
        payload, sort_keys=True, ensure_ascii=False,
    ).encode('utf-8')
    payload['plan_sha256'] = hashlib.sha256(canonical).hexdigest()
    write_json(args.output, payload)
    print(json.dumps({
        'selected': len(selected),
        'known_bytes': total,
        'blockers': len(blockers),
        'coverage_warnings': coverage.get('warnings', []),
    }, indent=2))
    return 1 if blockers or payload['test_signal_records_selected'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
