#!/usr/bin/env python3
"""Kiểm chứng phân tích `preprocess_v0.1` trên fixture synthetic deterministic."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
from typing import Any, Mapping

import numpy as np
from scipy import __version__ as scipy_version
from scipy.signal import sosfreqz
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMGC_CORE = ROOT / "packages" / "semg-core"
if str(SEMGC_CORE) not in sys.path:
    sys.path.insert(0, str(SEMGC_CORE))

from semg_core.preprocessing import (  # noqa: E402
    design_butterworth_bandpass_sos,
    design_notch_sos,
    preprocess_channel,
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"YAML root phải là object: {path}")
    return dict(payload)


def finite_db(value: float, floor: float) -> float:
    return float(20.0 * math.log10(max(float(value), floor)))


def effective_zero_phase_gain_db(sos: np.ndarray, frequency_hz: float, fs: float, floor: float) -> float:
    _, response = sosfreqz(sos, worN=np.asarray([frequency_hz], dtype=np.float64), fs=fs)
    one_pass = float(abs(response[0]))  # type: ignore
    return finite_db(one_pass * one_pass, floor)


def evaluate_criterion(criterion: Mapping[str, Any], value_db: float) -> dict[str, Any]:
    minimum = criterion.get("min_gain_db")
    maximum = criterion.get("max_gain_db")
    passed = True
    if minimum is not None:
        passed = passed and value_db >= float(minimum)
    if maximum is not None:
        passed = passed and value_db <= float(maximum)
    return {
        "id": str(criterion["id"]),
        "path": str(criterion["path"]),
        "frequency_hz": float(criterion["frequency_hz"]),
        "measured_gain_db": float(value_db),
        "min_gain_db": None if minimum is None else float(minimum),
        "max_gain_db": None if maximum is None else float(maximum),
        "passed": bool(passed),
    }


def sinusoidal_amplitude(signal: np.ndarray, time_s: np.ndarray, frequency_hz: float) -> float:
    signal = np.asarray(signal, dtype=np.float64)
    time_s = np.asarray(time_s, dtype=np.float64)
    if signal.size != time_s.size or signal.size < 2:
        raise ValueError("signal và time_s phải có cùng length >= 2")
    omega_t = 2.0 * np.pi * float(frequency_hz) * time_s
    cosine = np.cos(omega_t)
    sine = np.sin(omega_t)
    a_cos = 2.0 * float(np.dot(signal, cosine)) / signal.size
    a_sin = 2.0 * float(np.dot(signal, sine)) / signal.size
    return float(np.hypot(a_cos, a_sin))


def make_multitone(profile: Mapping[str, Any], fs: float) -> tuple[np.ndarray, np.ndarray]:
    fixture = profile["fixture"]
    duration_s = float(fixture["duration_s"])
    sample_count = int(round(duration_s * fs))
    time_s = np.arange(sample_count, dtype=np.float64) / fs
    signal = np.zeros(sample_count, dtype=np.float64)
    for component in fixture["components"]:
        frequency_hz = float(component["frequency_hz"])
        amplitude_uV = float(component["amplitude_uV"])
        phase_rad = float(component["phase_rad"])
        signal += amplitude_uV * np.sin(2.0 * np.pi * frequency_hz * time_s + phase_rad)
    return time_s, signal


def core_kwargs(config: Mapping[str, Any], *, notch_enabled: bool) -> dict[str, Any]:
    steps = config["steps"]
    return {
        "mean_center_enabled": bool(steps["mean_center"]["enabled"]),
        "bandpass_low_hz": float(steps["bandpass"]["low_cut_hz"]),
        "bandpass_high_hz": float(steps["bandpass"]["high_cut_hz"]),
        "bandpass_order": int(steps["bandpass"]["order"]),
        "nyquist_margin_ratio": float(steps["bandpass"]["nyquist_margin_ratio"]),
        "notch_enabled": bool(notch_enabled),
        "notch_frequency_hz": float(steps["notch"]["line_frequency_hz"]),
        "notch_q_factor": float(steps["notch"]["q_factor"]),
    }


def run_theoretical(config: Mapping[str, Any], profile: Mapping[str, Any]) -> dict[str, Any]:
    fs = float(profile["sampling_rate_hz"])
    floor = float(profile["numerical_floor"])
    steps = config["steps"]
    bandpass = design_butterworth_bandpass_sos(
        sampling_rate_hz=fs,
        low_cut_hz=float(steps["bandpass"]["low_cut_hz"]),
        high_cut_hz=float(steps["bandpass"]["high_cut_hz"]),
        order=int(steps["bandpass"]["order"]),
        nyquist_margin_ratio=float(steps["bandpass"]["nyquist_margin_ratio"]),
    )
    notch = design_notch_sos(
        sampling_rate_hz=fs,
        line_frequency_hz=float(steps["notch"]["line_frequency_hz"]),
        q_factor=float(steps["notch"]["q_factor"]),
    )

    measurements: dict[str, dict[str, float]] = {"bandpass": {}, "bandpass_plus_notch": {}}
    results: list[dict[str, Any]] = []
    for criterion in profile["criteria"]["theoretical"]:
        frequency = float(criterion["frequency_hz"])
        path = str(criterion["path"])
        bp_db = effective_zero_phase_gain_db(bandpass, frequency, fs, floor)
        if path == "bandpass":
            measured = bp_db
        elif path == "bandpass_plus_notch":
            notch_db = effective_zero_phase_gain_db(notch, frequency, fs, floor)
            measured = bp_db + notch_db
        else:
            raise ValueError(f"Theoretical path không hỗ trợ: {path}")
        measurements[path][f"{frequency:g}"] = float(measured)
        results.append(evaluate_criterion(criterion, measured))
    return {
        "measurements": measurements,
        "criteria": results,
        "passed": bool(all(item["passed"] for item in results)),
    }


def run_empirical(config: Mapping[str, Any], profile: Mapping[str, Any]) -> tuple[dict[str, Any], np.ndarray]:
    fs = float(profile["sampling_rate_hz"])
    floor = float(profile["numerical_floor"])
    time_s, source = make_multitone(profile, fs)
    guard_s = float(profile["fixture"]["analysis_edge_guard_s"])
    guard = int(round(guard_s * fs))
    if 2 * guard >= source.size:
        raise ValueError("Edge guard quá lớn so với fixture")
    interior = slice(guard, source.size - guard)
    time_interior = time_s[interior]
    source_interior = source[interior]

    bandpass_result = preprocess_channel(source, sampling_rate_hz=fs, **core_kwargs(config, notch_enabled=False))
    notch_result = preprocess_channel(source, sampling_rate_hz=fs, **core_kwargs(config, notch_enabled=True))

    outputs = {
        "bandpass": bandpass_result.samples_uV[interior],
        "bandpass_plus_notch": notch_result.samples_uV[interior],
    }
    measurements: dict[str, dict[str, Any]] = {"bandpass": {}, "bandpass_plus_notch": {}}
    results: list[dict[str, Any]] = []
    for criterion in profile["criteria"]["empirical"]:
        frequency = float(criterion["frequency_hz"])
        path = str(criterion["path"])
        input_amp = sinusoidal_amplitude(source_interior, time_interior, frequency)
        output_amp = sinusoidal_amplitude(outputs[path], time_interior, frequency)
        gain_db = finite_db(output_amp / max(input_amp, floor), floor)
        measurements[path][f"{frequency:g}"] = {
            "input_amplitude_uV": input_amp,
            "output_amplitude_uV": output_amp,
            "gain_db": gain_db,
        }
        results.append(evaluate_criterion(criterion, gain_db))
    return {
        "fixture": {
            "sampling_rate_hz": fs,
            "sample_count": int(source.size),
            "duration_s": float(source.size / fs),
            "analysis_edge_guard_s": guard_s,
            "analysis_sample_count": int(source_interior.size),
        },
        "measurements": measurements,
        "criteria": results,
        "passed": bool(all(item["passed"] for item in results)),
    }, source


def run_zero_phase(config: Mapping[str, Any], profile: Mapping[str, Any]) -> dict[str, Any]:
    fs = float(profile["sampling_rate_hz"])
    cfg = profile["criteria"]["zero_phase"]
    sample_count = int(cfg["impulse_sample_count"])
    if sample_count % 2 == 0:
        raise ValueError("Impulse sample count phải là số lẻ")
    center = sample_count // 2
    impulse = np.zeros(sample_count, dtype=np.float64)
    impulse[center] = 1.0
    result = preprocess_channel(impulse, sampling_rate_hz=fs, **core_kwargs(config, notch_enabled=False))
    output = result.samples_uV
    peak_offset = int(np.argmax(np.abs(output)) - center)
    left = output[:center][::-1]
    right = output[center + 1 :]
    maximum = max(float(np.max(np.abs(output))), 1e-15)
    symmetry_error = float(np.max(np.abs(left - right)) / maximum)
    passed = (
        abs(peak_offset) <= int(cfg["max_abs_peak_offset_samples"])
        and symmetry_error <= float(cfg["max_normalized_symmetry_error"])
    )
    return {
        "sample_count": sample_count,
        "center_index": center,
        "peak_offset_samples": peak_offset,
        "normalized_symmetry_error": symmetry_error,
        "max_abs_peak_offset_samples": int(cfg["max_abs_peak_offset_samples"]),
        "max_normalized_symmetry_error": float(cfg["max_normalized_symmetry_error"]),
        "passed": bool(passed),
    }


def run_edge(config: Mapping[str, Any], profile: Mapping[str, Any]) -> dict[str, Any]:
    fs = float(profile["sampling_rate_hz"])
    cfg = profile["criteria"]["edge"]
    duration_s = float(cfg["duration_s"])
    sample_count = int(round(duration_s * fs))
    time_s = np.arange(sample_count, dtype=np.float64) / fs
    frequency = float(cfg["frequency_hz"])
    amplitude = float(cfg["amplitude_uV"])
    source = amplitude * np.sin(2.0 * np.pi * frequency * time_s + 0.3)
    result = preprocess_channel(source, sampling_rate_hz=fs, **core_kwargs(config, notch_enabled=False))
    output = result.samples_uV

    guard_s = float(config["edge_policy"]["recommended_record_edge_guard_s"])
    guard = int(round(guard_s * fs))
    if guard <= 0 or 2 * guard >= sample_count:
        raise ValueError("Edge guard không hợp lệ")
    interior = slice(guard, sample_count - guard)
    time_interior = time_s[interior]
    output_interior = output[interior]

    omega = 2.0 * np.pi * frequency * time_interior
    cosine = np.cos(omega)
    sine = np.sin(omega)
    a_cos = 2.0 * float(np.dot(output_interior, cosine)) / output_interior.size
    a_sin = 2.0 * float(np.dot(output_interior, sine)) / output_interior.size
    fitted_all = a_cos * np.cos(2.0 * np.pi * frequency * time_s) + a_sin * np.sin(2.0 * np.pi * frequency * time_s)
    error = output - fitted_all
    interior_rmse = float(np.sqrt(np.mean(np.square(error[interior]))))
    edge_values = np.concatenate([error[:guard], error[-guard:]])
    edge_rmse = float(np.sqrt(np.mean(np.square(edge_values))))
    ratio = float(edge_rmse / max(interior_rmse, 1e-15))
    passed = (
        interior_rmse <= float(cfg["max_interior_rmse_uV"])
        and ratio >= float(cfg["min_edge_to_interior_rmse_ratio"])
        and guard_s > 0
    )
    return {
        "frequency_hz": frequency,
        "duration_s": duration_s,
        "edge_guard_s": guard_s,
        "edge_guard_samples": guard,
        "interior_rmse_uV": interior_rmse,
        "edge_rmse_uV": edge_rmse,
        "edge_to_interior_rmse_ratio": ratio,
        "max_interior_rmse_uV": float(cfg["max_interior_rmse_uV"]),
        "min_edge_to_interior_rmse_ratio": float(cfg["min_edge_to_interior_rmse_ratio"]),
        "passed": bool(passed),
    }


def run_determinism(config: Mapping[str, Any], profile: Mapping[str, Any], source: np.ndarray) -> dict[str, Any]:
    fs = float(profile["sampling_rate_hz"])
    cfg = profile["criteria"]["determinism"]
    repeat_count = int(cfg["repeat_count"])
    hashes: list[str] = []
    for _ in range(repeat_count):
        result = preprocess_channel(source, sampling_rate_hz=fs, **core_kwargs(config, notch_enabled=False))
        hashes.append(result.diagnostics.output_hash_sha256)
    identical = len(set(hashes)) == 1
    required = bool(cfg["require_identical_hashes_in_same_environment"])
    passed = identical if required else True
    return {
        "repeat_count": repeat_count,
        "hashes": hashes,
        "identical_hashes": identical,
        "require_identical_hashes_in_same_environment": required,
        "passed": bool(passed),
    }


def render_evidence(report: Mapping[str, Any]) -> str:
    lines = [
        "# Bằng chứng Day 6 — Kiểm chứng preprocessing v0.1",
        "",
        f"- Config: `{report['config']['config_id']}`",
        f"- Config SHA-256: `{report['config']['sha256']}`",
        f"- Sampling rate kiểm chứng: `{report['profile']['sampling_rate_hz']} Hz`",
        f"- Trạng thái kiểm chứng phân tích: **{report['overall']['analytical_verification_status'].upper()}**",
        "- Trạng thái xác nhận lâm sàng: **CHƯA XÁC NHẬN**",
        "",
        "## Tiêu chí lý thuyết",
        "",
        "| ID | Đường xử lý | Hz | Gain dB | Kết quả |",
        "|---|---|---:|---:|---|",
    ]
    for item in report["theoretical"]["criteria"]:
        lines.append(f"| {item['id']} | {item['path']} | {item['frequency_hz']:.1f} | {item['measured_gain_db']:.4f} | {'PASS' if item['passed'] else 'FAIL'} |")
    lines += ["", "## Tiêu chí thực nghiệm", "", "| ID | Đường xử lý | Hz | Gain dB | Kết quả |", "|---|---|---:|---:|---|"]
    for item in report["empirical"]["criteria"]:
        lines.append(f"| {item['id']} | {item['path']} | {item['frequency_hz']:.1f} | {item['measured_gain_db']:.4f} | {'PASS' if item['passed'] else 'FAIL'} |")
    zp = report["zero_phase"]
    edge = report["edge"]
    det = report["determinism"]
    lines += [
        "",
        "## Pha bằng không",
        "",
        f"- Peak offset: `{zp['peak_offset_samples']} sample`.",
        f"- Normalized symmetry error: `{zp['normalized_symmetry_error']:.3e}`.",
        f"- Kết quả: **{'PASS' if zp['passed'] else 'FAIL'}**.",
        "",
        "## Hành vi tại biên",
        "",
        f"- Interior RMSE: `{edge['interior_rmse_uV']:.6g} uV`.",
        f"- Edge RMSE: `{edge['edge_rmse_uV']:.6g} uV`.",
        f"- Edge/interior ratio: `{edge['edge_to_interior_rmse_ratio']:.3f}`.",
        f"- Edge guard: `{edge['edge_guard_s']} s`.",
        f"- Kết quả: **{'PASS' if edge['passed'] else 'FAIL'}**.",
        "",
        "## Tính xác định trong cùng môi trường",
        "",
        f"- Repeat count: `{det['repeat_count']}`.",
        f"- Hashes giống nhau: `{det['identical_hashes']}`.",
        f"- Hash: `{det['hashes'][0] if det['hashes'] else 'N/A'}`.",
        "",
        "## Giới hạn",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    lines += [
        "",
        "> Kết quả này là analytical verification cho MVP-0 offline trên fixture synthetic. Đây không phải xác nhận lâm sàng, không chứng minh hiệu quả chẩn đoán và không xác nhận realtime behavior.",
        "",
    ]
    return "\n".join(lines)


def render_validation_report(report: Mapping[str, Any]) -> str:
    status = report["overall"]["analytical_verification_status"].upper()
    ready = "SẴN SÀNG" if report["overall"]["all_passed"] else "CHƯA SẴN SÀNG"
    return f"""# Báo cáo kiểm chứng phân tích — `preprocess_v0.1`

