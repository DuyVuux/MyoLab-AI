from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "qa-validation/evidence/day05-validation-report.json"

def main() -> int:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(ROOT / "qa-validation/automated-tests/governance/test_day05_privacy_gate.py")], cwd=ROOT)
    upstream = json.loads((ROOT / "qa-validation/evidence/day05-day04-handoff-snapshot.json").read_text(encoding="utf-8"))
    status = "BLOCKED_WITH_EVIDENCE_UPSTREAM_DAY04"
    report = {"engineering_validation": "PASS" if result.returncode == 0 else "FAIL", "tests_passed": result.returncode == 0, "day05_status": status, "site_privacy_approval_required": True, "go_for_day06": False}
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return result.returncode
if __name__ == "__main__": raise SystemExit(main())
