import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import signal

BENCHMARK_VERSION = "public-metric-benchmark-v1.1"

def _bandpass(values_v: np.ndarray, fs_hz: float, low_hz: float, high_hz: float, order: int) -> np.ndarray:
    if not (0 < low_hz < high_hz < fs_hz / 2):
        raise ValueError("BANDPASS_NYQUIST_INVALID")
    sos = signal.butter(order, [low_hz, high_hz], btype="bandpass", fs=fs_hz, output="sos")
    return signal.sosfiltfilt(sos, values_v)

def compute_metrics_from_bronze(df: pd.DataFrame, 
                                low_hz: float = 20.0, 
                                high_hz: float = 400.0, 
                                order: int = 4,
                                nperseg: int = 1024,
                                noverlap: int = 512) -> dict:
    if df.empty:
        raise ValueError("EMPTY_DATAFRAME")
        
    source_id = str(df["source_id"].iloc[0])
    signal_name = str(df["signal_name"].iloc[0])
    fs_hz = float(df["fs_hz"].iloc[0])
    
    time_s = df["time_s"].to_numpy()
    values_v = df["value_v"].to_numpy()
    
    reasons = []
    if values_v.size < max(nperseg, 16):
        reasons.append("INSUFFICIENT_SAMPLES")
    if high_hz >= fs_hz / 2:
        reasons.append("PROCESSING_PROFILE_NOT_ELIGIBLE_FOR_FS")
    if not np.isfinite(values_v).all():
        reasons.append("NONFINITE_INPUT")
        
    if reasons:
        return {
            "source_id": source_id,
            "signal_name": signal_name,
            "fs_hz": fs_hz,
            "unit": "V",
            "sample_count": values_v.size,
            "status": "UNAVAILABLE",
            "reason_codes": tuple(sorted(set(reasons))),
            "rms": None, "mav": None, "mdf_hz": None, "mnf_hz": None,
            "benchmark_version": BENCHMARK_VERSION,
        }

    y = _bandpass(values_v, fs_hz, low_hz, high_hz, order)
    rms = float(np.sqrt(np.mean(np.square(y))))
    mav = float(np.mean(np.abs(y)))
    
    f, p = signal.welch(
        y, fs=fs_hz, window="hann", nperseg=nperseg, noverlap=noverlap,
        detrend="constant", scaling="density"
    )
    keep = (f >= low_hz) & (f <= min(high_hz, fs_hz / 2))
    f, p = f[keep], p[keep]
    total = float(np.trapezoid(p, f))
    
    if total <= 0 or len(f) < 2:
        return {
            "source_id": source_id,
            "signal_name": signal_name,
            "fs_hz": fs_hz,
            "unit": "V",
            "sample_count": values_v.size,
            "status": "UNAVAILABLE",
            "reason_codes": ("ZERO_OR_INSUFFICIENT_SPECTRAL_POWER",),
            "rms": rms, "mav": mav, "mdf_hz": None, "mnf_hz": None,
            "benchmark_version": BENCHMARK_VERSION,
        }
        
    mnf = float(np.trapezoid(f * p, f) / total)
    seg = 0.5 * (p[:-1] + p[1:]) * np.diff(f)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    half = total / 2.0
    idx = int(np.searchsorted(cum, half, side="left"))
    
    if idx == 0:
        mdf = float(f[0])
    else:
        c0, c1 = cum[idx - 1], cum[idx]
        frac = 0.0 if c1 == c0 else (half - c0) / (c1 - c0)
        mdf = float(f[idx - 1] + frac * (f[idx] - f[idx - 1]))
        
    return {
        "source_id": source_id,
        "signal_name": signal_name,
        "fs_hz": fs_hz,
        "unit": "V",
        "sample_count": values_v.size,
        "status": "AVAILABLE",
        "reason_codes": (),
        "rms": rms, "mav": mav, "mdf_hz": mdf, "mnf_hz": mnf,
        "benchmark_version": BENCHMARK_VERSION,
    }

def process_bronze_to_gold(bronze_dir: Path, gold_parquet_path: Path, gold_summary_path: Path):
    gold_parquet_path.parent.mkdir(parents=True, exist_ok=True)
    gold_summary_path.parent.mkdir(parents=True, exist_ok=True)
    
    rows = []
    for path in sorted(bronze_dir.rglob("*.parquet")):
        try:
            df = pd.read_parquet(path)
            row = compute_metrics_from_bronze(df)
            rows.append(row)
        except Exception as exc:
            rows.append({
                "source_id": path.stem,
                "signal_name": path.stem,
                "fs_hz": None,
                "unit": None,
                "sample_count": None,
                "status": "UNAVAILABLE",
                "reason_codes": (type(exc).__name__ + ":" + str(exc),),
                "rms": None, "mav": None, "mdf_hz": None, "mnf_hz": None,
                "benchmark_version": BENCHMARK_VERSION,
            })
            
    out_df = pd.DataFrame(rows)
    if not out_df.empty:
        out_df.to_parquet(gold_parquet_path, index=False)
    
    available = int((out_df["status"] == "AVAILABLE").sum()) if not out_df.empty else 0
    unavailable = int((out_df["status"] != "AVAILABLE").sum()) if not out_df.empty else 0
    report = {
        "benchmark_version": BENCHMARK_VERSION,
        "rows": len(rows),
        "available": available,
        "unavailable": unavailable,
    }
    gold_summary_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
