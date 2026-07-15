# Day 3 Ingestion Validation Evidence

**Date:**  
**Commit:**  
**Operator:**  
**Python version:**  
**NumPy version:**  

## Fixture identity

- CSV: `data-platform/synthetic-data/golden_signal_01.csv`
- Manifest: `data-platform/synthetic-data/golden_signal_01.manifest.json`
- SHA-256:
- Sample count:
- Sampling rate:
- Phase counts:

## Commands executed

```bash
bash scripts/dev/run_day3_checks.sh
```

## Results

- Day 2 regression:
- Fixture hash verification:
- Protocol validation:
- Canonical import:
- JSON Schema validation:
- Pytest:
- Artifact check:

## Negative-test evidence

| Test | Expected code | Observed | Pass |
|---|---|---|---|
| Source hash mismatch | `SOURCE_HASH_MISMATCH` | | |
| Non-monotonic time | `TIME_NOT_MONOTONIC` | | |
| Forbidden identifier | `FORBIDDEN_PHI_KEY_PRESENT` | | |
| Unsupported unit | `UNSUPPORTED_SIGNAL_UNIT` | | |

## Known limitations

- Synthetic engineering fixture only.
- No spectral or physiological validation.
- No vendor-specific parser.
- No QC heuristics, preprocessing, features, or inference.
- No MFCV eligibility.

## Self-review result

- [ ] PASS
- [ ] PASS WITH DOCUMENTED WARNING
- [ ] FAIL / carry blocker to Day 4
