from pathlib import Path
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/semg-core"))

from semg_core.processing.notch import NotchSpec, apply_notch  # noqa: E402


def main():
    fs_hz = 2000.0
    time = np.arange(int(fs_hz * 4)) / fs_hz
    values = (
        np.sin(2 * np.pi * 50 * time)
        + 0.7 * np.sin(2 * np.pi * 173 * time)
    )
    result = apply_notch(
        values,
        fs_hz,
        NotchSpec(True, 50, 30),
        source_window_id="analytic",
        profile_id="research-notch-50hz-q30-v0.1",
    )

    frequencies = np.fft.rfftfreq(len(values), 1 / fs_hz)
    input_spectrum = np.abs(np.fft.rfft(values))
    output_spectrum = np.abs(np.fft.rfft(result.values))
    index = np.argmin(abs(frequencies - 173))
    unrelated_ratio = float(output_spectrum[index] / input_spectrum[index])
    attenuation_db = float(result.metadata["attenuation_db"]["50Hz"])
    passed = attenuation_db > 25 and unrelated_ratio > 0.95

    output = {
        "target_attenuation_db": attenuation_db,
        "unrelated_173hz_amplitude_ratio": unrelated_ratio,
        "pre_notch_spectral_evidence_ref": result.metadata[
            "pre_notch_spectral_evidence_ref"
        ],
        "status": "PASS" if passed else "FAIL",
    }
    evidence_path = ROOT / "qa-validation/evidence/day42-analytical-results.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(output, indent=2) + "\n")

    report_path = ROOT / "qa-validation/analytical/notch-verification-v0.1.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = f"""# Notch Analytical Verification v0.1

Status: **{output['status']}**

Explicit synthetic research case: 50 Hz mains, Q=30, Fs=2000 Hz. No
site/default mains frequency is inferred.

- 50 Hz attenuation: {attenuation_db:.3f} dB (required >25 dB).
- Unrelated 173 Hz amplitude ratio: {unrelated_ratio:.6f} (required >0.95).
- Pre-notch evidence ref: `{output['pre_notch_spectral_evidence_ref']}`.

The evidence reference is computed before modification and persists in result
provenance. Harmonics are filtered only when explicitly listed.
"""
    report_path.write_text(report)
    print(json.dumps(output, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
