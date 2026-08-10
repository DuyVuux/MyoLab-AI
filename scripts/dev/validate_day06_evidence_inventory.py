from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "qa-validation/evidence/day06-validation-report.json"


def main() -> int:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            str(
                ROOT
                / "qa-validation/automated-tests/governance/"
                "test_day06_evidence_inventory.py"
            ),
        ],
        cwd=ROOT,
        check=False,
    )

    report = {
        "engineering_validation": "PASS" if result.returncode == 0 else "FAIL",
        "tests_passed": result.returncode == 0,
        "day06_status": "BLOCKED_WITH_EVIDENCE_UPSTREAM_DAY05",
        "ready_for_data_request": result.returncode == 0,
        "go_for_day07": False,
        "real_site_evidence_received": False,
    }
    REPORT.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
