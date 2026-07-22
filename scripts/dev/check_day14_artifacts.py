#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "docs/plans/DAY14_EXECUTION_PLAN.md",
    "docs/06-ai-signal-processing/technical-confidence-spec.md",
    "services/inference-service/confidence/technical_confidence_v0.1.yaml",
    "services/inference-service/src/confidence.py",
    "services/inference-service/src/explainability.py",
    "services/inference-service/src/result_formatter.py",
    "packages/semg-core/semg_core/technical_confidence.py",
    "packages/semg-core/semg_core/safety_wording.py",
    "packages/common-schemas/json/explainable-inference-result.schema.json",
    "scripts/data/run_explainable_inference.py",
    "qa-validation/evidence/day14-explainable-inference.json",
    "mlops/registry/confidence_engines.yaml",
]


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    if missing:
        print("Thiếu artifact Day 14:\n" + "\n".join(f"- {item}" for item in missing))
        return 1
    print("Day 14 artifact check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
