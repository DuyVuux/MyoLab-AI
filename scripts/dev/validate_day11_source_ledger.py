from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "services/signal-ingestion-service/src/provenance/source_ledger.py"
SCHEMA_PATH = ROOT / "packages/common-schemas/json/source-record.schema.json"
GOLDEN = ROOT / "qa-validation/test-data/golden/provenance/day11/synthetic-mr4-source.csv"


def load_module():
    spec = importlib.util.spec_from_file_location("day11_source_ledger_validator", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_module()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)

    with tempfile.TemporaryDirectory(prefix="day11-validate-") as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "synthetic.csv"
        source.write_bytes(GOLDEN.read_bytes())
        before = source.read_bytes()

        ledger = module.JsonlSourceLedger(tmp_path / "ledger.jsonl")
        result = ledger.register_source(
            source,
            storage_reference="qa://day11/validator",
            metadata=module.SourceMetadata(
                original_filename="synthetic.csv",
                device_vendor="Noraxon",
                device_family="Ultium EMG",
                software_name="Noraxon MR",
                software_version="4.0.22",
                export_family="MR4_SINGLE_CSV",
            ),
            governance=module.GovernanceMetadata(
                deidentification_status="NOT_APPLICABLE_SYNTHETIC",
                governance_status="APPROVED_FOR_DEFINED_PURPOSE",
                research_reuse_eligible=False,
                retention_class="SYNTHETIC_QA",
            ),
            evidence_status="VERIFIED",
            ingestion_timestamp=datetime(2026, 8, 10, tzinfo=timezone.utc),
        )
        jsonschema.Draft202012Validator(schema).validate(asdict(result.source_record))
        if source.read_bytes() != before:
            raise RuntimeError("Raw bytes changed during registration")
        ledger.verify_source(source, result.source_record)

    print("DAY11 source ledger contract validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
