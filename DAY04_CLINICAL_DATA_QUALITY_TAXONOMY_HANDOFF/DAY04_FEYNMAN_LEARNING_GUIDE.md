# DAY04 Feynman Learning Guide — Artifact vs Physiological Variation in sEMG

## 1. The one-sentence idea

A QC system should answer **“Can I trust this measurement for this downstream calculation?”**, not **“Is this patient normal?”**.

## 2. Why sEMG makes this hard

Surface EMG is measured through skin and electrodes. The recorded waveform depends on both the biological source and the acquisition path. A strange waveform can therefore come from:

1. a true measurement problem;
2. a real physiological/pathological difference;
3. both at the same time;
4. insufficient evidence to decide.

The dangerous shortcut is to call every unusual signal “noise”. In MotionLab, complex patients are exactly the population for which that shortcut is unsafe.

## 3. Four boxes to remember

### Box A — Measurement fact
What did we actually observe?

Examples: missing samples, a flat plateau, a narrow spectral component, an unusual channel.

### Box B — Artifact hypothesis
Can the fact be explained by the measurement system?

Examples: dropout, clipping, poor contact, movement contamination.

### Box C — Physiological variation possibility
Could the waveform be biologically meaningful?

DAY04 does not diagnose it. It preserves that possibility.

### Box D — Clinical interpretation
A clinician combines signal evidence with history, examination, task and other modalities. QC must not impersonate this layer.

## 4. A simple analogy

Imagine a microphone recording a singer.

- cable disconnected → measurement problem;
- fan hum → environmental interference;
- singer has a naturally unusual voice → real source variation;
- distorted sound but you do not know whether it came from the microphone or singer → ambiguity.

Deleting every unusual sound would destroy the song. sEMG QC has the same core problem, with much higher clinical stakes.

## 5. FR-030: three QC scales

### Session
“Is this recording session supportable overall?”

### Channel
“Is this muscle/channel trustworthy?”

### Window
“Is this short interval trustworthy?”

A session can be usable even when one window is not. This is why DAY04 reason records always carry `scope` and `target_ref`.

## 6. Missing/dropout

This is the easiest category conceptually because missing samples are a measurement fact. But the **severity threshold** is still protocol/metric dependent.

A 5 ms gap and a 5 s gap are not equivalent. DAY04 defines the reason code; it does not invent the acceptable duration.

## 7. Clipping/saturation

Clipping means the acquisition chain cannot represent the true amplitude and the waveform is limited by hardware/software range.

But to claim clipping confidently, you need acquisition/ADC evidence. A flat-looking waveform alone is not sufficient in every system.

Therefore DAY04 uses `CLIPPING_SATURATION_SUSPECTED` and keeps device-dependent details `NOT_VERIFIED` when absent.

## 8. Baseline/noise level

“Noise level high” only makes sense relative to a protocol/reference. Without the protocol, a universal number would be a hidden assumption.

So:

`BASELINE_NOISE_ELEVATED` requires reference provenance, while the threshold remains `TBD` until approved.

## 9. Power-line interference

The concept is stable: electrical mains can introduce narrow-band interference. But DAY04 does not freeze site frequency, detector formula or threshold. Those belong to later detector design/site validation.

## 10. Motion artifact / low-frequency contamination

Movement can contaminate sEMG, especially around electrode-skin/cable mechanics. But low-frequency energy can also coexist with real physiological/task-related changes.

Therefore:

- indicator evidence → `LOW_FREQUENCY_CONTAMINATION_SUSPECTED`;
- unresolved cause → `ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED`;
- raw is preserved.

## 11. Poor contact/channel abnormality

FR-036 is deliberately cautious: flag suspected poor contact/channel abnormality and **do not turn it into pathology**.

That wording is important. QC is allowed to say “this channel needs review.” It is not allowed to say “this waveform proves disease.”

## 12. Why stroke/atrophy/body habitus are context, not noise labels

These contexts can change acquisition difficulty and waveform characteristics. But they are properties of the case, not proof of measurement failure.

Correct logic:

`clinical context + signal evidence + acquisition evidence → cautious QC/review`

Wrong logic:

`stroke → noisy signal → delete`

## 13. PASS does not mean healthy

This is one of the most important ideas.

`PASS` means: under the current supported QC policy, no quality reason requires warning/failure.

It does **not** mean:
- healthy patient;
- normal muscle;
- no fatigue;
- no disease.

## 14. WARNING does not mean abnormal diagnosis

WARNING means the data need review or have a non-blocking quality concern. It routes attention; it does not issue a clinical conclusion.

## 15. FAIL means unsupported downstream computation

When QC FAIL blocks a metric, the statement is:

> “This data does not support this downstream calculation under the current validated policy.”

It is not:

> “The patient has an abnormal condition.”

## 16. Why reason codes matter

Without reason codes:

