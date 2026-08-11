from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MAN=ROOT/'qa-validation/evidence/day23-artifact-manifest.json'
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def main():
 data=json.loads(MAN.read_text()); errors=[]
 for item in data['artifacts']:
  p=ROOT/item['path']
  if not p.is_file(): errors.append('missing:'+item['path']); continue
  if sha(p)!=item['sha256']: errors.append('hash:'+item['path'])
 forbidden=['__pycache__','.pytest_cache','.pyc']
 for p in ROOT.rglob('*'):
  s=str(p.relative_to(ROOT))
  if any(x in s for x in forbidden): errors.append('forbidden:'+s)
 if errors:
  print(json.dumps({'status':'FAIL','errors':errors},indent=2)); return 2
 print(f'DAY23 ARTIFACT MANIFEST: PASS ({len(data["artifacts"])}/{len(data["artifacts"])})'); return 0
if __name__=='__main__': raise SystemExit(main())
