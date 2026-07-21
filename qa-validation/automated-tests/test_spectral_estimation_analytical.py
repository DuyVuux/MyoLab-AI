from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "scripts" / "data"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from verify_spectral_estimation import build_report  # noqa: E402


def test_all_spectral_verification_checks_pass() -> None:
    report = build_report()
    assert report["verification_status"] == "passed"
    assert len(report["checks"]) >= 7
    assert all(item["status"] == "passed" for item in report["checks"])
