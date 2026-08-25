from pathlib import Path
import re, sys
root=Path(__file__).resolve().parent
ov=root/'canonical-repo-overlay'
required=[
 'apps/web-portal/src/contracts/automation/index.ts',
 'apps/web-portal/src/data/automation/automation-repository.ts',
 'apps/web-portal/src/data/automation/real-automation-repository.ts',
 'apps/web-portal/src/lib/api/automation/endpoints.ts',
 'scripts/dev/audit_ui_i1_backend_contracts.py',
 'scripts/dev/verify_ui_i1_foundation.sh',
]
missing=[x for x in required if not (ov/x).exists()]
assert not missing, missing
# UI-I1 overlay must not add files to use-case route/component trees.
for p in ov.rglob('*'):
    if p.is_file():
        rel=p.relative_to(ov).as_posix().lower()
        assert '/uc1/' not in rel and '/uc2/' not in rel and '/uc3/' not in rel and '/uc4/' not in rel, rel
# No TODO placeholders in executable TS/Python files.
for p in list(ov.rglob('*.ts'))+list(ov.rglob('*.tsx'))+list(ov.rglob('*.py')):
    text=p.read_text(encoding='utf-8')
    assert 'TODO' not in text, p
print('UI-I1 package structural verification: PASS')