## 1. Phạm vi

- MVP-0 ngoại tuyến.
- Fixture synthetic có tính xác định.
- Sampling rate: {report['profile']['sampling_rate_hz']} Hz.
- Band-pass/conditional notch theo config `{report['config']['config_id']}`.

## 2. Khả năng truy xuất

- Config path: `{report['config']['path']}`
- Config SHA-256: `{report['config']['sha256']}`
- Verification profile: `{report['profile']['profile_id']}`
- Verification report schema: `{report['schema_version']}`

## 3. Kết quả

| Hạng mục | Kết quả |
|---|---|
| Đáp ứng lý thuyết | {'PASS' if report['theoretical']['passed'] else 'FAIL'} |
| Thực nghiệm đa tần | {'PASS' if report['empirical']['passed'] else 'FAIL'} |
| Pha bằng không | {'PASS' if report['zero_phase']['passed'] else 'FAIL'} |
| Hành vi tại biên | {'PASS' if report['edge']['passed'] else 'FAIL'} |
| Tính xác định trong cùng môi trường | {'PASS' if report['determinism']['passed'] else 'FAIL'} |
| Overall analytical verification | **{status}** |

## 4. Quyết định

- Trạng thái kiểm chứng phân tích preprocessing: **{status}**.
- Trạng thái xác nhận lâm sàng: **CHƯA XÁC NHẬN**.
- Khả năng tương thích thời gian thực: **KHÔNG**.
- Mức sẵn sàng cho windowing Day 7: **{ready}**.

