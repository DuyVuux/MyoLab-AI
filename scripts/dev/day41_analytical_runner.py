from pathlib import Path
import json
import sys

import numpy as np
from scipy.signal import chirp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/semg-core"))

from semg_core.processing.bandpass import (  # noqa: E402
    BandpassSpec,
    apply_bandpass,
    causal_group_delay_samples,
    frequency_response,
)


def gain_db(frequencies, amplitudes, target_hz):
    index = np.argmin(abs(frequencies - target_hz))
    return float(20 * np.log10(max(amplitudes[index], 1e-15)))


def main():
    spec = BandpassSpec(20, 400, 4)
    fs_hz = 2000.0
    frequencies, amplitudes = frequency_response(spec, fs_hz)

    time = np.arange(int(fs_hz * 2)) / fs_hz
    values = chirp(
        time,
        f0=40,
        f1=300,
        t1=time[-1],
        method="linear",
    )
    result = apply_bandpass(
        values,
        fs_hz,
        spec,
        source_window_id="analytical-chirp",
        profile_id="research-bandpass-analytical-20-400-v0.1",
        profile_fingerprint="day41-evidence",
    )
    lag = int(
        np.argmax(np.correlate(result.values, values, mode="full"))
        - (len(values) - 1)
    )

    measured = {
        "5Hz": gain_db(frequencies, amplitudes, 5),
        "100Hz": gain_db(frequencies, amplitudes, 100),
        "700Hz": gain_db(frequencies, amplitudes, 700),
    }
    causal_delay_100 = causal_group_delay_samples(
        BandpassSpec(20, 400, 4, phase_mode="CAUSAL"),
        fs_hz,
        100,
    )
    passed = (
        measured["100Hz"] > -0.2
        and measured["5Hz"] < -24
        and measured["700Hz"] < -18
        and abs(lag) <= 2
        and 0 < causal_delay_100 < 20
    )
    output = {
        "fs_hz": fs_hz,
        "spec": spec.__dict__,
        "gain_db": measured,
        "zero_phase_bulk_lag_samples": lag,
        "causal_group_delay_100hz_samples": causal_delay_100,
        "tolerances": {
            "100Hz_min_db": -0.2,
            "5Hz_max_db": -24,
            "700Hz_max_db": -18,
            "bulk_lag_abs_max_samples": 2,
            "causal_group_delay_100hz_range_samples": [0, 20],
        },
        "status": "PASS" if passed else "FAIL",
    }

    evidence_path = ROOT / "qa-validation/evidence/day41-analytical-results.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(output, indent=2) + "\n")

    report_path = ROOT / "qa-validation/analytical/bandpass-verification-v0.1.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = f"""# Band-Pass Verification v0.1

Status: **{output['status']}**

Research-only explicit test profile: Butterworth SOS order 4, 20–400 Hz,
Fs=2000 Hz, zero-phase. This is **not** a site/global default.

| Probe | Measured | Tolerance |
|---|---:|---:|
| 5 Hz | {measured['5Hz']:.3f} dB | < -24 dB |
| 100 Hz | {measured['100Hz']:.3f} dB | > -0.2 dB |
| 700 Hz | {measured['700Hz']:.3f} dB | < -18 dB |
| Chirp bulk lag | {lag} samples | abs <= 2 |
| Causal group delay at 100 Hz | {causal_delay_100:.3f} samples | 0 < d < 20 |

The tabulated frequency-response probes describe the single-pass IIR design.
Forward/backward zero-phase execution applies the magnitude response twice, so its
stopband attenuation is stronger than the single-pass design curve.

Zero-phase `sosfiltfilt` is acausal and therefore appropriate here only for
offline research processing. A future real-time profile must use causal
filtering and expose group-delay/timing compensation explicitly. Raw arrays
remain unchanged and masks are preserved.
"""
    report_path.write_text(report)
    print(json.dumps(output, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
