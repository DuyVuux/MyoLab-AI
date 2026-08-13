# M5-R Remediation Decision Ledger v1.0

## Scope

This ledger records the approved architecture decisions for the remediation
cycle between Day72 and Day73. The objective is to make `PUBLIC_BENCHMARK_READY`
and `ML_GO` scientifically possible without forcing either outcome.

## Decisions

DEC-M5R-01
Decision: ENABLE_KNOWN_TRUTH_SYNTHETIC_PERTURBATION_TARGET
Rationale: Create a defensible supervised research target that can support
`ML_GO` without fabricating clinical artifact labels.
Constraint: `NO_INJECTED_CORRUPTION` means no project-injected corruption; it
does not mean clean clinical signal.

DEC-M5R-02
Decision: PUBLIC_BENCHMARK_PRIMARY_EXECUTION_OFFLINE_BATCH
Rationale: Keep the primary benchmark deterministic and reproducible by using
versioned offline code, config, seeds, input hashes and output hashes.
Constraint: `feature-extraction-service` is a secondary integration-validation
path, not the primary evidence path.

DEC-M5R-03
Decision: CREATE_PUBLIC_FEATURE_WINDOW_CONTRACT_V1_2
Rationale: Separate dataset adaptation from QC, windowing, feature extraction,
perturbation generation and ML evaluation.
Constraint: Do not overload adapter records with feature, target, prediction or
evaluation fields.

## Approved Layering

```text
SourceRecord
  -> CanonicalSignalRecord
  -> PublicFeatureWindowRecord
  -> ResearchExampleRecord
```

## Gate Principle

`ML_GO` is valid only when ML has incremental value over deterministic baseline
under a valid target, subject-level split, derivative-leakage controls,
untouched locked evaluation, reproducibility evidence and public-dataset
coverage. `ML_NO_GO` remains a valid scientific outcome.
