from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import pytest
from data.day27.label_mapping import LabelMappingError, map_label, validate_label_map


def test_verified_mapping():
    cfg = json.loads((ROOT/"qa-validation/test-data/day27/label-map.synthetic-verified.json").read_text())
    mapping = validate_label_map(cfg)
    assert map_label("OPEN", mapping) == "hand_open"


def test_unknown_does_not_default_to_rest():
    cfg = json.loads((ROOT/"qa-validation/test-data/day27/label-map.synthetic-verified.json").read_text())
    mapping = validate_label_map(cfg)
    with pytest.raises(LabelMappingError):
        map_label("UNKNOWN", mapping)
