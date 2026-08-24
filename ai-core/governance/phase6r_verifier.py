#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

PROHIBITED_CLAIMS = [
    re.compile(r'\b(?:is|are|was|were|has been) clinically validated\b', re.I),
    re.compile(r'\bvalidated at vinmec\b', re.I),
    re.compile(r'\bvinmec validated\b', re.I),
    re.compile(r'\bproduction ood model\b', re.I),
    re.compile(r'\bcalibrated clinical probability\b', re.I),
    re.compile(r'\bclinical artifact detector\b', re.I),
]

TEXT_EXTENSIONS = {'.md', '.txt', '.yaml', '.yml', '.json', '.csv', '.py', '.sh'}
EXCLUDE_DIRS = {'.venv', 'node_modules', '.git', '.agents', '.pytest_cache', '__pycache__', 'phase6r-research-ml-complete(1)', '.next', 'json', 'dist', 'build'}

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''

def find_matching_files(root: Path, patterns: list[str]) -> list[Path]:
    output = []
    compiled = [re.compile(p, re.I) for p in patterns]
    for file_path in root.rglob('*'):
        if any(part in EXCLUDE_DIRS for part in file_path.parts):
            continue
        if file_path.is_file():
            posix_path = file_path.as_posix()
            if any(rx.search(posix_path) for rx in compiled):
                output.append(file_path)
    return sorted(set(output))

def contains_token(paths: list[Path], token: str) -> bool:
    token_lower = token.lower()
    return any(token_lower in read_text(p).lower() for p in paths)

def audit_claim_boundaries(root: Path) -> list[dict[str, str]]:
    violations = []
    for file_path in root.rglob('*'):
        if any(part in EXCLUDE_DIRS for part in file_path.parts):
            continue
        if not file_path.is_file() or file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        rel_path = file_path.relative_to(root).as_posix()
        if 'tests/' in rel_path or 'automated-tests' in rel_path or 'scripts/dev/' in rel_path or 'linter' in rel_path or 'validator' in rel_path:
            continue
        file_content = read_text(file_path)
        for pattern in PROHIBITED_CLAIMS:
            if pattern.search(file_content):
                violations.append({'path': rel_path, 'pattern': pattern.pattern})
    return violations

def evaluate_phase6r_entry(root: Path) -> dict:
    required_roots = ['ai-core', 'qa-validation', 'docs']
    repo_shape_ok = all((root / d).exists() for d in required_roots)

    m5_files = find_matching_files(root, [r'm5[-_]?r', r'public[-_ ]benchmark'])
    gate_files = find_matching_files(root, [r'gate[-_]?e[-_]?r'])
    index_files = find_matching_files(root, [r'public[-_ ]benchmark.*evidence', r'evidence.*public[-_ ]benchmark'])
    contract_files = find_matching_files(root, [r'contract', r'schema', r'record'])
    leakage_files = find_matching_files(root, [r'leakage'])
    split_files = find_matching_files(root, [r'split'])
    repro_files = find_matching_files(root, [r'reproduc', r'reproduction'])
    ml_dec_files = find_matching_files(root, [r'ml[-_ ]?(feasibility|decision|gate)', r'classical[-_ ]ml'])

    m5_ready = contains_token(m5_files, 'PUBLIC_BENCHMARK_READY')
    feature_contract_ok = any(
        'publicfeaturewindowrecord' in read_text(p).lower() and ('v1.2' in read_text(p).lower() or 'version: 1.2' in read_text(p).lower())
        for p in contract_files
    )

    detected_ml_decision = None
    all_ml_content = '\n'.join(read_text(p) for p in ml_dec_files)
    for token in ['ML_GO', 'ML_NO_GO', 'INSUFFICIENT_LABELS', 'INSUFFICIENT_DATA', 'INSUFFICIENT_EVIDENCE']:
        if token in all_ml_content:
            detected_ml_decision = token
            break

    leakage_pass = any('pass' in read_text(p).lower() and 'leakage' in read_text(p).lower() for p in leakage_files)
    repro_pass = any('pass' in read_text(p).lower() for p in repro_files)
    claim_violations = audit_claim_boundaries(root)

    critical_checks = [
        repo_shape_ok,
        m5_ready,
        bool(gate_files),
        bool(index_files),
        feature_contract_ok,
        bool(split_files),
        leakage_pass,
        repro_pass,
        detected_ml_decision is not None,
        len(claim_violations) == 0
    ]

    execution_allowed = all(critical_checks)
    phase_entry_status = 'PASS' if execution_allowed else 'BLOCKED_WITH_EVIDENCE'

    return {
        'repository_root': str(root.resolve()),
        'repository_shape': 'PASS' if repo_shape_ok else 'FAIL',
        'm5r_public_benchmark_ready': 'PASS' if m5_ready else 'FAIL',
        'gate_e_r_evidence': 'PASS' if bool(gate_files) else 'FAIL',
        'public_feature_contract_v1_2': 'PASS' if feature_contract_ok else 'FAIL',
        'leakage_audit': 'PASS' if leakage_pass else 'FAIL',
        'reproducibility': 'PASS' if repro_pass else 'FAIL',
        'starting_ml_decision': detected_ml_decision or 'UNKNOWN',
        'claim_boundary_violations': claim_violations,
        'claim_boundaries': [
            'RESEARCH_ONLY',
            'NOT_CLINICALLY_VALIDATED',
            'NOT_FOR_CLINICAL_USE',
            'CORE_SYSTEM_MUST_RUN_WITH_ML_OFF'
        ],
        'execution_allowed': execution_allowed,
        'phase_entry_status': phase_entry_status
    }

def main() -> int:
    parser = argparse.ArgumentParser(description='Phase 6R Entry Gate Verifier')
    parser.add_argument('--repo-root', type=Path, default=Path('.'))
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    result = evaluate_phase6r_entry(args.repo_root)
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    print(payload)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + '\n', encoding='utf-8')

    return 0 if result['execution_allowed'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
