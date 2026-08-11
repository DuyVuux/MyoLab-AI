
# MotionLab Data Intelligence — Feynman Learning Guide — Motion-Artifact / Low-Frequency Contamination Indicator

> **Day:** DAY27
> **Phase:** Phase 2 — sEMG Quality Intelligence Foundation
> **Architecture:** DAY21 LabelingFunctionOutput + DAY22 WindowIdentity
> **Safety:** raw immutable · weak-label candidate only · preserve physiology · DAY30 aggregation deferred
> **Status:** Engineering handoff; site/expert validation not claimed

## Learning objectives
By the end, a junior engineer should explain what the detector measures, what it cannot infer, why WindowIdentity matters, how a weak label differs from truth, and how to debug false-allow versus false-block without altering raw physiology.

## Mental model
Think of DAY22 as the coordinate grid, DAY21 as the grammar, and today's detector as one witness. A witness reports evidence about one window; it does not sentence the whole session. DAY30 is the jury for deterministic aggregation, while later clinician annotation provides a higher evidence tier.

## Concept — Low-frequency contamination
### Simple explanation
Low-frequency contamination is used only to turn an observable property of a fixed DAY22 window into reviewable evidence.
### Analogy
A laboratory alarm is like a smoke sensor: it can report a pattern associated with smoke, but it cannot prove why the smoke exists or whether the building is unusable.
### Limits of the analogy
Physiological sEMG is non-stationary and context-dependent; unlike a simple smoke sensor, the same numerical pattern can have multiple acquisition or physiological causes.
### Formal technical model
Let the immutable core window be `x[n]`, `n ∈ [s,e)`, with native sample rate `Fs`. The detector computes a deterministic evidence vector `phi(x, Fs, config)` and maps it to a weak candidate. No operation may replace `x`, change `Fs`, or manufacture missing context.
### MotionLab example
A stroke or paresis session can produce low activation or unusual spectral content for physiological reasons. Therefore detector evidence must remain separate from pathology interpretation.
### Counterexample
If an engineer sees an unusual feature and immediately writes `session=FAIL`, the evidence hierarchy has collapsed and the design violates DAY21/22 and DAY30 boundaries.
### Teach-back
Explain in your own words why this concept can produce a useful warning without becoming clinical ground truth.

## Concept — Baseline excursion
### Simple explanation
Baseline excursion is used only to turn an observable property of a fixed DAY22 window into reviewable evidence.
### Analogy
A laboratory alarm is like a smoke sensor: it can report a pattern associated with smoke, but it cannot prove why the smoke exists or whether the building is unusable.
### Limits of the analogy
Physiological sEMG is non-stationary and context-dependent; unlike a simple smoke sensor, the same numerical pattern can have multiple acquisition or physiological causes.
### Formal technical model
Let the immutable core window be `x[n]`, `n ∈ [s,e)`, with native sample rate `Fs`. The detector computes a deterministic evidence vector `phi(x, Fs, config)` and maps it to a weak candidate. No operation may replace `x`, change `Fs`, or manufacture missing context.
### MotionLab example
A stroke or paresis session can produce low activation or unusual spectral content for physiological reasons. Therefore detector evidence must remain separate from pathology interpretation.
### Counterexample
If an engineer sees an unusual feature and immediately writes `session=FAIL`, the evidence hierarchy has collapsed and the design violates DAY21/22 and DAY30 boundaries.
### Teach-back
Explain in your own words why this concept can produce a useful warning without becoming clinical ground truth.

