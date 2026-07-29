from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from .signal_quality import compute_channel_statistics, stats_to_dict

UNIT_TO_UV = {"V": 1_000_000.0, "mV": 1_000.0, "uV": 1.0, "µV": 1.0}


def load_profile(path: Path) -> dict[str, Any]:
    profile = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict):
        raise ValueError("Mapping profile root must be object")
    if str(profile.get("verification_status", "")).upper() != "VERIFIED":
        raise ValueError("Mapping profile is not VERIFIED")
    return profile


def _read_signal_csv(path: Path, profile: dict[str, Any]) -> pd.DataFrame:
    text_cfg = profile.get("text", {})
    return pd.read_csv(
        path,
        encoding=text_cfg.get("encoding", "utf-8"),
        sep=text_cfg.get("delimiter", ","),
        skiprows=max(int(text_cfg.get("header_rows", 1)) - 1, 0),
    )


def run_structural_eda(
    data_root: Path,
    metadata: pd.DataFrame,
    profile: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    signal_cfg = profile.get("signal", {})
    source_unit = signal_cfg.get("source_unit")
    if source_unit not in UNIT_TO_UV:
        raise ValueError(f"Unsupported or unknown source unit: {source_unit}")
    factor = UNIT_TO_UV[source_unit]
    fs = signal_cfg.get("sampling_rate_hz")
    if fs is None or float(fs) <= 0:
        raise ValueError("sampling_rate_hz must be verified before real EDA")
    fs = float(fs)
    channel_defs = signal_cfg.get("channels", [])
    if len(channel_defs) != 4:
        raise ValueError(f"Expected four channel mappings, observed {len(channel_defs)}")

    file_rows: list[dict[str, object]] = []
    channel_rows: list[dict[str, object]] = []
    for record in metadata.to_dict(orient="records"):
        rel = Path(str(record["relative_path"]))
        source_path = (data_root / rel).resolve()
        if data_root.resolve() not in source_path.parents:
            raise ValueError(f"Path escapes data root: {rel}")
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        table = _read_signal_csv(source_path, profile)
        source_columns = [str(item["source_column"]) for item in channel_defs]
        missing = [name for name in source_columns if name not in table.columns]
        if missing:
            raise ValueError(f"Missing signal columns in {rel}: {missing}")
        n_samples = int(len(table))
        file_rows.append({
            "relative_path": str(rel),
            "subject_id": record.get("subject_id"),
            "repetition_id": record.get("repetition_id"),
            "source_label": record.get("source_label"),
            "canonical_label": record.get("canonical_label"),
            "partition": record.get("partition"),
            "sample_count": n_samples,
            "duration_s": n_samples / fs,
            "channel_count": len(source_columns),
            "sampling_rate_hz": fs,
            "source_unit": source_unit,
            "canonical_unit": "uV",
        })
        for channel in channel_defs:
            values_uv = pd.to_numeric(table[str(channel["source_column"])], errors="coerce").to_numpy(dtype=float) * factor
            stats = stats_to_dict(compute_channel_statistics(values_uv, fs))
            channel_rows.append({
                "relative_path": str(rel),
                "subject_id": record.get("subject_id"),
                "repetition_id": record.get("repetition_id"),
                "source_label": record.get("source_label"),
                "canonical_label": record.get("canonical_label"),
                "partition": record.get("partition"),
                "source_column": channel["source_column"],
                "canonical_channel_id": channel["canonical_id"],
                **stats,
            })
    return pd.DataFrame(file_rows), pd.DataFrame(channel_rows)
