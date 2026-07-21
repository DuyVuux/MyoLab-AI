#!/usr/bin/env python3
"""Kiểm chứng MDF/MNF bằng các phân bố PSD có nghiệm biết trước."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "packages" / "semg-core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from semg_core.spectral_features import extract_frequency_features  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("qa-validation/evidence/day10-mdf-mnf-verification.json"),
    )
    parser.add_argument(
        "--evidence-md",
        type=Path,
        default=Path("qa-validation/evidence/day10-mdf-mnf-verification.md"),
    )
    return parser.parse_args()


def _check(name: str, observed: float, expected: float, tolerance: float) -> dict:
    passed = abs(observed - expected) <= tolerance
    return {
        "name": name,
        "observed": observed,
        "expected": expected,
        "absolute_tolerance": tolerance,
        "passed": passed,
    }


def main() -> int:
    args = parse_args()
    f = np.arange(20.0, 401.0, 1.0)
    checks: list[dict] = []

    uniform = extract_frequency_features(f, np.ones_like(f))
    checks.append(_check("uniform_mdf", uniform.mdf_hz, 210.0, 1e-12))
    checks.append(_check("uniform_mnf", uniform.mnf_hz, 210.0, 1e-12))

    tone_psd = np.zeros_like(f)
    tone_psd[np.where(f == 80.0)[0][0]] = 10.0
    tone = extract_frequency_features(f, tone_psd)
    checks.append(_check("single_bin_mdf", tone.mdf_hz, 80.0, 1e-12))
    checks.append(_check("single_bin_mnf", tone.mnf_hz, 80.0, 1e-12))

    weighted = np.zeros_like(f)
    weighted[np.where(f == 60.0)[0][0]] = 1.0
    weighted[np.where(f == 120.0)[0][0]] = 3.0
    weighted_values = extract_frequency_features(f, weighted)
    checks.append(_check("weighted_mnf", weighted_values.mnf_hz, 105.0, 1e-12))
    checks.append({
        "name": "weighted_mdf_inside_dominant_bin",
        "observed": weighted_values.mdf_hz,
        "expected_interval": [119.5, 120.5],
        "passed": 119.5 <= weighted_values.mdf_hz <= 120.5,
    })

    gaussian = np.exp(-0.5 * ((f - 100.0) / 15.0) ** 2)
    base = extract_frequency_features(f, gaussian)
    scaled = extract_frequency_features(f, gaussian * 9.0)
    checks.append(_check("scale_invariant_mdf", scaled.mdf_hz, base.mdf_hz, 1e-12))
    checks.append(_check("scale_invariant_mnf", scaled.mnf_hz, base.mnf_hz, 1e-12))

    passed = all(item["passed"] for item in checks)
    payload = {
        "schema_version": "frequency-feature-verification.v0.1",
        "status": "passed" if passed else "failed",
        "frequency_axis": {"low_hz": 20.0, "high_hz": 400.0, "df_hz": 1.0},
        "checks": checks,
        "limitations": [
            "Kiểm chứng dùng PSD synthetic có nghiệm biết trước.",
            "Kết quả không phải clinical validation hoặc fatigue classification.",
        ],
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Bằng chứng kiểm chứng MDF/MNF Day 10",
        "",
        f"- Trạng thái: **{payload['status']}**",
        "- Dải tần kiểm thử: 20–400 Hz, df = 1 Hz",
        "",
        "| Kiểm tra | Kết quả |",
        "|---|---:|",
    ]
    for item in checks:
        lines.append(f"| {item['name']} | {'PASS' if item['passed'] else 'FAIL'} |")
    lines += [
        "",
        "> Đây là bằng chứng toán học/phần mềm trên PSD synthetic, không phải bằng chứng lâm sàng.",
        "",
    ]
    args.evidence_md.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"MDF/MNF verification: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
