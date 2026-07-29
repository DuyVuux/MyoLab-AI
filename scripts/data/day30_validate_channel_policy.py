#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day30.channel_policy import (
    decide_mendeley_ch4,
    expand_grabmyo_primary_channels,
    grabmyo_excluded_channels,
)
from day30.policy_validation import validate_channel_policy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
        default="ai-core/configs/day30_channel_policy.research.yaml",
    )
    parser.add_argument(
        "--output",
        default="qa-validation/evidence/day30/day30-channel-decision.json",
    )
    args = parser.parse_args()
    policy_validation = validate_channel_policy(ROOT / args.policy)
    ch4 = decide_mendeley_ch4(
        {
            "EMG_Raw_CH1": 3.478,
            "EMG_RAW_CH2": 3.098,
            "EMG_RAW_CH3": 3.626,
            "EMG_RAW_CH4": 0.039,
        }
    )
    result = {
        "schema_version": "day30-channel-decision.v1",
        "mendeley_ch4": ch4,
        "grabmyo_primary_channels": list(expand_grabmyo_primary_channels()),
        "grabmyo_excluded_channels": list(grabmyo_excluded_channels()),
        "direct_anatomical_mapping_allowed": False,
        "pass": (
            policy_validation["pass"]
            and ch4["status"] == "QUARANTINED_EXCLUDED_PRIMARY"
        ),
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
