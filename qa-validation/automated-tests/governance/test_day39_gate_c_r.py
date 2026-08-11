from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_day39_gate_evaluator_passes():
    """Verify that Day 39 Gate Evaluator executes successfully and returns QC_RESEARCH_CORE_READY."""
    script = ROOT / "scripts/dev/day39_gate_evaluator.py"
    assert script.exists(), f"Gate evaluator script missing at {script}"

    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Gate evaluator failed: {proc.stderr}\nOutput: {proc.stdout}"

    decision_file = ROOT / "qa-validation/evidence/day39-gate-decision.json"
    assert decision_file.exists(), f"Gate decision output missing at {decision_file}"

    data = json.loads(decision_file.read_text(encoding="utf-8"))
    assert data.get("gate") == "GATE-C-R"
    assert data.get("status") == "QC_RESEARCH_CORE_READY"
    assert data.get("claim_scope") == "RESEARCH_ONLY"
    assert data.get("checks", {}).get("required_evidence_complete") is True
    assert data.get("checks", {}).get("freeze_hashes_match") is True
    assert data.get("checks", {}).get("site_threshold_status_not_verified") is True
    assert data.get("checks", {}).get("hard_integrity_false_allow_unresolved") is False
    assert data.get("checks", {}).get("final_qc_false_allow_zero") is True
    assert data.get("checks", {}).get("reproducibility_pass") is True
    assert data.get("checks", {}).get("locked_evaluation_consumed_zero") is True


def test_day39_claim_linter_passes():
    """Verify that Day 39 Claim Linter scans executive docs and finds zero forbidden claims."""
    script = ROOT / "scripts/dev/day39_claim_linter.py"
    assert script.exists(), f"Claim linter script missing at {script}"

    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Claim linter failed: {proc.stderr}\nOutput: {proc.stdout}"
    assert "DAY39 CLAIM LINTER PASS" in proc.stdout
