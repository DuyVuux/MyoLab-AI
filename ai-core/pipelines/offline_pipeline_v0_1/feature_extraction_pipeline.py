#!/usr/bin/env python3
import sys
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal

# Add paths to import from other services
current_file = Path(__file__).resolve()
project_root = current_file.parents[3]
adapters_dir = project_root / "data-platform" / "adapters" / "vinmec"
feature_extraction_dir = project_root / "services" / "feature-extraction-service" / "src"
sys.path.insert(0, str(adapters_dir))
sys.path.insert(0, str(feature_extraction_dir))

from noraxon_parser import parse_noraxon_separated_emg, discover_vinmec_emg_files, sha256_file
from routers.extraction import extract_time_domain, extract_frequency_domain
from schemas.api_schemas import TimeDomainMathRequest, FrequencyDomainMathRequest

BENCHMARK_VERSION = "public-metric-benchmark-v1.0"
CLAIM_SCOPE = "RESEARCH_ONLY"

def _bandpass(values_v: np.ndarray, fs_hz: float, low_hz: float, high_hz: float, order: int) -> np.ndarray:
    if not (0 < low_hz < high_hz < fs_hz / 2):
        raise ValueError("BANDPASS_NYQUIST_INVALID")
    sos = signal.butter(order, [low_hz, high_hz], btype="bandpass", fs=fs_hz, output="sos")
    return signal.sosfiltfilt(sos, values_v)

def compute_metrics(
    path: Path,
    *,
    profile_id: str = "day68-site-research-bandpass20-400-v0.1",
    low_hz: float = 20.0,
    high_hz: float = 400.0,
    order: int = 4,
    nperseg: int = 1024,
    noverlap: int = 512,
) -> dict:
    try:
        df = parse_noraxon_separated_emg(path)
        fs_hz = df["fs_hz"].iloc[0]
        signal_name = df["signal_name"].iloc[0]
        values = df["value_v"].to_numpy()
        source_sha256 = sha256_file(path)
    except Exception as exc:
        return {
            "source_id": "src_sha256_" + sha256_file(path),
            "signal_name": path.stem,
            "fs_hz": None,
            "unit": None,
            "sample_count": None,
            "status": "UNAVAILABLE",
            "reason_codes": (type(exc).__name__ + ":" + str(exc),),
            "rms": None,
            "mav": None,
            "mdf_hz": None,
            "mnf_hz": None,
            "profile_id": profile_id,
            "benchmark_version": BENCHMARK_VERSION,
        }

    reasons = []
    if values.size < max(nperseg, 16):
        reasons.append("INSUFFICIENT_SAMPLES")
    if not np.isfinite(values).all():
        reasons.append("NONFINITE_INPUT")
    if high_hz >= fs_hz / 2:
        reasons.append("PROCESSING_PROFILE_NOT_ELIGIBLE_FOR_FS")
        
    if reasons:
        return {
            "source_id": "src_sha256_" + source_sha256,
            "signal_name": signal_name,
            "fs_hz": fs_hz,
            "unit": "V",
            "sample_count": int(values.size),
            "status": "UNAVAILABLE",
            "reason_codes": tuple(sorted(set(reasons))),
            "rms": None,
            "mav": None,
            "mdf_hz": None,
            "mnf_hz": None,
            "profile_id": profile_id,
            "benchmark_version": BENCHMARK_VERSION,
        }

    raw_hash = hashlib.sha256(values.tobytes()).hexdigest()
    y = _bandpass(values, fs_hz, low_hz, high_hz, order)
    if raw_hash != hashlib.sha256(values.tobytes()).hexdigest():
        raise RuntimeError("RAW_MUTATION_DETECTED")
        
    # Call the new Feature Extraction Service API router logic
    try:
        td_req = TimeDomainMathRequest(samples_uv=y.tolist(), amplitude_unit="V")
        td_res = extract_time_domain(td_req)
        rms = td_res.rms
        mav = td_res.mav
    except Exception as e:
        return {
            "source_id": "src_sha256_" + source_sha256,
            "signal_name": signal_name,
            "fs_hz": fs_hz,
            "unit": "V",
            "sample_count": int(values.size),
            "status": "UNAVAILABLE",
            "reason_codes": ("TIME_DOMAIN_ERROR",),
            "rms": None,
            "mav": None,
            "mdf_hz": None,
            "mnf_hz": None,
            "profile_id": profile_id,
            "benchmark_version": BENCHMARK_VERSION,
        }

    f, p = signal.welch(
        y,
        fs=fs_hz,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        detrend="constant",
        scaling="density",
    )
    keep = (f >= low_hz) & (f <= min(high_hz, fs_hz / 2))
    f, p = f[keep], p[keep]
    
    try:
        fd_req = FrequencyDomainMathRequest(
            frequencies_hz=f.tolist(),
            psd_uv2_per_hz=p.tolist(),
            minimum_power_uv2=0.0
        )
        fd_res = extract_frequency_domain(fd_req)
        mdf = fd_res.mdf_hz
        mnf = fd_res.mnf_hz
    except Exception as e:
        return {
            "source_id": "src_sha256_" + source_sha256,
            "signal_name": signal_name,
            "fs_hz": fs_hz,
            "unit": "V",
            "sample_count": int(values.size),
            "status": "UNAVAILABLE",
            "reason_codes": ("ZERO_OR_INSUFFICIENT_SPECTRAL_POWER",),
            "rms": rms,
            "mav": mav,
            "mdf_hz": None,
            "mnf_hz": None,
            "profile_id": profile_id,
            "benchmark_version": BENCHMARK_VERSION,
        }

    return {
        "source_id": "src_sha256_" + source_sha256,
        "signal_name": signal_name,
        "fs_hz": fs_hz,
        "unit": "V",
        "sample_count": int(values.size),
        "status": "AVAILABLE",
        "reason_codes": (),
        "rms": rms,
        "mav": mav,
        "mdf_hz": mdf,
        "mnf_hz": mnf,
        "profile_id": profile_id,
        "benchmark_version": BENCHMARK_VERSION,
    }


def benchmark_raw_root(raw_root: Path) -> pd.DataFrame:
    rows = []
    for path in discover_vinmec_emg_files(raw_root):
        rows.append(compute_metrics(path))
    return pd.DataFrame(rows)


def write_outputs(df: pd.DataFrame, parquet_path: Path, report_path: Path) -> None:
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(parquet_path, index=False)
    except ImportError as exc:
        raise RuntimeError("PARQUET_ENGINE_UNAVAILABLE: install pyarrow or fastparquet") from exc
        
    available = int((df["status"] == "AVAILABLE").sum()) if not df.empty else 0
    unavailable = int((df["status"] != "AVAILABLE").sum()) if not df.empty else 0
    report = {
        "benchmark_version": BENCHMARK_VERSION,
        "claim_scope": CLAIM_SCOPE,
        "rows": int(len(df)),
        "available": available,
        "unavailable": unavailable,
        "metrics": ["RMS", "MAV", "MDF", "MNF"],
        "interpretation": "TECHNICAL_RESEARCH_ONLY_NO_DIAGNOSTIC_INTERPRETATION",
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw-root", type=Path, required=True)
    p.add_argument("--parquet", type=Path, required=True)
    p.add_argument("--summary-json", type=Path, required=True)
    args = p.parse_args()
    df = benchmark_raw_root(args.raw_root)
    write_outputs(df, args.parquet, args.summary_json)
    print(json.dumps({"rows": len(df), "parquet": str(args.parquet)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
