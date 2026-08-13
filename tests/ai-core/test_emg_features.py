import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))
from pipelines.emg_feature_extraction import compute_metrics_from_bronze

def test_compute_metrics_from_bronze():
    fs = 2000
    seconds = 1.0
    freq = 100.0
    n = int(fs * seconds)
    t = np.arange(n) / fs
    # Generate in Volts
    x = 100.0 * 1e-6 * np.sin(2*np.pi*freq*t)
    
    df = pd.DataFrame({
        "time_s": t,
        "value_v": x,
        "source_id": "test_id",
        "signal_name": "test_signal",
        "fs_hz": fs
    })
    
    result = compute_metrics_from_bronze(df)
    assert result["status"] == "AVAILABLE"
    assert result["rms"] is not None and result["rms"] > 0
    assert result["mav"] is not None and result["mav"] > 0
    assert 90 < result["mdf_hz"] < 110
    assert 90 < result["mnf_hz"] < 110

def test_insufficient_samples_returns_unavailable():
    df = pd.DataFrame({
        "time_s": [0.0],
        "value_v": [0.0],
        "source_id": "test_id",
        "signal_name": "test_signal",
        "fs_hz": 2000
    })
    
    result = compute_metrics_from_bronze(df)
    assert result["status"] == "UNAVAILABLE"
    assert "INSUFFICIENT_SAMPLES" in result["reason_codes"]
    assert result["rms"] is None
