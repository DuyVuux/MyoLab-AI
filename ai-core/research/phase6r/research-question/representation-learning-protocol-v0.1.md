# Phase 6R Representation-Learning Applicability Decision

## Decision

`representation_learning_applicability = NOT_JUSTIFIED`

`starting_ml_decision = ML_NO_GO`

The active research-ML feasibility decision is `ML_NO_GO`. No separate, defensible representation-learning target has been established in the current governed configuration. Under the no-forced-ML rule, Phase 6R therefore does not train an SSL encoder merely to create an AI artifact.

## Evidence basis

- M5-R / Gate E-R: supplied preflight reports ready/pass.
- PublicFeatureWindowRecord v1.2: supplied preflight reports PASS.
- Reproducibility: supplied preflight reports PASS.
- Leakage audit: `PASS` after evidence-based re-audit.
- Claim-boundary audit: `PASS` after context-aware re-audit.
- Starting ML feasibility decision: `ML_NO_GO`.

## Scientific rationale

A representation-learning experiment must answer a technical question distinct from the failed/not-justified classical ML path. No such approved question is present in the active configuration. Training an encoder now would invert the required order from evidence → question → applicability → experiment.

## Consequences

- Handcrafted baseline: no new Phase 6R baseline is fabricated; Phase 5R feasibility evidence remains authoritative.
- SSL encoder: `SKIPPED_BY_GOVERNANCE`.
- Representation evaluation: `NOT_RUN`.
- Embedding supportability: `NOT_RUN`; existing metadata/rule-based supportability remains the baseline.
- Calibration/selective prediction: `NOT_APPLICABLE` because no valid probabilistic research head is promoted.
- Ablation: `NOT_APPLICABLE` because no Phase 6R model was trained.
- Core system remains ML default OFF.

## Claim boundary

RESEARCH_ONLY | NOT_CLINICALLY_VALIDATED | NOT_FOR_CLINICAL_USE | CORE_ML_DEFAULT_OFF
