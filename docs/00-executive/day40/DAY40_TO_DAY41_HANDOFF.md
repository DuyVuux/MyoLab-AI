# DAY40 → DAY41 Handoff

## Status

`PASS` — highest claim: `PROCESSING_PROFILE_CONTRACT_READY`.

## Actual result

DAY40 established the Phase 3R processing-profile contract without enabling any unverified DSP transform. The active profile `research-native-grid-preserve-v0.1` preserves native sampling grid, physical units, masks and QC authority. It requires explicit runtime Fs/unit and deterministic profile fingerprinting.

## Tests

- DAY40 focused: **46/46 PASS**.
- Upstream QC/research/property regression: **863 PASS**, 1 historical DAY21 anti-future-scope guard deselected.
- DAY38 frozen QC hashes: **15/15 MATCH**.
- Contract validator: PASS; active profiles=1, site assumptions=0, enabled unverified transforms=0.

## Frozen decisions

- no implicit 20–450 Hz band-pass;
- no implicit 50/60 Hz notch;
- no implicit resampling target;
- no normalization fitting;
- no locked-set fitting/adaptation;
- automatic processing only with DAY31 `ALLOW_PROFILED_PROCESSING`;
- raw and masks remain immutable/preserved;
- base deterministic DSP profile does not require distribution support to be `SUPPORTED`.

## Limitations

Band-pass/notch/rectification/smoothing/normalization are contract-only and disabled. Public raw processing and site/clinical validation are not performed.

## DAY41 may begin

YES. DAY41 must create analytical sinusoid/chirp/impulse evidence and only then create a new versioned profile enabling band-pass. It must not mutate the DAY40 preserve profile in place.
