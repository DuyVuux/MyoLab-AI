from __future__ import annotations

import json
from pathlib import Path
import pytest
import subprocess
import sys

def test_phase7r_accelerated_critical_path_execution(tmp_path: Path):
    repo = Path(".").resolve()
    script = repo / "scripts/dev/finish_phase7r_critical_path.py"
    assert script.is_file()
    
    cmd = [sys.executable, str(script), str(repo)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"stdout: {res.stdout}\nstderr: {res.stderr}"
    assert "Phase 7R accelerated critical path completed." in res.stdout
    assert "Final-R: READY_WITH_LIMITATIONS" in res.stdout or "Final-R: PORTFOLIO_RESEARCH_READY" in res.stdout

def test_phase7r_required_artifacts_exist():
    repo = Path(".").resolve()
    expected_artifacts = [
        repo / "qa-validation/validation-reports/final-parser-integrity-validation-v1.0.md",
        repo / "qa-validation/evidence/final-parser-integrity-results-v1.0.json",
        repo / "qa-validation/validation-reports/final-qc-validation-v1.0.md",
        repo / "qa-validation/validation-reports/final-qc-locked-evaluation-v1.0.md",
        repo / "ai-core/metrics/final-qc-metrics-v1.0.json",
        repo / "qa-validation/validation-reports/final-processing-metric-validation-v1.0.md",
        repo / "qa-validation/evidence/final-processing-metric-results-v1.0.json",
        repo / "qa-validation/evidence/locked-technical-validation-ledger-v1.0.json",
        repo / "qa-validation/validation-reports/final-workflow-safety-v1.0.md",
        repo / "qa-validation/evidence/final-workflow-safety-results-v1.0.json",
        repo / "clinical/studies/nonclinical-time-on-task-v1.0.md",
        repo / "clinical/studies/process-mining-demo-analysis-v1.0.md",
        repo / "clinical/studies/process-variant-comparison-v1.0.csv",
        repo / "qa-validation/evidence/nonclinical-workflow-study-status-v1.0.json",
        repo / "docs/00-executive/final-research-validation-report.md",
        repo / "docs/00-executive/M7-R-final-research-validation-report.md",
        repo / "ai-core/metrics/final-kpi-snapshot-v1.0.json",
        repo / "scripts/demo/bootstrap_and_run.sh",
        repo / "docs/portfolio/architecture-overview.md",
        repo / "docs/portfolio/demo-guide.md",
        repo / "docs/portfolio/limitations-and-claims.md",
        repo / "docs/portfolio/cv-and-interview-evidence-map.md",
        repo / "docs/portfolio/reproducible-release-runbook.md",
        repo / "CHANGELOG.md",
        repo / "qa-validation/evidence/final-release-audit-v1.0.json",
        repo / "docs/portfolio/final-evidence-index.md",
        repo / "docs/portfolio/project-provenance-statement.md",
        repo / "docs/portfolio/cv-positioning.md",
        repo / "docs/00-executive/gates/FINAL-R-portfolio-readiness-decision.md",
        repo / "docs/00-executive/milestones/M7-R-portfolio-release.md",
        repo / "phase7r-accelerated-completion-report.md"
    ]
    for art in expected_artifacts:
        assert art.is_file(), f"Missing artifact: {art}"

def test_phase7r_locked_ledger_contract():
    repo = Path(".").resolve()
    ledger_path = repo / "qa-validation/evidence/locked-technical-validation-ledger-v1.0.json"
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert data["locked_evaluation_status"] == "CONSUMED_ONCE_AFTER_FREEZE"
    assert data["retuning_performed"] is False
    assert data["parser"]["status"] == "PASS"
    assert data["qc"]["status"] == "PASS"
    assert data["processing_metrics"]["status"] == "PASS"

def test_phase7r_release_audit_clean():
    repo = Path(".").resolve()
    audit_path = repo / "qa-validation/evidence/final-release-audit-v1.0.json"
    data = json.loads(audit_path.read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["secret_findings_count"] == 0
    assert data["claim_violations_count"] == 0
