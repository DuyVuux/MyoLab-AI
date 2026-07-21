from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np

from frequency_feature_config import load_frequency_feature_config
from frequency_feature_extractor import (
    FREQ_FEATURE_BLOCKED_BY_SPECTRAL,
    FrequencyFeatureExtractor,
)
from spectral_result_models import (
    SpectralEstimationResult,
    SpectralWindowRow,
    SpectralWindowValues,
)


CONFIG = Path("services/feature-extraction-service/configs/frequency_features_v0.1.yaml")


def _spectral_result(*, blocked: bool = False) -> SpectralEstimationResult:
    if blocked:
        return SpectralEstimationResult(
            session_id="SYN-001",
            status="blocked",
            downstream_allowed=False,
            config_id="spectral_estimation_v0.1",
            inherited_windowing_status="blocked",
            inherited_windowing_config_id="windowing_v0.1",
            inherited_window_plan_hash_sha256=None,
            frequency_axis_hz=None,
            estimator_metadata=None,
            reason_codes=("SPECTRAL_ESTIMATION_BLOCKED_BY_WINDOWING",),
            rows=(),
            result_hash_sha256=None,
            limitations=(),
        )
    axis = tuple(float(x) for x in np.arange(20.0, 401.0, 1.0))
    psd = np.zeros(len(axis), dtype=float)
    psd[60] = 2.0  # 80 Hz
    values = SpectralWindowValues(
        psd_uV2_per_hz=tuple(float(x) for x in psd),
        band_power_uV2=2.0,
        full_power_uV2=2.0,
        time_domain_variance_uV2=2.0,
        window_weighted_power_uV2=2.0,
        parseval_ratio=1.0,
        peak_frequency_hz=80.0,
    )
    row = SpectralWindowRow(
        spectral_row_id="SR-1",
        session_id="SYN-001",
        channel_id="CH1",
        muscle="vastus_lateralis",
        side="right",
        role="primary",
        phase_id="active_contraction",
        profile_id="frequency_domain",
        window_id="W1",
        window_index=0,
        start_sample=0,
        end_sample_exclusive=1000,
        start_time_s=0.0,
        end_time_exclusive_s=1.0,
        center_time_s=0.5,
        sample_count=1000,
        status="computed",
        values=values,
        reason_codes=(),
        spectral_estimator_id="spectral_estimation_v0.1",
        windowing_config_id="windowing_v0.1",
        preprocess_config_id="preprocess_v0.1",
        source_signal_hash_sha256="a" * 64,
        window_plan_hash_sha256="b" * 64,
    )
    return SpectralEstimationResult(
        session_id="SYN-001",
        status="completed",
        downstream_allowed=True,
        config_id="spectral_estimation_v0.1",
        inherited_windowing_status="completed",
        inherited_windowing_config_id="windowing_v0.1",
        inherited_window_plan_hash_sha256="b" * 64,
        frequency_axis_hz=axis,
        estimator_metadata={
            "frequency_bin_spacing_hz": 1.0,
            "rayleigh_resolution_hz": 1.0,
        },
        reason_codes=(),
        rows=(row,),
        result_hash_sha256="c" * 64,
        limitations=(),
    )


def test_extractor_computes_mdf_mnf() -> None:
    result = FrequencyFeatureExtractor(load_frequency_feature_config(CONFIG)).run(
        _spectral_result()
    )
    assert result.status == "completed"
    assert result.computed_row_count == 1
    assert result.rows[0].values is not None
    assert result.rows[0].values.mdf_hz == 80.0
    assert result.rows[0].values.mnf_hz == 80.0


def test_extractor_blocks_if_spectral_blocked() -> None:
    result = FrequencyFeatureExtractor(load_frequency_feature_config(CONFIG)).run(
        _spectral_result(blocked=True)
    )
    assert result.status == "blocked"
    assert result.reason_codes == (FREQ_FEATURE_BLOCKED_BY_SPECTRAL,)


def test_extractor_blocks_on_wrong_spectral_config() -> None:
    spectral = replace(_spectral_result(), config_id="other")
    result = FrequencyFeatureExtractor(load_frequency_feature_config(CONFIG)).run(spectral)
    assert result.status == "blocked"
