#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'qa-validation/evidence/day02-artifact-manifest.json'

STATIC_EXCLUDE={
    Path('qa-validation/evidence/day02-artifact-manifest.json'),
    Path('qa-validation/evidence/day02-validation-report.json'),
}


def sha256_file(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def collect():
    rows=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if rel in STATIC_EXCLUDE: continue
        if '__pycache__' in rel.parts or '.pytest_cache' in rel.parts or p.suffix=='.pyc': continue
        rows.append({'path':rel.as_posix(),'sha256':sha256_file(p),'bytes':p.stat().st_size})
    return rows


def main():
    current=collect()
    if not MANIFEST.exists():
        print('[DAY02] artifact manifest missing'); return 2
    expected=json.loads(MANIFEST.read_text(encoding='utf-8'))['files']
    if expected!=current:
        exp={x['path']:x for x in expected}; cur={x['path']:x for x in current}
        print('[DAY02] artifact manifest mismatch')
        print(' missing:',sorted(set(exp)-set(cur)))
        print(' extra:',sorted(set(cur)-set(exp)))
        print(' changed:',sorted(k for k in set(exp)&set(cur) if exp[k]!=cur[k]))
        return 2
    forbidden=[]
    for p in ROOT.rglob('*'):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        s=rel.as_posix().lower()
        if '__pycache__' in rel.parts or '.pytest_cache' in rel.parts or p.suffix=='.pyc': forbidden.append(str(rel))
        if any(x in s for x in ['/raw/','patient_raw','patient-name','mrn_']): forbidden.append(str(rel))
    if forbidden:
        print('[DAY02] forbidden artifacts:',forbidden); return 2
    report_path=ROOT/'qa-validation/evidence/day02-validation-report.json'
    if not report_path.is_file():
        print('[DAY02] validation report missing'); return 2
    report=json.loads(report_path.read_text(encoding='utf-8'))
    if report.get('status')!='GO_FOR_DAY_03' or report.get('tests_passed')!=20:
        print('[DAY02] final validation report is not GO_FOR_DAY_03/20 passed:', report); return 2
    print(f'[DAY02] artifact manifest PASS ({len(current)} static files)')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
