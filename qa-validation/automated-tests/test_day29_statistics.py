from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day29.cross_day_drift import robust_shift
from day29.descriptive_stats import channel_statistics, mad


def test_basic_statistics():
    x = np.array([-1.0, 0.0, 1.0])
    stats = channel_statistics(x)
    assert stats["sample_count"] == 3
    assert np.isclose(stats["mean"], 0.0)
    assert np.isclose(stats["mav"], 2.0 / 3.0)
    assert np.isclose(stats["rms"], np.sqrt(2.0 / 3.0))


def test_mad_is_robust():
    x = np.array([0.0, 0.0, 1.0, 1000.0])
    assert mad(x) == 0.5


def test_robust_shift_direction():
    a = np.array([1.0, 1.1, 0.9, 1.05])
    b = np.array([2.0, 2.1, 1.9, 2.05])
    assert robust_shift(a, b) > 0
