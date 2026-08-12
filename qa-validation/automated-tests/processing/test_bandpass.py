import hashlib

import numpy as np
import pytest

from semg_core.processing.bandpass import (
    BandpassSpec,
    apply_bandpass,
    causal_group_delay_samples,
    frequency_response,
)


def array_hash(values):
    return hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()


def tone(fs_hz, frequency_hz, duration_seconds=2.0):
    time = np.arange(int(fs_hz * duration_seconds)) / fs_hz
    return np.sin(2 * np.pi * frequency_hz * time)


def db_at(frequencies, amplitudes, target_hz):
    index = np.argmin(abs(frequencies - target_hz))
    return 20 * np.log10(max(amplitudes[index], 1e-15))


def test_frequency_response_pass_stop_tolerance():
    spec = BandpassSpec(20, 400, 4)
    frequencies, amplitudes = frequency_response(spec, 2000)
    assert db_at(frequencies, amplitudes, 100) > -0.2
    assert db_at(frequencies, amplitudes, 5) < -24
    assert db_at(frequencies, amplitudes, 700) < -18


def test_nyquist_fail_closed():
    with pytest.raises(ValueError, match="NYQUIST"):
        frequency_response(BandpassSpec(20, 600, 4), 1000)


def test_tone_attenuation_and_raw_immutable():
    fs_hz = 2000
    values = (
        tone(fs_hz, 5)
        + tone(fs_hz, 100)
        + tone(fs_hz, 700)
    )
    before = array_hash(values.copy())
    result = apply_bandpass(
        values,
        fs_hz,
        BandpassSpec(20, 400, 4),
        source_window_id="w1",
        profile_id="p",
        profile_fingerprint="fp",
    )
    assert array_hash(values) == before
    assert result.mask.shape == values.shape
    assert np.isfinite(result.values).all()

    output_spectrum = np.abs(np.fft.rfft(result.values))
    frequencies = np.fft.rfftfreq(values.size, 1 / fs_hz)
    amp_100 = output_spectrum[np.argmin(abs(frequencies - 100))]
    amp_5 = output_spectrum[np.argmin(abs(frequencies - 5))]
    amp_700 = output_spectrum[np.argmin(abs(frequencies - 700))]
    assert amp_100 > 20 * amp_5
    assert amp_100 > 20 * amp_700


def test_zero_phase_chirp_has_no_bulk_lag():
    from scipy.signal import chirp

    fs_hz = 2000
    time = np.arange(fs_hz * 2) / fs_hz
    values = chirp(time, f0=40, f1=300, t1=time[-1], method="linear")
    result = apply_bandpass(
        values,
        fs_hz,
        BandpassSpec(20, 400, 4),
        source_window_id="w",
        profile_id="p",
        profile_fingerprint="fp",
    )
    output = np.nan_to_num(result.values)
    lag = np.argmax(np.correlate(output, values, mode="full")) - (len(values) - 1)
    assert abs(lag) <= 2


def test_mask_preserved_and_not_filled():
    fs_hz = 2000
    values = tone(fs_hz, 100)
    mask = np.zeros_like(values, dtype=bool)
    mask[800:1000] = True
    result = apply_bandpass(
        values,
        fs_hz,
        BandpassSpec(20, 400, 4),
        mask=mask,
        source_window_id="w",
        profile_id="p",
        profile_fingerprint="fp",
    )
    assert np.array_equal(result.mask, mask)
    assert np.isnan(result.values[mask]).all()


def test_deterministic_replay():
    values = tone(2000, 100)
    kwargs = {
        "source_window_id": "w",
        "profile_id": "p",
        "profile_fingerprint": "fp",
    }
    first = apply_bandpass(values, 2000, BandpassSpec(20, 400, 4), **kwargs)
    second = apply_bandpass(values, 2000, BandpassSpec(20, 400, 4), **kwargs)
    assert np.array_equal(first.values, second.values, equal_nan=True)
    assert first.metadata["output_hash"] == second.metadata["output_hash"]


def test_causal_group_delay_is_explicit_and_positive_in_passband():
    delay = causal_group_delay_samples(
        BandpassSpec(20, 400, 4, phase_mode="CAUSAL"),
        2000,
        100,
    )
    assert delay > 0
    assert delay < 20
