#!/usr/bin/env python3
"""Kiểm chứng hình học hai window profile bằng các case tính tay."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SEMGC_PATH = ROOT / "packages" / "semg-core"
FEATURE_PATH = ROOT / "services" / "feature-extraction-service" / "src"
for path in (SEMGC_PATH, FEATURE_PATH):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from semg_core.windowing import (  # noqa: E402
    assess_window_validity,
    build_fixed_window_geometries,
    overlap_to_hop_samples,
    seconds_to_exact_samples,
)
from window_config import load_windowing_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "services/feature-extraction-service/configs/windowing_v0.1.yaml"
        ),
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("qa-validation/evidence/day7-window-geometry.json"),
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=Path("qa-validation/evidence/day7-windowing-evidence.md"),
    )
    return parser.parse_args()


def _build_profile(
    *,
    profile_id: str,
    config: dict[str, Any],
    time_s: np.ndarray,
    fs: float,
    phase_start: int,
    phase_end: int,
    invalid_sample_index: int,
) -> dict[str, Any]:
    profile = config["profiles"][profile_id]
    window_samples = seconds_to_exact_samples(
        float(profile["duration_ms"]) / 1000.0,
        fs,
    )
    hop_samples = overlap_to_hop_samples(
        window_samples,
        float(profile["overlap_fraction"]),
    )
    geometries = build_fixed_window_geometries(
        time_s=time_s,
        sampling_rate_hz=fs,
        phase_id="active_contraction",
        phase_start_sample=phase_start,
        phase_end_sample_exclusive=phase_end,
        window_size_samples=window_samples,
        hop_size_samples=hop_samples,
    )
    samples = np.ones(time_s.size, dtype=np.float64)
    mask_all = np.ones(time_s.size, dtype=np.bool_)
    mask_invalid = mask_all.copy()
    mask_invalid[invalid_sample_index] = False
    validity_all = assess_window_validity(
        samples=samples,
        valid_sample_mask=mask_all,
        geometries=geometries,
        minimum_valid_sample_ratio=1.0,
    )
    validity_invalid = assess_window_validity(
        samples=samples,
        valid_sample_mask=mask_invalid,
        geometries=geometries,
        minimum_valid_sample_ratio=1.0,
    )
    invalid_indices = [
        item.window_index for item in validity_invalid if item.status == "invalid"
    ]
    return {
        "profile_id": profile_id,
        "purpose": profile["purpose"],
        "window_size_samples": window_samples,
        "hop_size_samples": hop_samples,
        "overlap_fraction": float(profile["overlap_fraction"]),
        "window_count": len(geometries),
        "remainder_samples": phase_end - geometries[-1].end_sample_exclusive,
        "first_window": geometries[0].to_dict(),
        "last_window": geometries[-1].to_dict(),
        "all_valid_count": sum(item.status == "valid" for item in validity_all),
        "invalid_window_indices": invalid_indices,
    }


def main() -> int:
    args = parse_args()
    config = load_windowing_config(args.config)
    fs = 1000.0
    phase_start = 5_000
    phase_end = 65_000
    phase_samples = phase_end - phase_start
    invalid_sample_index = 5_750
    time_s = np.arange(70_000, dtype=np.float64) / fs

    profiles = {
        profile_id: _build_profile(
            profile_id=profile_id,
            config=config,
            time_s=time_s,
            fs=fs,
            phase_start=phase_start,
            phase_end=phase_end,
            invalid_sample_index=invalid_sample_index,
        )
        for profile_id in ("time_domain", "frequency_domain")
    }

    time_profile = profiles["time_domain"]
    frequency_profile = profiles["frequency_domain"]
    checks = {
        "phase_has_60000_samples": phase_samples == 60_000,
        "time_window_size_is_500": time_profile["window_size_samples"] == 500,
        "time_hop_is_250": time_profile["hop_size_samples"] == 250,
        "time_window_count_is_239": time_profile["window_count"] == 239,
        "time_first_window_is_5000_5500": (
            time_profile["first_window"]["start_sample"] == 5_000
            and time_profile["first_window"]["end_sample_exclusive"] == 5_500
        ),
        "time_last_window_ends_at_phase_end": (
            time_profile["last_window"]["end_sample_exclusive"] == 65_000
        ),
        "time_masked_sample_affects_windows_2_3": (
            time_profile["invalid_window_indices"] == [2, 3]
        ),
        "frequency_window_size_is_1000": (
            frequency_profile["window_size_samples"] == 1_000
        ),
        "frequency_hop_is_500": frequency_profile["hop_size_samples"] == 500,
        "frequency_window_count_is_119": (
            frequency_profile["window_count"] == 119
        ),
        "frequency_first_window_is_5000_6000": (
            frequency_profile["first_window"]["start_sample"] == 5_000
            and frequency_profile["first_window"]["end_sample_exclusive"] == 6_000
        ),
        "frequency_last_window_ends_at_phase_end": (
            frequency_profile["last_window"]["end_sample_exclusive"] == 65_000
        ),
        "frequency_masked_sample_affects_windows_0_1": (
            frequency_profile["invalid_window_indices"] == [0, 1]
        ),
        "no_partial_window_in_both_profiles": (
            time_profile["remainder_samples"] == 0
            and frequency_profile["remainder_samples"] == 0
        ),
    }
    passed = all(checks.values())
    payload = {
        "schema_version": "window-geometry-verification.v0.1",
        "status": "pass" if passed else "fail",
        "config_id": config["config_id"],
        "sampling_rate_hz": fs,
        "phase": {
            "phase_id": "active_contraction",
            "start_sample": phase_start,
            "end_sample_exclusive": phase_end,
            "sample_count": phase_samples,
        },
        "masked_sample_index": invalid_sample_index,
        "profiles": [profiles["time_domain"], profiles["frequency_domain"]],
        "checks": checks,
        "limitations": list(config.get("limitations", [])),
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    rows = [
        "# Bằng chứng kiểm chứng segmentation và windowing v0.1",
        "",
        f"- Trạng thái: **{payload['status'].upper()}**",
        f"- Config: `{config['config_id']}`",
        f"- Sampling rate: `{fs:g} Hz`",
        f"- Active phase: `{phase_samples}` mẫu, tương ứng `60 s`",
        f"- Mẫu invalid dùng để kiểm tra half-open overlap: `{invalid_sample_index}`",
        "",
        "## Hai profile được khóa theo protocol",
        "",
        "| Profile | Mục đích | L | H | Overlap | Số window | Invalid windows trong case kiểm tra |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for profile_id in ("time_domain", "frequency_domain"):
        profile = profiles[profile_id]
        rows.append(
            f"| `{profile_id}` | `{profile['purpose']}` | "
            f"{profile['window_size_samples']} | {profile['hop_size_samples']} | "
            f"{profile['overlap_fraction']:.2f} | {profile['window_count']} | "
            f"`{profile['invalid_window_indices']}` |"
        )
    rows.extend(
        [
            "",
            "## Kiểm tra tính tay",
            "",
            "| Kiểm tra | Kết quả |",
            "|---|---|",
        ]
    )
    for key, value in checks.items():
        rows.append(f"| `{key}` | {'PASS' if value else 'FAIL'} |")
    rows.extend(["", "## Giới hạn", ""])
    rows.extend(f"- {item}" for item in payload["limitations"])
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(
        "WINDOW GEOMETRY VERIFICATION: "
        f"{payload['status'].upper()} time={time_profile['window_count']} "
        f"frequency={frequency_profile['window_count']}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
