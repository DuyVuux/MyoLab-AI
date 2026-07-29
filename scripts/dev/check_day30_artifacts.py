#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = (
    "ai-core/configs/day30_harmonization.research.yaml",
    "ai-core/configs/day30_sampling_policy.research.yaml",
    "ai-core/configs/day30_channel_policy.research.yaml",
    "ai-core/configs/day30_windowing_policy.research.yaml",
    "ai-core/data/day30/policy_validation.py",
    "ai-core/data/day30/windowing.py",
    "data-platform/contracts/day30/storage-contract.yaml",
    "scripts/data/day30_run_harmonization.py",
    "scripts/dev/stress_test_day30.py",
    "scripts/dev/run_day30_checks.sh",
    "qa-validation/requirements/day30-acceptance-criteria.md",
    "packages/common-schemas/json/day30-window-index.v1.schema.json",
)
PROHIBITED_SUFFIXES = frozenset(
    {".pkl", ".pickle", ".joblib", ".onnx", ".pt", ".pth", ".mat", ".dat", ".hea"}
)
SAFE_ROOTS = (
    ROOT / "ai-core",
    ROOT / "data-platform",
    ROOT / "docs",
    ROOT / "environment",
    ROOT / "packages",
    ROOT / "qa-validation",
    ROOT / "scripts",
)


def _is_day30_asset(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if relative.parts[0] == "day30_dual_dataset_harmonization_pack":
        return False
    return "day30" in relative.as_posix().lower()


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    day30_assets = sorted(
        path
        for root in SAFE_ROOTS
        for path in root.rglob("*")
        if path.is_file() and _is_day30_asset(path)
    )
    prohibited = [
        str(path.relative_to(ROOT))
        for path in day30_assets
        if path.suffix.lower() in PROHIBITED_SUFFIXES
    ]
    unsafe_flags: list[str] = []
    unsafe_patterns = {
        "training": re.compile(r"(?:training_allowed:\s*true|\"training_allowed\"\s*:\s*true)", re.IGNORECASE),
        "pooled": re.compile(r"(?:pooled_training_allowed:\s*true|\"pooled_training_allowed\"\s*:\s*true)", re.IGNORECASE),
        "test": re.compile(r"(?:test_set_opened:\s*true|\"test_set_opened\"\s*:\s*true)", re.IGNORECASE),
    }
    for path in day30_assets:
        if path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in unsafe_patterns.items():
            if pattern.search(content):
                unsafe_flags.append(f"{path.relative_to(ROOT)}:{name}")
    result = {
        "schema_version": "day30-artifact-check.v1",
        "asset_count": len(day30_assets),
        "missing": missing,
        "prohibited_raw_or_model_artifacts": prohibited,
        "unsafe_flags": unsafe_flags,
        "reference_pack_excluded": True,
        "pass": not missing and not prohibited and not unsafe_flags,
    }
    output = ROOT / "qa-validation/evidence/day30/day30-artifact-check.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
