# Day 26 — Reproducibility, Model Governance & Deployment Constraints

**Project:** sEMG Clinical Intelligence compatible with Noraxon Ultium EMG / myoRESEARCH  
**schema_version:** `1.0`  
**status:** `PROVISIONAL_LOCKED_FOR_DAY26_BLUEPRINT`  
**trainingAllowed:** `false`  
**Generated for:** Day 26 Workstream 8  
**Date:** `2026-07-27`

## Purpose

This package locks the reproducibility, experiment-tracking, model-governance,
serialization, release, rollback, license, and deployment contracts required
before any baseline training begins.

It creates **no trained model**, performs **no fitting or hyperparameter tuning**,
and does **not open or evaluate a sealed test set**.

## Required outputs

```text
docs/09-mlops-devops/
├── experiment-tracking-spec.md
├── model-registry-spec.md
└── reproducible-training-policy.md

docs/research/day26/
└── 09-reproducibility-and-governance.md
```

## Machine-readable contracts

```text
schemas/
├── experiment-manifest.schema.json
├── model-registry-record.schema.json
├── release-manifest.schema.json
└── rollback-record.schema.json
```

Schema-checked blueprint examples are in `examples/`. No example contains a real
model artifact or fabricated performance result.

## Core Day 26 decisions

1. **Hybrid tracking:** content-addressed file manifests are the governance
   source of truth; a local MLflow server is the search/UI convenience layer.
2. **Reference environment:** exact core versions are provisionally locked in
   `configs/environment-lock.research.yaml` and `environment/requirements-core.lock.txt`.
3. **CPU-first:** GPU is not required unless profiling later demonstrates a
   justified need under a site-confirmed workload.
4. **Secure serialization:** `pickle`/`joblib` are not accepted as the default
   pilot release format. Untrusted arbitrary deserialization is prohibited.
5. **Registry states:** `draft`, `research`, `candidate`,
   `validated-for-engineering`, `pilot-candidate`, `rejected`, `archived`.
6. **No clinical-validation wording:** this package never uses
   `clinical validated` as a registry state.
7. **License gate:** unclear, non-commercial, research-only, DUA-restricted,
   or redistribution-restricted inputs block promotion unless the intended use
   is explicitly cleared.
8. **Human review and abstention:** mandatory for all future pilot-facing paths.

## Validation

Run:

```bash
cd day26-reproducibility-governance
./verify_day26_governance.sh
```

Expected behavior:

- validates all JSON schemas;
- validates all YAML examples against those schemas;
- verifies referenced SHA-256 hashes;
- confirms `trainingAllowed=false` in Day 26 examples;
- scans for forbidden registry wording;
- writes `validation/VALIDATION_REPORT.md`.

## Scope boundary

This is a **governance and reproducibility blueprint**, not an inference runtime,
not a medical device release, and not evidence of clinical performance.
