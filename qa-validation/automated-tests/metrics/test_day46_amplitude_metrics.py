"""DAY46 automated unit tests for RMS and MAV metric calculation and fail-closed gates."""

import sys
from pathlib import Path
import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SEMG_ROOT = REPO_ROOT / "packages" / "semg-core"
if str(SEMG_ROOT) not in sys.path:
    sys.path.insert(0, str(SEMG_ROOT))

from semg_core.metrics.amplitude import evaluate_amplitude_metric
from semg_core.provenance.processing_manifest import (
    CodeComponentRef,
    ProcessedArtifactRef,
    ProcessingManifest,
    ProcessingOutcome,
    ProcessingProfileRef,
    RawSourceRef,
    WindowRef,
)


def sample_manifest_dict():
    return {
        "manifest_id": "pman_sha256_" + "1" * 64,
        "processing_run_id": "prun_sha256_" + "2" * 64,
        "final_artifact": {"artifact_id": "part_sha256_" + "3" * 64},
        "window": {"window_id": "w1"},
        "profile": {
            "profile_id": "p",
            "config_fingerprint": "pprof_sha256_" + "4" * 64,
        },
    }


def sample_manifest_object():
    return ProcessingManifest(
        schema_version="0.1",
        manifest_contract_version="0.1.0",
        manifest_id="pman_sha256_" + "1" * 64,
        processing_run_id="prun_sha256_" + "2" * 64,
        outcome=ProcessingOutcome.COMPLETED,
        correlation_id="corr_123",
        source=RawSourceRef(source_id="src_sha256_" + "a" * 64, sha256="a" * 64),
        window=WindowRef(
            window_id="w1",
            session_id="s1",
            channel_id="ch1",
            start_sample=0,
            end_sample_exclusive=1000,
        ),
        profile=ProcessingProfileRef(
            profile_id="p",
            version="1.0",
            config_fingerprint="pprof_sha256_" + "4" * 64,
        ),
        code_components=(
            CodeComponentRef("semg-core", "0.1.0", "c" * 64),
        ),
        input_sha256="b" * 64,
        input_mask_sha256="0" * 64,
        native_fs_hz=1000.0,
        processed_fs_hz=1000.0,
        input_units="uV",
        output_units="uV",
        is_resampled=False,
        partition="benchmark-open",
        evidence_tier="TIER1_DIRECT_SEMG",
        qc_eligibility_ref="qc_ref_1",
        normalization_eligibility_ref=None,
        fitting_performed=False,
        steps=(),
        final_artifact=ProcessedArtifactRef(
            artifact_id="part_sha256_" + "3" * 64,
            output_sha256="d" * 64,
            mask_sha256="0" * 64,
            sample_count=2,
            units="uV",
        ),
        reason_codes=(),
    )


def test_known_answer_rms():
    r = evaluate_amplitude_metric(
        metric_name="RMS",
        values=np.array([3.0, 4.0]),
        units="uV",
        processing_permission="ALLOW_PROFILED_PROCESSING",
        qc_signal_quality="PASS",
        mask=np.zeros(2, bool),
        processing_manifest=sample_manifest_dict(),
    )
    assert r.status == "AVAILABLE"
    assert r.value is not None
    assert abs(r.value - (12.5 ** 0.5)) < 1e-12
    assert r.units == "uV"
    assert r.metric_id.startswith("metric_sha256_")


def test_known_answer_mav():
    r = evaluate_amplitude_metric(
        metric_name="MAV",
        values=np.array([-3.0, 4.0]),
        units="uV",
        processing_permission="ALLOW_PROFILED_PROCESSING",
        qc_signal_quality="PASS",
        mask=np.zeros(2, bool),
        processing_manifest=sample_manifest_dict(),
    )
    assert r.status == "AVAILABLE"
    assert r.value == 3.5
    assert r.units == "uV"


def test_object_manifest_input():
    r = evaluate_amplitude_metric(
        metric_name="RMS",
        values=np.array([3.0, 4.0]),
        units="uV",
        processing_permission="ALLOW_PROFILED_PROCESSING",
        qc_signal_quality="PASS",
        mask=np.zeros(2, bool),
        processing_manifest=sample_manifest_object(),
    )
    assert r.status == "AVAILABLE"
    assert abs(r.value - (12.5 ** 0.5)) < 1e-12


def test_qc_block_returns_null():
    r = evaluate_amplitude_metric(
        metric_name="RMS",
        values=np.ones(4),
        units="uV",
        processing_permission="BLOCK_UNSUPPORTED_METRIC",
        qc_signal_quality="FAIL",
        mask=np.zeros(4, bool),
        processing_manifest=sample_manifest_dict(),
    )
    assert r.status == "UNAVAILABLE"
    assert r.value is None
    assert "QC_FAIL_BLOCKS_METRIC" in r.reason_codes
    assert "METRIC_NOT_ELIGIBLE" in r.reason_codes


def test_mask_returns_null():
    r = evaluate_amplitude_metric(
        metric_name="MAV",
        values=np.ones(4),
        units="uV",
        processing_permission="ALLOW_PROFILED_PROCESSING",
        qc_signal_quality="PASS",
        mask=np.array([0, 1, 0, 0], bool),
        processing_manifest=sample_manifest_dict(),
    )
    assert r.status == "UNAVAILABLE"
    assert r.value is None
    assert "MASKED_WINDOW_EXCLUDED_FROM_METRIC" in r.reason_codes


def test_nan_returns_null():
    r = evaluate_amplitude_metric(
        metric_name="RMS",
        values=np.array([1.0, np.nan]),
        units="uV",
        processing_permission="ALLOW_PROFILED_PROCESSING",
        qc_signal_quality="PASS",
        mask=np.zeros(2, bool),
        processing_manifest=sample_manifest_dict(),
    )
    assert r.status == "UNAVAILABLE"
    assert r.value is None
    assert "NONFINITE_INPUT" in r.reason_codes


def test_missing_provenance_returns_null():
    bad_manifest = {"manifest_id": "pman_123"}
    r = evaluate_amplitude_metric(
        metric_name="RMS",
        values=np.array([1.0, 2.0]),
        units="uV",
        processing_permission="ALLOW_PROFILED_PROCESSING",
        qc_signal_quality="PASS",
        mask=np.zeros(2, bool),
        processing_manifest=bad_manifest,
    )
    assert r.status == "UNAVAILABLE"
    assert r.value is None
    assert "PROCESSING_PROVENANCE_INCOMPLETE" in r.reason_codes


def test_unsupported_metric_raises_valueerror():
    with pytest.raises(ValueError, match="UNSUPPORTED_METRIC"):
        evaluate_amplitude_metric(
            metric_name="MEDIAN_FREQ",
            values=np.array([1.0, 2.0]),
            units="uV",
            processing_permission="ALLOW_PROFILED_PROCESSING",
            qc_signal_quality="PASS",
            mask=np.zeros(2, bool),
            processing_manifest=sample_manifest_dict(),
        )


def test_deterministic_id():
    kw = dict(
        metric_name="MAV",
        values=np.array([1.0, 2.0]),
        units="uV",
        processing_permission="ALLOW_PROFILED_PROCESSING",
        qc_signal_quality="PASS",
        mask=np.zeros(2, bool),
        processing_manifest=sample_manifest_dict(),
    )
    r1 = evaluate_amplitude_metric(**kw)
    r2 = evaluate_amplitude_metric(**kw)
    assert r1.metric_id == r2.metric_id
