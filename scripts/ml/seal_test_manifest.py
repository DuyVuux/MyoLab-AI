#!/usr/bin/env python3
"""Create a Day 26 template seal only. It never reads or prints test member IDs."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import yaml

p=argparse.ArgumentParser(); p.add_argument('--template',required=True); p.add_argument('--output',required=True); a=p.parse_args()
data=yaml.safe_load(Path(a.template).read_text(encoding='utf-8'))
if data.get('opened') is not False or data.get('open_count') != 0:
    raise SystemExit('Test seal template must be unopened')
raw=json.dumps(data,sort_keys=True,separators=(',',':')).encode()
data['template_sha256']=hashlib.sha256(raw).hexdigest()
out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(out)
