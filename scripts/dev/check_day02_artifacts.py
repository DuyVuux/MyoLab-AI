#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'qa-validation/evidence/day02-artifact-manifest.json'

def sha256_file(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def get_managed_paths(root: Path, manifest: dict) -> list[Path]:
    return [root / item["path"] for item in manifest.get("files", [])]

def main() -> int:
    if not MANIFEST.exists():
        print('[DAY02] artifact manifest missing')
        return 2
        
    manifest_data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    expected_files = manifest_data.get('files', [])
    
    missing = []
    hash_mismatch = []
    forbidden = []
    
    for item in expected_files:
        rel_path = item["path"]
        full_path = ROOT / rel_path
        
        if not full_path.is_file():
            missing.append(rel_path)
            continue
            
        current_hash = sha256_file(full_path)
        if "sha256" in item and current_hash != item["sha256"]:
            hash_mismatch.append(rel_path)
            
        s = rel_path.lower()
        if any(x in s for x in ['/raw/', 'patient_raw', 'patient-name', 'mrn_']):
            forbidden.append(rel_path)

    if missing or hash_mismatch or forbidden:
        print('[DAY02] artifact validation failed')
        if missing:
            print(' missing:', missing)
        if hash_mismatch:
            print(' hash mismatch:', hash_mismatch)
        if forbidden:
            print(' forbidden artifacts:', forbidden)
        return 2
        
    report_path = ROOT / 'qa-validation/evidence/day02-validation-report.json'
    if not report_path.is_file():
        print('[DAY02] validation report missing')
        return 2
        
    report = json.loads(report_path.read_text(encoding='utf-8'))
    if report.get('status') != 'GO_FOR_DAY_03' or report.get('tests_passed') != 20:
        print('[DAY02] final validation report is not GO_FOR_DAY_03/20 passed:', report)
        return 2
        
    print(f'[DAY02] artifact manifest PASS ({len(expected_files)} static files)')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
