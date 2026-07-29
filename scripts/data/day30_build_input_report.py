#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]

KEY_FINDINGS = [
    "amplitude_scale_difference_about_40x",
    "sampling_rate_2048_vs_2000",
    "mendeley_dc_offset",
    "mendeley_ch4_low_amplitude_anomaly",
    "grabmyo_u1_u4_noise_floor",
    "channel_count_mismatch",
    "gesture_ontology_mismatch",
    "cross_day_vs_single_session",
]


def _load_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required evidence is missing: {path}")
    if path.suffix.lower() in {".yaml", ".yml"}:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"Evidence root must be an object: {path}")
    return document


def _dataset_input(path: Path) -> dict[str, Any]:
    decision = _load_mapping(path)
    return {
        "readiness_status": decision.get("status"),
        "test_set_opened": decision.get("test_set_opened"),
        "test_signal_rows_read": decision.get("test_signal_rows_read"),
        "source": str(path.relative_to(ROOT)),
    }


def build_report(
    mendeley_readiness: Path,
    grabmyo_readiness: Path,
) -> dict[str, Any]:
    mendeley = _dataset_input(mendeley_readiness)
    grabmyo = _dataset_input(grabmyo_readiness)
    statuses = {mendeley["readiness_status"], grabmyo["readiness_status"]}
    overall = (
        "GO_FOR_DAY30_HARMONIZATION"
        if statuses == {"GO_FOR_DAY30_HARMONIZATION"}
        else "BLOCKED_WITH_EVIDENCE"
    )
    return {
        "schema_version": "day30-pre-day30-input-baseline.v1",
        "overall_status": overall,
        "governance": {
            "test_set_opened": False,
            "training_allowed": False,
            "fatigue_inference_allowed": False,
        },
        "key_findings": KEY_FINDINGS,
        "datasets": {
            "mendeley": mendeley,
            "grabmyo": grabmyo,
        },
        "real_data_signal_rows_read": 0,
        "source_kind": "tracked_compact_readiness_evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the compact Day 30 input gate without reading signal rows."
    )
    parser.add_argument(
        "--mendeley-readiness",
        default=(
            "qa-validation/evidence/pre-day30/mendeley/"
            "day28-readiness-decision.yaml"
        ),
    )
    parser.add_argument(
        "--grabmyo-readiness",
        default=(
            "qa-validation/evidence/pre-day30/grabmyo/"
            "day29-readiness-decision.yaml"
        ),
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        report = build_report(
            ROOT / args.mendeley_readiness,
            ROOT / args.grabmyo_readiness,
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["overall_status"] == "GO_FOR_DAY30_HARMONIZATION" else 2
    except (OSError, ValueError, TypeError) as error:
        print(f"day30 input report failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
