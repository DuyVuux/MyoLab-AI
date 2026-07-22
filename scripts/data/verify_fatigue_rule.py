#!/usr/bin/env python3
"""Kiểm chứng các nhánh logic chính của fatigue_rule_v0.1."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in reversed((ROOT / "packages/semg-core", ROOT / "services/inference-service/src")):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from evidence_result_models import ChannelEvidence, FatigueEvidenceResult
from rule_config import load_rule_config
from rule_engine import ExplainableRuleEngine


def make_evidence(pattern: str, *, downstream: bool = True) -> FatigueEvidenceResult:
    channels = () if not downstream else (
        ChannelEvidence(
            channel_id="CH1",
            muscle="vastus_lateralis",
            side="right",
            role="primary",
            phase_id="active_contraction",
            status="evaluated",
            frequency_domain_status="supporting",
            amplitude_domain_status="supporting",
            pattern_category=pattern,
            feature_assessments=(),
            reason_codes=(),
        ),
    )
    return FatigueEvidenceResult(
        session_id=f"VERIFY_{pattern}",
        status="completed" if downstream else "abstained",
        downstream_allowed=downstream,
        abstention=not downstream,
        config_id="fatigue_evidence_v0.1",
        trend_config_id="trend_features_v0.1",
        trend_result_hash_sha256="a" * 64,
        reason_codes=(),
        channels=channels,
        result_hash_sha256="b" * 64 if downstream else None,
        limitations=(),
    )


def main() -> int:
    engine = ExplainableRuleEngine(
        load_rule_config(ROOT / "services/inference-service/rules/fatigue_rule_v0.1.yaml")
    )
    expected = {
        "multi_domain_change_pattern_observed": "supported_pattern",
        "frequency_decline_pattern_observed": "supported_pattern",
        "amplitude_increase_pattern_observed": "inconclusive",
        "partial_change_pattern_observed": "inconclusive",
        "evidence_mixed_or_opposite": "inconclusive",
        "insufficient_evidence": "inconclusive",
        "no_predefined_change_pattern_observed": "no_supported_pattern",
    }
    checks = []
    for pattern, conclusion in expected.items():
        result = engine.run(make_evidence(pattern))
        passed = result.overall_conclusion == conclusion
        checks.append({
            "check_id": pattern,
            "expected": conclusion,
            "actual": result.overall_conclusion,
            "passed": passed,
        })
    abstained = engine.run(make_evidence("insufficient_evidence", downstream=False))
    checks.append({
        "check_id": "upstream_abstention",
        "expected": "abstained",
        "actual": abstained.overall_conclusion,
        "passed": abstained.overall_conclusion == "abstained" and abstained.abstention,
    })
    payload = {
        "schema_version": "fatigue-rule-verification.v0.1",
        "passed": all(item["passed"] for item in checks),
        "checks": checks,
    }
    out_json = ROOT / "qa-validation/evidence/day13-rule-verification.json"
    out_md = ROOT / "qa-validation/evidence/day13-rule-verification.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Bằng chứng kiểm chứng Rule Engine Day 13", "", f"- Kết quả: **{'PASS' if payload['passed'] else 'FAIL'}**", ""]
    for item in checks:
        lines.append(f"- `{item['check_id']}`: {item['actual']} — {'PASS' if item['passed'] else 'FAIL'}")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("FATIGUE RULE VERIFICATION:", "PASS" if payload["passed"] else "FAIL")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
