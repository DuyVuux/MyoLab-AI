# GATE E-R — Public Benchmark Readiness

## Decision

**Status: `BLOCKED_WITH_EVIDENCE`**  
**Required milestone claim `PUBLIC_BENCHMARK_READY`: NOT ACHIEVED.**

The gate itself is fully evaluated. It is blocked because the current DAY67
and DAY68 execution evidence is site-derived from
`VINMEC_MOTION_LAB_EXAMPLE_OUTPUT`, while the Phase 5R milestone is explicitly
a **public cross-dataset benchmark**.

## Evidence that passed

- DAY66 anti-leakage protocol was frozen before benchmark outcome analysis.
- DAY67 site raw evidence is hashed and PHI-aware.
- DAY68 feature Parquet SHA-256 is
  `4575223ace0b8ea6a24499666769b5dae3231e8b85c0505f7dc986062b5efee8`.
- DAY68 contains 12/12 available RMS/MAV/MDF/MNF rows.
- DAY69 explicitly marks absent public comparisons `INCOMPARABLE/UNKNOWN`.
- DAY70 links claims to denominators and refuses supervised accuracy without
  reference labels.
- DAY71 reaches an evidence-supported `ML_NO_GO`; no model or fake probability
  is generated.
- No patient raw payload, PHI, or private site CSV is included in this release package.

## Blocking evidence

1. `DAY67_DAY68_EVIDENCE_ORIGIN_IS_SITE_NOT_PUBLIC`.
2. `NO_PUBLIC_CROSS_DATASET_FEATURE_COMPARISON`.
3. `PUBLIC_GENERALIZATION_NOT_ESTABLISHED`.

The DAY64-selected public datasets remain governance/catalog inputs, but their
raw/feature outcomes are not present in the supplied DAY68 feature table.
Therefore a public benchmark milestone cannot be inferred from the filename
`public-feature-summary-v1.1.parquet`.

## Leakage status

No evidence indicates post-freeze threshold tuning, normalization fitting,
feature selection, algorithm selection, or model training on locked outcomes.
The original DAY66 policy remains the benchmark authority.

## Reproducibility status

The package reproduces DAY69–72 decisions from the frozen DAY68 Parquet input
and its exact SHA. A complete public benchmark clean-clone reproduction is
**not established** because the required public-domain feature outcomes are
absent. This is a milestone blocker, not hidden as a tooling pass.

## Required remediation

Materialize at least the DAY64 core public sources under the DAY66 frozen
protocol, run DAY67/68 on them without post-hoc tuning, append their feature
rows with source/version/split provenance, then rerun DAY69–72. Do not modify
DAY66 splits based on observed final outcomes.

## Claim boundary

Research-only engineering evidence. No clinical effectiveness, diagnostic,
Vinmec validation, hospital readiness, site validation, or representative
clinical cohort claim.
