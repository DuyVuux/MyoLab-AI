# DAY13 Acceptance Criteria — Unit / Time / Count / Sampling Validation Engine

## Automated
- `time_count_unit.py` imports under Python 3.11+ and Pydantic v2.
- Happy path and boundary tests pass.
- Duplicate/non-monotonic timestamps fail closed.
- Metadata count mismatch fails closed; missing count is NOT_EVALUATED, never invented.
- `begin_time` mismatch fails closed; absent value is not promoted from the first sample.
- Each signal's declared sampling rate is validated independently; mixed rates are allowed.
- Unknown unit fails; missing unit is surfaced and no default unit is inferred.
- V↔uV conversion is explicit, registry-backed, immutable and provenance-complete.
- Same input/config/registry yields deterministic validation ID/report.
- Golden fixtures pass; corrupted fixtures fail.
- Raw fixture bytes remain unchanged.

## Manual / expert
- Confirm unit registry symbols reflect observed formats and do not imply unverified semantics.
- Confirm numeric tolerances are engineering serialization/clock tolerances, not clinical thresholds.
- Confirm DAY13 does not implement MR4 parsing, channel ontology, QC, preprocessing or model logic.
- Confirm upstream DAY12 Pydantic contracts remain untouched.

## Status
`GO_FOR_DAY_14` only if automated checks and human review pass and no upstream blocking evidence remains.
