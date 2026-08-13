import csv
import hashlib
from pathlib import Path
import math

import numpy as np
import pandas as pd

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def parse_noraxon_separated_emg(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    
    if len(rows) < 5:
        raise ValueError("INGEST_SCHEMA_ERROR: signal CSV too short")
    
    header = [x.strip() for x in rows[0]]
    values = rows[1]
    meta = dict(zip(header, values))
    
    if meta.get("type") != "signal":
        raise ValueError("SIGNAL_TYPE_UNSUPPORTED")
    
    name = meta.get("name") or path.stem
    unit = (meta.get("units") or "").strip()
    if unit not in {"uV", "V", "mV"}:
        raise ValueError("UNIT_MISMATCH")
    
    fs_hz = float(meta["frequency"])
    if not math.isfinite(fs_hz) or fs_hz <= 0:
        raise ValueError("TIMESTAMP_INVALID")
    
    count_declared = int(meta["count"]) if meta.get("count") else None
    
    blank_idx = next((i for i, row in enumerate(rows[2:], start=2) if not any(x.strip() for x in row)), None)
    if blank_idx is None or blank_idx + 2 > len(rows):
        raise ValueError("INGEST_SCHEMA_ERROR: blank separator missing")
    
    data_header = [x.strip() for x in rows[blank_idx + 1]]
    if data_header[:2] != ["time", "value"]:
        raise ValueError("INGEST_SCHEMA_ERROR: expected time,value")
    
    data_rows = [r for r in rows[blank_idx + 2 :] if r and any(x.strip() for x in r)]
    t = np.asarray([float(r[0]) for r in data_rows], dtype=float)
    x = np.asarray([float(r[1]) for r in data_rows], dtype=float)
    
    if count_declared is not None and count_declared != len(x):
        raise ValueError("COUNT_MISMATCH")
    if len(t) > 1 and not np.all(np.diff(t) > 0):
        raise ValueError("TIMESTAMP_INVALID")
    if not np.isfinite(x).all():
        raise ValueError("NONFINITE_INPUT")
    
    # Convert unit to V for bronze
    if unit == "uV":
        x = x * 1e-6
    elif unit == "mV":
        x = x * 1e-3
        
    df = pd.DataFrame({"time_s": t, "value_v": x})
    df["source_id"] = "src_sha256_" + sha256_file(path)
    df["signal_name"] = name
    df["fs_hz"] = fs_hz
    return df

def convert_to_bronze(raw_root: Path, bronze_out_dir: Path) -> list[Path]:
    bronze_out_dir.mkdir(parents=True, exist_ok=True)
    out_files = []
    # Discover matching raw files
    for path in sorted(raw_root.rglob("*.csv")):
        if not path.name.startswith("Ultium_EMG-"):
            continue
        try:
            df = parse_noraxon_separated_emg(path)
            out_name = path.stem + "_bronze.parquet"
            out_path = bronze_out_dir / out_name
            df.to_parquet(out_path, index=False)
            out_files.append(out_path)
        except Exception as e:
            print(f"Skipping {path.name}: {e}")
    return out_files
