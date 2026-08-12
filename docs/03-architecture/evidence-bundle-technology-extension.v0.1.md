# Session Evidence Bundle Technology Extension v0.1

## Purpose
DAY50 converges QC, processing provenance, metrics, distribution support, uncertainty, unsupported capabilities, limitations, and event correlation into one deterministic research evidence artifact.

## Authority boundaries
- QC and Distribution Support remain separate concepts. `SHIFTED` is not pathology and is not automatically QC FAIL.
- Deterministic rule confidence is ordinal only; it is never converted to probability.
- `calibrated_probability` and conformal outputs require explicit calibration evidence; this project currently has none for the deterministic QC path.
- Unsupported or unavailable metrics use `value: null` plus explicit reason codes.
- MFCV supportability is recording/geometry specific. Synthetic known-delay mechanics cannot become a site MFCV measurement.
- Activation timing synthetic known-onset evidence cannot become real event-aligned accuracy.

## Referential integrity
Every metric must reference the exact DAY45 `processing_manifest_id`. Orphan source/manifest references cause bundle rejection. The bundle carries content-addressed source refs and processing identifiers; waveform data is not embedded.

## Event correlation
`event_correlation_id` links the evidence bundle to the processing lifecycle. Persistent event storage remains deferred to DAY53.

## Current uncertainty posture
The reference bundle uses `RULE_CONFIDENCE` with an ordinal level and `calibrated_probability: null`. No OOD score, calibrated probability, conformal set, or diagnostic confidence is fabricated.
