from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day30.channel_policy import (
    channel_summary,
    decide_mendeley_ch4,
    expand_grabmyo_primary_channels,
    grabmyo_excluded_channels,
)
from day30.normalization import remove_dc_mean, validate_scaling_policy
from day30.sample_rate import (
    rational_resample_factors,
    resample_polyphase,
    samples_for_ms,
)


def test_sample_rounding_policy_is_explicit_half_up() -> None:
    assert samples_for_ms(2048, 150) == 307
    assert samples_for_ms(2048, 200) == 410
    assert samples_for_ms(2048, 75) == 154
    assert rational_resample_factors(2048, 2000) == (125, 128)


@pytest.mark.parametrize(
    ("sampling_rate_hz", "duration_ms"),
    [(0, 200), (-1, 200), (2000, 0), (2000, -1), (float("nan"), 200)],
)
def test_sample_conversion_rejects_invalid_inputs(
    sampling_rate_hz: float, duration_ms: float
) -> None:
    with pytest.raises(ValueError):
        samples_for_ms(sampling_rate_hz, duration_ms)


def test_polyphase_resampling_is_finite_and_shape_safe() -> None:
    source = np.arange(2048 * 2, dtype=float).reshape(2048, 2)
    result = resample_polyphase(source, 2048, 2000, axis=0)
    assert result.shape == (2000, 2)
    assert np.isfinite(result).all()
    assert not np.shares_memory(source, result)


def test_signal_transformations_reject_nonfinite_input() -> None:
    with pytest.raises(ValueError, match="finite"):
        remove_dc_mean(np.array([[1.0], [np.nan]]))
    with pytest.raises(ValueError, match="finite"):
        resample_polyphase(np.array([0.0, np.inf]), 2048, 2000)


def test_dc_removal_is_per_channel_without_amplitude_normalization() -> None:
    source = np.array([[1.0, 10.0], [3.0, 14.0], [5.0, 18.0]])
    result = remove_dc_mean(source, axis=0)
    assert np.allclose(result.mean(axis=0), 0.0)
    assert np.allclose(result.std(axis=0), source.std(axis=0))
    validate_scaling_policy("training_fold_per_feature_zscore")
    with pytest.raises(ValueError):
        validate_scaling_policy("global_dataset_zscore")


def test_channel_contract_and_robust_summary() -> None:
    assert len(expand_grabmyo_primary_channels()) == 28
    assert grabmyo_excluded_channels() == ("U1", "U2", "U3", "U4")
    summary = channel_summary([0.0, 1.0, 2.0, 100.0], active_threshold=0.5)
    assert summary["median"] == 1.5
    assert summary["active_channel_fraction"] == 0.75


def test_channel_decision_rejects_invalid_statistics() -> None:
    with pytest.raises(ValueError, match="positive"):
        decide_mendeley_ch4(
            {
                "EMG_Raw_CH1": 0.0,
                "EMG_RAW_CH2": 0.0,
                "EMG_RAW_CH3": 0.0,
                "EMG_RAW_CH4": 0.0,
            }
        )
    with pytest.raises(ValueError, match="finite"):
        channel_summary([1.0, float("nan")])
