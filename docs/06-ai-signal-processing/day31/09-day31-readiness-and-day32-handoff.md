# Day 31 readiness and Day 32 handoff

The authoritative decision is generated at:

```text
qa-validation/evidence/day31/day31-readiness-decision.json
```

`GO_FOR_DAY32_SEPARATE_BASELINE_SMOKE` requires all of:

- Day 30 preflight accepted;
- exact 14-feature contract validation;
- golden mathematical checks;
- Mendeley 42-dimensional smoke;
- GRABMyo 392-dimensional smoke;
- quality audit;
- stress test;
- reproducibility manifest;
- zero test signal rows read;
- no training, fitting, or pooled-training execution.

`GO_FOR_DAY32_SEPARATE_BASELINE_FULL` additionally requires real
train/validation feature materialization, a resolved dependency lock, and
explicit Day 32 training authorization.

Day 31 never grants training by itself. Every readiness artifact keeps
`training_allowed`, `model_fitting_allowed`, `scaler_fitting_allowed`,
`pooled_training_allowed`, and `test_signal_access_allowed` false.
