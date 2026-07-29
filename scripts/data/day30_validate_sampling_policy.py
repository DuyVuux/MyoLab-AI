#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day30.policy_validation import validate_sampling_policy
from day30.sample_rate import rational_resample_factors, samples_for_ms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
        default="ai-core/configs/day30_sampling_policy.research.yaml",
    )
    parser.add_argument(
        "--output",
        default="qa-validation/evidence/day30/day30-sampling-policy-validation.json",
    )
    args = parser.parse_args()
    result = validate_sampling_policy(ROOT / args.policy)
    result.update(
        {
            "schema_version": "day30-sampling-validation.v1",
            "native_sample_counts": {
                str(duration): {
                    "mendeley_2000": samples_for_ms(2000, duration),
                    "grabmyo_2048": samples_for_ms(2048, duration),
                }
                for duration in (75, 100, 125, 150, 200, 250, 500, 1000)
            },
            "grabmyo_2048_to_2000": dict(
                zip(("up", "down"), rational_resample_factors(2048, 2000))
            ),
            "primary_mode": "native_rate",
            "sample_rounding": "round_half_up",
        }
    )
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
