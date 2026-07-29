# Day 28 — Scope và Gates

## In-scope

- Reconcile Day 27 manifests.
- Train/validation-only EDA.
- Structural, label, hierarchy and signal-quality audit.
- Dataset card và Day 29 readiness decision.
- Experiment eligibility update theo Day 26.

## Out-of-scope

- Training/tuning/calibration.
- Test-set EDA.
- Noraxon/Motion Lab compatibility claim.
- Fatigue model claim.
- MFCV.
- Clinical performance claim.

## Gate order

```text
Day27 external-data gate
→ test visibility guard
→ structural/label/signal audit
→ Day28 quality gate
→ Day29 training preflight
```
