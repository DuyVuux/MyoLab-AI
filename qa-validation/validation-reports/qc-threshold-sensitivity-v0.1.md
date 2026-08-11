# QC Threshold Sensitivity v0.1 — DAY35 Validation Report

## Scope
Research-only synthetic development evidence. No clinical/site validation; no public raw dataset evaluation; no expert annotation; no locked truth consumption.

## Readiness outcome
Five detector families were scorable after DAY35 introduced versioned aligned synthetic fixtures for the DAY33 localization-defect branches. `LF_POOR_CONTACT` remained `HOLD_NOT_SCORABLE` because cross-channel positive truth is absent.

## Selection objective
`weighted_error = 3*FN + 1*FP`, with ties resolved by smallest normalized distance from the upstream provisional setting. The 3:1 weight is a research engineering preference, not a clinical risk model.

## Selected research profile

| Family | Selected parameters | Evidence class |
|---|---|---|
| Missing/dropout/flatline | missing=0.01; zero-run=0.25; flatline epsilon=1e-12 | RESEARCH_HEURISTIC |
| Clipping | repeated extrema=0.10 | RESEARCH_HEURISTIC |
| Baseline noise | RMS=0.00020; MAD=0.00010 | RESEARCH_HEURISTIC |
| Power-line | warning ratio=0.08 | RESEARCH_HEURISTIC |
| Motion/low-frequency | ratio=0.22; drift=0.20; transient-z=6.0 | RESEARCH_HEURISTIC |
| Poor contact | HOLD | SITE_NOT_VERIFIED |

The selected values equal the existing provisional defaults because those defaults were among zero-weighted-error candidates and the deterministic tie-break avoids unnecessary config drift. This should not be interpreted as independent clinical confirmation of the defaults.

## Primary synthetic denominators

- Missing/dropout/flatline: TP=6, FP=0, TN=6, FN=0.
- Clipping: TP=2, FP=0, TN=3, FN=0.
- Baseline: TP=2, FP=0, TN=2, FN=0.
- Power-line: TP=2, FP=0, TN=2, FN=0.
- Motion: TP=2, FP=0, TN=2, FN=0.

These tiny constructed strata are verification fixtures, not an estimate of real-world detector performance.

## Robustness
The selected operating points were replayed on synthetic strata at 1000/2000/4000 Hz and 0.25/0.50 s windows. All enumerated synthetic positive/negative pairs were separated as expected. This is descriptive implementation evidence only.

## DAY33 repair policy
DAY33 v0.1 is not changed. DAY35 creates a separate aligned fixture version with local positive events inside the core and exact event bounds. This preserves the DAY34 benchmark-quality finding in project history.

## Locked-set governance
DAY33 sealed locked entries observed in manifest: 6. Outcomes consumed: 0. Threshold selection does not read locked signal payloads or truth.

## Site policy
`site_threshold_status = NOT_VERIFIED`; every site-template threshold is null. No DAY35 selected parameter is allowed to auto-populate the site template.

## Final conclusion
DAY35 supports `RESEARCH_THRESHOLDS_FROZEN_V0.1` with limitations. It does not support `CLINICALLY_VALIDATED`, `SITE_VALIDATED`, or any diagnostic-performance claim.
