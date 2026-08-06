#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "packages" / "clinical-governance"
sys.path.insert(0, str(PKG))

from pre_day41_01.portfolio import validate_portfolio  # noqa: E402


def main() -> int:
    portfolio = ROOT / "clinical/governance/task-portfolio.v0.1.yaml"
    schema = ROOT / "packages/common-schemas/json/pre-day41-task-portfolio.schema.json"
    result = validate_portfolio(portfolio, schema)
    report = {
        "day": "PRE_DAY41_01",
        "gate": "PORTFOLIO_GATE_PASS" if result.ok else "BLOCKED_SCOPE_COLLISION",
        "ok": result.ok,
        "branch_ids": list(result.branch_ids),
        "errors": list(result.errors),
        "warnings": list(result.warnings),
        "training_executed": False,
        "sealed_test_rows_read": 0,
        "real_patient_rows_read": 0,
        "mfcv_site_eligibility": "NOT_VERIFIED",
        "handoff_target": "GO_FOR_PRE_DAY41_02_FUNCTIONAL_ANATOMY" if result.ok else "BLOCKED",
    }
    out = ROOT / "qa-validation/evidence/pre-day41-01-validation-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
