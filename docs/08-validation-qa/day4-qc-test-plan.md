# Day 4 QC Test Plan

## Objective

Verify deterministic behavior, schema compliance, abstention, and MFCV capability isolation.

## Fixtures and expected results

| Fixture | Expected status | Expected code | Analysis allowed |
|---|---|---|---:|
| Day 3 golden | pass | none | true |
| qc_fail_nonfinite | fail | NONFINITE_RATIO_EXCESSIVE | false |
| qc_fail_flatline | fail | FLATLINE_EXCESSIVE | false |
| qc_warning_clipping | warning | CLIPPING_SUSPECTED | true |
| qc_warning_powerline | warning | POWERLINE_NOISE_HIGH | true |
| qc_warning_motion_artifact | warning | MOTION_ARTIFACT_HIGH | true |
| qc_fail_short_duration | fail | ACTIVE_DURATION_TOO_SHORT | false |

All fixtures are synthetic and `clinical_use_allowed=false`.

## Test layers

1. Pure-math unit tests.
2. Check-level tests through QualityGate.
3. Ingestion-to-QC integration tests.
4. JSON Schema validation.
5. Day 1–3 regression.
6. Artifact/safety-marker check.

## Critical assertions

- Every fail requires abstention.
- MFCV ineligibility does not block basic sEMG.
- Warning does not become a critical fail in v0.1.
- No raw arrays appear in QC JSON.
- No NaN/Infinity appears in serialized JSON.
- Check order and reason-code order are deterministic.
