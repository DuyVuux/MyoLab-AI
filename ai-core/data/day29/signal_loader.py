from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from .contracts import RecordMeta


def _load_csv(path: Path, channel_columns: tuple[str, ...]) -> tuple[np.ndarray, tuple[str, ...]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = tuple(reader.fieldnames or ())
        if not headers:
            raise ValueError(f"CSV không có header: {path}")

        selected = channel_columns or tuple(
            name for name in headers if name.lower() not in {"time", "timestamp", "sample", "index"}
        )
        if not selected:
            raise ValueError(f"Không xác định được channel columns: {path}")
        missing = [name for name in selected if name not in headers]
        if missing:
            raise ValueError(f"CSV thiếu channel columns {missing}: {path}")

        rows: list[list[float]] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                rows.append([float(row[name]) for name in selected])
            except (TypeError, ValueError, KeyError) as exc:
                raise ValueError(f"CSV lỗi tại {path}:{row_number}: {exc}") from exc
    return np.asarray(rows, dtype=float), selected


def load_signal(record: RecordMeta) -> tuple[np.ndarray, tuple[str, ...]]:
    path = record.signal_path
    if not path.exists():
        raise FileNotFoundError(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        data, names = _load_csv(path, record.channel_columns)
    elif suffix == ".npy":
        data = np.load(path, allow_pickle=False)
        names = record.channel_columns or tuple(f"ch{index + 1:02d}" for index in range(data.shape[1]))
    elif suffix == ".npz":
        bundle = np.load(path, allow_pickle=False)
        if "signal" not in bundle:
            raise ValueError(f"NPZ phải có array 'signal': {path}")
        data = bundle["signal"]
        names = record.channel_columns or tuple(f"ch{index + 1:02d}" for index in range(data.shape[1]))
    else:
        raise ValueError(f"Canonical format chưa hỗ trợ: {suffix} ({path})")

    data = np.asarray(data, dtype=float)
    if data.ndim == 1:
        data = data[:, None]
    if data.ndim != 2:
        raise ValueError(f"Signal phải có shape [samples, channels], nhận {data.shape}")
    if data.shape[1] != record.channel_count:
        raise ValueError(
            f"Channel count mismatch record={record.record_id}: "
            f"metadata={record.channel_count}, observed={data.shape[1]}"
        )
    if len(names) != data.shape[1]:
        raise ValueError("Số channel names không khớp signal")
    return data, tuple(names)
