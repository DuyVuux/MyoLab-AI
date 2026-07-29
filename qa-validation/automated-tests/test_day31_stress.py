from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))

from stress_test_day31 import run_stress


def test_day31_stress_is_deterministic_bounded_and_fail_closed() -> None:
    first = run_stress(windows=96, channels=28)
    second = run_stress(windows=96, channels=28)

    assert first["pass"] is True
    assert first["feature_digest_sha256"] == second["feature_digest_sha256"]
    assert first["feature_rows_generated"] == 96 * 28 * 14
    assert first["forbidden_partition_attacks_blocked"] == first[
        "forbidden_partition_attacks"
    ]
    assert first["malformed_signal_attacks_blocked"] == first[
        "malformed_signal_attacks"
    ]
    assert first["nonfinite_attacks_blocked"] == first["nonfinite_attacks"]
    assert first["infinite_features_emitted"] == 0
    assert first["test_signal_rows_read"] == 0
    assert first["training_executed"] is False
    assert first["model_fitting_executed"] is False
    assert first["pooled_training_executed"] is False

