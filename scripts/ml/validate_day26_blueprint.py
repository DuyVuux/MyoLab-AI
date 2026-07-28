#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path
import yaml

p=argparse.ArgumentParser(); p.add_argument('--root',default='.'); p.add_argument('--output',required=True); a=p.parse_args(); root=Path(a.root)
config_paths=[
'ai-core/configs/task_contracts.research.yaml','ai-core/configs/feature_groups.research.yaml','ai-core/configs/model_ladder.research.yaml','ai-core/configs/evaluation_regimes.research.yaml','ai-core/configs/personalization_strategies.research.yaml','ai-core/configs/fatigue_experiments.research.yaml','ai-core/configs/experiment_matrix.draft.yaml']
errors=[]
for rel in config_paths:
    d=yaml.safe_load((root/rel).read_text(encoding='utf-8'))
    if d.get('trainingAllowed') is not False: errors.append(f'{rel}: trainingAllowed must be false')
    st=d.get('execution_state')
    if st is not None and st!='NOT_RUN': errors.append(f'{rel}: execution_state must be NOT_RUN')
m=yaml.safe_load((root/'ai-core/configs/experiment_matrix.draft.yaml').read_text(encoding='utf-8'))
if m.get('outer_test_opened') is not False: errors.append('outer test must be unopened')
ids=set()
for row in m.get('experiments',[]):
    if row['id'] in ids: errors.append(f'duplicate experiment {row["id"]}')
    ids.add(row['id'])
    if row.get('result_status')!='NOT_RUN': errors.append(f'{row["id"]}: fake/non-NOT_RUN result')
status={'blueprint_valid':not errors,'training_execution_allowed':False,'test_set_sealed':True,'result_status':'NOT_RUN','day27_allowed':not errors,'day29_training_blocked_until_gates_pass':True,'experiment_count':len(ids),'errors':errors}
out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(status,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(status,ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
