"""DAY48 automated unit tests for research-only activation-timing eligibility."""

import sys
from pathlib import Path
import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SEMG_ROOT = REPO_ROOT / "packages" / "semg-core"
if str(SEMG_ROOT) not in sys.path:
    sys.path.insert(0, str(SEMG_ROOT))

from semg_core.metrics.activation_timing import TimingRequest, evaluate_activation_timing


def req(**k) -> TimingRequest:
    d = dict(
        fs_hz=1000.0,
        event_sample=100,
        sync_status="VERIFIED",
        processing_permission="ALLOW_PROFILED_PROCESSING",
        threshold=1.0,
        min_consecutive_samples=5,
        filter_delay_samples=0.0,
    )
    d.update(k)
    return TimingRequest(**d)


def make_signal() -> np.ndarray:
    x = np.zeros(500)
    x[150:] = 2.0
    return x


def test_missing_marker():
    r = evaluate_activation_timing(make_signal(), req(event_sample=None))
    assert r.status == "NOT_AVAILABLE"


def test_sync_unknown():
    r = evaluate_activation_timing(make_signal(), req(sync_status="UNKNOWN"))
    assert "MULTIMODAL_SYNC_NOT_VERIFIED" in r.reason_codes


def test_known_onset():
    r = evaluate_activation_timing(make_signal(), req())
    assert r.status == "ACTIVATION_TIMING_RESEARCH_ONLY"
    assert r.onset_sample == 150.0
    assert abs(r.relative_to_event_s - 0.05) < 1e-12


def test_filter_delay_correction():
    r = evaluate_activation_timing(make_signal(), req(filter_delay_samples=10.0))
    assert r.status == "ACTIVATION_TIMING_RESEARCH_ONLY"
    assert r.onset_sample == 140.0
    assert abs(r.relative_to_event_s - 0.04) < 1e-12


def test_no_threshold_no_invention():
    r = evaluate_activation_timing(make_signal(), req(threshold=None))
    assert r.status == "NOT_AVAILABLE"


def test_blocked_metric():
    r = evaluate_activation_timing(make_signal(), req(processing_permission="ABSTAIN"))
    assert r.status == "NOT_AVAILABLE"
