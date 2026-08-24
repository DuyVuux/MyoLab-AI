from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

TRAIN_ROLES = {'train', 'training', 'development_train', 'dev_train', 'benchmark_development_train'}
DEV_ROLES = {'dev', 'development', 'validation', 'val', 'development_validation', 'benchmark_development'}
CAL_ROLES = {'calibration', 'calibrate', 'cal'}
EVAL_ROLES = {'eval', 'evaluation', 'test', 'locked', 'locked_eval', 'locked_evaluation', 'benchmark_locked'}

COLUMN_CANDIDATES = {
    'dataset': ('dataset', 'dataset_id', 'dataset_name', 'source_dataset'),
    'subject': ('subject', 'subject_id', 'participant', 'participant_id'),
    'session': ('session', 'session_id', 'visit', 'day', 'recording_session'),
    'split': ('split', 'partition', 'fold_role', 'dataset_split'),
    'source_window': ('source_window_id', 'source_window', 'parent_window_id', 'origin_window_id', 'window_identity'),
    'example': ('example_id', 'record_id', 'research_example_id', 'window_id'),
}

FORBIDDEN_FEATURE_IDENTIFIERS = {
    'dataset', 'dataset_name', 'dataset_id', 'subject', 'subject_id', 'participant_id',
    'source_file', 'source_filename', 'source_path', 'file_path', 'filepath', 'session', 'session_id',
    'transform_filename', 'generator_identity', 'label', 'target', 'class_label',
}

TARGET_SUBDIRS = ['ai-core', 'qa-validation', 'docs', 'configs', 'scripts']
EXCLUDE_DIRS = {'.venv', 'node_modules', '.git', '.agents', '.pytest_cache', '__pycache__', 'phase6r-research-ml-continuation', '.next', 'json', 'dist', 'build'}

@dataclass(frozen=True)
class Finding:
    check: str
    status: str
    reason: str
    details: dict[str, Any]

def _norm_key(value: Any) -> str:
    return '' if value is None else str(value).strip()

def _find_column(keys: Iterable[str], role: str) -> str | None:
    low = {str(k).strip().lower(): str(k) for k in keys}
    for candidate in COLUMN_CANDIDATES[role]:
        if candidate in low:
            return low[candidate]
    return None

def _split_role(value: Any) -> str | None:
    raw = _norm_key(value).lower().replace('-', '_').replace(' ', '_')
    if raw in TRAIN_ROLES or raw.startswith('train'):
        return 'TRAIN'
    if raw in DEV_ROLES or raw.startswith('validation') or raw.startswith('development'):
        return 'DEVELOPMENT'
    if raw in CAL_ROLES or raw.startswith('calibr'):
        return 'CALIBRATION'
    if raw in EVAL_ROLES or 'locked' in raw or raw.startswith('test') or raw.startswith('eval'):
        return 'EVALUATION'
    return None

