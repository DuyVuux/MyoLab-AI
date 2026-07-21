import pytest
import numpy as np

from semg_core.io import NormalizedSignal, NormalizedChannel
from result_models import QCResult, MFCVEligibilityResult, AbstentionResult
from pipeline import PreprocessingPipeline

def test_conditional_notch_orchestration() -> None:
    config = {
        "config_id": "test_cfg",
        "steps": {
            "mean_center": {"enabled": True},
            "bandpass": {
                "order": 4,
                "low_cut_hz": 20.0,
                "high_cut_hz": 400.0,
                "nyquist_margin_ratio": 0.90
            },
            "notch": {
                "line_frequency_hz": 50.0,
                "q_factor": 30.0,
                "trigger_reason_code": "POWERLINE_NOISE_HIGH"
            }
        },
        "edge_policy": {
            "recommended_record_edge_guard_s": 0.5
        }
    }
    pipeline = PreprocessingPipeline(config)
    
    # Fake signal
    samples = np.sin(2 * np.pi * 50.0 * np.arange(1000) / 1000.0) * 10.0
    signal = NormalizedSignal(
        session_id="SESS1",
        sampling_rate_hz=1000.0,
        time_s=1.0,
        channels={"ch1": NormalizedChannel(
            channel_id="ch1",
            muscle="Biceps",
            side="Right",
            role="Agonist",
            source_column="ch1_raw",
            source_unit="uV",
            samples_uV=samples
        )},
        protocol_ref="test",
        phase_markers=[],
        source_file_name="test.csv",
        source_hash_sha256="hash",
        data_source="synth",
        processing_history=[],
    )
    
    # 1. QC pass -> notch skipped
    qc_pass = QCResult(
        session_id="SESS1",
        status="pass",
        analysis_allowed=True,
        checks=(),
        reason_codes=(),
        mfcv=MFCVEligibilityResult(eligible=True, reason_codes=()),
        abstention=AbstentionResult(required=False, reason=None),
    )
    res_pass = pipeline.run(signal, qc_pass)
    
    # Find notch step record
    notch_step_pass = next(s for s in res_pass.steps if s.step_id == "conditional_powerline_notch")
    assert notch_step_pass.status == "skipped"
    assert not res_pass.signal.channels["ch1"].qa_diagnostics["notch_applied"]
    
    # 2. QC warning powerline -> notch applied
    qc_warn = QCResult(
        session_id="SESS1",
        status="warning",
        analysis_allowed=True,
        checks=(),
        reason_codes=("POWERLINE_NOISE_HIGH",),
        mfcv=MFCVEligibilityResult(eligible=True, reason_codes=()),
        abstention=AbstentionResult(required=False, reason=None),
    )
    res_warn = pipeline.run(signal, qc_warn)

    
    notch_step_warn = next(s for s in res_warn.steps if s.step_id == "conditional_powerline_notch")
    assert notch_step_warn.status == "applied"
    assert res_warn.signal.channels["ch1"].qa_diagnostics["notch_applied"]