## Concept — Transient movement energy
### Simple explanation
Transient movement energy is used only to turn an observable property of a fixed DAY22 window into reviewable evidence.
### Analogy
A laboratory alarm is like a smoke sensor: it can report a pattern associated with smoke, but it cannot prove why the smoke exists or whether the building is unusable.
### Limits of the analogy
Physiological sEMG is non-stationary and context-dependent; unlike a simple smoke sensor, the same numerical pattern can have multiple acquisition or physiological causes.
### Formal technical model
Let the immutable core window be `x[n]`, `n ∈ [s,e)`, with native sample rate `Fs`. The detector computes a deterministic evidence vector `phi(x, Fs, config)` and maps it to a weak candidate. No operation may replace `x`, change `Fs`, or manufacture missing context.
### MotionLab example
A stroke or paresis session can produce low activation or unusual spectral content for physiological reasons. Therefore detector evidence must remain separate from pathology interpretation.
### Counterexample
If an engineer sees an unusual feature and immediately writes `session=FAIL`, the evidence hierarchy has collapsed and the design violates DAY21/22 and DAY30 boundaries.
### Teach-back
Explain in your own words why this concept can produce a useful warning without becoming clinical ground truth.

## Concept — Physiology preservation
### Simple explanation
Physiology preservation is used only to turn an observable property of a fixed DAY22 window into reviewable evidence.
### Analogy
A laboratory alarm is like a smoke sensor: it can report a pattern associated with smoke, but it cannot prove why the smoke exists or whether the building is unusable.
### Limits of the analogy
Physiological sEMG is non-stationary and context-dependent; unlike a simple smoke sensor, the same numerical pattern can have multiple acquisition or physiological causes.
### Formal technical model
Let the immutable core window be `x[n]`, `n ∈ [s,e)`, with native sample rate `Fs`. The detector computes a deterministic evidence vector `phi(x, Fs, config)` and maps it to a weak candidate. No operation may replace `x`, change `Fs`, or manufacture missing context.
### MotionLab example
A stroke or paresis session can produce low activation or unusual spectral content for physiological reasons. Therefore detector evidence must remain separate from pathology interpretation.
### Counterexample
If an engineer sees an unusual feature and immediately writes `session=FAIL`, the evidence hierarchy has collapsed and the design violates DAY21/22 and DAY30 boundaries.
### Teach-back
Explain in your own words why this concept can produce a useful warning without becoming clinical ground truth.

## Worked examples
### Example 1
Synthetic 2-Hz baseline drift raises low-frequency/drift evidence and produces a review warning.
### Example 2
Slow 8-Hz activity can be task-related; the detector does not hard FAIL it.
### Example 3
A movement transient is detected from robust derivative evidence while the original raw array remains byte-equivalent.

## Counterexamples and junior mistakes
1. Creating a new `window_id` from floating timestamps. 2. Filtering raw before measuring the artifact. 3. Treating a weak rule score as calibrated probability. 4. Converting UNKNOWN into PASS. 5. Using one healthy-derived threshold across clinical protocols. 6. Letting one detector block the session before DAY30/31. 7. Calling synthetic fixture truth clinical validation. 8. Editing the shared registry instead of applying a reviewed delta.

## Debugging thought process
Start with contracts, not plots. Check exact `window_id`, sample bounds, native Fs, config version and context status. Then reproduce the evidence metric. Next ask whether another physiological explanation exists. Finally verify serialization and raw immutability. Never "fix" a failing test by making the detector more confident than the evidence permits.

## What not to learn yet
Do not spend this day on Transformers, deep anomaly detection, learned OOD scores, automated denoising, model calibration, conformal prediction, or final clinical thresholds. Those are not needed to satisfy today's acceptance criteria and can create scope/safety debt.