`FAIL`

is not auditable.

With reason codes:

`FAIL + QUALITY_BLOCKED + target window + underlying evidence + config version`

is reviewable, reproducible and safer.

## 17. Evidence status and QC status are different axes

A reason can be:

- `signal_quality = WARNING`
- `evidence_status = UNKNOWN`

That means “the system is warning because the cause is unresolved.”

Do not mix evidence certainty with quality disposition.

## 18. Thresholds are not taxonomy

Taxonomy answers **what kind of issue is this?**

Threshold answers **when is the issue severe enough to change disposition?**

DAY04 defines the first and explicitly leaves many instances of the second for later site validation.

## 19. Provenance

A QC reason without provenance becomes impossible to reproduce later.

Minimum mental model:

`reason = code + scope + target + evidence + config/version + limitation`

## 20. Synthetic tests versus site validation

Synthetic tests prove contract logic:

- physiology-only reason does not become FAIL;
- ambiguity becomes WARNING;
- blocking reason becomes FAIL;
- invalid objects fail schema validation.

Synthetic tests do **not** prove sensitivity/specificity on MotionLab patients.

## 21. Example: post-stroke atypical channel

Observation: amplitude/morphology is unusual.

Question 1: Is there evidence of dropout/clipping/contact failure?  
If no → do not call artifact.

Question 2: Could clinical context/physiology explain it?  
Possibly → preserve.

Question 3: Can we distinguish cause now?  
If no → unresolved + review.

## 22. Example: visible missing segment

Observation: samples are absent.

Reason: `MISSING_DROPOUT`.

What DAY04 still does not know: how much missing data invalidates each future metric. That is policy/validation work.

## 23. Example: suspected clipping

Observation: repeated plateaus near a candidate limit.

If device range is unknown, evidence is incomplete. Use suspected/not-verified semantics rather than a confident assertion.

## 24. Common beginner mistake: “cleaner looks better”

A smoother waveform can look aesthetically better while being scientifically worse if meaningful physiology was removed.

Signal processing quality is not visual prettiness.

## 25. Common beginner mistake: one universal pipeline

Complex protocols and patients may require different eligibility and QC policies. This is why later preprocessing is profile-specific and versioned.

## 26. Common beginner mistake: reference healthy waveform as ground truth

Healthy reference data can help engineering, but it cannot define every difference in a pathological patient as artifact.

## 27. Common beginner mistake: hard-code threshold early

A threshold copied from a paper may use different electrodes, hardware, sampling rate, task and population. DAY04 marks those values as not site-validated unless evidence supports them.

## 28. The role of clinician review

Review is not a failure of automation. In clinical software, **correct abstention and exception routing are part of successful automation**.

## 29. What DAY04 actually implements

- taxonomy;
- typed reason schema;
- deterministic aggregation semantics;
- review guidance;
- synthetic contract tests.

It does not implement clinically validated detectors.

## 30. What comes later

Later QC work must add:

- controlled synthetic artifact tests;
- expert-annotated real windows;
- detector sensitivity/error analysis;
- versioned threshold/config decisions;
- retrospective validation.

## 31. Mental checklist

Before labeling a signal artifact, ask:

1. What is the measurement fact?
2. What acquisition evidence supports artifact?
3. Could physiology explain it?
4. Is the cause unresolved?
5. What scope is affected?
6. Which downstream metric is unsupported?
7. Which version/config produced the reason?
8. Do we need clinician review?

## 32. Counterexample

Bad:

“Patient has stroke, channel amplitude is low, therefore signal quality FAIL.”

Good:

“Low/atypical amplitude is observed. No confirmed acquisition defect is available. Preserve raw; mark physiological variation possible or unresolved; clinician/technical review if the downstream metric depends on this evidence.”

## 33. Self-check questions

1. Why is pathology not a synonym for noise?
2. Why can PASS coexist with an abnormal clinical condition?
3. What makes `QUALITY_BLOCKED` different from diagnosis?
4. Why is a threshold not frozen in DAY04?
5. When should `ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED` be used?
6. Why must context tags stay separate from QC-failure reason codes?

## 34. Answers

1. Pathology may create real physiological signal differences; noise/artifact is a measurement-quality concept.
2. PASS concerns data supportability under QC policy, not clinical normality.
3. QUALITY_BLOCKED limits unsupported computation; diagnosis interprets patient condition.
4. Site/protocol/device evidence and clinician approval are still required.
5. When evidence cannot safely distinguish acquisition artifact from physiology.
6. Because context modifies interpretation but does not prove measurement failure.

## 35. Teach-back exercise

Explain to a teammate in two minutes:

> “Why would a safe sEMG system sometimes keep a strange waveform instead of cleaning it automatically?”

A correct answer must mention measurement evidence, possible physiology, raw preservation, uncertainty/review and downstream eligibility.
