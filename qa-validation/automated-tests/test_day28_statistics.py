from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day28.label_audit import audit_labels
from day28.signal_quality import compute_channel_statistics


def test_channel_statistics_constant_signal() -> None:
    stats = compute_channel_statistics([5.0] * 100, 1000.0)
    assert stats.std_uV == 0.0
    assert stats.flatline_ratio == 1.0
    assert stats.rms_uV == 5.0


def test_nonfinite_ratio_is_reported() -> None:
    stats = compute_channel_statistics([1.0, float("nan"), 2.0, float("inf")], 1000.0)
    assert stats.nonfinite_ratio == 0.5
    assert stats.finite_count == 2


def test_label_audit_preserves_unknown() -> None:
    frame = pd.DataFrame([
        {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "train"},
        {"subject_id": "S1", "source_label": "Grip", "canonical_label": "hand_close", "partition": "train"},
        {"subject_id": "S1", "source_label": "Flexion", "canonical_label": "wrist_flexion", "partition": "train"},
        {"subject_id": "S1", "source_label": "Extension", "canonical_label": "wrist_extension", "partition": "train"},
        {"subject_id": "S1", "source_label": "Pronation", "canonical_label": "unknown", "partition": "train"},
    ])
    summary = audit_labels(frame, ["train", "validation"])
    assert summary.unknown_row_count == 1
    assert summary.hand_open_supported is False
    assert summary.core_classes_missing == []


def test_test_partition_is_rejected() -> None:
    frame = pd.DataFrame([
        {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "test"},
    ])
    with pytest.raises(ValueError, match="Sealed test"):
        audit_labels(frame, ["train", "validation"])
