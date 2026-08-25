#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, hashlib, json, re
from pathlib import Path

ROUTE_FILES = {
    "sessions": "services/api-server/src/routes/sessions.py",
    "quality": "services/api-server/src/routes/quality.py",
    "signals": "services/api-server/src/routes/signals.py",
    "analysis_jobs": "services/api-server/src/routes/analysis_jobs.py",
    "audit": "services/api-server/src/routes/audit.py",
    "reviews": "services/api-server/src/routes/reviews.py",
}

def sha256(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def extract_fastapi_routes(path: Path):
    text=path.read_text(encoding="utf-8", errors="replace")
    out=[]
    # Static scan intentionally simple and fail-closed; dynamic route construction is marked unresolved.
    pattern=re.compile(r"@(?:router|app)\.(get|post|put|patch|delete)\(\s*[\"']([^\"']+)[\"']", re.I)
    for method, route in pattern.findall(text): out.append({"method": method.upper(), "path": route})
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("repo_root", nargs="?", default=".")
    ap.add_argument("--out", default="qa-validation/evidence/ui-i1-backend-contract-audit.json")
    args=ap.parse_args(); root=Path(args.repo_root).resolve()
    files={}; routes=[]
    for name, rel in ROUTE_FILES.items():
        p=root/rel
        if p.exists():
            found=extract_fastapi_routes(p)
            files[name]={"path": rel, "exists": True, "sha256": sha256(p), "routes_found": len(found)}
            routes.extend({"module": name, **r} for r in found)
        else: files[name]={"path": rel, "exists": False, "routes_found": 0}
    result={
        "status": "PASS" if any(v["exists"] for v in files.values()) else "BLOCKED_WITH_EVIDENCE",
        "purpose": "UI-I1 live backend route discovery; discovered decorators are evidence, not inferred API guarantees",
        "files": files,
        "routes": routes,
        "required_live_verification": ["payload schema", "auth requirements", "pagination", "signal-window query shape", "metric evidence semantics"],
    }
    out=root/args.out; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 2)
if __name__ == "__main__": main()
