from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from spectral_config import load_spectral_config
from spectral_extractor import (
    SPECTRAL_BLOCKED_BY_WINDOWING,
    SPECTRAL_PREPROCESS_CONFIG_MISMATCH,
    SPECTRAL_PROFILE_PURPOSE_MISMATCH,
    SPECTRAL_WINDOWS_EXCLUDED,
    SpectralEstimator,
)
from window_config import load_windowing_config
from windowing import WindowingPipeline


ROOT = Path(__file__).resolve().parents[3]
WINDOW_CONFIG = ROOT / "services/feature-extraction-service/configs/windowing_v0.1.yaml"
SPECTRAL_CONFIG = ROOT / "services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml"


def window_pipeline() -> WindowingPipeline:
    return WindowingPipeline(load_windowing_config(WINDOW_CONFIG))


def estimator(config: dict | None = None) -> SpectralEstimator:
    return SpectralEstimator(config or load_spectral_config(SPECTRAL_CONFIG))


def test_golden_extracts_one_psd_per_frequency_window(
    make_preprocessing_result,
    protocol,
) -> None:
    windowing = window_pipeline().run(make_preprocessing_result(), protocol)
    result = estimator().run(windowing)

    assert result.status == "completed"
    assert result.downstream_allowed is True
    assert result.total_row_count == 119
    assert result.computed_row_count == 119
    assert result.not_computed_row_count == 0
    assert result.usable_window_ratio == pytest.approx(1.0)
    assert result.channel_count == 1
    assert result.frequency_axis_hz is not None
    assert len(result.frequency_axis_hz) == 381
    assert result.frequency_axis_hz[0] == pytest.approx(20.0)
    assert result.frequency_axis_hz[-1] == pytest.approx(400.0)

    first = result.rows[0]
    assert first.status == "computed"
    assert first.profile_id == "frequency_domain"
    assert first.values is not None
    assert first.values.peak_frequency_hz == pytest.approx(80.0)
    assert first.values.band_power_uV2 == pytest.approx(1250.0, rel=1e-10)
    assert first.start_sample == 5000
    assert first.end_sample_exclusive == 6000
    assert len(first.values.psd_uV2_per_hz) == 381


def test_invalid_windows_are_not_computed(
    make_preprocessing_result,
    protocol,
) -> None:
    windowing = window_pipeline().run(
        make_preprocessing_result(mask_false_indices=(5750,)),
        protocol,
    )
    result = estimator().run(windowing)
    assert result.status == "completed_with_exclusions"
    assert result.total_row_count == 119
    assert result.computed_row_count == 117
    assert result.not_computed_row_count == 2
    assert SPECTRAL_WINDOWS_EXCLUDED in result.reason_codes
    excluded = [row for row in result.rows if row.status == "not_computed"]
    assert [row.window_index for row in excluded] == [0, 1]


def test_result_hash_is_deterministic(make_preprocessing_result, protocol) -> None:
    windowing = window_pipeline().run(make_preprocessing_result(), protocol)
    first = estimator().run(windowing)
    second = estimator().run(windowing)
    assert first.result_hash_sha256 == second.result_hash_sha256
    assert [row.spectral_row_id for row in first.rows] == [
        row.spectral_row_id for row in second.rows
    ]


def test_upstream_block_is_propagated(make_preprocessing_result, protocol) -> None:
    windowing = window_pipeline().run(
        make_preprocessing_result(downstream_allowed=False),
        protocol,
    )
    result = estimator().run(windowing)
    assert result.status == "blocked"
    assert result.downstream_allowed is False
    assert result.rows == ()
    assert SPECTRAL_BLOCKED_BY_WINDOWING in result.reason_codes


def test_preprocess_config_mismatch_blocks(make_preprocessing_result, protocol) -> None:
    window_config = deepcopy(load_windowing_config(WINDOW_CONFIG))
    window_config["input_contract"]["required_preprocess_config_id"] = "preprocess_v0.2"
    windowing = WindowingPipeline(window_config).run(
        make_preprocessing_result(preprocess_config_id="preprocess_v0.2"),
        protocol,
    )
    result = estimator().run(windowing)
    assert result.status == "blocked"
    assert SPECTRAL_PREPROCESS_CONFIG_MISMATCH in result.reason_codes


def test_profile_purpose_mismatch_blocks(make_preprocessing_result, protocol) -> None:
    windowing = window_pipeline().run(make_preprocessing_result(), protocol)
    config = deepcopy(load_spectral_config(SPECTRAL_CONFIG))
    config["input_contract"]["required_profile_purpose"] = "wrong_purpose"
    result = estimator(config).run(windowing)
    assert result.status == "blocked"
    assert SPECTRAL_PROFILE_PURPOSE_MISMATCH in result.reason_codes


def test_json_contains_no_raw_samples(make_preprocessing_result, protocol) -> None:
    windowing = window_pipeline().run(make_preprocessing_result(), protocol)
    payload = estimator().run(windowing).to_dict()
    text = str(payload)
    assert "samples_uV" not in text
    assert "raw_samples" not in text
    assert payload["config"]["mdf_mnf_computed"] is False
    assert payload["frequency_axis"]["unit"] == "Hz"
    assert payload["rows"][0]["spectral"]["psd"]["unit"] == "uV^2/Hz"
