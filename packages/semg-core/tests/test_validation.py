from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SEMGC_PATH = ROOT / "packages" / "semg-core"
if str(SEMGC_PATH) not in sys.path:
    sys.path.insert(0, str(SEMGC_PATH))

from semg_core.validation import (  # noqa: E402
    infer_sampling_rate_hz,
    relative_timing_jitter,
    validate_time_axis,
)


def test_sampling_rate_inference() -> None:
    time_s = np.arange(10_000, dtype=float) / 1000.0
    assert abs(infer_sampling_rate_hz(time_s) - 1000.0) < 1e-9
    assert relative_timing_jitter(time_s) < 1e-10
    assert validate_time_axis(time_s, 1000.0) == []


def test_sampling_rate_mismatch_is_blocking() -> None:
    time_s = np.arange(1000, dtype=float) / 500.0
    issues = validate_time_axis(time_s, 1000.0)
    assert "SAMPLING_RATE_MISMATCH" in {issue.code for issue in issues if issue.blocking}
