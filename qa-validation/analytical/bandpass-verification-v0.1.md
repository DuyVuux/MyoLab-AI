# Band-Pass Verification v0.1

Status: **PASS**

Research-only explicit test profile: Butterworth SOS order 4, 20–400 Hz,
Fs=2000 Hz, zero-phase. This is **not** a site/global default.

| Probe | Measured | Tolerance |
|---|---:|---:|
| 5 Hz | -49.584 dB | < -24 dB |
| 100 Hz | -0.000 dB | > -0.2 dB |
| 700 Hz | -35.858 dB | < -18 dB |
| Chirp bulk lag | 0 samples | abs <= 2 |
| Causal group delay at 100 Hz | 3.681 samples | 0 < d < 20 |

The tabulated frequency-response probes describe the single-pass IIR design.
Forward/backward zero-phase execution applies the magnitude response twice, so its
stopband attenuation is stronger than the single-pass design curve.

Zero-phase `sosfiltfilt` is acausal and therefore appropriate here only for
offline research processing. A future real-time profile must use causal
filtering and expose group-delay/timing compensation explicitly. Raw arrays
remain unchanged and masks are preserved.
