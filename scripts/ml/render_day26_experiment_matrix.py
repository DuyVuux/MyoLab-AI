#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import yaml

p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--csv',required=True); p.add_argument('--json',required=True); a=p.parse_args()
data=yaml.safe_load(Path(a.config).read_text(encoding='utf-8'))
rows=data['experiments']
fields=['id','task','hypothesis','feature_group','model','regime','personalization','fatigue_architecture','primary_metric','result_status']
cp=Path(a.csv); cp.parent.mkdir(parents=True,exist_ok=True)
with cp.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows({k:r.get(k,'') for k in fields} for r in rows)
Path(a.json).write_text(json.dumps({'trainingAllowed':data['trainingAllowed'],'outer_test_opened':data['outer_test_opened'],'experiments':rows},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Rendered {len(rows)} experiments')
