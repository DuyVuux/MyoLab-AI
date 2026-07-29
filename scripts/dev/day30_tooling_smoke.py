#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))
sys.path.insert(0, str(ROOT / "scripts" / "data"))

from day30.channel_policy import decide_mendeley_ch4
from day30.contracts import PROJECT_CLASS_ORDER
from day30.ontology import build_ontology_report, load_supported_canonical_labels
from day30.policy_validation import (
    validate_channel_policy,
    validate_sampling_policy,
    validate_storage_contract,
    validate_windowing_policy,
)
from day30.preflight import validate_pre_day30_report
from day30.readiness import CONTRACT_CHECKS, decide_readiness
from day30.sample_rate import rational_resample_factors
from day30.view_registry import build_view_registry
from day30_build_input_report import build_report


def main() -> int:
    input_report = build_report(
        ROOT
        / "qa-validation/evidence/pre-day30/mendeley/"
        "day28-readiness-decision.yaml",
        ROOT
        / "qa-validation/evidence/pre-day30/grabmyo/"
        "day29-readiness-decision.yaml",
    )
    preflight = validate_pre_day30_report(input_report)
    mendeley = load_supported_canonical_labels(
        ROOT
        / "data-platform/manifests/public-datasets/"
        "mendeley-4channel-hand-gesture-v2/label-dictionary.yaml"
    )
    grabmyo = load_supported_canonical_labels(
        ROOT
        / "data-platform/manifests/public-datasets/"
        "grabmyo-canonical/label-dictionary.yaml"
    )
    ontology = build_ontology_report(mendeley, grabmyo, PROJECT_CLASS_ORDER)
    registry = build_view_registry(ontology)
    policies = {
        "sampling": validate_sampling_policy(
            ROOT / "ai-core/configs/day30_sampling_policy.research.yaml"
        ),
        "channels": validate_channel_policy(
            ROOT / "ai-core/configs/day30_channel_policy.research.yaml"
        ),
        "windowing": validate_windowing_policy(
            ROOT / "ai-core/configs/day30_windowing_policy.research.yaml"
        ),
        "storage": validate_storage_contract(
            ROOT / "data-platform/contracts/day30/storage-contract.yaml"
        ),
    }
    ch4 = decide_mendeley_ch4(
        {
            "EMG_Raw_CH1": 3.478,
            "EMG_RAW_CH2": 3.098,
            "EMG_RAW_CH3": 3.626,
            "EMG_RAW_CH4": 0.039,
        }
    )
    checks = {name: True for name in CONTRACT_CHECKS}
    readiness = decide_readiness(checks)
    result = {
        "schema_version": "day30-tooling-validation.v1",
        "preflight_pass": preflight["pass"],
        "intersection": ontology["intersection"],
        "view_count": len(registry["views"]),
        "policy_bundle_pass": all(item["pass"] for item in policies.values()),
        "ch4_status": ch4["status"],
        "resample_ratio": list(rational_resample_factors(2048, 2000)),
        "readiness_status": readiness["status"],
        "training_allowed": False,
        "pooled_training_allowed": False,
        "test_set_opened": False,
        "real_data_signal_rows_read": 0,
    }
    result["pass"] = (
        result["preflight_pass"]
        and result["intersection"]
        == ["rest", "hand_close", "wrist_flexion", "wrist_extension"]
        and result["view_count"] == 4
        and result["policy_bundle_pass"]
        and result["ch4_status"] == "QUARANTINED_EXCLUDED_PRIMARY"
        and result["resample_ratio"] == [125, 128]
        and result["readiness_status"]
        == "GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE"
    )
    output = ROOT / "qa-validation/evidence/day30/day30-tooling-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