## Flashcards
- **Q:** What owns temporal identity? **A:** DAY22 WindowIdentity.
- **Q:** What owns weak-label grammar? **A:** DAY21 LabelingFunctionOutput.
- **Q:** Can detector output be ground truth? **A:** No.
- **Q:** Can it be expert label? **A:** No.
- **Q:** What if evidence is insufficient? **A:** ABSTAIN/UNKNOWN.
- **Q:** Can raw be edited? **A:** No.
- **Q:** Can native Fs be changed? **A:** No.
- **Q:** Who owns final aggregation? **A:** DAY30.
- **Q:** Who owns metric blocking? **A:** DAY31.
- **Q:** Does WARNING mean pathology? **A:** No.
- **Q:** Does unusual spectrum mean unusable? **A:** Not necessarily.
- **Q:** Why version config? **A:** Replay/audit.
- **Q:** Why exact window_id? **A:** Cross-detector alignment.
- **Q:** What is false allow? **A:** Bad evidence allowed as good.
- **Q:** What is false block? **A:** Usable/physiological data incorrectly blocked.
- **Q:** Why preserve context? **A:** Avoid misreading isolated waveform crops.
- **Q:** Can synthetic truth validate clinic? **A:** No.
- **Q:** What is evidence provenance? **A:** Rule/config/registry/window references.
- **Q:** What is Option B delta? **A:** Day-owned change reconciled into shared registry.
- **Q:** Why no auto-clean? **A:** It can destroy the evidence and physiology.
- **Q:** Why deterministic? **A:** Same input/config must replay.
- **Q:** Why typed failures? **A:** No silent fallback.
- **Q:** Can one LF decide session? **A:** No.
- **Q:** What is Preserve Physiology? **A:** Do not normalize pathology into healthy-looking signal.
- **Q:** Next aggregation milestone? **A:** DAY30.

## Exercises
### Beginner 1
Given a WindowIdentity, list the exact sample indices a detector may read.
### Beginner 2
Write an ABSTAIN candidate when required context is unknown.
### Beginner 3
Explain why a PASS_CANDIDATE is weaker than final PASS.
### Intermediate 1
Design a negative test proving raw samples are bitwise unchanged.
### Intermediate 2
Create two plausible explanations for the same suspicious feature and decide what supportability should be.
### Integration exercise
Trace one window from DAY22 → detector → DAY21 candidate → future DAY30 aggregation, naming what each layer is allowed and forbidden to do.

## Quiz
1. Can a detector invent a new window ID?
2. Can it resample to simplify FFT?
3. Does candidate confidence equal calibrated probability?
4. Who owns final session state?
5. What does `ground_truth_claim=false` protect?
6. When should a detector abstain?
7. Why retain native samples?
8. Why do site/config unknowns remain explicit?
9. Why are weak labels useful?
10. Why are weak labels risky?
11. What is a false-block scenario?
12. What is a false-allow scenario?
13. Why reconcile registry deltas?
14. Can synthetic fixtures establish clinical performance?
15. What is the next safe handoff?

## Answers
1 No. 2 No. 3 No. 4 DAY30. 5 It prevents detector evidence from masquerading as reference truth. 6 When input/context cannot support the rule. 7 For provenance and physiology preservation. 8 To prevent silent guesses. 9 They cheaply prioritize/review evidence. 10 They can be biased/correlated. 11 Blocking true physiological variation. 12 Missing a real acquisition artifact. 13 To preserve Option-B shared source-of-truth. 14 No. 15 Carry candidate evidence and limitations forward without expanding authority.

## Final teach-back gate
Without notes, explain the detector to a clinician and to a software engineer. The clinician explanation must avoid causal/diagnostic overclaim. The engineering explanation must include exact WindowIdentity linkage, read-only sample slice, configuration version, candidate serialization and failure semantics. If either explanation implies automated cleaning or final session decision, revisit the guide.

## Readiness checklist
- [ ] I can distinguish evidence from pathology.
- [ ] I can explain ABSTAIN/UNKNOWN.
- [ ] I know why raw is immutable.
- [ ] I can trace a candidate to the exact DAY22 window.
- [ ] I can explain why final aggregation is deferred.
- [ ] I can identify site assumptions that remain NOT_VERIFIED.


## Deep DSP reasoning: low frequency is evidence, not a diagnosis

Surface EMG can contain low-frequency energy for many reasons: electrode/cable movement, changing skin-electrode impedance, baseline drift, voluntary slow contractions, movement-related modulation, task transitions, and clinical motor patterns. The mathematical observation “a large fraction of energy lies below 15 Hz” is therefore not identical to the semantic claim “motion artifact.” DAY27 deliberately keeps those layers separate.

