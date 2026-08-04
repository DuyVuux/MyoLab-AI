import sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "quantitative"))
from day37.supportability import metric_event

def test_supported_event():
    event = metric_event("similarity", "cosine", 0.9, "SUPPORTED", [], {"hash":"x"})
    assert event["hard_fatigue_diagnosis_allowed"] is False

def test_ineligible_zero_sentinel_blocked():
    with pytest.raises(ValueError):
        metric_event(
            "cocontraction", "mean_cci", 0,
            "NOT_ELIGIBLE_ANATOMICAL_MAPPING_UNVERIFIED",
            ["MAPPING_UNVERIFIED"], {"hash":"x"}
        )
