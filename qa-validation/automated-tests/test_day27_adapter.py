from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import numpy as np
from data.day27.profile_driven_csv_adapter import convert_wide_csv_smoke


def test_smoke_conversion_units_and_shape(tmp_path):
    profile = json.loads((ROOT/"qa-validation/test-data/day27/profile.synthetic-verified.json").read_text())
    source = ROOT/"qa-validation/test-data/day27/signal.synthetic.csv"
    result = convert_wide_csv_smoke(source, profile, tmp_path)
    payload = np.load(result.npz_path, allow_pickle=False)
    assert payload["samples_uV"].shape == (3, 4)
    assert payload["samples_uV"][0, 0] == 1.0
    assert result.channel_count == 4
