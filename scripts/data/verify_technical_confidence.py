#!/usr/bin/env python3
"""Kiểm chứng công thức confidence, cap và wording guard."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "packages/semg-core") not in sys.path:
    sys.path.insert(0, str(ROOT / "packages/semg-core"))

from semg_core.technical_confidence import ConfidenceComponent, weighted_score, categorize_score, apply_conclusion_cap
from semg_core.safety_wording import safe_summary, scan_prohibited_phrases


def main() -> int:
    components = [
        ConfidenceComponent("qc", 1.0, 0.35, "R", {}),
        ConfidenceComponent("usable", 0.8, 0.25, "R", {}),
        ConfidenceComponent("trend", 0.5, 0.20, "R", {}),
        ConfidenceComponent("consistency", 1.0, 0.20, "R", {}),
    ]
    score = weighted_score(components)
    thresholds = {"engineering_high_min": 0.8, "engineering_moderate_min": 0.6, "engineering_low_min": 0.4}
    capped, cap_reason = apply_conclusion_cap(0.9, "inconclusive", {"inconclusive": 0.59})
    safe = safe_summary("supported_pattern")
    hits = scan_prohibited_phrases([safe], ["chẩn đoán mỏi cơ", "bắt buộc dừng bài tập"])
    checks = [
        {"check_id": "weighted_known_answer", "passed": abs(score - 0.85) < 1e-12, "actual": score},
        {"check_id": "category_high", "passed": categorize_score(score, thresholds) == "engineering_high"},
        {"check_id": "inconclusive_cap", "passed": capped == 0.59 and cap_reason == "CONFIDENCE_CAPPED_BY_INCONCLUSIVE"},
        {"check_id": "safe_wording", "passed": hits == (), "hits": list(hits)},
    ]
    payload = {"schema_version": "technical-confidence-verification.v0.1", "passed": all(item["passed"] for item in checks), "checks": checks}
    out_json = ROOT / "qa-validation/evidence/day14-confidence-verification.json"
    out_md = ROOT / "qa-validation/evidence/day14-confidence-verification.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out_md.write_text("# Bằng chứng kiểm chứng confidence Day 14\n\n" + "\n".join(f"- `{item['check_id']}`: {'PASS' if item['passed'] else 'FAIL'}" for item in checks) + "\n", encoding="utf-8")
    print("TECHNICAL CONFIDENCE VERIFICATION:", "PASS" if payload["passed"] else "FAIL")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
