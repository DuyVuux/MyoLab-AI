# Artifact vs Physiological Variation Guidance v0.1

## 1. Purpose

This document defines the DAY04 review boundary for MotionLab sEMG quality assessment. It is a **data-quality interpretation guide**, not a diagnostic guideline and not a signal-cleaning recipe.

The central rule is:

> An atypical sEMG waveform is not automatically an acquisition artifact, and a patient/pathology/body-habitus context is never by itself a reason to label a signal as noise.

## 2. Source-derived definitions

The SRS baseline defines:

- **Artifact**: a measurement/noise problem supported by rule/model/evidence; it is not synonymous with pathology.
- **Physiological variation**: signal difference that may reflect physiology, pathology, or muscle state and must not be automatically removed.
- **Quality gate**: determines whether data support the next processing/metric step.
- **Abstention**: the system does not force a metric/interpretation when evidence is insufficient.

The PRD specifically warns that stroke, paralysis/paresis, muscle atrophy and body habitus can make sEMG harder to process. This is a reason for safer evidence handling, **not** a reason to normalize the waveform toward a healthy template.

## 3. Four-layer reasoning model

### Layer A — Measurement fact
What is directly observed or computed without clinical interpretation?

Examples:
- samples are missing;
- timestamps have a gap;
- a channel reaches a device-dependent limit, if that limit is known;
- a spectral indicator contains a narrow-band component;
- a channel differs strongly from neighboring/repeated observations.

### Layer B — Acquisition-artifact hypothesis
Does the measurement fact support a measurement-quality explanation?

Examples:
- suspected dropout;
- suspected clipping/saturation;
- suspected power-line interference;
- suspected motion/low-frequency contamination;
- suspected poor contact.

Use **suspected** unless the required acquisition evidence is sufficient.

### Layer C — Physiological-variation possibility
Could the signal difference plausibly be physiological/pathological/state-related rather than a measurement failure?

DAY04 does not diagnose the cause. It only prevents the QC layer from erasing potentially meaningful signal.

This state is **not a diagnosis**; it is an evidence-preservation and review state.

### Layer D — Clinical interpretation
This is outside autonomous QC. A clinician may interpret evidence using patient context and the complete clinical workflow. DAY04 does not automate that conclusion.

## 4. Decision matrix

| Situation | QC handling | Allowed output | Forbidden shortcut |
|---|---|---|---|
| Missing/dropout is directly observed | Record data-integrity reason | Typed reason + affected scope | Calling missing data “normal” |
| Device limit is known and clipping evidence is convincing | Artifact candidate may be raised | `CLIPPING_SATURATION_SUSPECTED` + evidence | Inferring pathology |
| Low-frequency energy appears during movement | Keep ambiguity unless protocol/evidence is sufficient | `LOW_FREQUENCY_CONTAMINATION_SUSPECTED` or `ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED` | Automatically high-pass/remove and call it artifact |
| Atypical low-amplitude/morphology in a complex clinical case | Preserve raw and context | `PHYSIOLOGICAL_VARIATION_POSSIBLE` or unresolved review | Calling stroke/atrophy/body habitus “noise” |
| Poor contact is suspected but not confirmed | Review | `POOR_CONTACT_SUSPECTED` + evidence status | Converting channel abnormality into disease label |
| Evidence cannot separate artifact from physiology | Review/abstain | `ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED` + `CLINICIAN_REVIEW_REQUIRED` | Forced cleanup or confident result |

## 5. Context tags are not QC-failure reason codes

The following are **context**, not measurement-artifact labels:

- stroke context;
- paralysis/paresis context;
- muscle-atrophy context;
- high-adiposity/body-habitus context;
- low-mass/body-habitus context.

They may change interpretation, protocol design, expected amplitude, electrode placement difficulty or confidence, but they are insufficient alone to produce `FAIL`.

## 6. PASS / WARNING / FAIL semantics

### PASS
No typed reason requiring warning/failure is present at the evaluated scope under the currently approved policy.

PASS does **not** mean “normal patient” and does **not** mean “no pathology”. It only means the data-quality gate has not found a blocking/warning condition under its supported rules.

### WARNING
Evidence is ambiguous, one or more channels/windows need review, or a policy-defined non-blocking quality concern exists.

WARNING should route to review; it should not be silently auto-cleaned.

### FAIL
A versioned policy and evidence support blocking specific downstream metrics/capabilities. FAIL is a data-supportability decision, not a clinical diagnosis.

## 7. Threshold policy for DAY04

No numerical clinical/site QC threshold is frozen in DAY04.

The SRS explicitly states FR-030..040 are capability requirements rather than fixed medical thresholds. Thresholds require site/protocol evidence and clinician approval. Therefore the taxonomy stores `TBD`, `NOT_VERIFIED` or `POLICY_DEPENDENT` where needed.

## 8. Provenance required for a reason

A reviewable reason record should contain:

- reason code;
- scope (`SESSION`, `CHANNEL`, `WINDOW`);
- target reference;
- signal-quality state;
- semantic class;
- evidence status;
- evidence references;
- rule/detector/config version when applicable;
- threshold/reference status when applicable;
- technical action suggestion when justified;
- limitation text for unresolved evidence.

## 9. Technical actions versus clinical recommendations

Allowed technical suggestions include:

- inspect channel/electrode setup;
- inspect raw data;
- confirm device/acquisition metadata;
- route to review;
- consider remeasurement under approved workflow;
- block only affected unsupported metrics.

DAY04 does not issue treatment, exercise-load or diagnostic recommendations.

## 10. Examples

### Example 1 — Missing interval
**Fact:** samples are absent in a time interval.  
**Reason:** `MISSING_DROPOUT`.  
**Clinical claim:** none.  
**Disposition:** policy-dependent based on affected duration/metric; DAY04 does not invent the threshold.

### Example 2 — Atypical channel in a post-stroke context
**Fact:** channel morphology/amplitude differs from other observations.  
**Context:** stroke is documented.  
**Evidence gap:** no acquisition defect is established.  
**Reason:** `PHYSIOLOGICAL_VARIATION_POSSIBLE` or `ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED`.  
**Forbidden:** “stroke signal is noise; delete window.”

### Example 3 — Suspected movement contamination
**Fact:** low-frequency contamination indicator is elevated.  
**Evidence:** task contains movement.  
**Reason:** `LOW_FREQUENCY_CONTAMINATION_SUSPECTED`; if physiology cannot be excluded, also unresolved/review.  
**Forbidden:** universal hard-coded cutoff presented as site-validated.

## 11. Boundary with future days

DAY04 designs taxonomy and typed reason semantics. It does **not** implement validated detectors or thresholds. Later QC days must use synthetic controlled artifacts plus expert-annotated real windows and sensitivity/error analysis before site claims are made.

## 12. Upstream limitation

The packaged DAY03 handoff contains no reviewed baseline-eligible site observation. Therefore DAY04 can be technically designed and tested, but its closeout cannot truthfully claim that DAY03 was accepted or that the taxonomy has been reviewed against real MotionLab observations.