def _load_tabular(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == '.csv':
        with path.open('r', encoding='utf-8-sig', errors='replace', newline='') as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix == '.jsonl':
        rows = []
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            line = line.strip()
            if line:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
        return rows
    if suffix == '.json':
        obj = json.loads(path.read_text(encoding='utf-8', errors='replace'))
        if isinstance(obj, list):
            return [x for x in obj if isinstance(x, dict)]
        if isinstance(obj, dict):
            for key in ('records', 'rows', 'examples', 'items', 'splits'):
                if isinstance(obj.get(key), list):
                    return [x for x in obj[key] if isinstance(x, dict)]
        return []
    if suffix == '.parquet':
        try:
            import pandas as pd
            return pd.read_parquet(path).to_dict(orient='records')
        except Exception:
            return []
    return []

def _get_target_files(root: Path) -> list[Path]:
    files = []
    subdirs = [root / d for d in TARGET_SUBDIRS if (root / d).exists()]
    if not subdirs:
        subdirs = [root]
    for subdir in subdirs:
        for p in subdir.rglob('*'):
            if any(part in EXCLUDE_DIRS for part in p.parts):
                continue
            if p.is_file():
                files.append(p)
    return files

def discover_split_records(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    sources: list[str] = []
    candidates = []
    for p in _get_target_files(root):
        low = p.name.lower()
        if p.suffix.lower() not in {'.csv', '.json', '.jsonl', '.parquet'}:
            continue
        if any(token in low for token in ('split', 'research-example', 'research_example', 'public-feature', 'public_feature')):
            candidates.append(p)
    for path in sorted(candidates):
        try:
            rows = _load_tabular(path)
        except Exception:
            continue
        if not rows:
            continue
        keys = set().union(*(row.keys() for row in rows[:20]))
        split_col = _find_column(keys, 'split')
        if not split_col:
            continue
        sources.append(str(path.relative_to(root)))
        for row in rows:
            row = dict(row)
            row['__source_file__'] = str(path.relative_to(root))
            records.append(row)
    return records, sources

def _overlap_check(records: list[dict[str, Any]], identity_role: str, check_name: str) -> Finding:
    if not records:
        return Finding(check_name, 'BLOCKED', 'No parseable split records discovered.', {})
    keys = set().union(*(row.keys() for row in records[:50]))
    split_col = _find_column(keys, 'split')
    id_col = _find_column(keys, identity_role)
    if not split_col:
        return Finding(check_name, 'BLOCKED', 'Split column not found.', {})
    if not id_col:
        return Finding(check_name, 'NOT_APPLICABLE', f'{identity_role} identity not present in discovered manifests.', {})
    dataset_col = _find_column(keys, 'dataset')
    roles = defaultdict(set)
    examples = defaultdict(list)
    for row in records:
        role = _split_role(row.get(split_col))
        ident = _norm_key(row.get(id_col))
        if not role or not ident:
            continue
        dataset = _norm_key(row.get(dataset_col)) if dataset_col else ''
        namespaced = f'{dataset}::{ident}' if dataset else ident
        roles[namespaced].add(role)
        examples[namespaced].append({'role': role, 'source': row.get('__source_file__')})
    bad = {k: sorted(v) for k, v in roles.items() if 'TRAIN' in v and 'EVALUATION' in v}
    if bad:
        sample = dict(list(bad.items())[:25])
        return Finding(check_name, 'FAIL', f'{identity_role} overlaps TRAIN and EVALUATION.', {'count': len(bad), 'sample': sample})
    return Finding(check_name, 'PASS', f'No {identity_role} overlap between TRAIN and EVALUATION.', {'identities_checked': len(roles)})

def _exact_example_overlap(records: list[dict[str, Any]]) -> Finding:
    if not records:
        return Finding('example_overlap', 'BLOCKED', 'No parseable split records discovered.', {})
    keys = set().union(*(row.keys() for row in records[:50]))
    split_col = _find_column(keys, 'split')
    example_col = _find_column(keys, 'example')
    if not split_col or not example_col:
        return Finding('example_overlap', 'NOT_APPLICABLE', 'Example identity not available.', {})
    roles = defaultdict(set)
    for row in records:
        ident = _norm_key(row.get(example_col))
        role = _split_role(row.get(split_col))
        if ident and role:
            roles[ident].add(role)
    bad = {k: sorted(v) for k, v in roles.items() if len(v) > 1 and 'TRAIN' in v and 'EVALUATION' in v}
    if bad:
        return Finding('example_overlap', 'FAIL', 'Same example identity occurs in train and evaluation.', {'count': len(bad), 'sample': dict(list(bad.items())[:25])})
    return Finding('example_overlap', 'PASS', 'No exact example identity train/evaluation overlap.', {'examples_checked': len(roles)})

def _feature_registry_check(root: Path) -> Finding:
    registries = [
        p for p in _get_target_files(root)
        if 'feature' in p.name.lower() and 'registr' in p.name.lower() and p.suffix.lower() in {'.yaml', '.yml', '.json', '.md'}
    ]
    if not registries:
        return Finding('feature_leakage', 'BLOCKED', 'No feature registry discovered for leakage audit.', {})
    offenders = []
    for path in registries:
        text = path.read_text(encoding='utf-8', errors='replace')
        tokens = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text.lower()))
        bad = sorted(tokens & FORBIDDEN_FEATURE_IDENTIFIERS)
        for line_no, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if any(re.search(rf'(^|[-\s\"\']){re.escape(name)}\s*[:,-]', low) for name in bad):
                if not any(h in low for h in ('forbidden', 'exclude', 'excluded', 'not a feature', 'leakage', 'do not include')):
                    offenders.append({'path': str(path.relative_to(root)), 'line': line_no, 'excerpt': line.strip()[:250]})
    if offenders:
        return Finding('feature_leakage', 'FAIL', 'Forbidden identity/target-like fields appear to be registered as model features.', {'count': len(offenders), 'sample': offenders[:25]})
    return Finding('feature_leakage', 'PASS', 'No forbidden identity/target-like feature registration detected.', {'registries': [str(p.relative_to(root)) for p in registries]})

def _locked_eval_check(root: Path) -> Finding:
    candidates = [
        p for p in _get_target_files(root)
        if p.suffix.lower() in {'.json', '.yaml', '.yml', '.md'}
        and any(t in p.name.lower() for t in ('leakage', 'locked', 'split', 'reproduc', 'evaluation'))
    ]
    evidence = []
    contaminated = []
    untouched = []
    for p in candidates:
        txt = p.read_text(encoding='utf-8', errors='replace')
        low = txt.lower()
        if 'locked_evaluation_contaminated' in low or re.search(r'locked[_ -]?eval(?:uation)?[^\n]{0,80}\bcontaminated\b', low):
            contaminated.append(str(p.relative_to(root)))
        if re.search(r'locked[_ -]?eval(?:uation)?[^\n]{0,100}\b(?:untouched|not used|excluded from tuning|pass)\b', low):
            untouched.append(str(p.relative_to(root)))
        if 'locked' in low and 'evaluation' in low:
            evidence.append(str(p.relative_to(root)))
    if contaminated:
        return Finding('locked_evaluation_guard', 'FAIL', 'Evidence indicates locked evaluation contamination.', {'files': contaminated[:25]})
    if untouched:
        return Finding('locked_evaluation_guard', 'PASS', 'Evidence explicitly states locked evaluation remained untouched/excluded from tuning.', {'files': untouched[:25]})
    return Finding('locked_evaluation_guard', 'BLOCKED', 'No explicit evidence proving locked evaluation was untouched.', {'candidate_files': evidence[:25]})

def audit_leakage(root: Path) -> dict:
    root = root.resolve()
    records, sources = discover_split_records(root)
    findings = [
        _overlap_check(records, 'subject', 'subject_overlap'),
        _overlap_check(records, 'source_window', 'source_derivative_leakage'),
        _exact_example_overlap(records),
        _feature_registry_check(root),
        _locked_eval_check(root),
    ]
    hard_fail = any(f.status == 'FAIL' for f in findings)
    blocked = any(f.status == 'BLOCKED' for f in findings)
    status = 'FAIL' if hard_fail else ('BLOCKED' if blocked else 'PASS')
    return {
        'status': status,
        'records_scanned': len(records),
        'split_sources': sources,
        'findings': [asdict(f) for f in findings],
        'pass_condition': 'All mandatory leakage checks PASS or are explicitly NOT_APPLICABLE with reason.',
        'claim_boundary': 'Leakage safety only; no clinical/site validity inference.',
    }
