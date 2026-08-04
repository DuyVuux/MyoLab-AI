import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "quantitative"))
from day37.repeatability import pair_repeatability, within_subject_cv, robust_mad_ratio, bland_altman

def test_pair_repeatability():
    r = pair_repeatability(1.0, 1.1)
    assert r["absolute_difference"] > 0
    assert r["symmetric_relative_difference"] > 0

def test_cv_eligibility():
    assert within_subject_cv([1, 2], True)[1] == "INSUFFICIENT_REPETITIONS"
    assert within_subject_cv([1, 2, 3], False)[1] == "METRIC_NOT_POSITIVE_RATIO_SCALE"
    value, reason = within_subject_cv([1.0, 1.1, 0.9], True)
    assert reason is None and value > 0

def test_rmad():
    value, reason = robust_mad_ratio([1.0, 1.1, 0.9])
    assert reason is None and value > 0

def test_bland_altman_systematic_shift():
    result = bland_altman([1,2,3,4], [3,4,5,6])
    assert abs(result["bias"] - 2.0) < 1e-12
