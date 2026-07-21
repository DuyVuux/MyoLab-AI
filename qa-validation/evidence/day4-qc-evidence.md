# Day 4 QC Evidence

**Commit:** `cf1ec8dfdce6d416e4947343022e8ccf1e0d429e`  
**Date:** `2026-07-20`  
**Python:** `3.12.3`  
**NumPy:** `2.5.1`  
**SciPy:** `1.18.0`  
**QC config:** `qc_v0.1`

## Commands

```bash
uv run bash scripts/dev/run_day4_checks.sh
```

## Results

| Test group | Result | Evidence path |
|---|---|---|
| Day 3 regression | PASS | |
| QC math helpers | PASS | |
| QualityGate tests | PASS | |
| Golden pass | PASS | `qa-validation/evidence/day4-qc-pass.json` |
| Nonfinite fail | PASS | `qa-validation/evidence/day4-qc-fail-nonfinite.json` |
| Flatline fail | PASS | `qa-validation/evidence/day4-qc-fail-flatline.json` |
| Short duration fail | PASS | `qa-validation/evidence/day4-qc-fail-short-duration.json` |
| Clipping warning | PASS | `qa-validation/evidence/day4-qc-warning-clipping.json` |
| Powerline warning | PASS | `qa-validation/evidence/day4-qc-warning-powerline.json` |
| Motion warning | PASS | `qa-validation/evidence/day4-qc-warning-motion.json` |
| JSON schema | PASS | |

## Safety assertions

- [x] Fail/import-rejected always abstains.
- [x] Warning remains visible.
- [x] MFCV ineligibility does not block basic sEMG.
- [x] No fatigue output is created.
- [x] No threshold is claimed clinically validated.

## Known limitations

- The thresholds used in v0.1 (such as those for flatlines, clipping, powerline noise, and motion artifacts) are provisional heuristics. They require formal review and validation by clinical domain experts in Day 5.
- MFCV evaluations remain disabled pending the implementation of specialized MFCV signal quality checks.
