#!/usr/bin/env python3
"""Check that mandatory Day 3 artifacts exist and contain safety markers."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "docs/05-data/normalized-signal-object.md",
    "docs/06-ai-signal-processing/data-ingestion-adapter-spec.md",
    "services/signal-ingestion-service/README.md",
    "services/signal-ingestion-service/src/importers/base_importer.py",
    "services/signal-ingestion-service/src/importers/csv_importer.py",
    "services/signal-ingestion-service/src/normalizers/unit_normalizer.py",
    "services/signal-ingestion-service/src/normalizers/channel_mapper.py",
    "services/signal-ingestion-service/src/normalizers/metadata_extractor.py",
    "services/signal-ingestion-service/src/validators/file_format_validator.py",
    "services/signal-ingestion-service/src/validators/metadata_validator.py",
    "packages/semg-core/semg_core/io.py",
    "packages/semg-core/semg_core/validation.py",
    "packages/common-schemas/json/normalized-signal-summary.schema.json",
    "data-platform/synthetic-data/generate_synthetic_semg.py",
    "data-platform/synthetic-data/golden_signal_01.csv",
    "data-platform/synthetic-data/golden_signal_01.manifest.json",
    "data-platform/synthetic-data/golden_signal_01.expected_ingestion_summary.json",
    "scripts/data/import_signal_session.py",
    "qa-validation/requirements/day3-acceptance-criteria.md",
    "qa-validation/evidence/day3-ingestion-evidence.template.md",
]


def main() -> int:
    failures: list[str] = []
    for relative in REQUIRED:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"Missing or empty: {relative}")

    manifest_path = ROOT / "data-platform/synthetic-data/golden_signal_01.manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("clinical_use_allowed") is not False:
            failures.append("Synthetic manifest must set clinical_use_allowed=false")
        electrode = manifest.get("electrode_config", {})
        if electrode.get("mfcv_candidate") is not False:
            failures.append("Day 3 single-bipolar fixture must not claim MFCV eligibility")
        if not manifest.get("source_hash_sha256"):
            failures.append("Synthetic manifest must preserve source_hash_sha256")
        phases = {item.get("phase_id") for item in manifest.get("phase_markers", [])}
        required_phases = {"baseline_rest", "active_contraction", "recovery"}
        if not required_phases <= phases:
            failures.append("Synthetic manifest must contain baseline/active/recovery phases")

    importer_path = ROOT / "services/signal-ingestion-service/src/importers/csv_importer.py"
    if importer_path.is_file():
        text = importer_path.read_text(encoding="utf-8")
        for token in ("SOURCE_HASH_MISMATCH", "validate_time_axis", "NormalizedSignal"):
            if token not in text:
                failures.append(f"csv_importer.py missing required behavior token: {token}")

    if failures:
        print("DAY 3 ARTIFACT CHECK FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("DAY 3 ARTIFACT CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
