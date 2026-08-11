# DAY36 FEYNMAN LEARNING GUIDE — Preserve Physiology and Distribution Support

## 1. The simple idea
Imagine a smoke detector and a map. The smoke detector asks whether there is smoke in the room. The map asks whether you are in a familiar building. Being in a new building does not mean there is smoke. Likewise, an unusual sEMG context does not automatically mean the signal is bad. DAY36 teaches the system to keep those two questions separate.

## 2. QC versus distribution support
QC is evidence about acquisition integrity: missing samples, dropout, clipping, line noise, motion contamination, time/unit problems and corroborated poor contact. Distribution support is evidence about whether a downstream algorithm was designed/evaluated for the descriptive context: sampling rate, electrode layout, protocol, task, session/day and related axes. A clean signal from a new layout may be `SHIFTED` but not bad. A severely dropped-out signal from the reference layout may be `SUPPORTED` as a domain yet still fail QC.

## 3. Why low amplitude is dangerous conceptually
Surface EMG amplitude depends on electrode placement, tissue geometry, contraction effort, muscle recruitment, body composition and many other factors. Therefore low amplitude cannot safely be equated with poor contact or disease. DAY28 already encoded a critical invariant: low target RMS relative to peers is only poor-contact evidence when corroborating artifact evidence exists. With no corroboration, the cause remains unresolved/reviewable.

DAY36 turns that principle into a metamorphic test: start with a deterministic clean waveform, multiply it by 0.10 or 0.25, keep the acquisition metadata unchanged, and require that the system does not suddenly claim poor contact or quality block.

## 4. Metamorphic testing
Sometimes an exact output value is not the main truth. Instead we know a relationship that must hold after a controlled transformation. If x is a clean synthetic waveform and y=0.1x, then mean absolute amplitude of y must be 0.1 of x. More importantly for safety, scaling alone must not create acquisition-artifact evidence. This is a metamorphic relation.

Other relations include: changing descriptive layout metadata should change distribution-support evidence but not the raw signal-quality verdict; severe dropout should remain a quality failure regardless of whether the domain metadata matches the reference.

## 5. SHIFTED is not OOD pathology
DAY36 deliberately does not implement an OOD model. `SHIFTED` is a descriptive state meaning that at least one declared context axis differs from the current research reference. There is no learned density, distance threshold, probability or calibrated confidence. Calling a patient/pathological signal OOD merely because it differs from healthy data would be scientifically and clinically misleading.

## 6. UNKNOWN is valuable
UNKNOWN is not failure to build the system. It is an honest output when support evidence is insufficient. If optional context modality is missing, the signal may still be QC-supportable while domain support is UNKNOWN. If a future model requires that modality, DAY31 can abstain for that model; a deterministic RMS metric might not require it.

## 7. Required versus optional modality
Missing required sEMG is fundamentally different from missing optional contextual data. Required sEMG means the core evidence needed for sEMG analysis does not exist, so fail-closed behavior is correct. Optional context missing means a support question cannot be fully answered, but it must not fabricate a hard signal-quality failure.

## 8. Seven axes in this challenge
1. Amplitude scaling — physiology-preservation sentinel.
2. Signal morphology — research morphology shift, not disease.
3. Sampling rate — 1000/2000/4000 Hz context variation.
4. Electrode layout — metadata-supported layout change.
5. Protocol/task — different task semantics.
6. Session/day — longitudinal context variation.
7. Missing modality — optional versus required evidence.

## 9. Worked examples
### Example A — Low amplitude
Input: same reference signal scaled to 10%. Expected: no automatic quality block; no poor-contact claim without corroboration. Distribution may remain supported because metadata context did not change.

### Example B — New layout
Input: clean waveform, layout B. Expected: distribution SHIFTED with an explicit reason. QC remains supportable/reviewable. No diagnosis.

### Example C — Severe dropout
Input: reference-domain waveform with 40% missing samples inside the core window. Expected: QC quality failure. Distribution can remain SUPPORTED because context matching cannot rescue acquisition corruption.

### Example D — Missing optional modality
Input: sEMG exists but optional context is absent. Expected: domain support UNKNOWN, no hard quality block.

### Example E — Missing required sEMG
Input: required modality absent. Expected: fail closed for quality/integrity and support UNKNOWN.

## 10. Common junior mistakes
- Treating SHIFTED as FAIL.
- Treating UNKNOWN as PASS.
- Assigning an OOD score because a status enum exists.
- Calling amplitude-scaled synthetic data stroke/atrophy.
- Using low RMS as direct poor-contact proof.
- Letting distribution support override a DAY29/DAY30 hard QC failure.
- Forgetting that research thresholds remain non-site evidence.

## 11. What not to learn today
Do not train an OOD detector, domain classifier, autoencoder or deep embedding model. Do not tune production thresholds. Do not study diagnostic biomarkers. DAY36 is about contracts, controlled transformations and safety semantics.

## 12. Flashcards
1. Q: What does QC ask? A: Whether acquisition/data evidence is structurally supportable.
2. Q: What does distribution support ask? A: Whether a downstream algorithm has evidence for the descriptive domain.
3. Q: Is SHIFTED pathology? A: No.
4. Q: Is UNKNOWN PASS? A: No.
5. Q: Can low amplitude alone mean poor contact? A: No.
6. Q: Can domain support rescue QC FAIL? A: No.
7. Q: Does DAY36 have an OOD model? A: No.
8. Q: Does DAY36 emit OOD score? A: No.
9. Q: What is amplitude scaling called? A: Physiology-preservation stress.
10. Q: Why use metamorphic tests? A: To verify invariant relationships under controlled transformations.
11. Q: Required modality missing behavior? A: Fail closed.
12. Q: Optional context missing behavior? A: Support may be UNKNOWN without quality failure.
13. Q: What is the highest DAY36 claim? A: DOMAIN_CHALLENGE_SET_READY.
14. Q: Clinical edge-case validation status? A: NOT_PERFORMED.
15. Q: Are research thresholds site thresholds? A: No.
16. Q: Why keep raw/domain axes explicit? A: Traceability and supportability reasoning.
17. Q: What does a deterministic seed give? A: Reproducible challenge waveform.
18. Q: Should morphology shift create diagnosis? A: Never.

## 13. Exercises
### Beginner
1. Explain why a clean signal at 4000 Hz can be SHIFTED but not bad.
2. Classify missing optional video context versus missing sEMG.
3. Explain why `0.1*x` is not a simulated stroke signal.

### Intermediate
4. Design a metamorphic test for electrode-layout metadata without modifying waveform samples.
5. Give an example where QC FAIL and distribution SUPPORTED coexist.

### Integration
6. Trace a QC PASS + distribution UNKNOWN case through DAY31 for (a) deterministic RMS where support is not required and (b) a future learned model where support is required.

## 14. Quiz answers
1. New domain != bad signal.
2. Low amplitude needs corroborating acquisition evidence before poor-contact suspicion.
3. No OOD score without a validated method.
4. UNKNOWN must be surfaced explicitly.
5. Required evidence missing can block; optional evidence missing should not invent a quality failure.
6. Distribution support is orthogonal to QC.

## 15. Readiness check
You are ready for DAY37 if you can explain every challenge case using three separate concepts: evidence about signal quality, evidence about domain support, and forbidden clinical interpretation. If you cannot explain those separately, error analysis will produce misleading false-allow/false-block labels.
