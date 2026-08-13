import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add data-platform to path so we can import adapters
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "data-platform"))
from adapters.vinmec.noraxon_parser import parse_noraxon_separated_emg

def make_csv(path: Path, fs=2000, seconds=1.0, unit="uV", freq=100.0, valid=True):
    if not valid:
        path.write_text("invalid\n", encoding="utf-8")
        return
    n = int(fs * seconds)
    t = np.arange(n) / fs
    x = 100.0 * np.sin(2*np.pi*freq*t)
    lines = [
        "type,name,time_units,begin_time,frequency,count,units",
        f"signal,Ultium_EMG-LT_TEST,s,0.00000,{fs},{n},{unit}",
        "",
        "time,value",
    ]
    lines += [f"{ti:.8f},{xi:.8f}" for ti, xi in zip(t, x)]
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")

def test_parse_success(tmp_path):
    p = tmp_path / "Ultium_EMG-LT_TEST.csv"
    make_csv(p)
    df = parse_noraxon_separated_emg(p)
    assert not df.empty
    assert "time_s" in df.columns
    assert "value_v" in df.columns
    assert df["signal_name"].iloc[0] == "Ultium_EMG-LT_TEST"
    assert df["fs_hz"].iloc[0] == 2000
    # verify conversion uV to V
    assert np.max(df["value_v"]) < 1e-3

def test_unknown_unit_fails_closed(tmp_path):
    p = tmp_path / "Ultium_EMG-LT_TEST.csv"
    make_csv(p, unit="mystery")
    with pytest.raises(ValueError, match="UNIT_MISMATCH"):
        parse_noraxon_separated_emg(p)

def test_short_csv_fails(tmp_path):
    p = tmp_path / "Ultium_EMG-LT_TEST.csv"
    make_csv(p, valid=False)
    with pytest.raises(ValueError, match="INGEST_SCHEMA_ERROR"):
        parse_noraxon_separated_emg(p)
