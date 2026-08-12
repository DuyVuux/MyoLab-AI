from pathlib import Path
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/semg-core"))

from semg_core.processing.envelope import build_envelope  # noqa: E402
from semg_core.processing.masking import metric_mask_eligibility  # noqa: E402


def main():
    fs_hz = 1000.0
    time = np.arange(1000) / fs_hz
    values = np.sin(2 * np.pi * 50 * time)
    mask = np.zeros(1000, dtype=bool)
    mask[400:450] = True
    identity = {
        "window_id": "day43-evidence",
        "session_id": "s",
        "channel_id": "c",
        "start_sample": 0,
        "end_sample_exclusive": 1000,
    }
    result = build_envelope(
        values,
        fs_hz,
        identity,
        mask=mask,
    )
    eligibility = metric_mask_eligibility(
        mask,
        qc_signal_quality="PASS",
        processing_permission="ALLOW_PROFILED_PROCESSING",
    )
    raw_expected = np.sin(2 * np.pi * 50 * time)
    passed = (
        len(values) == len(result.values)
        and np.array_equal(mask, result.mask)
        and not eligibility["eligible"]
    )
    output = {
        "sample_count_in": len(values),
        "sample_count_out": len(result.values),
        "mask_count_in": int(mask.sum()),
        "mask_count_out": int(result.mask.sum()),
        "masked_values_are_nan": bool(np.isnan(result.values[mask]).all()),
        "raw_unchanged": bool(np.allclose(values, raw_expected)),
        "metric_eligible": bool(eligibility["eligible"]),
        "metric_reason_codes": eligibility["reason_codes"],
        "status": "PASS" if passed else "FAIL",
    }
    evidence_path = (
        ROOT / "qa-validation/evidence/day43-envelope-masking-evidence.json"
    )
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
