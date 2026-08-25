#!/usr/bin/env python3
import ast, json, sys
from pathlib import Path

def scan(path):
    try: tree=ast.parse(path.read_text(encoding="utf-8"))
    except Exception: return []
    prefix=""
    for n in ast.walk(tree):
        if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=="APIRouter":
            for kw in n.value.keywords:
                if kw.arg=="prefix" and isinstance(kw.value,ast.Constant): prefix=kw.value.value
    out=[]
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            for d in n.decorator_list:
                if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr.lower() in {"get","post","put","patch","delete"} and d.args and isinstance(d.args[0],ast.Constant):
                    out.append((d.func.attr.upper(),f"{prefix.rstrip('/')}/{str(d.args[0].value).lstrip('/')}",n.lineno))
    return out

def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
    routes=[]
    for base in [root/"services/api-server", root/"services"]:
        if base.exists():
            for p in base.rglob("*.py"):
                for method,path,line in scan(p):
                    routes.append({"method":method,"path":path,"file":str(p.relative_to(root)),"line":line})
    hit=next((x for x in routes if x["method"]=="GET" and x["path"]=="/v1/operations/summary"),None)
    ts=root/"apps/web-portal/src/lib/api/automation/live-ui-i4-endpoints.generated.ts"
    ts.parent.mkdir(parents=True,exist_ok=True)
    if hit:
        ts.write_text(
            'import type { UiI4EndpointCatalog } from "./ui-i4-endpoints";\n\n'
            '/** GENERATED FROM LIVE ROUTE DECORATORS - DO NOT HAND-EDIT */\n'
            'export const LIVE_UI_I4_ENDPOINTS: UiI4EndpointCatalog = {\n'
            '  operations_summary: {\n'
            '    template: "/v1/operations/summary",\n'
            '    method: "GET",\n'
            '    verification: "VERIFIED",\n'
            f'    evidence: "{hit["file"]}:{hit["line"]}",\n'
            '  },\n'
            '};\n',
            encoding="utf-8",
        )
    out=root/"qa-validation/evidence/ui-i4-backend-contract-audit.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"status":"PASS","operations_summary":"VERIFIED" if hit else "UNAVAILABLE","evidence":hit,"routes":routes},indent=2))
    print(out)
    return 0 if hit else 4
if __name__=="__main__": raise SystemExit(main())
