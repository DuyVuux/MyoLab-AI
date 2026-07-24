from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from gesture_replay_engine import (
    SCENARIO_IDS,
    ReplayContext,
    ReplayRepetition,
    ReplayScenarioError,
    build_replay_windows,
    canonical_result_hash,
)


EXPECTED_SCENARIO_IDS = frozenset(
    {
        "uc1_golden_correct",
        "uc1_ambiguous_prediction",
        "uc1_no_activity",
        "uc1_fatigue_confidence_drop",
        "uc1_electrode_shift_warning",
        "uc1_qc_fail_abstention",
        "uc1_device_disconnect",
    }
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
REPO_ROOT = Path(__file__).resolve().parents[3]
ACTIVE_GESTURES = (
    "hand_open",
    "hand_close",
    "wrist_flexion",
    "wrist_extension",
)


def repetition_records(
    *,
    id_prefix: str = "REP-D20",
    source_hash: str = "a" * 64,
    raw_signal_ref: str = "RAW-REF-D20-001",
    channel_ids: tuple[str, ...] = ("CH01", "CH02", "CH03", "CH04"),
    sampling_rate_hz: float = 1000.0,
    first_start_sample: int = 5000,
    window_size_samples: int = 1000,
    stride_samples: int = 1250,
) -> tuple[ReplayRepetition, ...]:
    records: list[ReplayRepetition] = []
    for occurrence in range(1, 4):
        for gesture_id in ACTIVE_GESTURES:
            index = len(records)
            start_sample = first_start_sample + index * stride_samples
            end_sample = start_sample + window_size_samples
            records.append(
                ReplayRepetition(
                    repetition_id=(
                        f"{id_prefix}-{gesture_id.upper()}-{occurrence:02d}"
                    ),
                    gesture_id=gesture_id,
                    quality="accepted",
                    raw_signal_ref=raw_signal_ref,
                    source_hash_sha256=source_hash,
                    start_sample=start_sample,
                    end_sample_exclusive=end_sample,
                    start_time_s=start_sample / sampling_rate_hz,
                    end_time_exclusive_s=end_sample / sampling_rate_hz,
                    channel_ids=channel_ids,
                )
            )
    return tuple(records)


@pytest.fixture
def replay_context() -> ReplayContext:
    return ReplayContext(
        session_id="SESSION-D20-001",
        analysis_id="AN21-0123456789ab",
        source_hash_sha256="a" * 64,
        calibration_id="CAL-SESSION-D20-001",
        sampling_rate_hz=1000.0,
        channel_ids=("CH01", "CH02", "CH03", "CH04"),
        repetitions=repetition_records(),
        rest_rms_uv=4.2,
        rest_sigma_uv=0.8,
        engineering_k=3.0,
        release_ratio=0.8,
        uncertain_band_ratio=0.1,
        latency_components_ms=(10.0, 200.0, 18.0, 14.0, 28.0),
        engine_id="gesture-replay",
        engine_version="0.1.0",
        model_version="synthetic-gesture-replay.v0.1",
        source_type="synthetic_replay",
        upstream_fatigue_status="stable",
        upstream_fatigue_reason_codes=(),
    )


def replay_windows(
    context: ReplayContext,
    scenario_id: str,
):
    return tuple(build_replay_windows(context=context, scenario_id=scenario_id))


def test_scenario_registry_is_explicit_and_complete() -> None:
    assert SCENARIO_IDS == EXPECTED_SCENARIO_IDS


def test_engine_imports_without_api_server_on_pythonpath(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = os.pathsep.join(
        [
            str(REPO_ROOT / "services/inference-service/src"),
            str(REPO_ROOT / "packages/semg-core"),
        ]
    )

    completed = subprocess.run(
        [sys.executable, "-c", "import gesture_replay_engine"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr


def test_unknown_scenario_raises_typed_error(replay_context: ReplayContext) -> None:
    with pytest.raises(ReplayScenarioError, match="UNKNOWN_REPLAY_SCENARIO"):
        replay_windows(replay_context, "uc1_not_registered")


def test_canonical_result_hash_is_order_independent_and_sensitive_to_values() -> None:
    first = canonical_result_hash(
        {"window": {"index": 2, "status": "active"}, "channels": ["CH01", "CH02"]}
    )
    reordered = canonical_result_hash(
        {"channels": ["CH01", "CH02"], "window": {"status": "active", "index": 2}}
    )
    changed = canonical_result_hash(
        {"channels": ["CH01", "CH02"], "window": {"status": "inactive", "index": 2}}
    )

    assert first == reordered
    assert first != changed
    assert SHA256_PATTERN.fullmatch(first)


def test_replay_windows_and_hashes_are_deterministic(
    replay_context: ReplayContext,
) -> None:
    first = replay_windows(replay_context, "uc1_golden_correct")
    second = replay_windows(replay_context, "uc1_golden_correct")

    assert first == second
    assert all(SHA256_PATTERN.fullmatch(window.result_hash_sha256) for window in first)
    assert len({window.result_hash_sha256 for window in first}) == len(first)


def test_context_values_are_propagated_instead_of_hardcoded(
    replay_context: ReplayContext,
) -> None:
    alternate_repetitions = repetition_records(
        id_prefix="ALT-REP",
        source_hash="b" * 64,
        raw_signal_ref="RAW-ALT-999",
        channel_ids=("ALT01", "ALT02"),
        sampling_rate_hz=2000.0,
        first_start_sample=1234,
        window_size_samples=800,
        stride_samples=1000,
    )
    alternate = replace(
        replay_context,
        session_id="SESSION-ALT-777",
        analysis_id="AN-ALT-888",
        source_hash_sha256="b" * 64,
        calibration_id="CAL-ALT-222",
        sampling_rate_hz=2000.0,
        channel_ids=("ALT01", "ALT02"),
        repetitions=alternate_repetitions,
        rest_rms_uv=1.25,
        rest_sigma_uv=0.25,
        engineering_k=2.0,
        latency_components_ms=(1.0, 2.0, 3.0, 4.0, 5.0),
        engine_id="alternate-replay-engine",
        engine_version="9.8.7",
        model_version="alternate-model.v3",
    )

    window = replay_windows(alternate, "uc1_golden_correct")[0]
    segment = window.segment_ref
    source_repetition = alternate.repetitions[0]

    assert (
        window.session_id,
        window.analysis_id,
        segment.raw_signal_ref,
        segment.source_hash_sha256,
        segment.calibration_id,
        segment.repetition_id,
        tuple(segment.channel_ids),
    ) == (
        alternate.session_id,
        alternate.analysis_id,
        source_repetition.raw_signal_ref,
        source_repetition.source_hash_sha256,
        alternate.calibration_id,
        source_repetition.repetition_id,
        source_repetition.channel_ids,
    )
    assert (
        segment.start_sample,
        segment.end_sample_exclusive,
        segment.start_time_s,
        segment.end_time_exclusive_s,
    ) == pytest.approx((1234, 2034, 1234 / 2000.0, 2034 / 2000.0))
    assert window.activity_gate.activation_threshold_uv == pytest.approx(1.75)
    assert (
        window.latency.acquisition_ms,
        window.latency.window_ms,
        window.latency.preprocess_ms,
        window.latency.inference_ms,
        window.latency.transport_render_ms,
        window.latency.total_ms,
    ) == pytest.approx((1.0, 2.0, 3.0, 4.0, 5.0, 15.0))
    assert (
        window.engine_id,
        window.engine_version,
        window.model_version,
    ) == (
        alternate.engine_id,
        alternate.engine_version,
        alternate.model_version,
    )


@pytest.mark.parametrize("scenario_id", sorted(EXPECTED_SCENARIO_IDS))
def test_every_scenario_uses_exact_half_open_window_provenance(
    replay_context: ReplayContext,
    scenario_id: str,
) -> None:
    windows = replay_windows(replay_context, scenario_id)

    assert windows
    occurrence_by_gesture: dict[str, int] = {}
    for window in windows:
        gesture_id = window.target_gesture
        occurrence = occurrence_by_gesture.get(gesture_id, 0)
        source_repetitions = [
            repetition
            for repetition in replay_context.repetitions
            if repetition.gesture_id == gesture_id
            and repetition.quality == "accepted"
        ]
        source = source_repetitions[occurrence]
        occurrence_by_gesture[gesture_id] = occurrence + 1
        segment = window.segment_ref

        assert segment.repetition_id == source.repetition_id
        assert segment.raw_signal_ref == source.raw_signal_ref
        assert segment.source_hash_sha256 == source.source_hash_sha256
        assert segment.start_sample == source.start_sample
        assert segment.end_sample_exclusive == source.end_sample_exclusive
        assert segment.start_time_s == pytest.approx(source.start_time_s)
        assert segment.end_time_exclusive_s == pytest.approx(
            source.end_time_exclusive_s
        )
        assert tuple(segment.channel_ids) == source.channel_ids
        assert segment.calibration_id == replay_context.calibration_id
        assert not hasattr(window, "raw_samples")


def test_golden_scenario_is_active_correct_and_high_confidence(
    replay_context: ReplayContext,
) -> None:
    windows = replay_windows(replay_context, "uc1_golden_correct")

    assert len(windows) == 4
    assert all(window.activity_gate.status == "active" for window in windows)
    assert all(window.quality_overlay.status == "pass" for window in windows)
    assert all(window.predicted_gesture == window.target_gesture for window in windows)
    assert all(
        window.engineering_confidence == "engineering_high" for window in windows
    )


def test_ambiguous_scenario_remains_a_prediction_not_no_activity(
    replay_context: ReplayContext,
) -> None:
    (window,) = replay_windows(replay_context, "uc1_ambiguous_prediction")

    assert window.activity_gate.status == "active"
    assert window.predicted_gesture != window.target_gesture
    assert window.engineering_confidence == "engineering_low"


@pytest.mark.parametrize(
    ("scenario_id", "window_index", "expected_gate", "expected_quality", "expected_device"),
    [
        pytest.param(
            "uc1_no_activity",
            0,
            "inactive",
            "pass",
            "connected",
            id="inactive",
        ),
        pytest.param(
            "uc1_qc_fail_abstention",
            0,
            "active",
            "fail",
            "connected",
            id="qc-fail",
        ),
        pytest.param(
            "uc1_device_disconnect",
            1,
            "inactive",
            "pass",
            "disconnected",
            id="device-disconnect",
        ),
    ],
)
def test_ineligible_windows_never_have_a_prediction(
    replay_context: ReplayContext,
    scenario_id: str,
    window_index: int,
    expected_gate: str,
    expected_quality: str,
    expected_device: str,
) -> None:
    window = replay_windows(replay_context, scenario_id)[window_index]

    assert (
        window.activity_gate.status,
        window.quality_overlay.status,
        window.device_state,
        window.predicted_gesture,
        window.engineering_confidence,
    ) == (
        expected_gate,
        expected_quality,
        expected_device,
        None,
        "not_available",
    )


def test_upstream_fatigue_abstention_suppresses_all_predictions(
    replay_context: ReplayContext,
) -> None:
    abstained_context = replace(
        replay_context,
        upstream_fatigue_status="abstain",
        upstream_fatigue_reason_codes=("UPSTREAM_FATIGUE_ABSTAINED",),
    )

    windows = replay_windows(abstained_context, "uc1_golden_correct")

    assert windows
    assert all(window.fatigue_overlay.status == "abstain" for window in windows)
    assert all(window.predicted_gesture is None for window in windows)
    assert all(window.engineering_confidence == "not_available" for window in windows)


def test_fatigue_warning_downgrades_engineering_confidence(
    replay_context: ReplayContext,
) -> None:
    baseline, warning = replay_windows(
        replay_context,
        "uc1_fatigue_confidence_drop",
    )

    assert baseline.engineering_confidence == "engineering_high"
    assert warning.base_engineering_confidence == "engineering_high"
    assert warning.engineering_confidence == "engineering_moderate"
    assert warning.predicted_gesture is not None
    assert warning.fatigue_overlay.status == "warning"
    assert warning.fatigue_overlay.confidence_adjustment_applied is True
    assert "CONFIDENCE_DOWNGRADED" in warning.fatigue_overlay.reason_codes


def test_electrode_shift_is_quality_warning_not_fatigue_warning(
    replay_context: ReplayContext,
) -> None:
    (window,) = replay_windows(replay_context, "uc1_electrode_shift_warning")

    assert window.quality_overlay.status == "warning"
    assert "ELECTRODE_SHIFT_SUSPECTED" in window.quality_overlay.reason_codes
    assert window.fatigue_overlay.status == "stable"
    assert window.fatigue_overlay.confidence_adjustment_applied is False
    assert "ELECTRODE_SHIFT_SUSPECTED" not in window.fatigue_overlay.reason_codes
