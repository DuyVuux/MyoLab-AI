"""Integrity-checked canonical signal I/O and deterministic output writers."""

from __future__ import annotations

import csv
import gzip
import io
import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np


class SourceIntegrityError(ValueError):
    """Raised when a source file does not match its provenance hash."""


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


class CanonicalWindowReader:
    """Read canonical CSV/NPY/NPZ windows within a configured data root.

    Binary formats require explicit channel identifiers either in each window
    row as ``channel_ids`` or in the constructor's record-level channel map.
    No anatomical or positional channel mapping is guessed.
    """

    def __init__(
        self,
        data_root: str | Path,
        *,
        channel_map: Mapping[str, Sequence[str]] | None = None,
    ) -> None:
        root = Path(data_root).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError("data_root must be an existing directory")
        self._data_root = root
        self._channel_map = {
            str(record_id): tuple(channels)
            for record_id, channels in (channel_map or {}).items()
        }
        self._verified_hashes: dict[Path, str] = {}

    @property
    def verified_source_count(self) -> int:
        return len(self._verified_hashes)

    def _resolve_source(self, row: Mapping[str, Any]) -> Path:
        raw_path = row.get("signal_path")
        if not isinstance(raw_path, str) or not raw_path:
            raise ValueError("signal_path must be a non-empty string")
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = self._data_root / path
        resolved = path.resolve()
        try:
            resolved.relative_to(self._data_root)
        except ValueError as error:
            raise PermissionError("signal path is outside data root") from error
        if not resolved.is_file():
            raise FileNotFoundError(resolved)
        return resolved

    def _verify_hash(self, path: Path, expected_hash: Any) -> None:
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise SourceIntegrityError("invalid expected source SHA-256")
        cached = self._verified_hashes.get(path)
        if cached is None:
            cached = _file_sha256(path)
            self._verified_hashes[path] = cached
        if cached != expected_hash:
            raise SourceIntegrityError(
                f"source SHA-256 mismatch for {path.name}"
            )

    def _channel_ids(
        self,
        row: Mapping[str, Any],
        width: int,
    ) -> tuple[str, ...]:
        raw = row.get("channel_ids")
        if raw is None:
            raw = self._channel_map.get(str(row.get("record_id")))
        if (
            not isinstance(raw, (list, tuple))
            or len(raw) != width
            or any(not isinstance(item, str) or not item for item in raw)
        ):
            raise ValueError(
                "explicit channel identifiers are required for binary signals"
            )
        identifiers = tuple(raw)
        if len({item.casefold() for item in identifiers}) != len(identifiers):
            raise ValueError("channel identifiers must be unique")
        return identifiers

    @staticmethod
    def _bounds(row: Mapping[str, Any]) -> tuple[int, int, int]:
        try:
            start = int(row["start_sample"])
            end = int(row["end_sample_exclusive"])
            record_samples = int(row["record_n_samples"])
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            raise ValueError("invalid window sample bounds") from error
        if start < 0 or end <= start or end > record_samples:
            raise ValueError("invalid window sample bounds")
        return start, end, record_samples

    def _read_csv(
        self,
        path: Path,
        start: int,
        end: int,
    ) -> tuple[np.ndarray, tuple[str, ...]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = tuple(reader.fieldnames or ())
            if not headers:
                raise ValueError("canonical CSV must contain a header")
            non_signal = {
                "time",
                "time_s",
                "timestamp",
                "sample",
                "index",
            }
            channels = tuple(
                header
                for header in headers
                if header.strip().casefold() not in non_signal
            )
            if not channels:
                raise ValueError("canonical CSV contains no signal channels")
            output: list[list[float]] = []
            for index, row in enumerate(reader):
                if index < start:
                    continue
                if index >= end:
                    break
                try:
                    output.append([float(row[channel]) for channel in channels])
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError(
                        f"non-numeric canonical CSV value at sample {index}"
                    ) from error
        values = np.asarray(output, dtype=np.float64)
        if values.shape != (end - start, len(channels)):
            raise ValueError("canonical CSV ended before the requested window")
        return values, channels

    def _read_binary(
        self,
        path: Path,
        row: Mapping[str, Any],
        start: int,
        end: int,
        record_samples: int,
    ) -> tuple[np.ndarray, tuple[str, ...]]:
        if path.suffix.lower() == ".npy":
            data = np.load(path, mmap_mode="r", allow_pickle=False)
        else:
            with np.load(path, allow_pickle=False) as bundle:
                if "signal" not in bundle:
                    raise ValueError("canonical NPZ must contain array 'signal'")
                data = np.asarray(bundle["signal"])
        if data.ndim == 1:
            data = data[:, None]
        if data.ndim != 2:
            raise ValueError("canonical signal must have [samples, channels] shape")
        if data.shape[0] != record_samples:
            raise ValueError("record_n_samples does not match source signal")
        channels = self._channel_ids(row, int(data.shape[1]))
        return np.asarray(data[start:end], dtype=np.float64).copy(), channels

    def __call__(
        self,
        row: Mapping[str, Any],
    ) -> tuple[np.ndarray, tuple[str, ...]]:
        path = self._resolve_source(row)
        self._verify_hash(path, row.get("source_file_sha256"))
        start, end, record_samples = self._bounds(row)
        suffix = path.suffix.lower()
        if suffix == ".csv":
            values, channels = self._read_csv(path, start, end)
        elif suffix in {".npy", ".npz"}:
            values, channels = self._read_binary(
                path,
                row,
                start,
                end,
                record_samples,
            )
        else:
            raise ValueError(
                f"unsupported canonical signal format: {suffix or '<none>'}"
            )
        if not bool(np.isfinite(values).all()):
            raise ValueError("source window contains non-finite samples")
        return values, channels


def _atomic_target(path: Path) -> tuple[Path, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    return Path(temporary_name), descriptor


def dump_json_strict(path: str | Path, value: Any) -> None:
    """Atomically write RFC-compliant JSON and reject NaN/Infinity."""

    output = Path(path)
    temporary, descriptor = _atomic_target(output)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(
                value,
                handle,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def write_feature_rows_csv_gzip(
    rows: Sequence[Mapping[str, Any]],
    output_path: str | Path,
) -> dict[str, Any]:
    """Write deterministic canonical CSV.gz and return its integrity summary."""

    if not rows:
        raise ValueError("feature rows must not be empty")
    output = Path(output_path)
    if not str(output).endswith(".csv.gz"):
        raise ValueError("fallback feature table path must end with .csv.gz")
    fieldnames = tuple(rows[0])
    if not fieldnames or any(tuple(row) != fieldnames for row in rows):
        raise ValueError("all feature rows must have identical ordered columns")

    temporary, descriptor = _atomic_target(output)
    try:
        with os.fdopen(descriptor, "wb") as raw, gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw,
            mtime=0,
        ) as compressed, io.TextIOWrapper(
            compressed,
            encoding="utf-8",
            newline="",
        ) as text:
            writer = csv.DictWriter(
                text,
                fieldnames=fieldnames,
                extrasaction="raise",
                lineterminator="\n",
            )
            writer.writeheader()
            for row in rows:
                serialized = dict(row)
                serialized["qc_flags"] = json.dumps(
                    serialized["qc_flags"],
                    ensure_ascii=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                writer.writerow(serialized)
        os.replace(temporary, output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return {
        "schema_version": "day31-feature-table-write.v1",
        "format": "csv_gzip",
        "path": str(output),
        "row_count": len(rows),
        "sha256": _file_sha256(output),
        "pass": True,
    }
