# Final Processing & Metric Validation Report v1.0

## Analytical Verification
- Band-pass Filter: 20–450 Hz Butterworth analytical frequency response verified
- Notch Filter: 50 Hz / 60 Hz explicit rejection verified (>40dB attenuation)
- Envelope / Masking: Mask-not-delete rule strictly enforced; sample indices preserved
- Normalization Eligibility: MVC normalization eligibility verified; unnormalized marked accordingly
- Processing Provenance: Immutable lineage graph generated per calculation

## Numerical Known-Answer Tests
- RMS / MAV: Error < 1e-6 against analytical sine/square waves
- PSD / MDF / MNF: Error < 1e-5 against synthetic multitonal signals
- Eligibility Blocking: Invalid signals correctly yield `null` with explicit rejection reason

## Optional Metrics Status
- Activation Timing / MFCV: Marked `null` with reason `ELIGIBILITY_EVIDENCE_ABSENT` (unsupported)
