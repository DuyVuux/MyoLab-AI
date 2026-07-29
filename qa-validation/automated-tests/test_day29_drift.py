from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day29.cross_day_drift import build_drift_summary


def test_drift_rows_forbid_fatigue_inference():
    rows = []
    for day, values in {"d1": [1.0, 1.1], "d2": [1.5, 1.6]}.items():
        for value in values:
            rows.append({
                "subject_id": "s1", "day_id": day, "canonical_label": "hand_close",
                "channel_id": "ch1", "rms": value,
            })
    output = build_drift_summary(rows, "rms")
    assert len(output) == 1
    assert output[0]["fatigue_inference_allowed"] is False
    assert output[0]["interpretation"] == "DISTRIBUTION_SHIFT_DESCRIPTIVE_ONLY"
