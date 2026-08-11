# DAY35 → DAY36 HANDOFF CONTEXT PACK

## 0. Metadata

```yaml
current_day: DAY35
next_day: DAY36
current_day_status: PASS_WITH_LIMITATIONS
highest_claim: RESEARCH_THRESHOLDS_FROZEN_V0.1
site_threshold_status: NOT_VERIFIED
locked_partition_consumed: 0
```

## 1. Executive Handoff
DAY35 completed detector-specific research threshold sensitivity. Five families have a reversible `RESEARCH_HEURISTIC` profile. Poor-contact remains HOLD. DAY33 history was not changed; aligned DAY35 fixtures repaired the scorable-truth geometry for dropout/flatline/clipping. No locked truth, public raw data, expert annotation, or clinical/site evidence was used.

## 2. Selected Research Profile
- Missing warning fraction 0.01; zero-run warning fraction 0.25; flatline epsilon 1e-12.
- Clipping repeated extrema 0.10 under synthetic ADC semantics only.
- Baseline RMS 0.00020; MAD 0.00010 synthetic reference profile.
- Power-line warning ratio 0.08 under synthetic 50 Hz metadata.
- Motion low-ratio 0.22; drift 0.20; transient-z 6.0.
- Poor contact: `HOLD_NOT_SCORABLE`.

## 3. DAY36 Must Preserve
- Synthetic low amplitude is physiology-preservation stress, not pathology.
- Research thresholds are not site thresholds.
- Distribution-support/shift is not QC failure or diagnosis by definition.
- Site-template remains null.
- Poor contact must not be activated from low amplitude alone.

## 4. Inputs for DAY36
- `configs/qc/thresholds.research-v0.1.yaml`
- `qa-validation/evidence/day35-threshold-selection-decision.v0.1.json`
- `qa-validation/evidence/day35-robustness-by-fs-window-v0.1.csv`
- `qa-validation/evidence/day35-scorable-truth-readiness-matrix.csv`
- DAY29/31 distribution-support contracts
- DAY33 research corpus + DAY35 aligned fixtures

## 5. Known Limitations
No public payload evaluation, no clinical validation, no expert annotation, no poor-contact positive known truth. Synthetic robustness is narrow and intentionally easy enough for engineering known-answer verification.

## 6. Recommended DAY36 First Action
Construct a challenge-axis matrix separating `QUALITY_FAILURE`, `DISTRIBUTION_UNSUPPORTED`, and `PHYSIOLOGY_PRESERVATION_STRESS`, then verify that low-amplitude/context shift cannot automatically produce `QUALITY_BLOCKED` without acquisition-artifact evidence.
