#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def load_module(repo: Path):
    ai_core_dir = repo / "ai-core"
    if str(ai_core_dir) not in sys.path:
        sys.path.insert(0, str(ai_core_dir))
    try:
        from governance import phase7r_release as mod
        return mod
    except ImportError:
        import importlib.util
        path = repo / "ai-core/governance/phase7r_release.py"
        spec = importlib.util.spec_from_file_location("phase7r_release", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load phase7r_release")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod


def discover_freeze_inputs(repo: Path) -> list[Path]:
    candidates = [
        repo / "qa-validation/evidence/public-benchmark-evidence-index.json",
        repo / "qa-validation/evidence/public-benchmark-evidence-index.yaml",
        repo / "qa-validation/evidence/research-dataset-freeze-v0.1.yaml",
        repo / "qa-validation/evidence/research-ml-splits-v0.1.csv",
        repo / "qa-validation/evidence/phase6r-leakage-audit.json",
        repo / "qa-validation/evidence/phase6r-branch-decision.json",
        repo / "docs/00-executive/milestones/m6-r-research-ml.md",
        repo / "docs/00-executive/gates/gate-f-r-research-ml-decision.md",
        repo / "ai-core/research/phase6r/governance/phase6r-to-locked-validation-handoff.yaml",
    ]
    for root in [repo / "qa-validation/evidence", repo / "ai-core/configs"]:
        if root.exists():
            for p in root.rglob("*"):
                n = p.name.lower()
                if p.is_file() and any(k in n for k in ("split", "freeze", "manifest", "contract", "threshold", "processing", "metric")):
                    if p.stat().st_size <= 5_000_000:
                        candidates.append(p)
    return [p for p in candidates if p.is_file()]


def write_json(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root", nargs="?", default=".")
    ap.add_argument("--freeze-only", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    mod = load_module(repo)

    evidence = repo / "qa-validation/evidence"
    entry = mod.evaluate_phase7_entry(repo)
    write_json(evidence / "phase7r-entry-preflight.json", entry.to_dict())
    if not entry.allowed:
        print("Phase 7R BLOCKED_WITH_EVIDENCE: entry preflight failed")
        return 2

    inputs = discover_freeze_inputs(repo)
    try:
        lock = mod.freeze_manifest(repo, inputs)
    except Exception as e:
        write_json(evidence / "phase7r-lock-failure.json", {"status": "BLOCKED_WITH_EVIDENCE", "error": str(e)})
        print(f"Phase 7R BLOCKED_WITH_EVIDENCE: {e}")
        return 3
    write_json(evidence / "final-locked-evaluation-cohort-v1.0.json", lock)

    checks = mod.verify_manifest(repo, lock)
    write_json(evidence / "phase7r-lock-verification.json", {"status": "PASS" if all(c.status == "PASS" for c in checks) else "FAIL", "checks": [c.__dict__ for c in checks]})
    if not all(c.status == "PASS" for c in checks):
        print("Phase 7R BLOCKED_WITH_EVIDENCE: lock verification failed")
        return 4

    if args.freeze_only:
        print("Phase 7R locked evaluation freeze PASS. No evaluation outcomes were consumed by this command.")
        return 0

    required = {
        "parser": repo / "qa-validation/validation-reports/final-parser-integrity-validation-v1.0.md",
        "qc": repo / "qa-validation/validation-reports/final-qc-locked-evaluation-v1.0.md",
        "metrics": repo / "qa-validation/validation-reports/final-processing-metric-validation-v1.0.md",
        "workflow_safety": repo / "qa-validation/validation-reports/final-workflow-safety-v1.0.md",
        "consolidated": repo / "docs/00-executive/M7-R-final-research-validation-report.md",
        "release_runbook": repo / "docs/portfolio/reproducible-release-runbook.md",
        "final_evidence_index": repo / "docs/portfolio/final-evidence-index.md",
    }
    missing = [name for name, p in required.items() if not p.is_file()]
    state = {
        "status": "BLOCKED_WITH_EVIDENCE" if missing else "READY_FOR_FINAL_GATE_AUDIT",
        "missing_validation_evidence": missing,
        "ml_default": "OFF",
        "research_ml": "RESEARCH_ML_NOT_JUSTIFIED",
        "locked_evaluation": "FROZEN",
        "clinical_validation": "NOT_PERFORMED",
    }
    write_json(evidence / "phase7r-completion-readiness.json", state)
    if missing:
        print("Phase 7R frozen successfully; validation execution remains incomplete:")
        for name in missing:
            print(f" - {name}")
        return 5
    print("Phase 7R evidence set is ready for final gate audit; no final status auto-promoted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
