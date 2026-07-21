#!/usr/bin/env python3
"""Kiểm chứng phân tích RMS/MAV bằng vector có nghiệm biết trước."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SEMGC_PATH = ROOT / "packages" / "semg-core"
if str(SEMGC_PATH) not in sys.path:
    sys.path.insert(0, str(SEMGC_PATH))

from semg_core.features import extract_time_domain_features, mean_absolute_value, root_mean_square  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kiểm chứng RMS/MAV với vector có nghiệm đóng.")
    parser.add_argument("--json-output", type=Path, default=Path("qa-validation/evidence/day8-time-domain-feature-verification.json"))
    parser.add_argument("--evidence-md", type=Path, default=Path("qa-validation/evidence/day8-time-domain-feature-evidence.md"))
    parser.add_argument("--validation-md", type=Path, default=Path("ai-core/validation-reports/analytical_validation_time_domain_features_v0.1.md"))
    return parser.parse_args()


def _relative_error(observed: float, expected: float) -> float:
    return abs(observed - expected) if expected == 0.0 else abs(observed - expected) / abs(expected)


def _case(case_id: str, values: np.ndarray, expected_rms: float, expected_mav: float, tolerance: float) -> dict[str, Any]:
    observed_rms = root_mean_square(values)
    observed_mav = mean_absolute_value(values)
    rms_error = _relative_error(observed_rms, expected_rms)
    mav_error = _relative_error(observed_mav, expected_mav)
    return {
        "case_id": case_id,
        "observed": {"rms": observed_rms, "mav": observed_mav},
        "expected": {"rms": expected_rms, "mav": expected_mav},
        "relative_error": {"rms": rms_error, "mav": mav_error},
        "tolerance": tolerance,
        "passed": rms_error <= tolerance and mav_error <= tolerance,
    }


def build_report() -> dict[str, Any]:
    cases = [
        _case("hand_vector", np.array([-3.0, -1.0, 1.0, 3.0]), math.sqrt(5.0), 2.0, 1e-12),
        _case("constant_absolute_magnitude", np.array([-5.0, 5.0, -5.0, 5.0]), 5.0, 5.0, 1e-12),
    ]
    fs = 1000.0
    amplitude = 100.0
    frequency_hz = 80.0
    t = np.arange(1000, dtype=np.float64) / fs
    sine = amplitude * np.sin(2.0 * np.pi * frequency_hz * t)
    cases.append(_case("integer_cycle_sine_80_hz", sine, amplitude / math.sqrt(2.0), 2.0 * amplitude / math.pi, 2e-3))

    base = np.array([-3.0, -1.0, 1.0, 3.0])
    factor = -2.5
    b = extract_time_domain_features(base)
    s = extract_time_domain_features(factor * base)
    scaling = {
        "case_id": "absolute_scaling_property",
        "observed": {"rms_ratio": s.rms / b.rms, "mav_ratio": s.mav / b.mav},
        "expected_ratio": abs(factor),
    }
    scaling["passed"] = abs(scaling["observed"]["rms_ratio"] - abs(factor)) <= 1e-12 and abs(scaling["observed"]["mav_ratio"] - abs(factor)) <= 1e-12

    rng = np.random.default_rng(20260721)
    violations = sum(root_mean_square(x) + 1e-12 < mean_absolute_value(x) for x in (rng.normal(size=500) for _ in range(100)))
    inequality = {"case_id": "rms_greater_or_equal_mav", "trial_count": 100, "violation_count": int(violations), "passed": violations == 0}

    large = np.array([1e300, -1e300, 1e300, -1e300])
    large_rms = root_mean_square(large)
    large_mav = mean_absolute_value(large)
    stability = {"case_id": "large_value_numerical_stability", "observed": {"rms": large_rms, "mav": large_mav}, "passed": math.isfinite(large_rms) and math.isfinite(large_mav)}

    passed = all(c["passed"] for c in cases) and scaling["passed"] and inequality["passed"] and stability["passed"]
    return {
        "schema_version": "time-domain-feature-verification.v0.1",
        "verification_status": "passed" if passed else "failed",
        "feature_extractor_id": "features_semg_v0.1",
        "scope": "software_dsp_analytical_verification_only",
        "cases": cases,
        "properties": [scaling, inequality, stability],
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()},
        "limitations": [
            "Kiểm chứng dùng vector toán học và synthetic signals, không dùng dữ liệu bệnh nhân.",
            "Pass không có nghĩa RMS/MAV đã được xác nhận là biomarker lâm sàng độc lập.",
            "Không kiểm chứng MDF/MNF, slope, FRS hoặc mô hình ML trong Day 8."
        ]
    }


def _evidence_md(report: dict[str, Any]) -> str:
    lines = ["# Bằng chứng kiểm chứng RMS/MAV — Day 8", "", f"**Trạng thái:** `{report['verification_status']}`", "", "| Case | RMS quan sát | RMS kỳ vọng | MAV quan sát | MAV kỳ vọng | Kết quả |", "|---|---:|---:|---:|---:|---|"]
    for c in report["cases"]:
        lines.append(f"| {c['case_id']} | {c['observed']['rms']:.12g} | {c['expected']['rms']:.12g} | {c['observed']['mav']:.12g} | {c['expected']['mav']:.12g} | {'PASS' if c['passed'] else 'FAIL'} |")
    lines += ["", "## Thuộc tính", ""] + [f"- `{p['case_id']}`: {'PASS' if p['passed'] else 'FAIL'}" for p in report["properties"]]
    lines += ["", "## Giới hạn", ""] + [f"- {x}" for x in report["limitations"]] + [""]
    return "\n".join(lines)


def _validation_md(report: dict[str, Any]) -> str:
    return "\n".join([
        "# Báo cáo analytical validation — RMS/MAV v0.1", "",
        "## Phạm vi", "",
        "Kiểm chứng công thức và thuộc tính số học của RMS/MAV trên vector kiểm soát.", "",
        "## Kết quả", "", f"- Trạng thái: `{report['verification_status']}`", "- Đơn vị pipeline: `uV`.", "- Normalization: `none`.", "",
        "## Kết luận được phép", "", "Implementation RMS/MAV đáp ứng test toán học đã định nghĩa cho MVP-0.", "",
        "## Kết luận không được phép", "", "- Không tuyên bố phát hiện mỏi cơ.", "- Không tuyên bố clinical validation.", "- Không suy rộng synthetic sang dữ liệu Motion Lab/Noraxon thật.", "",
        "## Giới hạn", "", *[f"- {x}" for x in report["limitations"]], ""
    ])


def main() -> int:
    args = parse_args()
    report = build_report()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    args.evidence_md.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_md.write_text(_evidence_md(report), encoding="utf-8")
    args.validation_md.parent.mkdir(parents=True, exist_ok=True)
    args.validation_md.write_text(_validation_md(report), encoding="utf-8")
    print("TIME-DOMAIN FEATURE VERIFICATION: " + report["verification_status"].upper())
    return 0 if report["verification_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
