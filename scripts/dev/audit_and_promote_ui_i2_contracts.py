#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

ROUTE_METHODS = {"get", "post", "put", "patch", "delete"}

@dataclass
class Route:
    method: str
    path: str
    file: str
    line: int

def const_str(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None

def router_prefix(tree: ast.AST) -> str:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            fn = node.value.func
            if isinstance(fn, ast.Name) and fn.id == "APIRouter":
                for kw in node.value.keywords:
                    if kw.arg == "prefix":
                        return const_str(kw.value) or ""
    return ""

def scan_file(path: Path, repo: Path) -> list[Route]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    prefix = router_prefix(tree)
    out: list[Route] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                continue
            method = dec.func.attr.lower()
            if method not in ROUTE_METHODS or not dec.args:
                continue
            path_arg = const_str(dec.args[0])
            if path_arg is None:
                continue
            full = f"{prefix.rstrip('/')}/{path_arg.lstrip('/')}"
            if not full.startswith("/"):
                full = "/" + full
            out.append(Route(
                method=method.upper(),
                path=full,
                file=str(path.relative_to(repo)),
                line=node.lineno,
            ))
    return out

def canonical(path: str) -> str:
    # Normalize FastAPI parameter names so {session_id} and {sessionId} compare.
    pieces = []
    for part in path.split("/"):
        if part.startswith("{") and part.endswith("}"):
            name = part[1:-1].replace("_", "").lower()
            if name == "sessionid": part = "{sessionId}"
            elif name in {"jobid", "analysisid"}: part = "{jobId}"
        pieces.append(part)
    return "/".join(pieces)

EXPECTED = {
    "sessions_collection": ("GET", "/v1/sessions"),
    "session_detail": ("GET", "/v1/sessions/{sessionId}"),
    "session_import": ("POST", "/v1/sessions/import"),
    "session_import_upload": ("POST", "/v1/sessions/import/upload"),
    "pipeline_job": ("GET", "/v1/analyses/{jobId}"),
    "session_preflight": ("GET", "/v1/sessions/{sessionId}/preflight"),
    "session_mapping": ("GET", "/v1/sessions/{sessionId}/mapping"),
    "session_mapping_resolve": ("POST", "/v1/sessions/{sessionId}/mapping/resolve"),
    "session_quality": ("GET", "/v1/sessions/{sessionId}/quality"),
}

DEFERRED = {
    "signal_window", "session_metrics", "session_evidence", "review_cases", "session_audit"
}

def match_expected(routes: list[Route]):
    index = {(r.method, canonical(r.path)): r for r in routes}
    result = {}
    for name, (method, path) in EXPECTED.items():
        route = index.get((method, canonical(path)))
        result[name] = {
            "template": path if route else None,
            "verification": "VERIFIED" if route else "UNAVAILABLE",
            "method": method,
            "evidence": (
                f"{route.file}:{route.line}" if route
                else "No matching live FastAPI decorator discovered"
            ),
        }
    for name in DEFERRED:
        result[name] = {
            "template": None,
            "verification": "UNAVAILABLE",
            "evidence": "Deferred to UI-I3",
        }
    return result

def render_ts(catalog: dict) -> str:
    lines = [
        'import type { AutomationEndpointCatalog } from "./endpoints";',
        "",
        "/** GENERATED FROM LIVE ROUTE DECORATORS — DO NOT HAND-EDIT */",
        "export const LIVE_AUTOMATION_ENDPOINTS: AutomationEndpointCatalog = {",
    ]
    ordered = [
        "sessions_collection", "session_detail", "session_import", "session_import_upload",
        "pipeline_job", "session_preflight", "session_mapping", "session_mapping_resolve",
        "session_quality", "signal_window", "session_metrics", "session_evidence",
        "review_cases", "session_audit",
    ]
    for name in ordered:
        entry = catalog[name]
        lines.append(f"  {name}: {{")
        t = entry.get("template")
        lines.append(f"    template: {json.dumps(t)},")
        lines.append(f"    verification: {json.dumps(entry['verification'])},")
        if entry.get("method"):
            lines.append(f"    method: {json.dumps(entry['method'])},")
        lines.append(f"    evidence: {json.dumps(entry['evidence'])},")
        lines.append("  },")
    lines.append("};")
    lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", nargs="?", default=".")
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()

    candidates = []
    for root in [
        repo / "services" / "api-server",
        repo / "services",
    ]:
        if root.exists():
            candidates.extend(root.rglob("*.py"))

    routes = []
    seen = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        routes.extend(scan_file(path, repo))

    catalog = match_expected(routes)

    out_json = repo / "qa-validation" / "evidence" / "ui-i2-backend-contract-audit.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps({
        "status": "PASS",
        "route_count": len(routes),
        "routes": [asdict(r) for r in routes],
        "catalog": catalog,
        "critical_required_verified": all(
            catalog[name]["verification"] == "VERIFIED"
            for name in [
                "sessions_collection",
                "session_detail",
                "session_import_upload",
                "pipeline_job",
                "session_preflight",
                "session_mapping",
                "session_mapping_resolve",
                "session_quality",
            ]
        ),
    }, indent=2), encoding="utf-8")

    out_ts = (
        repo / "apps" / "web-portal" / "src" / "lib" / "api" /
        "automation" / "live-endpoints.generated.ts"
    )
    out_ts.parent.mkdir(parents=True, exist_ok=True)
    out_ts.write_text(render_ts(catalog), encoding="utf-8")

    print(out_json)
    verified = [k for k, v in catalog.items() if v["verification"] == "VERIFIED"]
    missing = [
        k for k in EXPECTED
        if catalog[k]["verification"] != "VERIFIED"
    ]
    print("VERIFIED:", ", ".join(sorted(verified)) or "(none)")
    print("MISSING UI-I2 CRITICAL:", ", ".join(missing) or "(none)")
    return 0 if not missing else 4

if __name__ == "__main__":
    raise SystemExit(main())
