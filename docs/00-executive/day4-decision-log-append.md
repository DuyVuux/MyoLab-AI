# Day 4 Decision Log — Append

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D4-01 | Signal Quality Gate runs after canonical ingestion and before preprocessing. | Prevent invalid or incompatible signals from entering DSP/inference. | ACCEPTED_MVP0 |
| D4-02 | Critical QC failure blocks downstream fatigue analysis and creates abstention. | Quality failure is not equivalent to no-fatigue. | ACCEPTED_MVP0 |
| D4-03 | Clipping, power-line, and motion-artifact checks are warning-only in qc_v0.1. | Device/protocol-specific thresholds are not locally validated. | PROVISIONAL |
| D4-04 | Absolute amplitude and baseline-noise pass/fail thresholds remain disabled. | Device range, gain, calibration, and acquisition history are unconfirmed. | ACCEPTED_MVP0 |
| D4-05 | MFCV eligibility is a capability gate and does not block basic sEMG analysis. | MFCV needs additional geometry/channels but RMS/MDF/MNF may still be possible. | ACCEPTED_MVP0 |
| D4-06 | QC spectral checks do not automatically trigger filtering. | QC evidence and preprocessing policy must remain separately versioned. | ACCEPTED_MVP0 |
| D4-07 | All Day 4 thresholds are synthetic/golden engineering defaults only. | Prevent accidental clinical overclaim. | EXTERNAL_REVIEW_REQUIRED |
