#!/usr/bin/env python3
"""Kiểm tra artifact và safety invariant của Day 10."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "packages/semg-core/semg_core/spectral_features.py",
    "services/feature-extraction-service/configs/frequency_features_v0.1.yaml",
    "services/feature-extraction-service/src/frequency_feature_config.py",
    "services/feature-extraction-service/src/frequency_feature_result_models.py",
    "services/feature-extraction-service/src/frequency_feature_extractor.py",
    "scripts/data/run_frequency_features.py",
    "scripts/data/verify_mdf_mnf.py",
    "packages/common-schemas/json/frequency-feature-row.schema.json",
    "packages/common-schemas/json/frequency-feature-extraction-result.schema.json",
    "qa-validation/requirements/day10-acceptance-criteria.md",
    "docs/06-ai-signal-processing/mdf-mnf-math-primer.md",
    "docs/06-ai-signal-processing/frequency-domain-feature-spec.md",
]


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    if missing:
        raise SystemExit("Thiếu artifact:\n- " + "\n- ".join(missing))
    config = (ROOT / "services/feature-extraction-service/configs/frequency_features_v0.1.yaml").read_text(encoding="utf-8")
    for required in (
        "clinical_validation_status: not_validated",
        "do_not_interpret_fatigue: true",
        "do_not_generate_frs: true",
        "do_not_train_ml: true",
    ):
        if required not in config:
            raise SystemExit(f"Thiếu safety invariant: {required}")
    for path in (ROOT / "docs").rglob("*.md"):
        if "day10" in str(path).lower() and not path.read_text(encoding="utf-8").strip():
            raise SystemExit(f"Markdown rỗng: {path}")
    print("Day 10 artifact/safety check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
