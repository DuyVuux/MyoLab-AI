from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

from data.day27.group_split import assert_no_overlap, build_subject_split


def test_subject_split_is_sealed_and_disjoint():
    rows = []
    for subject in range(12):
        for rep in range(3):
            rows.append({"subject_id":f"S{subject:02d}","repetition_id":str(rep)})
    split = build_subject_split(rows, dataset_id="FIXTURE")
    assert split["testSetSealed"] is True
    assert split["testOpened"] is False
    assert_no_overlap(split["groups"])
    assert set(split["groups"]["train"]) | set(split["groups"]["validation"]) | set(split["groups"]["test"]) == {f"S{i:02d}" for i in range(12)}
