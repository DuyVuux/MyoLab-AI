#!/usr/bin/env python3
import json
import sys
from pathlib import Path
import numpy as np
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]
SEMGC_PATH = ROOT / "packages" / "semg-core"
INGESTION_PATH = ROOT / "services" / "signal-ingestion-service" / "src"
QC_PATH = ROOT / "services" / "quality-gate-service" / "src"
PREPROC_PATH = ROOT / "services" / "preprocessing-service" / "src"

for path in (SEMGC_PATH, INGESTION_PATH, QC_PATH, PREPROC_PATH):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from semg_core.io import NormalizedSignal, NormalizedChannel, PhaseMarker, ProtocolRef
from result_models import QCResult, MFCVEligibilityResult, AbstentionResult
from pipeline import PreprocessingPipeline
from preprocess_result_models import PreprocessingRunResult

def create_fake_signal():
    samples = np.sin(2 * np.pi * 50.0 * np.arange(1000) / 1000.0) * 10.0
    return NormalizedSignal(
        session_id="E2E_TEST",
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

pipeline = PreprocessingPipeline(config)
schema = json.loads((ROOT / "packages" / "common-schemas" / "json" / "preprocessing-result.schema.json").read_text())
signal = create_fake_signal()

def run_scenario(name, qc_result):
    res = pipeline.run(signal, qc_result)
    res_dict = res.to_dict()
    validate(instance=res_dict, schema=schema)
    out_file = ROOT / f"qa-validation/evidence/e2e_{name}.json"
    out_file.write_text(json.dumps(res_dict, indent=2))
    print(f"Scenario {name} validation PASSED. Written to {out_file}")

# Scenario A: Golden (QC pass)
qc_pass = QCResult(
    session_id="E2E_TEST",
    status="pass",
    analysis_allowed=True,
    checks=(),
    reason_codes=(),
    mfcv=MFCVEligibilityResult(eligible=True, reason_codes=()),
    abstention=AbstentionResult(required=False, reason=None),
)
run_scenario("A_Golden", qc_pass)

# Scenario B: Powerline warning
qc_warn = QCResult(
    session_id="E2E_TEST",
    status="warning",
    analysis_allowed=True,
    checks=(),
    reason_codes=("POWERLINE_NOISE_HIGH",),
    mfcv=MFCVEligibilityResult(eligible=True, reason_codes=()),
    abstention=AbstentionResult(required=False, reason=None),
)
run_scenario("B_Powerline", qc_warn)

# Scenario C: Flatline fail
qc_fail = QCResult(
    session_id="E2E_TEST",
    status="fail",
    analysis_allowed=False,
    checks=(),
    reason_codes=("FLATLINE_DETECTED",),
    mfcv=MFCVEligibilityResult(eligible=False, reason_codes=("FLATLINE",)),
    abstention=AbstentionResult(required=True, reason="FLATLINE"),
)
run_scenario("C_Flatline", qc_fail)
