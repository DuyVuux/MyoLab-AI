#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "docs/plans/DAY15_EXECUTION_PLAN.md",
    "docs/03-architecture/offline-analysis-orchestration.md",
    "docs/05-data/offline-analysis-manifest-contract.md",
    "ai-core/configs/offline_analysis_mvp0.yaml",
    "ai-core/pipelines/analysis_manifest.py",
    "ai-core/pipelines/offline_analysis.py",
    "ai-core/pipelines/run_offline_analysis.py",
    "packages/common-schemas/json/offline-analysis-manifest.schema.json",
    "scripts/data/verify_offline_analysis_package.py",
    "qa-validation/evidence/day15-golden-run/11-analysis-manifest.json",
    "qa-validation/evidence/day15-warning-run/11-analysis-manifest.json",
    "qa-validation/evidence/day15-abstained-run/11-analysis-manifest.json",
    "mlops/registry/analysis_pipelines.yaml",
]


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    if missing:
        print("Thiếu artifact Day 15:\n" + "\n".join(f"- {item}" for item in missing))
        return 1
    print("Day 15 artifact check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
