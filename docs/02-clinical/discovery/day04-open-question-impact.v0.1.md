# DAY04 Open-Question Impact

DAY04 does not silently close site/protocol unknowns.

| Item | DAY04 impact | Status after DAY04 |
|---|---|---|
| OQ-004 — current filters/normalization/window/protocol | QC taxonomy explicitly requires protocol/reference provenance for baseline/noise and policy-dependent decisions. | `TBD / OPEN` |
| Site QC thresholds | DAY04 defines reason semantics only; threshold values require site evidence + clinician approval. | `TBD / NOT_VERIFIED` |
| Power-line applicability/site frequency | Detector capability is defined, but site/config-specific reference is not assumed. | `NOT_VERIFIED` |
| Clipping/ADC characteristics | Clipping reason requires known acquisition/device characteristics where applicable. | `NOT_VERIFIED` |
| Artifact vs physiological variation in complex cases | Ambiguity is explicitly representable and routes to review. | `DISCOVERY_REQUIRED / CLINICIAN_REVIEW_REQUIRED` |

**No clinical/site QC threshold is closed in DAY04.**

DAY03 remains evidence-blocked in the packaged handoff, so no site-observation finding is upgraded to `SITE_VERIFIED` here.
