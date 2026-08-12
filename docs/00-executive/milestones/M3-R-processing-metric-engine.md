# M3-R — Processing / Metric Research Engine

## Decision
`PROCESSING_METRIC_RESEARCH_READY`

DAY40–50 has been audited as one Phase 3R system. Versioned preprocessing configuration, deterministic processing provenance, RMS/MAV, MDF/MNF, conditional activation timing, MFCV supportability and Session Evidence Bundle semantics are frozen by content hash.

## Frozen boundary
- Processing profiles/configs and code listed in `day51-phase3-freeze-manifest.v0.1.json`.
- Metric registry and PSD definition are versioned.
- Evidence bundle schema is frozen at v0.1.
- Distribution support remains informational research-only.
- Uncertainty extension point is typed, but calibrated probability/conformal output is not enabled without a validated probabilistic model.

## Unsupported / not verified
- Real aligned activation-timing evaluation cohort.
- Site MFCV geometry.
- Calibrated probability/conformal prediction/OOD numeric score.

## Claim boundary
Research engineering readiness only; no clinical, site, diagnostic or hospital-ready claim.
