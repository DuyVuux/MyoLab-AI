# Day 26 — Master Experiment Blueprint

## Architecture

```text
Canonical dataset + sealed groups
→ grouped outer regime
→ grouped inner selection
→ fold-contained preprocessing/features
→ classical model / metric / context engine
→ optional fold-contained calibrator
→ threshold/abstention policy selected inner-only
→ one-time outer evaluation
→ subject/repetition aggregation
→ human review
```

## Task A

- Primary prediction unit: repetition.
- Primary metric: subject-macro repetition Macro F1.
- Minimum model ladder: Dummy×2, LDA, Logistic Regression, Linear SVM, Random Forest.
- Primary benchmark: cross-subject zero-shot.
- Realism: cross-session/day/reapply and personalized new-subject.

## Task B

- Default semantics: context/supportability/confidence adjustment/abstention.
- Priority architecture: separate fatigue-context engine.
- Priority experiments: E-fatigue-2/3; E0 mandatory baseline; E1 conditional; E4 governed recalibration.
- Report fatigue strata without hard diagnosis claim.

## Task C

- Deterministic metric engine only until target/reference standard is locked.
- Compare repeatability, compatibility and missing-data behavior.

## Global safety and governance

- Test set sealed.
- Result status `NOT_RUN` on Day 26.
- No auto retraining.
- No MFCV outputs when eligibility unknown/false.
- No clinical claims from public healthy data.
