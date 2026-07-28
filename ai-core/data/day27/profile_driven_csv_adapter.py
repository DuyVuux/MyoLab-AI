from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .contracts import canonical_sha256, find_placeholders
from .hashing import sha256_file


class AdapterError(ValueError):
    pass


UNIT_TO_UV = {"V": 1_000_000.0, "mV": 1_000.0, "uV": 1.0, "µV": 1.0}


@dataclass(frozen=True)
class CanonicalSmokeResult:
    npz_path: Path
    sidecar_path: Path
    sample_count: int
    channel_count: int


def validate_profile(profile: dict[str, Any]) -> None:
    placeholders = find_placeholders(profile, include_none=False)
    if placeholders:
        raise AdapterError("PROFILE_NOT_VERIFIED:" + ",".join(placeholders[:20]))
    if profile.get("verificationStatus") != "VERIFIED":
        raise AdapterError("PROFILE_STATUS_NOT_VERIFIED")
    signal = profile.get("signal")
    if not isinstance(signal, dict):
        raise AdapterError("SIGNAL_BLOCK_REQUIRED")
    fs = signal.get("samplingRateHz")
    if not isinstance(fs, (int, float)) or fs <= 0:
        raise AdapterError("INVALID_SAMPLING_RATE")
    unit = signal.get("sourceUnit")
    if unit not in UNIT_TO_UV:
        raise AdapterError(f"UNSUPPORTED_OR_UNKNOWN_UNIT:{unit}")


def convert_wide_csv_smoke(
    source: Path,
    profile: dict[str, Any],
    output_dir: Path,
    *,
    metadata: dict[str, str] | None = None,
) -> CanonicalSmokeResult:
    validate_profile(profile)
    if profile.get("sourceFormat") != "wide_csv":
        raise AdapterError("PROFILE_SOURCE_FORMAT_NOT_WIDE_CSV")
    text = profile["text"]
    signal = profile["signal"]
    channel_specs = signal["channels"]
    source_columns = [item["sourceColumn"] for item in channel_specs]
    canonical_ids = [item["canonicalId"] for item in channel_specs]
    delimiter = text.get("delimiter", ",")
    encoding = text.get("encoding", "utf-8")

    rows: list[list[float]] = []
    times: list[float] = []
    with source.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if reader.fieldnames is None:
            raise AdapterError("CSV_HEADER_REQUIRED")
        missing = [column for column in source_columns if column not in reader.fieldnames]
        if missing:
            raise AdapterError("MISSING_CHANNEL_COLUMNS:" + ",".join(missing))
        time_cfg = signal["time"]
        time_column = time_cfg.get("sourceColumn")
        fs = float(signal["samplingRateHz"])
        for index, row in enumerate(reader):
            try:
                rows.append([float(row[column]) for column in source_columns])
                if time_column:
                    times.append(float(row[time_column]))
                else:
                    times.append(index / fs)
            except (TypeError, ValueError) as exc:
                raise AdapterError(f"NON_NUMERIC_ROW:{index + 2}") from exc

    if not rows:
        raise AdapterError("NO_SIGNAL_ROWS")
    samples = np.asarray(rows, dtype=np.float64)
    samples_uv = samples * UNIT_TO_UV[str(signal["sourceUnit"])]
    time_s = np.asarray(times, dtype=np.float64)
    if not np.all(np.diff(time_s) > 0):
        raise AdapterError("TIME_NOT_STRICTLY_INCREASING")
    if not np.isfinite(samples_uv).all():
        raise AdapterError("NONFINITE_SIGNAL")

    output_dir.mkdir(parents=True, exist_ok=True)
    source_hash = sha256_file(source)
    npz_path = output_dir / f"{source.stem}.canonical-smoke.npz"
    np.savez_compressed(npz_path, time_s=time_s, samples_uV=samples_uv)
    sidecar = {
        "schemaVersion": "canonical-smoke-sidecar.v1",
        "sourcePath": str(source),
        "sourceSha256": source_hash,
        "adapterProfileId": profile["profileId"],
        "adapterProfileSha256": canonical_sha256(profile),
        "samplingRateHz": signal["samplingRateHz"],
        "sourceUnit": signal["sourceUnit"],
        "canonicalUnit": "uV",
        "channelIds": canonical_ids,
        "sampleCount": int(samples_uv.shape[0]),
        "channelCount": int(samples_uv.shape[1]),
        "metadata": metadata or {},
        "clinicalUseAllowed": False,
        "motionLabTransferVerified": False,
    }
    sidecar_path = output_dir / f"{source.stem}.canonical-smoke.json"
    sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return CanonicalSmokeResult(npz_path, sidecar_path, sidecar["sampleCount"], sidecar["channelCount"])
