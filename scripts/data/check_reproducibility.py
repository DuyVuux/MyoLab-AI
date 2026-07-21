#!/usr/bin/env python3
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "services" / "quality-gate-service" / "src"))
sys.path.insert(0, str(ROOT / "services" / "preprocessing-service" / "src"))

from semg_core.io import NormalizedSignal, NormalizedChannel, PhaseMarker, ProtocolRef
from result_models import QCResult, MFCVEligibilityResult, AbstentionResult
from pipeline import PreprocessingPipeline

def create_fake_signal():
    samples = np.sin(2 * np.pi * 50.0 * np.arange(1000) / 1000.0) * 10.0
    return NormalizedSignal(
        session_id="REPRO_TEST",
        sampling_rate_hz=1000.0,
        time_s=np.arange(1000) / 1000.0,
        channels={"ch1": NormalizedChannel(
            channel_id="ch1",
            muscle="Biceps",
            side="Right",
            role="Agonist",
            source_column="raw",
            source_unit="uV",
            samples_uV=samples
        )},
        protocol_ref=ProtocolRef("test", "v1"),
        phase_markers=[PhaseMarker("phase1", 0.0, 1.0)],
        source_file_name="fake.csv",
        source_hash_sha256="a" * 64,
        data_source="synth",
        processing_history=[],
    )

config = {
    "config_id": "preprocess_v0.1",
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
        "recommended_record_edge_guard_s": 0.0
    }
}

qc_pass = QCResult(
    session_id="REPRO_TEST",
    status="pass",
    analysis_allowed=True,
    checks=(),
    reason_codes=(),
    mfcv=MFCVEligibilityResult(eligible=True, reason_codes=()),
    abstention=AbstentionResult(required=False, reason=None),
)

pipeline1 = PreprocessingPipeline(config)
res1 = pipeline1.run(create_fake_signal(), qc_pass)
hash1 = res1.signal.combined_output_hash_sha256

pipeline2 = PreprocessingPipeline(config)
res2 = pipeline2.run(create_fake_signal(), qc_pass)
hash2 = res2.signal.combined_output_hash_sha256

print(f"Run 1 Hash: {hash1}")
print(f"Run 2 Hash: {hash2}")
print(f"Match: {hash1 == hash2}")
