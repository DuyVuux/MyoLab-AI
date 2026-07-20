# Day 4 Acceptance Criteria

## AC-D4-01 — Golden basic QC

Given the Day 3 golden session, when QC v0.1 runs, then:

- status is `pass`;
- `analysis_allowed=true`;
- abstention is not required;
- MFCV is not eligible;
- no top-level reason code is produced.

## AC-D4-02 — Non-finite critical failure

A fixture with 2% active-phase NaN values must produce `NONFINITE_RATIO_EXCESSIVE`, block analysis, and require abstention.

## AC-D4-03 — Flatline critical failure

A fixture with a four-second active-phase constant segment must produce `FLATLINE_EXCESSIVE`, block analysis, and require abstention.

## AC-D4-04 — Warning-only heuristics

Clipping, strong 50 Hz, and strong 5 Hz fixtures must produce warning status and keep `analysis_allowed=true`.

## AC-D4-05 — Active duration

A 30-second active phase for the 60-second protocol must produce `ACTIVE_DURATION_TOO_SHORT` and abstention.

## AC-D4-06 — MFCV isolation

MFCV ineligibility reason codes must not cause a basic sEMG fail or warning by themselves.

## AC-D4-07 — Contract and safety

- QC output matches JSON Schema.
- No raw arrays in output.
- No JSON NaN/Infinity.
- All fixture manifests are synthetic and `clinical_use_allowed=false`.
- Day 1–3 tests remain green.
