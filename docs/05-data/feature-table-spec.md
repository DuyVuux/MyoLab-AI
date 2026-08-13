# Public Feature Window Table Spec v1.2

## Purpose

`PublicFeatureWindowRecord.v1.2` is the feature-layer contract for the M5-R
remediation cycle. It separates public/raw adaptation from QC, windowing,
feature extraction and downstream research examples.

## Required Columns

```text
schema_version
dataset_id
subject_id
session_id
split
window_id
channel_id
task
start_sample
end_sample
fs_hz
qc_status
qc_reason_codes
metric_eligible
rms
mav
mdf_hz
mnf_hz
processing_profile
feature_registry_version
source_hash
```

## Rules

- `split` is `DEVELOPMENT` or `LOCKED_EVALUATION`.
- `subject_id` is the leakage group boundary.
- `metric_eligible=true` requires `qc_status=QC_ELIGIBLE`.
- Ineligible windows retain null feature values plus explicit reason codes.
- Features are not imputed to improve visualizations or model results.
- `source_hash` is the SHA-256 of the source payload represented by the window.
- The table does not contain perturbation labels, predictions, model scores or
  evaluation outcomes.

## Relationship To Other Records

```text
CanonicalSignalRecord
  -> PublicFeatureWindowRecord
  -> ResearchExampleRecord
```

Synthetic perturbation labels live in `ResearchExampleRecord.v1.0`, not in this
feature table.