The implementation calculates three complementary features. First, low-frequency band-power ratio summarizes slow spectral energy relative to the available analysis band. Second, a normalized baseline slope describes large excursions over the window while scaling by a robust amplitude estimate. Third, a transient derivative score catches sudden movement-like changes that may not dominate the entire PSD. Using multiple evidence features improves reviewability, but correlated evidence must not be treated as independent votes. DAY34/35 later address agreement and threshold evidence.

### Why robust scale matters
A slope of 0.1 units/second can be enormous for one channel and negligible for another. Normalizing by a robust within-window scale makes the engineering statistic less dependent on absolute amplitude. Median absolute deviation is resistant to isolated spikes compared with standard deviation. This does not make the threshold universal; it only improves numerical behavior.

### Why no high-pass cleaning
A high-pass filter could make a suspicious window look cleaner, but it changes the very waveform a clinician may need to inspect. It can also remove genuine slow physiological modulation. DAY27 therefore performs feature extraction without replacing the raw array. Later processing profiles may include approved high-pass/band-pass transforms, but they must preserve pre-filter QC evidence and provenance.

### Ambiguous slow voluntary activity
Imagine a patient with slow, sustained activation where movement or neurological impairment produces substantial low-frequency modulation. The detector may cross an engineering threshold although the signal is meaningful. The correct DAY27 behavior is a review warning with limited evidence strength, not a hard fail and certainly not an “artifact removed” result. This is the practical meaning of Preserve Physiology.

### False-allow and false-block
False allow means a severe acquisition artifact is not surfaced. False block means a real physiological pattern is treated as invalid acquisition. In clinical sEMG the second error can be especially damaging because the system could erase evidence from the very populations MotionLab cares about. Therefore DAY27 is deliberately conservative about causal claims and final blocking.

### Synthetic injection limits
Synthetic drift/transients are valuable because their injected truth is known exactly, enabling regression tests. But synthetic waveforms do not capture all electrode mechanics or patient physiology. Passing synthetic tests establishes engineering correctness, not clinical sensitivity/specificity. Expert windows remain necessary later in Phase 2.

## Reproducibility walkthrough

A reproducible detector invocation is fully determined by: the exact DAY22 `window_id`, source/session/channel identity embedded in that window, native sample values in the core range, native sampling rate, detector configuration version, LF rule version, and registry version. If any of these change, comparison should be treated as a new evidence computation rather than silently reusing the prior result.

The first evidence reference is always the canonical window ID. Additional evidence references in these engineering implementations encode compact metric summaries for testability; a production evidence store may later replace those strings with immutable evidence-object IDs without changing the window linkage contract.

## Failure-mode matrix

| Failure / ambiguity | Safe behavior | Unsafe behavior |
|---|---|---|
| Window exceeds raw bounds | typed failure | truncate silently |
| Insufficient samples | ABSTAIN | PASS by default |
| Non-finite core samples | ABSTAIN / explicit reason | replace/interpolate |
| Site/reference metadata unknown | UNKNOWN/ABSTAIN | infer common default |
| Suspicious evidence with plausible physiology | WARNING/UNKNOWN + review | causal artifact diagnosis |
| Detector warning | candidate only | final session FAIL |
| Synthetic fixture PASS | engineering evidence only | clinical-valid claim |

## Troubleshooting playbook

When a test unexpectedly changes candidate label, first print the exact WindowIdentity boundaries and realized duration. Second verify native Fs and detector config. Third recompute the intermediate evidence statistic with the same window. Fourth check whether the threshold is engineering provisional or site verified. Fifth inspect whether a context field was missing and should have triggered abstention. Only after those checks should the rule itself be modified. Never tune a threshold merely to make a single fixture pass.

When a clinician disagrees with a candidate, preserve the disagreement. Do not overwrite the detector result. Later annotation/adjudication stages need both the original machine evidence and the expert outcome to measure false allow, false block, rule coverage and correlated labeling-function errors.

## Architecture boundary with Active Learning

DAY26–28 make windows richer candidates for later annotation acquisition, but they do not choose which windows clinicians must label. DAY32 defines acquisition policy and DAY33 executes the first real clinician-annotated window round. A detector warning can become one input to acquisition priority, but not the sole priority rule; otherwise the annotation set would become biased toward the detector's existing blind spots and assumptions.

