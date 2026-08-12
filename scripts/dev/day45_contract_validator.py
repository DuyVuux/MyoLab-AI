#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys
import yaml
import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SEMG_ROOT = ROOT / "packages/semg-core"
sys.path.insert(0, str(SEMG_ROOT))
from semg_core.provenance.processing_manifest import (
    CodeComponentRef, ProcessingOutcome, ProcessingProfileRef, ProcessingStepRecord,
    RawSourceRef, WindowRef, build_processing_manifest, canonical_sha256,
)


def main() -> int:
    required = [
        "data-platform/contracts/processing-manifest.v0.1.yaml",
        "data-platform/events/processing-event-emission-contract.v0.1.yaml",
        "packages/semg-core/semg_core/provenance/processing_manifest.py",
        "packages/common-schemas/json/processing-manifest.schema.json",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"missing required outputs: {missing}")
    contract = yaml.safe_load((ROOT / required[0]).read_text())
    events = yaml.safe_load((ROOT / required[1]).read_text())
    if contract["claim_scope"] != "RESEARCH_ONLY":
        raise SystemExit("claim scope violation")
    expected_events = {
        "PROCESSING_STARTED", "PROCESSING_COMPLETED",
        "PROCESSING_FAILED", "REPROCESS_TRIGGERED",
    }
    if set(events["allowed_event_types"]) != expected_events:
        raise SystemExit("processing event set mismatch")
    if events["persistent_event_store_implemented"] is not False:
        raise SystemExit("DAY45 must not claim persistent event store")
    schema = json.loads((ROOT / required[3]).read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    print(
        json.dumps(
            {
                "status": "PASS",
                "events": len(expected_events),
                "required_outputs": len(required),
            }
        )
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
