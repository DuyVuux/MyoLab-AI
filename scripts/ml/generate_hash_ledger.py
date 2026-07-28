#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

p=argparse.ArgumentParser()
p.add_argument('--root', required=True)
p.add_argument('--output', required=True)
a=p.parse_args()
root=Path(a.root)
rows=[]
for f in sorted(x for x in root.rglob('*') if x.is_file()):
    rows.append({'path':str(f.relative_to(root)),'size_bytes':f.stat().st_size,'sha256':digest(f)})
out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'root':str(root),'files':rows},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Wrote {len(rows)} hashes to {out}')
