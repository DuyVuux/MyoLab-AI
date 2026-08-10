#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "services/signal-ingestion-service/src/normalization/channel_mapper.py"
ONTOLOGY = ROOT / "clinical/ontologies/muscle-channel-ontology.v0.1.yaml"
POLICY = ROOT / "configs/validation/metadata-policy.v0.1.yaml"
LAYOUT = ROOT / "data-platform/contracts/channel-layout-context.v0.1.yaml"
RETENTION = ROOT / "data-platform/storage/unlabeled-corpus-retention-policy.v0.1.md"


def load_module():
    spec = importlib.util.spec_from_file_location("day14_validator_mapper", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load DAY14 channel mapper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures: list[str] = []
    mod = load_module()
    try:
        ontology = mod.load_ontology(ONTOLOGY)
        policy = mod.load_metadata_policy(POLICY)
        layout = yaml.safe_load(LAYOUT.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"contract load failed: {exc}")
        ontology = None
        policy = None
        layout = None

    if ontology is not None:
        if ontology["principles"]["fuzzy_matching_allowed"] is not False:
            failures.append("fuzzy mapping must remain disabled")
        if ontology["principles"]["site_mapping_coverage_complete"] is not False:
            failures.append("site coverage must not be claimed complete")

    if layout is not None:
        forbidden = set(layout.get("forbidden_at_day14", []))
        if "ood_score" not in forbidden:
            failures.append("DAY14 must explicitly forbid ood_score")
        default = layout.get("default_site_state", {})
        if default.get("geometry_status") not in {"UNKNOWN", "NOT_VERIFIED"}:
            failures.append("default site geometry cannot be promoted")

    if (
        policy is not None
        and policy.get("safety", {}).get("autofill_missing_metadata") is not False
    ):
        failures.append("metadata autofill must remain false")

    if not RETENTION.is_file():
        failures.append("missing DAY11 augmentation backfill: unlabeled corpus retention policy")

    result = {
        "day": 14,
        "ontology_loaded": ontology is not None,
        "metadata_policy_loaded": policy is not None,
        "layout_contract_loaded": layout is not None,
        "day11_retention_policy_present": RETENTION.is_file(),
        "ood_readiness_level": "METADATA_CONTRACT_ONLY",
        "ssl_readiness_level": "DATA_PROVENANCE_POLICY_ONLY",
        "ood_model_executed": False,
        "ssl_training_executed": False,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
