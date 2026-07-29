from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day29.contracts import RecordMeta
from day29.hierarchy_audit import audit_hierarchy
from day29.label_audit import audit_labels


def rec(record_id: str, day: str, source: str = "grip", canonical: str = "hand_close") -> RecordMeta:
    return RecordMeta(
        record_id=record_id, subject_id="s1", day_id=day, session_id=day,
        repetition_id=record_id, source_label=source, canonical_label=canonical,
        partition="train", signal_path=Path(f"/tmp/{record_id}.csv"),
        sampling_rate_hz=2048.0, signal_unit="uV", channel_count=2,
    )


def test_multi_day_hierarchy_verified():
    result = audit_hierarchy([rec("r1", "d1"), rec("r2", "d2")])
    assert result["status"] == "VERIFIED"


def test_duplicate_record_conflicting():
    result = audit_hierarchy([rec("r1", "d1"), rec("r1", "d2")])
    assert result["status"] == "CONFLICTING"


def test_unknown_cannot_be_rest():
    with pytest.raises(ValueError):
        audit_labels([rec("r1", "d1", source="unknown", canonical="rest")])
