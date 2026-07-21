#!/usr/bin/env python3
"""Kiểm chứng toán học/DSP cho spectral_estimation_v0.1.

Script chỉ dùng tín hiệu synthetic có nghiệm/đặc tính biết trước. Kết quả là
analytical software verification, không phải xác nhận lâm sàng.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.signal import periodogram

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "packages" / "semg-core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from semg_core.spectral import (  # noqa: E402
    estimate_periodogram_psd,
    estimate_welch_psd,
    integrate_uniform_psd,
    select_frequency_band,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kiểm chứng spectral estimator v0.1")
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("qa-validation/evidence/day9-spectral-verification.json"),
    )
    parser.add_argument(
        "--evidence-md",
        type=Path,
        default=Path("qa-validation/evidence/day9-spectral-verification.md"),
    )
    parser.add_argument(
        "--validation-md",
        type=Path,
        default=Path(
            "ai-core/validation-reports/analytical_validation_spectral_estimation_v0.1.md"
        ),
    )
    return parser.parse_args()


def _naive_dft(values: np.ndarray) -> np.ndarray:
    n = values.size
    indices = np.arange(n)
    matrix = np.exp(-2j * np.pi * np.outer(indices, indices) / n)
    return matrix @ values


def _relative_error(actual: float, expected: float) -> float:
    if expected == 0:
        return abs(actual)
    return abs(actual - expected) / abs(expected)


def build_report() -> dict[str, Any]:
    fs = 1000.0
    n = 1000
    time_s = np.arange(n, dtype=np.float64) / fs
    checks: list[dict[str, Any]] = []

    # 1. DFT reference vs FFT.
    vector = np.array([0.0, 1.0, -2.0, 3.0, 0.5, -0.25, 1.5, -1.0], dtype=np.float64)
    dft = _naive_dft(vector)
    fft = np.fft.fft(vector)
    max_dft_fft_error = float(np.max(np.abs(dft - fft)))
    checks.append(
        {
            "check_id": "dft_fft_equivalence",
            "status": "passed" if max_dft_fft_error <= 1e-10 else "failed",
            "metrics": {
                "sample_count": int(vector.size),
                "max_absolute_complex_error": max_dft_fft_error,
                "threshold": 1e-10,
            },
            "meaning_vi": "FFT phải cho cùng kết quả số với DFT trực tiếp trong sai số dấu phẩy động.",
        }
    )

    # 2. Frequency-axis geometry.
    single = 10.0 * np.sin(2.0 * np.pi * 80.0 * time_s)
    single_estimate = estimate_welch_psd(
        single,
        sampling_rate_hz=fs,
        nperseg_samples=n,
        noverlap_samples=0,
        nfft_samples=n,
    )
    band_f, band_p = select_frequency_band(
        single_estimate.frequencies_hz,
        single_estimate.psd_uV2_per_hz,
        low_hz=20.0,
        high_hz=400.0,
    )
    geometry_ok = (
        single_estimate.frequencies_hz.size == 501
        and band_f.size == 381
        and abs(single_estimate.frequency_bin_spacing_hz - 1.0) <= 1e-12
        and abs(single_estimate.rayleigh_resolution_hz - 1.0) <= 1e-12
        and single_estimate.frequencies_hz[-1] == 500.0
    )
    checks.append(
        {
            "check_id": "frequency_axis_geometry",
            "status": "passed" if geometry_ok else "failed",
            "metrics": {
                "sampling_rate_hz": fs,
                "sample_count": n,
                "one_sided_bin_count": int(single_estimate.frequencies_hz.size),
                "nyquist_hz": float(single_estimate.frequencies_hz[-1]),
                "bin_spacing_hz": float(single_estimate.frequency_bin_spacing_hz),
                "rayleigh_resolution_hz": float(single_estimate.rayleigh_resolution_hz),
                "analysis_band_bin_count": int(band_f.size),
            },
            "meaning_vi": "Fs=1000 Hz, N=1000 cho trục một phía 0--500 Hz và khoảng cách bin 1 Hz.",
        }
    )

    # 3. Single-tone peak and power.
    single_peak = float(band_f[int(np.argmax(band_p))])
    expected_single_power = 10.0**2 / 2.0
    single_power_error = _relative_error(single_estimate.full_power_uV2, expected_single_power)
    single_ok = abs(single_peak - 80.0) <= 0.5 and single_power_error <= 1e-8
    checks.append(
        {
            "check_id": "single_tone_peak_and_power",
            "status": "passed" if single_ok else "failed",
            "metrics": {
                "expected_peak_hz": 80.0,
                "observed_peak_hz": single_peak,
                "expected_variance_uV2": expected_single_power,
                "integrated_psd_power_uV2": float(single_estimate.full_power_uV2),
                "relative_power_error": single_power_error,
                "parseval_ratio": single_estimate.parseval_ratio,
            },
            "meaning_vi": "Sine biên độ 10 uV phải có công suất trung bình 50 uV^2 và peak tại 80 Hz.",
        }
    )

    # 4. Multi-tone total power and dominant component.
    multi = (
        4.0 * np.sin(2.0 * np.pi * 40.0 * time_s)
        + 8.0 * np.sin(2.0 * np.pi * 120.0 * time_s)
        + 2.0 * np.sin(2.0 * np.pi * 220.0 * time_s)
    )
    multi_estimate = estimate_welch_psd(
        multi,
        sampling_rate_hz=fs,
        nperseg_samples=n,
        noverlap_samples=0,
        nfft_samples=n,
    )
    multi_f, multi_p = select_frequency_band(
        multi_estimate.frequencies_hz,
        multi_estimate.psd_uV2_per_hz,
        low_hz=20.0,
        high_hz=400.0,
    )
    multi_peak = float(multi_f[int(np.argmax(multi_p))])
    expected_multi_power = (4.0**2 + 8.0**2 + 2.0**2) / 2.0
    multi_error = _relative_error(multi_estimate.full_power_uV2, expected_multi_power)
    multi_ok = abs(multi_peak - 120.0) <= 0.5 and multi_error <= 1e-8
    checks.append(
        {
            "check_id": "multitone_dominant_frequency_and_power",
            "status": "passed" if multi_ok else "failed",
            "metrics": {
                "expected_dominant_frequency_hz": 120.0,
                "observed_dominant_frequency_hz": multi_peak,
                "expected_total_power_uV2": expected_multi_power,
                "integrated_psd_power_uV2": float(multi_estimate.full_power_uV2),
                "relative_power_error": multi_error,
            },
            "meaning_vi": "Thành phần 120 Hz có biên độ lớn nhất và tổng PSD phải khớp tổng công suất các sine trực giao.",
        }
    )

    # 5. Welch full-window vs modified periodogram.
    periodogram_estimate = estimate_periodogram_psd(
        multi,
        sampling_rate_hz=fs,
        nfft_samples=n,
    )
    max_psd_diff = float(
        np.max(
            np.abs(
                multi_estimate.psd_uV2_per_hz
                - periodogram_estimate.psd_uV2_per_hz
            )
        )
    )
    equivalence_ok = max_psd_diff <= 1e-10
    checks.append(
        {
            "check_id": "welch_full_window_periodogram_equivalence",
            "status": "passed" if equivalence_ok else "failed",
            "metrics": {
                "max_absolute_psd_difference": max_psd_diff,
                "threshold": 1e-10,
                "nperseg_samples": n,
                "noverlap_samples": 0,
            },
            "meaning_vi": "Với một segment bằng toàn outer window và overlap 0, Welch v0.1 tương đương modified periodogram.",
        }
    )

    # 6. Hann leakage reduction for an off-bin tone.
    offbin = np.sin(2.0 * np.pi * 80.5 * time_s)
    leakage: dict[str, float] = {}
    for taper in ("boxcar", "hann"):
        frequencies, spectrum = periodogram(
            offbin,
            fs=fs,
            window=taper,
            detrend=False,
            return_onesided=True,
            scaling="spectrum",
            nfft=n,
        )
        total = float(np.sum(spectrum))
        far_mask = np.abs(frequencies - 80.5) > 4.0
        leakage[taper] = float(np.sum(spectrum[far_mask]) / total)
    improvement_factor = leakage["boxcar"] / max(leakage["hann"], 1e-30)
    leakage_ok = leakage["hann"] < leakage["boxcar"] * 0.1
    checks.append(
        {
            "check_id": "hann_reduces_far_spectral_leakage",
            "status": "passed" if leakage_ok else "failed",
            "metrics": {
                "off_bin_frequency_hz": 80.5,
                "boxcar_far_leakage_ratio": leakage["boxcar"],
                "hann_far_leakage_ratio": leakage["hann"],
                "improvement_factor": improvement_factor,
                "pass_rule": "hann_ratio < 0.1 * boxcar_ratio",
            },
            "meaning_vi": "Hann giảm sidelobe/leakage xa peak cho tone không nằm đúng frequency bin, đổi lại main lobe rộng hơn.",
        }
    )

    # 7. Parseval-like consistency on deterministic white noise.
    rng = np.random.default_rng(20260721)
    noise = rng.normal(0.0, 5.0, n)
    noise_estimate = estimate_welch_psd(
        noise,
        sampling_rate_hz=fs,
        nperseg_samples=n,
        noverlap_samples=0,
        nfft_samples=n,
    )
    ratio = float(noise_estimate.parseval_ratio or 0.0)
    parseval_ok = 0.95 <= ratio <= 1.05
    checks.append(
        {
            "check_id": "psd_integral_window_weighted_power_consistency",
            "status": "passed" if parseval_ok else "failed",
            "metrics": {
                "time_domain_variance_uV2": float(noise_estimate.time_domain_variance_uV2),
                "window_weighted_power_uV2": float(noise_estimate.window_weighted_power_uV2),
                "integrated_psd_power_uV2": float(noise_estimate.full_power_uV2),
                "parseval_ratio": ratio,
                "accepted_range": [0.95, 1.05],
            },
            "meaning_vi": "Tích phân PSD density phải khớp công suất miền thời gian đã chuẩn hóa theo năng lượng Hann; variance không trọng số được giữ riêng để QA.",
        }
    )

    # 8. Quy luật scale: nhân biên độ c thì PSD và power nhân c^2.
    scaled_estimate = estimate_welch_psd(
        2.0 * multi,
        sampling_rate_hz=fs,
        nperseg_samples=n,
        noverlap_samples=0,
        nfft_samples=n,
    )
    power_scale_ratio = float(
        scaled_estimate.full_power_uV2 / multi_estimate.full_power_uV2
    )
    nonzero = multi_estimate.psd_uV2_per_hz > 1e-18
    psd_scale_error = float(
        np.max(
            np.abs(
                scaled_estimate.psd_uV2_per_hz[nonzero]
                / multi_estimate.psd_uV2_per_hz[nonzero]
                - 4.0
            )
        )
    )
    scaling_ok = abs(power_scale_ratio - 4.0) <= 1e-10 and psd_scale_error <= 1e-8
    checks.append(
        {
            "check_id": "amplitude_scaling_squares_psd_and_power",
            "status": "passed" if scaling_ok else "failed",
            "metrics": {
                "amplitude_scale_factor": 2.0,
                "expected_power_scale_factor": 4.0,
                "observed_power_scale_factor": power_scale_ratio,
                "maximum_psd_scale_absolute_error": psd_scale_error,
            },
            "meaning_vi": "Nhân tín hiệu với 2 phải làm PSD và công suất tích phân tăng 4 lần; đây là kiểm tra đơn vị và chuẩn hóa bắt buộc.",
        }
    )

    status = "passed" if all(item["status"] == "passed" for item in checks) else "failed"
    return {
        "schema_version": "spectral-verification.v0.1",
        "verification_id": "day9-spectral-estimation-v0.1",
        "verification_status": status,
        "clinical_validation_status": "not_validated",
        "data_source": "deterministic_synthetic_signals",
        "configuration": {
            "sampling_rate_hz": fs,
            "outer_window_samples": n,
            "method": "welch",
            "taper": "hann",
            "detrend": "constant",
            "scaling": "density",
            "nperseg_samples": n,
            "noverlap_samples": 0,
            "nfft_samples": n,
            "analysis_band_hz": [20.0, 400.0],
        },
        "checks": checks,
        "limitations": [
            "Tín hiệu kiểm thử là synthetic và có cấu trúc biết trước.",
            "Kiểm chứng peak/power không chứng minh MDF/MNF hay fatigue interpretation đúng trên dữ liệu thật.",
            "Welch v0.1 chỉ có một segment; chưa đánh giá trade-off nhiều segment trên dữ liệu Motion Lab.",
            "Dải 20-400 Hz và Hann cần được đánh giá lại sau audit Noraxon và local validation.",
        ],
    }


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Bằng chứng kiểm chứng spectral estimation v0.1",
        "",
        f"- Trạng thái: **{report['verification_status']}**",
        "- Loại bằng chứng: kiểm chứng toán học/DSP trên tín hiệu synthetic xác định",
        "- Xác nhận lâm sàng: **chưa có**",
        "",
        "## Kết quả",
        "",
        "| Kiểm tra | Trạng thái | Ý nghĩa |",
        "|---|---|---|",
    ]
    for item in report["checks"]:
        lines.append(
            f"| `{item['check_id']}` | {item['status']} | {item['meaning_vi']} |"
        )
    lines.extend(["", "## Chỉ số chi tiết", ""])
    for item in report["checks"]:
        lines.append(f"### `{item['check_id']}`")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(item["metrics"], indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
    lines.extend(["## Giới hạn", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def _validation_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Báo cáo kiểm chứng phân tích — Spectral Estimation v0.1",
            "",
            "> Tài liệu này là bằng chứng kiểm chứng phần mềm/DSP trên dữ liệu synthetic; không phải xác nhận lâm sàng.",
            "",
            f"**Kết quả:** `{report['verification_status']}`",
            "",
            "## Phạm vi đã kiểm chứng",
            "",
            "- DFT trực tiếp tương đương FFT trong sai số số học.",
            "- Trục tần số một phía, Nyquist, bin spacing và Rayleigh resolution.",
            "- Peak và tổng power của sine/multi-tone có nghiệm biết trước.",
            "- Welch full-window tương đương modified periodogram.",
            "- Hann giảm far spectral leakage trên tone lệch bin.",
            "- Nhân biên độ tín hiệu 2 lần làm PSD/công suất tăng 4 lần.",
            "- Tích phân PSD density khớp công suất miền thời gian đã chuẩn hóa theo năng lượng Hann; variance không trọng số được lưu riêng.",
            "",
            "## Ngoài phạm vi",
            "",
            "- MDF, MNF và trend theo thời gian.",
            "- Fatigue status, FRS, ML hoặc clinical interpretation.",
            "- Tối ưu tham số trên dữ liệu Noraxon/Motion Lab thật.",
            "",
            "## Quyết định",
            "",
            "Spectral estimator được phép dùng làm upstream kỹ thuật cho Day 10 nếu toàn bộ checker Day 9 pass; trạng thái xác nhận lâm sàng vẫn là `not_validated`.",
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    report = build_report()
    for path, content in (
        (args.json_output, json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"),
        (args.evidence_md, _markdown(report)),
        (args.validation_md, _validation_markdown(report)),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Spectral verification: {report['verification_status']}")
    for item in report["checks"]:
        print(f"- {item['check_id']}: {item['status']}")
    return 0 if report["verification_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
