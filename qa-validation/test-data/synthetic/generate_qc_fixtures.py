#!/usr/bin/env python3
"""Generate deterministic Day 4 QC fixtures from the Day 3 golden signal.

All outputs are synthetic engineering fixtures. They must never be used as
clinical evidence or as model-performance data.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np


DEFAULT_SOURCE_MANIFEST = Path(
    "data-platform/synthetic-data/golden_signal_01.manifest.json"
)
DEFAULT_OUTPUT_DIR = Path("qa-validation/test-data/synthetic")


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_source(manifest_path: Path) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    csv_path = manifest_path.parent / manifest["signal_file"]
    raw = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=np.float64)
    if raw.dtype.names is None or len(raw.dtype.names) != 2:
        raise ValueError("Day 4 generator expects one time column and one signal channel")
    time_column, signal_column = raw.dtype.names
    return manifest, np.asarray(raw[time_column]), np.asarray(raw[signal_column])


def write_fixture(
    output_dir: Path,
    *,
    stem: str,
    session_id: str,
    fixture_type: str,
    source_manifest: dict[str, Any],
    time_s: np.ndarray,
    signal_uV: np.ndarray,
    phase_markers: list[dict[str, Any]] | None = None,
    extra_limitations: list[str] | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{stem}.csv"
    manifest_path = output_dir / f"{stem}.manifest.json"

    np.savetxt(
        csv_path,
        np.column_stack([time_s, signal_uV]),
        delimiter=",",
        header="time_s,VL_R_01",
        comments="",
        fmt=("%.6f", "%.9f"),
    )
    digest = compute_sha256(csv_path)

    manifest = copy.deepcopy(source_manifest)
    manifest["session_id"] = session_id
    manifest["fixture_type"] = fixture_type
    manifest["signal_file"] = csv_path.name
    manifest["source_hash_sha256"] = digest
    manifest["clinical_use_allowed"] = False
    manifest["analysis_ready"] = True
    if phase_markers is not None:
        manifest["phase_markers"] = phase_markers
    limitations = list(manifest.get("limitations", []))
    limitations.extend(extra_limitations or [])
    manifest["limitations"] = list(dict.fromkeys(limitations))
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "stem": stem,
        "session_id": session_id,
        "fixture_type": fixture_type,
        "csv": str(csv_path),
        "manifest": str(manifest_path),
        "source_hash_sha256": digest,
        "sample_count": int(time_s.size),
    }


def _active_bounds(manifest: dict[str, Any], sampling_rate_hz: float) -> tuple[int, int]:
    marker = next(
        item
        for item in manifest["phase_markers"]
        if item["phase_id"] == "active_contraction"
    )
    start = int(round(float(marker["start_s"]) * sampling_rate_hz))
    end = int(round(float(marker["end_s"]) * sampling_rate_hz))
    return start, end


def generate_all(
    source_manifest_path: Path,
    output_dir: Path,
    *,
    overwrite: bool,
) -> list[dict[str, Any]]:
    source_manifest, time_s, source_signal = load_source(source_manifest_path)
    fs = float(source_manifest["sampling_rate_hz"])
    active_start, active_end = _active_bounds(source_manifest, fs)
    active_count = active_end - active_start

    expected_paths = [
        output_dir / f"{stem}{suffix}"
        for stem in (
            "qc_fail_nonfinite",
            "qc_fail_flatline",
            "qc_warning_clipping",
            "qc_warning_powerline",
            "qc_warning_motion_artifact",
            "qc_fail_short_duration",
        )
        for suffix in (".csv", ".manifest.json")
    ]
    existing = [path for path in expected_paths if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing QC fixtures: "
            + ", ".join(str(path) for path in existing)
        )

    outputs: list[dict[str, Any]] = []

    # 2% non-finite samples within active phase -> critical fail at qc_v0.1.
    nonfinite = source_signal.copy()
    n_missing = int(round(0.02 * active_count))
    missing_indexes = np.linspace(
        active_start,
        active_end - 1,
        num=n_missing,
        dtype=np.int64,
    )
    nonfinite[missing_indexes] = np.nan
    outputs.append(
        write_fixture(
            output_dir,
            stem="qc_fail_nonfinite",
            session_id="SYNTH_D4_FAIL_NONFINITE",
            fixture_type="qc_critical_nonfinite_ratio",
            source_manifest=source_manifest,
            time_s=time_s,
            signal_uV=nonfinite,
            extra_limitations=["Contains deterministic 2% active-phase NaN samples."],
        )
    )

    # 4 seconds / 60 seconds = 6.67% flatline -> critical fail (>5%).
    flatline = source_signal.copy()
    flat_start = active_start + int(round(20.0 * fs))
    flat_end = flat_start + int(round(4.0 * fs))
    flatline[flat_start:flat_end] = 12.345678
    outputs.append(
        write_fixture(
            output_dir,
            stem="qc_fail_flatline",
            session_id="SYNTH_D4_FAIL_FLATLINE",
            fixture_type="qc_critical_flatline",
            source_manifest=source_manifest,
            time_s=time_s,
            signal_uV=flatline,
            extra_limitations=["Contains a deterministic 4-second active-phase flatline."],
        )
    )

    # 0.75% samples pinned to repeated extrema -> warning (>0.5%).
    clipping = source_signal.copy()
    n_clipped = int(round(0.0075 * active_count))
    clip_indexes = np.linspace(
        active_start,
        active_end - 1,
        num=n_clipped,
        dtype=np.int64,
    )
    clipping[clip_indexes[::2]] = 500.0
    clipping[clip_indexes[1::2]] = -500.0
    outputs.append(
        write_fixture(
            output_dir,
            stem="qc_warning_clipping",
            session_id="SYNTH_D4_WARN_CLIPPING",
            fixture_type="qc_warning_repeated_extrema",
            source_manifest=source_manifest,
            time_s=time_s,
            signal_uV=clipping,
            extra_limitations=["Contains repeated extrema for clipping-heuristic testing."],
        )
    )

    # Strong deterministic 50 Hz component -> warning-only in qc_v0.1.
    powerline = source_signal.copy()
    active_time = time_s[active_start:active_end]
    powerline[active_start:active_end] += 220.0 * np.sin(
        2.0 * np.pi * 50.0 * active_time + 0.1
    )
    outputs.append(
        write_fixture(
            output_dir,
            stem="qc_warning_powerline",
            session_id="SYNTH_D4_WARN_POWERLINE",
            fixture_type="qc_warning_powerline_50hz",
            source_manifest=source_manifest,
            time_s=time_s,
            signal_uV=powerline,
            extra_limitations=["Contains a strong synthetic 50 Hz component."],
        )
    )

    # Strong deterministic 5 Hz component -> low-frequency motion warning.
    motion = source_signal.copy()
    motion[active_start:active_end] += 220.0 * np.sin(
        2.0 * np.pi * 5.0 * active_time + 0.3
    )
    outputs.append(
        write_fixture(
            output_dir,
            stem="qc_warning_motion_artifact",
            session_id="SYNTH_D4_WARN_MOTION",
            fixture_type="qc_warning_low_frequency_motion",
            source_manifest=source_manifest,
            time_s=time_s,
            signal_uV=motion,
            extra_limitations=["Contains a strong synthetic 5 Hz component."],
        )
    )

    # 5 s baseline + 30 s active + 5 s recovery. Import succeeds; QC fails duration.
    short_end_s = 40.0
    short_count = int(round(short_end_s * fs))
    short_time = time_s[:short_count]
    short_signal = source_signal[:short_count]
    short_markers = [
        {"phase_id": "baseline_rest", "start_s": 0.0, "end_s": 5.0},
        {"phase_id": "active_contraction", "start_s": 5.0, "end_s": 35.0},
        {"phase_id": "recovery", "start_s": 35.0, "end_s": 40.0},
    ]
    outputs.append(
        write_fixture(
            output_dir,
            stem="qc_fail_short_duration",
            session_id="SYNTH_D4_FAIL_SHORT_DURATION",
            fixture_type="qc_critical_active_duration_short",
            source_manifest=source_manifest,
            time_s=short_time,
            signal_uV=short_signal,
            phase_markers=short_markers,
            extra_limitations=["Active phase is intentionally 30 seconds instead of 60 seconds."],
        )
    )

    index_path = output_dir / "day4_qc_fixture_index.json"
    index_payload = {
        "schema_version": "day4-qc-fixture-index.v0.1",
        "source_manifest": str(source_manifest_path),
        "clinical_use_allowed": False,
        "fixtures": outputs,
    }
    index_path.write_text(
        json.dumps(index_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        outputs = generate_all(
            args.source_manifest,
            args.output_dir,
            overwrite=args.overwrite,
        )
    except (FileNotFoundError, FileExistsError, ValueError, OSError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"generated": outputs}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
