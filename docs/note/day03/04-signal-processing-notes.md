# Day 3 Signal Processing Notes

## Pipeline boundary

```text
CSV bytes
→ parse
→ validate time/unit/provenance
→ normalize unit
→ canonical object
→ QC (next)
→ preprocessing (later)
```

## Do not perform today

- band-pass/notch;
- rectification/envelope;
- windowing;
- RMS/MAV;
- PSD/MDF/MNF;
- slope;
- MFCV;
- fatigue inference.

## Questions

1. Which transformations are lossless metadata/canonicalization?
2. Which transformations alter signal samples?
3. Why must source unit remain stored after conversion?
4. Why are NaN values not silently filled during ingestion?
5. Why must the source hash be computed before filtering?
