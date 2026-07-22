#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "docs/plans/DAY13_EXECUTION_PLAN.md",
    "docs/06-ai-signal-processing/explainable-rule-engine-spec.md",
    "services/inference-service/rules/fatigue_rule_v0.1.yaml",
    "services/inference-service/src/rule_config.py",
    "services/inference-service/src/rule_engine.py",
    "services/inference-service/src/rule_result_models.py",
    "packages/semg-core/semg_core/fatigue_rules.py",
    "packages/common-schemas/json/fatigue-rule-result.schema.json",
    "scripts/data/run_fatigue_rule.py",
    "scripts/dev/run_day13_checks.sh",
    "qa-validation/evidence/day13-fatigue-rule.json",
    "mlops/registry/rule_engines.yaml",
]


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    if missing:
        print("Thiếu artifact Day 13:")
        print("\n".join(f"- {item}" for item in missing))
        return 1
    for md in (ROOT / "docs").rglob("*.md"):
        if md.stat().st_size == 0:
            print("Markdown rỗng:", md)
            return 1
    print("Day 13 artifact check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
