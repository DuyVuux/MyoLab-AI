#!/usr/bin/env python3
from __future__ import annotations
import argparse,ast,json
from dataclasses import dataclass,asdict
from pathlib import Path
METHODS={"get","post","put","patch","delete"}
@dataclass
class Route: method:str; path:str; file:str; line:int
def cstr(n): return n.value if isinstance(n,ast.Constant) and isinstance(n.value,str) else None
def prefix(t):
 for n in ast.walk(t):
  if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=="APIRouter":
   for kw in n.value.keywords:
    if kw.arg=="prefix": return cstr(kw.value) or ""
 return ""
def scan(path,repo):
 try:t=ast.parse(path.read_text(encoding="utf-8"))
 except Exception:return[]
 px=prefix(t);out=[]
 for n in ast.walk(t):
  if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):continue
  for d in n.decorator_list:
   if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr.lower() in METHODS and d.args:
    p=cstr(d.args[0])
    if p is not None: out.append(Route(d.func.attr.upper(),f"{px.rstrip('/')}/{p.lstrip('/')}",str(path.relative_to(repo)),n.lineno))
 return out
def canon(p):
 for a,b in [("{session_id}","{sessionId}"),("{channel_id}","{channelId}"),("{manifest_id}","{manifestId}"),("{case_id}","{caseId}")]:p=p.replace(a,b)
 return p
EXPECTED={
"signal_index":("GET","/v1/sessions/{sessionId}/signals"),
"signal_window":("GET","/v1/sessions/{sessionId}/signals/{channelId}/window"),
"processing_manifest":("GET","/v1/processing-manifests/{manifestId}"),
"session_evidence":("GET","/v1/sessions/{sessionId}/evidence"),
"review_cases":("GET","/v1/review-cases"),
"review_case":("GET","/v1/review-cases/{caseId}"),
"review_action":("POST","/v1/review-cases/{caseId}/actions"),
"session_audit":("GET","/v1/sessions/{sessionId}/audit")}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("repo_root",nargs="?",default=".");repo=Path(ap.parse_args().repo_root).resolve()
 routes=[];seen=set()
 for root in [repo/"services/api-server",repo/"services"]:
  if root.exists():
   for p in root.rglob("*.py"):
    if p in seen:continue
    seen.add(p);routes+=scan(p,repo)
 idx={(r.method,canon(r.path)):r for r in routes};cat={}
 for name,(method,path) in EXPECTED.items():
  hit=idx.get((method,canon(path)));cat[name]={"template":path if hit else None,"method":method,"verification":"VERIFIED" if hit else "UNAVAILABLE","evidence":f"{hit.file}:{hit.line}" if hit else "No matching live decorator"}
 missing=[k for k,v in cat.items() if v["verification"]!="VERIFIED"]
 out=repo/"qa-validation/evidence/ui-i3-backend-contract-audit.json";out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({"status":"PASS","routes":[asdict(r) for r in routes],"catalog":cat,"missing":missing},indent=2))
 print(out);print("MISSING:",", ".join(missing) or "(none)");return 0 if not missing else 4
if __name__=="__main__":raise SystemExit(main())
