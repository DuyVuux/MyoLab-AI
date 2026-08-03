# Day 33 Results Summary

## Scope

Day 33 evaluated Day 32 development predictions at repetition and subject level. Sealed test partitions remained closed, Mendeley and GRABMyo were evaluated separately, and synthetic outputs are marked as tooling validation only.

## Synthetic Tooling Validation

- Mode: `TOOLING_VALIDATION`
- Prediction rows: 256
- Repetition rows: 64
- Subject count: 8
- Primary metric: 0.966667
- Bootstrap 95% CI: [0.933333, 1.000000]
- Failure cases: 9

Synthetic results are not research benchmarks.

## Mendeley Real Development Evaluation

- Dataset: `mendeley-4channel-hand-gesture-v2`
- Run: `day32-baseline-v1`
- Prediction rows: 37657
- Repetition rows: 639
- Subject count: 32
- Primary metric, subject-macro repetition-macro F1: 0.739405
- Subject-cluster bootstrap 95% CI: [0.667319, 0.801871]
- Failure cases registered: 179

Mendeley Day 32 OOF window predictions did not include complete class score vectors, so Day 33 uses deterministic label-only majority aggregation and does not manufacture probability confidence.

## GRABMyo Real Development Evaluation

- Dataset: `grabmyo-physionet-v1.1.0`
- Run: `grabmyo-primary4-baseline-v1`
- Prediction rows: 2856
- Repetition rows: 2856
- Subject count: 34
- Primary metric, subject-macro repetition-macro F1: 0.981686
- Subject-cluster bootstrap 95% CI: [0.967184, 0.993317]
- Failure cases registered: 50

GRABMyo Day 32 OOF trial predictions expose decision scores. Day 33 reports margins from those scores but does not treat them as probabilities. Cross-day/session summaries are development performance summaries only, not fatigue claims.

## Protocol Guards

- Sealed test rows read: 0 for all runs.
- Pooled evaluation executed: false for all runs.
- Synthetic results used as benchmark: false.
- Fatigue inference allowed: false.

## Primary Evidence Folders

- `qa-validation/evidence/day33/synthetic-evaluation/`
- `qa-validation/evidence/day33/real-development/mendeley/`
- `qa-validation/evidence/day33/real-development/grabmyo/`
- `qa-validation/evidence/day33/predictions/`
