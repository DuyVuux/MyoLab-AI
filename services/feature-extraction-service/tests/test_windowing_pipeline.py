from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from window_config import load_windowing_config
from windowing import (
    WINDOWING_BLOCKED_BY_PREPROCESSING,
    WINDOWING_PHASE_NOT_FOUND,
    WINDOWING_PHASE_TOO_SHORT,
    WINDOWING_PREPROCESS_CONFIG_MISMATCH,
    WINDOWING_PROTOCOL_CONFIG_MISMATCH,
    WINDOWING_PROTOCOL_REF_MISMATCH,
    WINDOWING_WINDOWS_EXCLUDED,
    WindowingPipeline,
)


ROOT = Path(__file__).resolve().parents[3]
CONFIG = (
    ROOT
    / "services"
    / "feature-extraction-service"
    / "configs"
    / "windowing_v0.1.yaml"
)


def pipeline() -> WindowingPipeline:
    return WindowingPipeline(load_windowing_config(CONFIG))


def test_golden_geometry_has_two_protocol_aligned_profiles(
    make_preprocessing_result,
    protocol,
) -> None:
    result = pipeline().run(make_preprocessing_result(), protocol)
    assert result.status == "completed"
    assert result.downstream_allowed is True
    assert result.plan is not None

    time_profile = result.plan.profiles["time_domain"]
    assert time_profile.window_count == 239
    assert time_profile.window_size_samples == 500
    assert time_profile.hop_size_samples == 250
    assert time_profile.remainder_samples == 0
    assert time_profile.channels["VL_R_01"].valid_window_count == 239

    frequency_profile = result.plan.profiles["frequency_domain"]
    assert frequency_profile.window_count == 119
    assert frequency_profile.window_size_samples == 1000
    assert frequency_profile.hop_size_samples == 500
    assert frequency_profile.remainder_samples == 0
    assert frequency_profile.channels["VL_R_01"].valid_window_count == 119


def test_plan_hash_is_deterministic(make_preprocessing_result, protocol) -> None:
    source = make_preprocessing_result()
    first = pipeline().run(source, protocol)
    second = pipeline().run(source, protocol)
    assert first.plan is not None and second.plan is not None
    assert first.plan.plan_hash_sha256 == second.plan.plan_hash_sha256


def test_get_window_samples_is_profile_specific_and_read_only(
    make_preprocessing_result,
    protocol,
) -> None:
    result = pipeline().run(make_preprocessing_result(), protocol)
    assert result.plan is not None
    time_samples = result.plan.get_window_samples("time_domain", "VL_R_01", 0)
    frequency_samples = result.plan.get_window_samples(
        "frequency_domain", "VL_R_01", 0
    )
    assert time_samples.size == 500
    assert frequency_samples.size == 1000
    assert time_samples.flags.writeable is False
    assert frequency_samples.flags.writeable is False


def test_half_open_mask_propagation_differs_by_profile(
    make_preprocessing_result,
    protocol,
) -> None:
    result = pipeline().run(
        make_preprocessing_result(mask_false_indices=(5750,)),
        protocol,
    )
    assert result.status == "completed"
    assert result.plan is not None

    time_channel = result.plan.profiles["time_domain"].channels["VL_R_01"]
    time_invalid = [
        item.window_index for item in time_channel.windows if item.status == "invalid"
    ]
    assert time_invalid == [2, 3]
    assert time_channel.valid_window_count == 237

    frequency_channel = result.plan.profiles["frequency_domain"].channels[
        "VL_R_01"
    ]
    frequency_invalid = [
        item.window_index
        for item in frequency_channel.windows
        if item.status == "invalid"
    ]
    assert frequency_invalid == [0, 1]
    assert frequency_channel.valid_window_count == 117
    assert WINDOWING_WINDOWS_EXCLUDED in result.reason_codes


def test_upstream_block_is_propagated(make_preprocessing_result, protocol) -> None:
    result = pipeline().run(
        make_preprocessing_result(downstream_allowed=False),
        protocol,
    )
    assert result.status == "blocked"
    assert result.downstream_allowed is False
    assert result.plan is None
    assert WINDOWING_BLOCKED_BY_PREPROCESSING in result.reason_codes


def test_missing_phase_blocks(make_preprocessing_result, protocol) -> None:
    result = pipeline().run(make_preprocessing_result(include_phase=False), protocol)
    assert result.status == "blocked"
    assert WINDOWING_PHASE_NOT_FOUND in result.reason_codes


def test_phase_shorter_than_shortest_profile_blocks(
    make_preprocessing_result,
    protocol,
) -> None:
    result = pipeline().run(
        make_preprocessing_result(
            total_duration_s=0.4,
            phase_start_s=0.0,
            phase_end_s=0.4,
        ),
        protocol,
    )
    assert result.status == "blocked"
    assert WINDOWING_PHASE_TOO_SHORT in result.reason_codes


def test_preprocess_version_mismatch_blocks(
    make_preprocessing_result,
    protocol,
) -> None:
    result = pipeline().run(
        make_preprocessing_result(preprocess_config_id="preprocess_v0.2"),
        protocol,
    )
    assert result.status == "blocked"
    assert WINDOWING_PREPROCESS_CONFIG_MISMATCH in result.reason_codes


def test_protocol_reference_mismatch_blocks(
    make_preprocessing_result,
    protocol,
) -> None:
    result = pipeline().run(
        make_preprocessing_result(protocol_version="9.9.9"),
        protocol,
    )
    assert result.status == "blocked"
    assert WINDOWING_PROTOCOL_REF_MISMATCH in result.reason_codes


def test_protocol_default_windowing_mismatch_blocks(
    make_preprocessing_result,
    protocol,
) -> None:
    changed = deepcopy(protocol)
    changed["analysis"]["default_windowing"]["time_domain_window_ms"] = 750
    result = pipeline().run(make_preprocessing_result(), changed)
    assert result.status == "blocked"
    assert WINDOWING_PROTOCOL_CONFIG_MISMATCH in result.reason_codes


def test_json_summary_contains_no_raw_samples(
    make_preprocessing_result,
    protocol,
) -> None:
    result = pipeline().run(make_preprocessing_result(), protocol)
    payload = result.to_dict()
    text = str(payload)
    assert "samples_uV" not in text
    assert payload["plan"]["config"]["taper_applied_during_windowing"] is False
    assert payload["plan"]["config"]["spectral_taper_default"] == "hann"
    profiles = {item["profile_id"]: item for item in payload["plan"]["profiles"]}
    assert profiles["time_domain"]["windowing"]["window_count"] == 239
    assert profiles["frequency_domain"]["windowing"]["window_count"] == 119
