from __future__ import annotations

import json
from pathlib import Path

import pytest

from data.group_split_v2 import GroupSplitError, assert_no_group_leakage, build_group_split

ROOT = Path(__file__).resolve().parents[2]
METADATA = ROOT / "qa-validation/test-data/synthetic/day25-subject-session-metadata.json"


def records() -> list[dict]:
    return json.loads(METADATA.read_text(encoding="utf-8"))


def test_subject_split_is_deterministic_and_sealed() -> None:
    first = build_group_split(records(), dataset_id="SYN", seed=2501)
    second = build_group_split(records(), dataset_id="SYN", seed=2501)
    assert first == second
    assert first["groupUnit"] == "subject"
    assert first["testSetSealed"] is True


def test_group_sets_do_not_overlap() -> None:
    result = build_group_split(records(), dataset_id="SYN", seed=2501)
    groups = result["groups"]
    assert_no_group_leakage(groups["train"], groups["validation"], groups["test"])


def test_window_grouping_is_rejected() -> None:
    with pytest.raises(GroupSplitError, match="GROUP_UNIT_MUST_BE_SUBJECT_OR_SESSION"):
        build_group_split(records(), dataset_id="SYN", group_unit="window")


def test_explicit_leakage_is_rejected() -> None:
    with pytest.raises(GroupSplitError, match="TRAIN_TEST_GROUP_LEAKAGE"):
        assert_no_group_leakage(["S1", "S2"], ["S3"], ["S2", "S4"])
