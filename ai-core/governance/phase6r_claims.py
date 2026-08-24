from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {'.md', '.txt', '.yaml', '.yml', '.json', '.csv', '.py', '.sh', '.toml'}
TARGET_SUBDIRS = ['ai-core', 'qa-validation', 'docs', 'configs', 'scripts']
EXCLUDE_DIRS = {'.venv', 'node_modules', '.git', '.agents', '.pytest_cache', '__pycache__', 'phase6r-research-ml-continuation', '.next', 'json', 'dist', 'build'}

UNSUPPORTED_PATTERNS = {
    'clinically_validated': re.compile(r'\bclinically validated\b', re.I),
    'validated_at_vinmec': re.compile(r'\bvalidated at vinmec\b', re.I),
    'vinmec_validated': re.compile(r'\bvinmec validated\b', re.I),
    'clinical_artifact_detector': re.compile(r'\bclinical artifact detector\b', re.I),
    'production_ood': re.compile(r'\bproduction(?:[- ]ready)? ood(?: model| score)?\b', re.I),
    'calibrated_clinical_probability': re.compile(r'\bcalibrated clinical probability\b', re.I),
    'clinical_predictor': re.compile(r'\bclinical predictor\b', re.I),
    'pathology_detector': re.compile(r'\bpathology detector\b', re.I),
}

NEGATION_HINTS = re.compile(
    r'\b(?:not|never|no|without|isn[\'’]t|aren[\'’]t|wasn[\'’]t|were not|không|chưa|không phải|không được)\b',
    re.I,
)
POLICY_HINTS = re.compile(
    r'\b(?:forbidden|unsafe|unsupported|prohibited|reject|must not|do not|cấm|không được|không claim|claim boundary|pattern|example|test fixture|negative test|provisional)\b',
    re.I,
)
CODE_ASSERT_HINTS = re.compile(r'(assert|self\.assert|pytest|expected|pattern|re\.compile|forbidden|unsafe|bad in|bad =|for bad)', re.I)

@dataclass(frozen=True)
class ClaimHit:
    path: str
    line: int
    claim_id: str
    classification: str
    excerpt: str

def _classification(line: str, suffix: str, rel_path: str) -> str:
    low = line.lower().strip()
    if NEGATION_HINTS.search(line):
        return 'NEGATED_OR_BOUNDARY'
    if POLICY_HINTS.search(line):
        return 'POLICY_OR_EXAMPLE_MENTION'
    if low.startswith('-') or low.startswith('*') or low.startswith('>') or low.startswith('"') or low.startswith("'") or low.startswith("`"):
        return 'POLICY_OR_EXAMPLE_MENTION'
    rel_low = rel_path.lower().replace('\\', '/')
    if suffix in ('.py', '.sh', '.json', '.yaml', '.yml') and (CODE_ASSERT_HINTS.search(line) or '/test' in rel_low or 'automated-tests/' in rel_low or rel_low.split('/')[-1].startswith('test_')):
        return 'TEST_OR_SCANNER_LITERAL'
    if any(token in low for token in ('allowed examples', 'unsafe examples', 'claim audit', 'claim-language', 'forbidden', 'boundary', 'spec')):
        return 'POLICY_OR_EXAMPLE_MENTION'
    return 'UNSUPPORTED_ASSERTION'

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

def audit_claim_boundaries(root: Path, *, exclude: Iterable[Path] = ()) -> dict:
    root = root.resolve()
    excluded = {p.resolve() for p in exclude}
    hits: list[ClaimHit] = []
    for path in _get_target_files(root):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if any(parent in excluded for parent in [path.resolve(), *path.resolve().parents]):
            continue
        try:
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, 1):
            for claim_id, pattern in UNSUPPORTED_PATTERNS.items():
                if not pattern.search(line):
                    continue
                classification = _classification(line, path.suffix.lower(), str(path.relative_to(root)))
                hits.append(ClaimHit(
                    path=str(path.relative_to(root)),
                    line=lineno,
                    claim_id=claim_id,
                    classification=classification,
                    excerpt=line.strip()[:300],
                ))
    blocking = [hit for hit in hits if hit.classification == 'UNSUPPORTED_ASSERTION']
    return {
        'status': 'PASS' if not blocking else 'FAIL',
        'blocking_count': len(blocking),
        'reviewed_hit_count': len(hits),
        'blocking_unsupported_assertions': [asdict(hit) for hit in blocking],
        'nonblocking_context_mentions': [asdict(hit) for hit in hits if hit not in blocking],
        'semantics': {
            'negated_boundary_is_not_violation': True,
            'policy_or_test_literal_is_not_violation': True,
            'positive_unsupported_assertion_blocks': True,
        },
    }
