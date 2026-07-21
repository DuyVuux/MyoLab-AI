from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from extractor import (
    FEATURE_EXTRACTION_BLOCKED_BY_WINDOWING,
    FEATURE_PREPROCESS_CONFIG_MISMATCH,
    FEATURE_PROFILE_PURPOSE_MISMATCH,
    FEATURE_WINDOWS_EXCLUDED,
    TimeDomainFeatureExtractor,
)
from feature_config import load_feature_config
from window_config import load_windowing_config
from windowing import WindowingPipeline


ROOT = Path(__file__).resolve().parents[3]
WINDOW_CONFIG = ROOT / "services/feature-extraction-service/configs/windowing_v0.1.yaml"
FEATURE_CONFIG = ROOT / "services/feature-extraction-service/configs/features_semg_v0.1.yaml"


def window_pipeline() -> WindowingPipeline:
    return WindowingPipeline(load_windowing_config(WINDOW_CONFIG))


def feature_extractor(config: dict | None = None) -> TimeDomainFeatureExtractor:
    return TimeDomainFeatureExtractor(config or load_feature_config(FEATURE_CONFIG))


def test_golden_extracts_one_row_per_time_domain_window(
    make_preprocessing_result,
    protocol,
) -> None:
    windowing = window_pipeline().run(make_preprocessing_result(), protocol)
    result = feature_extractor().run(windowing)

    assert result.status == "completed"
    assert result.downstream_allowed is True
    assert result.total_row_count == 239
    assert result.computed_row_count == 239
    assert result.not_computed_row_count == 0
    assert result.usable_window_ratio == pytest.approx(1.0)
    assert result.channel_count == 1

    first = result.rows[0]
    assert first.status == "computed"
    assert first.profile_id == "time_domain"
    assert first.values is not None
    assert first.values.rms == pytest.approx(50.0 / (2.0**0.5), rel=1e-12)
    assert first.values.mav == pytest.approx(
        2.0 * 50.0 / 3.141592653589793,
        rel=2e-3,
    )
    assert first.values.amplitude_unit == "uV"
    assert first.start_sample == 5000
    assert first.end_sample_exclusive == 5500


def test_invalid_windows_are_emitted_as_not_computed_rows(
    make_preprocessing_result,
    protocol,
) -> None:
    windowing = window_pipeline().run(
        make_preprocessing_result(mask_false_indices=(5750,)),
        protocol,
    )
    result = feature_extractor().run(windowing)

    assert result.status == "completed_with_exclusions"
    assert result.total_row_count == 239
    assert result.computed_row_count == 237
    assert result.not_computed_row_count == 2
    assert FEATURE_WINDOWS_EXCLUDED in result.reason_codes

    excluded = [row for row in result.rows if row.status == "not_computed"]
    assert [row.window_index for row in excluded] == [2, 3]
    assert all(row.values is None for row in excluded)
    assert all(row.reason_codes for row in excluded)


def test_result_hash_and_row_ids_are_deterministic(
    make_preprocessing_result,
    protocol,
) -> None:
    windowing = window_pipeline().run(make_preprocessing_result(), protocol)
    first = feature_extractor().run(windowing)
    second = feature_extractor().run(windowing)
    assert first.result_hash_sha256 == second.result_hash_sha256
    assert [row.feature_row_id for row in first.rows] == [
        row.feature_row_id for row in second.rows
    ]


def test_upstream_block_is_propagated(
    make_preprocessing_result,
    protocol,
) -> None:
    windowing = window_pipeline().run(
        make_preprocessing_result(downstream_allowed=False),
        protocol,
    )
    result = feature_extractor().run(windowing)
    assert result.status == "blocked"
    assert result.downstream_allowed is False
    assert result.rows == ()
    assert FEATURE_EXTRACTION_BLOCKED_BY_WINDOWING in result.reason_codes


def test_preprocess_config_mismatch_blocks(
    make_preprocessing_result,
    protocol,
) -> None:
    window_config = deepcopy(load_windowing_config(WINDOW_CONFIG))
    window_config["input_contract"]["required_preprocess_config_id"] = "preprocess_v0.2"
    windowing = WindowingPipeline(window_config).run(
        make_preprocessing_result(preprocess_config_id="preprocess_v0.2"),
        protocol,
    )
    assert windowing.downstream_allowed is True
    result = feature_extractor().run(windowing)
    assert result.status == "blocked"
    assert FEATURE_PREPROCESS_CONFIG_MISMATCH in result.reason_codes


def test_profile_purpose_mismatch_blocks(
    make_preprocessing_result,
    protocol,
) -> None:
    windowing = window_pipeline().run(make_preprocessing_result(), protocol)
    config = deepcopy(load_feature_config(FEATURE_CONFIG))
    config["input_contract"]["required_profile_purpose"] = "wrong_purpose"
    result = feature_extractor(config).run(windowing)
    assert result.status == "blocked"
    assert FEATURE_PROFILE_PURPOSE_MISMATCH in result.reason_codes


def test_json_contains_no_raw_samples(
    make_preprocessing_result,
    protocol,
) -> None:
    windowing = window_pipeline().run(make_preprocessing_result(), protocol)
    payload = feature_extractor().run(windowing).to_dict()
    text = str(payload)
    assert "samples_uV" not in text
    assert "raw_samples" not in text
    assert payload["summary"]["computed_row_count"] == 239
    assert payload["rows"][0]["features"]["rms"]["unit"] == "uV"
