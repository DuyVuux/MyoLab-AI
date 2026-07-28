#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path
import yaml

root=Path(__file__).resolve().parents[2]
required=[
'docs/plans/DAY26_EXECUTION_PLAN.md','docs/research/day26/00-research-protocol.md','docs/research/day26/02-feature-engineering-review.md','docs/research/day26/03-classical-model-candidate-review.md','docs/research/day26/04-validation-and-leakage-review.md','docs/research/day26/05-personalization-and-adaptation-strategy.md','docs/research/day26/06-fatigue-distribution-shift-blueprint.md','docs/research/day26/08-metrics-calibration-abstention.md','docs/research/day26/09-reproducibility-and-governance.md','docs/research/day26/10-master-experiment-blueprint.md','ai-core/configs/experiment_matrix.draft.yaml','ai-core/configs/evaluation_regimes.research.yaml','docs/09-mlops-devops/model-registry-spec.md','docs/09-mlops-devops/reproducible-training-policy.md']
errors=[]
for rel in required:
    if not (root/rel).is_file(): errors.append(f'missing: {rel}')
for p in (root/'ai-core/configs').glob('*.yaml'):
    d=yaml.safe_load(p.read_text(encoding='utf-8'))
    if isinstance(d,dict) and 'trainingAllowed' in d and d['trainingAllowed'] is not False:
        errors.append(f'training enabled in {p.relative_to(root)}')
# Executable Python should not import sklearn estimators or call .fit in Day 26 pack.
for base in [root/'ai-core/experiments',root/'scripts/ml']:
    for p in base.glob('*.py'):
        text=p.read_text(encoding='utf-8')
        if re.search(r'\.fit\s*\(',text): errors.append(f'fit call found: {p.relative_to(root)}')
        if 'sklearn.' in text: errors.append(f'sklearn estimator import found: {p.relative_to(root)}')
# Prohibited registry state.
reg=yaml.safe_load((root/'ai-core/configs/model_registry_states.research.yaml').read_text(encoding='utf-8'))
if any('clinical' in s for s in reg['states']): errors.append('clinical state in allowed registry states')
if errors:
    print('\n'.join(errors),file=sys.stderr); raise SystemExit(1)
print('Day 26 artifact and safety checks: PASS')
