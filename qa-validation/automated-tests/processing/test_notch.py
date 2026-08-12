import numpy as np
import pytest

from semg_core.processing.notch import NotchSpec, apply_notch


def synthetic_signal(fs_hz=2000, duration_seconds=4):
    time = np.arange(int(fs_hz * duration_seconds)) / fs_hz
    return (
        np.sin(2 * np.pi * 50 * time)
        + 0.4 * np.sin(2 * np.pi * 100 * time)
        + 0.7 * np.sin(2 * np.pi * 173 * time)
    )


def test_unknown_mains_disabled_is_identity_copy():
    values = synthetic_signal()
    result = apply_notch(
        values,
        2000,
        NotchSpec(enabled=False),
        source_window_id="w",
        profile_id="p",
    )
    assert np.array_equal(values, result.values)
    assert result.metadata["pre_notch_spectral_summary"] == {}


def test_enabled_without_mains_fails_closed():
    with pytest.raises(ValueError, match="NO_SILENT"):
        apply_notch(
            synthetic_signal(),
            2000,
            NotchSpec(enabled=True, q_factor=30),
            source_window_id="w",
            profile_id="p",
        )


def test_exactly_one_q_or_bandwidth():
    with pytest.raises(ValueError):
        NotchSpec(True, 50, 30, 2).validate(2000)


def test_50hz_attenuation_and_collateral_preservation():
    values = synthetic_signal()
    result = apply_notch(
        values,
        2000,
        NotchSpec(True, 50, 30, None, (1,)),
        source_window_id="w",
        profile_id="p",
    )
    assert result.metadata["attenuation_db"]["50Hz"] > 25

    frequencies = np.fft.rfftfreq(values.size, 1 / 2000)
    input_spectrum = np.abs(np.fft.rfft(values))
    output_spectrum = np.abs(np.fft.rfft(result.values))
    index = np.argmin(abs(frequencies - 173))
    assert output_spectrum[index] / input_spectrum[index] > 0.95


def test_harmonic_requires_explicit_list():
    values = synthetic_signal()
    base = apply_notch(
        values,
        2000,
        NotchSpec(True, 50, 30, None, (1,)),
        source_window_id="w",
        profile_id="p",
    )
    harmonic = apply_notch(
        values,
        2000,
        NotchSpec(True, 50, 30, None, (1, 2)),
        source_window_id="w",
        profile_id="p",
    )
    assert "100Hz" not in base.metadata["attenuation_db"]
    assert harmonic.metadata["attenuation_db"]["100Hz"] > 20


def test_pre_evidence_ref_deterministic_and_raw_immutable():
    values = synthetic_signal()
    before = values.copy()
    spec = NotchSpec(True, 50, 30, None, (1, 2))
    first = apply_notch(
        values,
        2000,
        spec,
        source_window_id="w",
        profile_id="p",
    )
    second = apply_notch(
        values,
        2000,
        spec,
        source_window_id="w",
        profile_id="p",
    )
    assert np.array_equal(values, before)
    assert (
        first.metadata["pre_notch_spectral_evidence_ref"]
        == second.metadata["pre_notch_spectral_evidence_ref"]
    )
    assert np.array_equal(first.values, second.values)


def test_mask_preserved():
    values = synthetic_signal()
    mask = np.zeros_like(values, dtype=bool)
    mask[100:200] = True
    result = apply_notch(
        values,
        2000,
        NotchSpec(True, 50, 30),
        mask=mask,
        source_window_id="w",
        profile_id="p",
    )
    assert np.array_equal(result.mask, mask)
    assert np.isnan(result.values[mask]).all()