## 5. Giới hạn

""" + "\n".join(f"- {item}" for item in report["limitations"]) + """

## 6. Tuyên bố an toàn

Báo cáo này chỉ xác nhận implementation phù hợp specification trên fixture kiểm soát. Nó không xác nhận giá trị lâm sàng, không xác nhận electrode placement, không xác nhận dữ liệu Noraxon thật và không tạo kết luận về mỏi cơ.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "services/preprocessing-service/configs/preprocess_v0.1.yaml")
    parser.add_argument("--profile", type=Path, default=ROOT / "qa-validation/configs/preprocess_verification_v0.1.yaml")
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--evidence-md", type=Path, required=True)
    parser.add_argument("--validation-md", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = args.config.resolve()
    profile_path = args.profile.resolve()
    config = load_yaml(config_path)
    profile = load_yaml(profile_path)
    if config.get("config_id") != profile.get("target_config_id"):
        raise SystemExit("Profile target_config_id không khớp config")
    if config.get("clinical_validation_status") != "not_validated":
        raise SystemExit("Day 6 không cho phép claim clinical validation")
    if config.get("mode", {}).get("execution") != "offline":
        raise SystemExit("Day 6 chỉ verify offline config")
    if config.get("mode", {}).get("realtime_compatible") is not False:
        raise SystemExit("Config không được claim realtime compatibility")

    theoretical = run_theoretical(config, profile)
    empirical, deterministic_source = run_empirical(config, profile)
    zero_phase = run_zero_phase(config, profile)
    edge = run_edge(config, profile)
    determinism = run_determinism(config, profile, deterministic_source)
    all_passed = all((theoretical["passed"], empirical["passed"], zero_phase["passed"], edge["passed"], determinism["passed"]))

    report = {
        "schema_version": "preprocessing-verification-report.v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": {
            "config_id": str(config["config_id"]),
            "path": str(config_path.relative_to(ROOT)),
            "sha256": file_sha256(config_path),
            "status": str(config.get("status")),
            "clinical_validation_status": str(config.get("clinical_validation_status")),
            "execution_mode": "offline_zero_phase",
            "realtime_compatible": False,
        },
        "profile": {
            "profile_id": str(profile["profile_id"]),
            "path": str(profile_path.relative_to(ROOT)),
            "sha256": file_sha256(profile_path),
            "sampling_rate_hz": float(profile["sampling_rate_hz"]),
            "clinical_validation_status": str(profile["clinical_validation_status"]),
        },
        "runtime_summary": {
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "scipy_version": scipy_version,
            "platform": platform.platform(),
        },
        "theoretical": theoretical,
        "empirical": empirical,
        "zero_phase": zero_phase,
        "edge": edge,
        "determinism": determinism,
        "overall": {
            "all_passed": bool(all_passed),
            "analytical_verification_status": "passed" if all_passed else "failed",
            "clinical_validation_status": "not_validated",
            "windowing_readiness": "ready" if all_passed else "blocked",
        },
        "limitations": list(profile.get("limitations", [])) + [
            "Exact output hash được yêu cầu trong cùng environment; qua environment khác cần numerical tolerance.",
            "Không kiểm chứng electrode placement, crosstalk, protocol adherence hoặc clinical interpretation.",
            "Không kiểm chứng MFCV/CV preprocessing.",
        ],
    }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_md.parent.mkdir(parents=True, exist_ok=True)
    args.validation_md.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.evidence_md.write_text(render_evidence(report), encoding="utf-8")
    args.validation_md.write_text(render_validation_report(report), encoding="utf-8")

    if not args.quiet:
        print(json.dumps({
            "all_passed": all_passed,
            "config_sha256": report["config"]["sha256"],
            "theoretical_passed": theoretical["passed"],
            "empirical_passed": empirical["passed"],
            "zero_phase_passed": zero_phase["passed"],
            "edge_passed": edge["passed"],
            "determinism_passed": determinism["passed"],
            "output": str(args.json_output),
        }, ensure_ascii=False, indent=2))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
