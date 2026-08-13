# Known-Truth Perturbation Target v1.0

## Purpose

Define a defensible supervised research target for Day71 remediation without
promoting public healthy sEMG data into clinical artifact ground truth.

## Target

Primary binary experiment:

```text
NO_INJECTED_CORRUPTION
vs
INJECTED_CORRUPTION
```

Optional second-stage experiment, only after binary supportability is
established:

```text
DROPOUT
CLIPPING
POWERLINE_INTERFERENCE
LOW_FREQUENCY_CONTAMINATION
```

## Semantics

`NO_INJECTED_CORRUPTION` means the perturbation generator did not inject a
corruption into that derived example. It does not mean the source signal is
clean, normal, clinical-grade or pathology-free.

## Scope

- Source windows must come from public development subjects only.
- All examples derived from the same source window inherit the source split.
- Locked evaluation subjects cannot be used to design perturbations, tune
  thresholds, select models or fit transforms.
- The task is research-only known-truth perturbation detection, not clinical
  artifact detection.

## Day71 ML_GO Meaning

`ML_GO` means the ML baseline provides incremental value over deterministic QC
under the pre-registered target and leakage controls. It does not mean a model
is clinically valid or deployment-ready.
