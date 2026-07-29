from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day29.contracts import RecordMeta
from day29.partition_guard import assert_record_visible


def make_record(partition: str, path: str = "/data/train/signal.csv") -> RecordMeta:
    return RecordMeta(
        record_id="r1", subject_id="s1", day_id="d1", session_id="sess1",
        repetition_id="rep1", source_label="g", canonical_label="hand_close",
        partition=partition, signal_path=Path(path), sampling_rate_hz=2048.0,
        signal_unit="uV", channel_count=2,
    )


def test_train_is_visible():
    assert_record_visible(make_record("train"))


def test_test_partition_is_blocked():
    with pytest.raises(PermissionError):
        assert_record_visible(make_record("test", "/data/test/signal.csv"))


def test_test_token_in_path_is_blocked():
    with pytest.raises(PermissionError):
        assert_record_visible(make_record("validation", "/data/sealed-test/signal.csv"))
