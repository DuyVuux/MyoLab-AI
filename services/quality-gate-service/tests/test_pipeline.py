from __future__ import annotations

from pathlib import Path

import numpy as np

from preprocess_config import load_preprocess_config
from pipeline import PreprocessingPipeline


ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "services" / "preprocessing-service" / "configs" / "preprocess_v0.1.yaml"


def signal_mix(fs: float = 1000.0, duration_s: float = 6.0) -> np.ndarray:
    t = np.arange(int(fs * duration_s), dtype=np.float64) / fs
    return (
        5.0 * np.sin(2 * np.pi * 5.0 * t)
        + 20.0 * np.sin(2 * np.pi * 80.0 * t)
        + 2.0 * np.sin(2 * np.pi * 450.0 * t)
    )


def test_completed_preserves_shape_and_metadata(make_signal, make_qc) -> None:
    signal = make_signal(signal_mix())
    result = PreprocessingPipeline(load_preprocess_config(CONFIG)).run(signal, make_qc())
    assert result.status == "completed"
    assert result.downstream_allowed is True
    assert result.signal is not None
    assert result.signal.time_s.shape == signal.time_s.shape
    assert result.signal.channels["VL_R_01"].samples_uV.shape == signal.channels["VL_R_01"].samples_uV.shape
    assert result.signal.channels["VL_R_01"].samples_uV.flags.writeable is False


def test_notch_is_skipped_without_powerline_reason(make_signal, make_qc) -> None:
    result = PreprocessingPipeline(load_preprocess_config(CONFIG)).run(
        make_signal(signal_mix()), make_qc()
    )
    steps = {step.step_id: step.status for step in result.steps}
    assert steps["conditional_powerline_notch"] == "skipped"


def test_notch_is_applied_when_qc_flags_powerline(make_signal, make_qc) -> None:
    result = PreprocessingPipeline(load_preprocess_config(CONFIG)).run(
        make_signal(signal_mix()),
        make_qc(status="warning", reasons=("POWERLINE_NOISE_HIGH",)),
    )
    steps = {step.step_id: step.status for step in result.steps}
    assert steps["conditional_powerline_notch"] == "applied"
    assert result.signal is not None
    assert result.signal.channels["VL_R_01"].qa_diagnostics["notch_applied"] is True


def test_qc_fail_blocks_without_running_filter(make_signal, make_qc) -> None:
    result = PreprocessingPipeline(load_preprocess_config(CONFIG)).run(
        make_signal(signal_mix()),
        make_qc(status="fail", allowed=False, reasons=("FLATLINE_EXCESSIVE",)),
    )
    assert result.status == "blocked"
    assert result.downstream_allowed is False
    assert result.signal is None
    assert "PREPROCESSING_BLOCKED_BY_QC" in result.reason_codes
    assert result.steps == ()


def test_nonfinite_is_blocked_even_if_external_qc_object_is_inconsistent(make_signal, make_qc) -> None:
    x = signal_mix()
    x[100] = np.nan
    result = PreprocessingPipeline(load_preprocess_config(CONFIG)).run(
        make_signal(x), make_qc()
    )
    assert result.status == "blocked"
    assert "PREPROCESSING_NONFINITE_UNSUPPORTED" in result.reason_codes


def test_output_hash_is_reproducible(make_signal, make_qc) -> None:
    pipeline = PreprocessingPipeline(load_preprocess_config(CONFIG))
    signal = make_signal(signal_mix())
    first = pipeline.run(signal, make_qc())
    second = pipeline.run(signal, make_qc())
    assert first.signal is not None and second.signal is not None
    assert first.signal.combined_output_hash_sha256 == second.signal.combined_output_hash_sha256
