#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

EXCLUDE={"/.next/","/node_modules/","/__pycache__/"}
def included(p,root):
    rel="/"+p.relative_to(root).as_posix()
    return p.is_file() and not any(x in rel for x in EXCLUDE)

def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
    targets=[
      root/"apps/web-portal/src",
      root/"apps/web-portal/e2e",
      root/"apps/web-portal/package.json",
      root/"pnpm-lock.yaml",
    ]
    files=[]
    for t in targets:
        if not t.exists(): continue
        if t.is_file(): files.append(t)
        else: files.extend(p for p in t.rglob("*") if included(p,root))
    manifest={}
    for p in sorted(set(files)):
        manifest[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    aggregate=hashlib.sha256("\n".join(f"{k}:{v}" for k,v in manifest.items()).encode()).hexdigest()
    out=root/"qa-validation/evidence/ui-final-freeze.json";out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"status":"PASS","file_count":len(manifest),"aggregate_sha256":aggregate,"files":manifest},indent=2))
    print(out);print("UI_FREEZE_SHA256",aggregate);return 0
if __name__=="__main__":raise SystemExit(main())