## Architecture boundary with DAY29–31

DAY29 adds integrity/synchronization supportability and begins Distribution/OOD readiness inputs. DAY30 aggregates detector evidence deterministically across window/channel/session. DAY31 defines blocking, abstention and metric handoff. Today's detector must remain small enough that each later layer can change policy without rewriting raw evidence. This separation is what makes QC versionable and auditable.


## Advanced reasoning workshop — Motion Artifact / Low-Frequency Contamination

### 1. Measurement fact, engineering inference, clinical interpretation
A reliable QC system must keep three semantic layers separate. A measurement fact is directly reproducible from the immutable samples and configuration: for example a band-power ratio, a baseline slope, or a target-to-peer RMS ratio. An engineering inference is the detector's rule-based mapping from those measurements to a candidate label such as `WARNING_CANDIDATE` or `UNKNOWN`. A clinical interpretation asks what the observed pattern means for the patient, task or diagnosis. DAY27 is authorized to perform the first two layers only. The third layer belongs to clinician review and later evidence workflows. This separation is not bureaucracy; it is what makes disagreement measurable. If the clinician disagrees, we can inspect whether the measurement was wrong, the rule was too broad, or the clinical context changed the meaning.

### 2. Why candidate labels must remain reversible
A candidate should be cheap to regenerate from source evidence. The raw waveform remains immutable, the WindowIdentity is deterministic, and detector configuration is versioned. Therefore a future threshold change can replay the same window and produce a new candidate without losing the old evidence. If the detector instead modified raw data or stored only a final PASS/FAIL, threshold migration would become impossible to audit. Reversibility also protects the project during site calibration: engineering thresholds can be replaced by site-validated thresholds while retaining the original evidence and version history.

### 3. Thresholds are policy inputs, not natural constants
Many signal-processing textbooks present convenient frequency bands or numerical thresholds. Those values are useful starting points for engineering tests but they do not automatically become MotionLab clinical thresholds. Window duration, sampling rate, sensor characteristics, electrode placement, protocol, pathology and preprocessing history all affect feature distributions. The correct lifecycle is: engineering provisional threshold → synthetic analytical verification → expert-window review → error analysis → evidence-gated threshold freeze. DAY35 is where threshold configuration is intentionally revisited. A junior engineer should therefore resist the urge to encode a number as if it were universal merely because a fixture passes.

### 4. Window duration changes what the detector can know
A 250-ms window and a 1-s window do not provide equivalent evidence. Spectral resolution improves with longer windows, but long windows can mix multiple task phases or transient artifacts. Short windows localize events but produce coarse frequency bins and more variable statistics. DAY22 deliberately made windowing profile-specific and versioned. DAY27 must consume the realized duration and native sample grid rather than assuming every window has the same number of samples. This is especially important when channels have heterogeneous sampling rates. The same requested duration can yield different sample counts, and the detector must remain correct without resampling.

### 5. Context prevents false certainty
The core window is where the numerical detector operates, but DAY22 preserves surrounding context because waveform meaning is temporal. A transient at the exact start of voluntary contraction may look suspicious in an isolated crop. A low-amplitude channel during a task where the muscle should be inactive may be completely expected. A narrow-band component may occur during a specific device state. The detector should not secretly use context it does not receive, but the evidence object must remain linked to a context-preserving annotation unit so later reviewers can inspect what happened around the core region.

### 6. Weak-supervision correlation problem
By DAY28 the project has several labeling functions: dropout, flatline, clipping, baseline noise, power-line, motion artifact and channel abnormality. Their outputs are not statistically independent. For example poor contact may simultaneously increase baseline noise and power-line susceptibility; motion artifact may also increase low-frequency power and baseline excursion. Counting each warning as an independent vote would overstate evidence. This is why DAY30 separates raw detector evidence from provisional weak labels and policy decisions, while DAY34/35 later examine agreement, correlations and thresholds. DAY27 should therefore emit provenance-rich evidence, not a synthetic “confidence probability” that pretends independence.

