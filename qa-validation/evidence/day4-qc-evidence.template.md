# Day 4 QC Evidence

**Commit:** `<fill>`  
**Date:** `<fill>`  
**Python:** `<fill>`  
**NumPy:** `<fill>`  
**QC config:** `qc_v0.1`

## Commands

```bash
bash scripts/dev/run_day4_checks.sh
```

## Results

| Test group | Result | Evidence path |
|---|---|---|
| Day 3 regression | | |
| QC math helpers | | |
| QualityGate tests | | |
| Golden pass | | `qa-validation/evidence/day4-qc-pass.json` |
| Nonfinite fail | | `qa-validation/evidence/day4-qc-fail-nonfinite.json` |
| Flatline fail | | `qa-validation/evidence/day4-qc-fail-flatline.json` |
| Short duration fail | | `qa-validation/evidence/day4-qc-fail-short-duration.json` |
| Clipping warning | | `qa-validation/evidence/day4-qc-warning-clipping.json` |
| Powerline warning | | `qa-validation/evidence/day4-qc-warning-powerline.json` |
| Motion warning | | `qa-validation/evidence/day4-qc-warning-motion.json` |
| JSON schema | | |

## Safety assertions

- [ ] Fail/import-rejected always abstains.
- [ ] Warning remains visible.
- [ ] MFCV ineligibility does not block basic sEMG.
- [ ] No fatigue output is created.
- [ ] No threshold is claimed clinically validated.

## Known limitations

- 
