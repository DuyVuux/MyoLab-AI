# DAY49 Research Decision Record — MFCV Feasibility & Gate

## Decision Status
`PASS_WITH_LIMITATIONS`

## Invariants
1. MFCV calculation requires explicit physical array geometry (IED, channel ordering, orientation evidence).
2. Unverified orientation or unrectified signal absence blocks calculation (`MFCV_UNSUPPORTED`).
3. Pairwise minimum (2 channels) is permitted only with explicit warning `PAIRWISE_MINIMUM_LOW_REDUNDANCY`.
4. All thresholds remain research fixture parameters only; no site clinical claim.