### 7. What deterministic means in this project
Determinism is stronger than “usually produces the same plot.” With the same raw bytes, same WindowIdentity, same native sampling rate, same configuration/rule/registry versions and same runtime numerical assumptions, the detector output should be identical within explicitly defined numerical serialization behavior. Random seeds are only appropriate for synthetic fixture generation, not production detector decisions. Determinism enables regression testing and allows a clinician-reviewed historical window to be re-evaluated after a software update. If results change, the change must be attributable to a versioned artifact rather than hidden state.

### 8. Failure must remain visible
A malformed input, unsupported shape, missing context or insufficient sample count should not disappear into a default PASS. Typed failure is appropriate when the input violates a contract; ABSTAIN/UNKNOWN is appropriate when the input is structurally valid but evidence is insufficient. This distinction matters operationally. A contract failure may indicate ingestion or software defects; an abstention may simply indicate that the current detector cannot support a conclusion for that window. Both are safer than silent fallback, but they imply different remediation paths.

## Case-study drill
Consider a de-identified lower-limb session with four channels. One channel has low activation, intermittent 50-Hz energy and a slow baseline excursion during a gait transition. The safe reasoning sequence is not “three detectors warned, therefore bad electrode.” First, each detector records its own measurement and candidate against the same WindowIdentity. Second, the reviewer checks whether the transition and pathology make low-frequency or low-amplitude behavior plausible. Third, acquisition evidence such as contact/impedance or repeated dropout can raise suspicion. Fourth, DAY30 later aggregates status deterministically, and DAY31 decides whether any downstream metric is blocked. The raw channel remains available throughout.

Now reverse the scenario: a healthy synthetic fixture has a strong injected artifact and every detector produces the expected warning. This demonstrates that the code can detect the engineered feature, but it still does not prove clinical sensitivity on MotionLab patients. Synthetic truth answers “did our algorithm respond to the perturbation we inserted?” Clinical validation answers a different question: “does this detector help distinguish acquisition problems from meaningful physiology in the intended population and workflow?”

## Oral exam prompts
1. Describe one scenario where the detector measurement is correct but the candidate interpretation should remain uncertain.
2. Explain why changing window duration can change a spectral or statistical feature without any raw signal corruption.
3. Explain how two correlated labeling functions can create false confidence if their votes are naively counted.
4. Give a concrete example of a typed input failure versus an evidence abstention.
5. Explain why preserving raw evidence is necessary for threshold migration and clinician disagreement analysis.
6. State what DAY30 and DAY31 are allowed to do that DAY27 is not.

## Final readiness statement
The engineer is ready to integrate DAY27 only if they can reproduce a candidate from a specific WindowIdentity, explain every configuration parameter and evidence status, demonstrate raw immutability, identify at least one physiological counterexample, and state clearly that detector output is weak evidence rather than expert truth or a final session decision.


## Additional self-check: explain the full evidence lifecycle
A robust explanation should start before the detector runs. The source file was ingested under immutable provenance, the canonical channel retains native sampling metadata, and DAY22 creates a stable contextual window. The detector reads only the core sample interval and computes versioned evidence. DAY21 defines how that evidence becomes a weak-label candidate. The candidate is then available for later aggregation, clinician annotation and threshold review without changing the raw signal. If the engineer cannot point to each ownership boundary, the implementation is too coupled.

When reviewing a candidate, ask five questions in order: Is the source/window identity correct? Is the numerical measurement reproducible? Was every required context field known rather than guessed? Could physiology plausibly explain the same measurement? What later layer is authorized to make the decision that this detector is not? This sequence is a practical defense against overconfident QC. It shifts debugging from “the graph looks strange” to an auditable chain of contracts and evidence.

Finally, remember that a safe QC detector can be valuable even when it abstains often. Early in a clinical project, explicit uncertainty may reduce false confident automation while generating high-value review cases for DAY32–34. The goal of DAY26–28 is therefore not maximal automatic labeling coverage. The goal is trustworthy, reproducible evidence that can support later policy and expert adjudication.
