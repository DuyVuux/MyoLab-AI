#!/usr/bin/env python3
"""Check required Day 2 artifacts and critical safety markers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_FILES = {
    "docs/11-operations/team-operating-model.md": [
        "Single-Operator Mode",
        "EXTERNAL_REVIEW_REQUIRED",
    ],
    "docs/02-clinical/protocol-library.md": [
        "quad-isometric-60s",
        "not approved",
    ],
    "docs/02-clinical/quality-escalation-policy.md": [
        "abstention",
        "analysis_allowed",
    ],
    "docs/06-ai-signal-processing/signal-import-spec.md": [
        "Generic CSV v0.1",
        "manifest",
    ],
    "docs/06-ai-signal-processing/signal-validation-spec.md": [
        "MFCV/CV eligibility",
        "Threshold policy",
    ],
    "clinical/protocols/quad-isometric-60s.v0.1.yaml": [
        "clinical_use_allowed: false",
        "minimum_sampling_rate_hz: 1000",
    ],
    "clinical/protocols/protocol-schema.json": [
        "sEMG Protocol Schema v0.1",
    ],
    "integrations/devices/generic-csv/format-spec.md": [
        "format fixture",
        "ACTIVE_DURATION_TOO_SHORT",
    ],
    "integrations/devices/generic-csv/adapter-config.yaml": [
        "direct_identifiers_allowed: false",
    ],
    "integrations/devices/generic-csv/sample_file.csv": [
        "time_s,VL_R_01",
    ],
    "integrations/devices/generic-csv/sample_file.manifest.json": [
        "format_only",
        "analysis_ready",
    ],
    "services/quality-gate-service/configs/qc_v0.1.yaml": [
        "critical_failure_blocks_analysis: true",
        "clinical_validation_status: not_validated",
    ],
    "services/quality-gate-service/src/reason_codes.py": [
        "ACTIVE_DURATION_TOO_SHORT",
        "MFCV_LINEAR_ARRAY_NOT_CONFIRMED",
    ],
    "packages/common-schemas/json/qc-result.schema.json": [
        "qc-result.v0.1",
        "analysis_allowed",
    ],
    "scripts/dev/validate_protocol.py": [
        "Draft202012Validator",
    ],
    "scripts/data/validate_signal_file.py": [
        "TIME_NOT_MONOTONIC",
        "expect-error",
    ],
    "qa-validation/requirements/day2-acceptance-criteria.md": [
        "Day 2",
        "expected negative test",
    ],
    "docs/01-product/backlog/day2-backlog.md": [
        "D2-001",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing: list[str] = []
    marker_failures: list[str] = []

    for relative, markers in REQUIRED_FILES.items():
        path = args.root / relative
        if not path.is_file():
            missing.append(relative)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in markers:
            if marker.lower() not in text.lower():
                marker_failures.append(f"{relative}: missing marker {marker!r}")

    if missing or marker_failures:
        print("DAY 2 ARTIFACT CHECK FAILED", file=sys.stderr)
        for item in missing:
            print(f"  MISSING: {item}", file=sys.stderr)
        for item in marker_failures:
            print(f"  CONTENT: {item}", file=sys.stderr)
        return 1

    print(f"DAY 2 ARTIFACT CHECK PASSED ({len(REQUIRED_FILES)} files checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
