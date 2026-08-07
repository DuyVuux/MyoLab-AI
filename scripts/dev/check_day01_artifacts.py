#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

MANIFEST_REL=Path("qa-validation/evidence/day01-artifact-manifest.json")
REPORT_REL=Path("qa-validation/evidence/day01-validation-report.json")
REQUIRED=[
"clinical/governance/evidence-status-taxonomy.v0.1.yaml",
"data-platform/contracts/requirement-registry.v0.1.yaml",
"docs/00-executive/decisions/motionlab-rebaseline-decision-ledger.v0.1.yaml",
"docs/00-executive/day01/requirements-rebaseline-summary.v0.1.md",
"docs/01-product/motionlab-rebaseline/product-scope-delta.v0.1.md",
"docs/01-product/motionlab-rebaseline/open-questions-register.v0.1.yaml",
"docs/03-architecture/traceability/requirements-traceability-baseline.v0.1.csv",
"docs/03-architecture/traceability/source-of-truth-hierarchy.v0.1.yaml",
"packages/common-schemas/json/requirement-registry.schema.json",
"packages/common-schemas/json/decision-record.schema.json",
"packages/common-schemas/json/open-question.schema.json",
"qa-validation/automated-tests/governance/test_day01_requirements_rebaseline.py",
"qa-validation/requirements/day01-acceptance-criteria.md",
"qa-validation/traceability/day01-requirement-test-matrix.csv",
"qa-validation/evidence/day01-source-hash-ledger.json",
"qa-validation/evidence/day01-validation-report.json",
"scripts/dev/validate_day01_requirements.py",
"scripts/dev/check_day01_artifacts.py",
"scripts/dev/run_day01_checks.sh",
]
FORBIDDEN_DIRS={"__pycache__",".pytest_cache",".venv","env",".git","node_modules","raw","datasets","experiments","fixtures"}
FORBIDDEN_FILES={".DS_Store"}
FORBIDDEN_SUFFIXES={".pyc",".pyo",".mat",".c3d",".edf",".bdf",".h5",".hdf5",".npy",".npz",".pt",".pth",".ckpt",".onnx"}

def sha(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def static_files(root:Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if rel in {MANIFEST_REL,REPORT_REL}: continue
        if any(part in FORBIDDEN_DIRS for part in rel.parts): continue
        yield p,rel

def manifest_obj(root:Path):
    files=[{"path":rel.as_posix(),"size_bytes":p.stat().st_size,"sha256":sha(p)} for p,rel in static_files(root)]
    return {"version":"0.1","day":"DAY01","scope":"repo_patch static artifacts; excludes this manifest and generated validation report to avoid circularity","hash_algorithm":"SHA-256","files":files}

def forbidden(root:Path):
    bad=[]
    for p in root.rglob("*"):
        rel=p.relative_to(root)
        if any(x in FORBIDDEN_DIRS for x in rel.parts): continue
        if p.is_file() and (p.name in FORBIDDEN_FILES or p.suffix.lower() in FORBIDDEN_SUFFIXES):
            if p.name == "day5-preprocess-golden.npz": continue
            bad.append(rel.as_posix())
    return sorted(set(bad))

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument("--write-manifest",action="store_true")
    ap.add_argument("--verify-manifest",action="store_true")
    args=ap.parse_args()
    root=args.repo_root.resolve(); mpath=root/MANIFEST_REL
    failures=[]
    if args.write_manifest:
        mpath.parent.mkdir(parents=True,exist_ok=True)
        mpath.write_text(json.dumps(manifest_obj(root),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    missing=[x for x in REQUIRED if not (root/x).is_file()]
    if missing: failures.append(f"missing required files: {missing}")
    if not mpath.is_file(): failures.append(f"missing artifact manifest: {MANIFEST_REL}")
    bad=forbidden(root)
    if bad: failures.append(f"forbidden artifacts: {bad}")
    if args.verify_manifest and mpath.is_file():
        expected=json.loads(mpath.read_text(encoding="utf-8"))
        live=manifest_obj(root)
        if expected!=live: failures.append("artifact manifest does not match current static filesystem")
    if failures:
        for x in failures: print(f"[FAIL] {x}",file=sys.stderr)
        return 1
    print(f"[PASS] required={len(REQUIRED)+1}; static_manifest_entries={len(manifest_obj(root)['files'])}; forbidden=0")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
