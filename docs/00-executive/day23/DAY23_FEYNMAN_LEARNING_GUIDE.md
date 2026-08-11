# DAY23 Feynman Learning Guide — Controlled Artifact Fixtures: Dropout, Missing & Flatline

## Learning objectives

By the end, explain why DAY22 owns *where*, DAY23 owns *what evidence is observed*, DAY21 owns *how weak-label candidates are represented*, and DAY30 owns *final aggregation*. Explain missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete.

## Concept 1: missingness

**Simple explanation.** Treat `missingness` as one piece of evidence, not a diagnosis and not a final session decision.

**Analogy.** A laboratory warning light can tell you something deserves inspection without telling you the biological cause.

**Where the analogy breaks.** sEMG is continuous physiological measurement with protocol- and acquisition-dependent semantics; a rule may be wrong outside its validated context.

**Formal model.** Let a DAY22 window be `W=(source, channel, [i,j), context, profile_hash)`. DAY23 computes a deterministic evidence function `e=f(W, x[i:j), config)` while preserving `x`. The weak label is `L=g(e, config)` and must carry `W.window_id`. Neither `e` nor `L` is expert ground truth.

**MotionLab example.** A window can be flagged or abstained while the raw channel remains unchanged and available for clinician review.

**Counterexample.** Replacing `window_id` with a timestamp string breaks stable lineage; using a detector output as a training truth creates circular validation.

**Teach-back.** Explain in two minutes what evidence is measured, which assumptions are configuration-bound, and which conclusions remain forbidden.

## Concept 2: dropout runs

**Simple explanation.** Treat `dropout runs` as one piece of evidence, not a diagnosis and not a final session decision.

**Analogy.** A laboratory warning light can tell you something deserves inspection without telling you the biological cause.

**Where the analogy breaks.** sEMG is continuous physiological measurement with protocol- and acquisition-dependent semantics; a rule may be wrong outside its validated context.

**Formal model.** Let a DAY22 window be `W=(source, channel, [i,j), context, profile_hash)`. DAY23 computes a deterministic evidence function `e=f(W, x[i:j), config)` while preserving `x`. The weak label is `L=g(e, config)` and must carry `W.window_id`. Neither `e` nor `L` is expert ground truth.

**MotionLab example.** A window can be flagged or abstained while the raw channel remains unchanged and available for clinician review.

**Counterexample.** Replacing `window_id` with a timestamp string breaks stable lineage; using a detector output as a training truth creates circular validation.

**Teach-back.** Explain in two minutes what evidence is measured, which assumptions are configuration-bound, and which conclusions remain forbidden.

## Concept 3: non-finite samples

**Simple explanation.** Treat `non-finite samples` as one piece of evidence, not a diagnosis and not a final session decision.

**Analogy.** A laboratory warning light can tell you something deserves inspection without telling you the biological cause.

**Where the analogy breaks.** sEMG is continuous physiological measurement with protocol- and acquisition-dependent semantics; a rule may be wrong outside its validated context.

**Formal model.** Let a DAY22 window be `W=(source, channel, [i,j), context, profile_hash)`. DAY23 computes a deterministic evidence function `e=f(W, x[i:j), config)` while preserving `x`. The weak label is `L=g(e, config)` and must carry `W.window_id`. Neither `e` nor `L` is expert ground truth.

**MotionLab example.** A window can be flagged or abstained while the raw channel remains unchanged and available for clinician review.

**Counterexample.** Replacing `window_id` with a timestamp string breaks stable lineage; using a detector output as a training truth creates circular validation.

**Teach-back.** Explain in two minutes what evidence is measured, which assumptions are configuration-bound, and which conclusions remain forbidden.

## Concept 4: flatline

**Simple explanation.** Treat `flatline` as one piece of evidence, not a diagnosis and not a final session decision.

**Analogy.** A laboratory warning light can tell you something deserves inspection without telling you the biological cause.

**Where the analogy breaks.** sEMG is continuous physiological measurement with protocol- and acquisition-dependent semantics; a rule may be wrong outside its validated context.

**Formal model.** Let a DAY22 window be `W=(source, channel, [i,j), context, profile_hash)`. DAY23 computes a deterministic evidence function `e=f(W, x[i:j), config)` while preserving `x`. The weak label is `L=g(e, config)` and must carry `W.window_id`. Neither `e` nor `L` is expert ground truth.

**MotionLab example.** A window can be flagged or abstained while the raw channel remains unchanged and available for clinician review.

**Counterexample.** Replacing `window_id` with a timestamp string breaks stable lineage; using a detector output as a training truth creates circular validation.

**Teach-back.** Explain in two minutes what evidence is measured, which assumptions are configuration-bound, and which conclusions remain forbidden.

## Concept 5: synthetic known truth

**Simple explanation.** Treat `synthetic known truth` as one piece of evidence, not a diagnosis and not a final session decision.

**Analogy.** A laboratory warning light can tell you something deserves inspection without telling you the biological cause.

**Where the analogy breaks.** sEMG is continuous physiological measurement with protocol- and acquisition-dependent semantics; a rule may be wrong outside its validated context.

**Formal model.** Let a DAY22 window be `W=(source, channel, [i,j), context, profile_hash)`. DAY23 computes a deterministic evidence function `e=f(W, x[i:j), config)` while preserving `x`. The weak label is `L=g(e, config)` and must carry `W.window_id`. Neither `e` nor `L` is expert ground truth.

**MotionLab example.** A window can be flagged or abstained while the raw channel remains unchanged and available for clinician review.

**Counterexample.** Replacing `window_id` with a timestamp string breaks stable lineage; using a detector output as a training truth creates circular validation.

**Teach-back.** Explain in two minutes what evidence is measured, which assumptions are configuration-bound, and which conclusions remain forbidden.

## Concept 6: weak labels

**Simple explanation.** Treat `weak labels` as one piece of evidence, not a diagnosis and not a final session decision.

**Analogy.** A laboratory warning light can tell you something deserves inspection without telling you the biological cause.

**Where the analogy breaks.** sEMG is continuous physiological measurement with protocol- and acquisition-dependent semantics; a rule may be wrong outside its validated context.

**Formal model.** Let a DAY22 window be `W=(source, channel, [i,j), context, profile_hash)`. DAY23 computes a deterministic evidence function `e=f(W, x[i:j), config)` while preserving `x`. The weak label is `L=g(e, config)` and must carry `W.window_id`. Neither `e` nor `L` is expert ground truth.

**MotionLab example.** A window can be flagged or abstained while the raw channel remains unchanged and available for clinician review.

**Counterexample.** Replacing `window_id` with a timestamp string breaks stable lineage; using a detector output as a training truth creates circular validation.

**Teach-back.** Explain in two minutes what evidence is measured, which assumptions are configuration-bound, and which conclusions remain forbidden.

## Concept 7: mask-not-delete

**Simple explanation.** Treat `mask-not-delete` as one piece of evidence, not a diagnosis and not a final session decision.

**Analogy.** A laboratory warning light can tell you something deserves inspection without telling you the biological cause.

**Where the analogy breaks.** sEMG is continuous physiological measurement with protocol- and acquisition-dependent semantics; a rule may be wrong outside its validated context.

**Formal model.** Let a DAY22 window be `W=(source, channel, [i,j), context, profile_hash)`. DAY23 computes a deterministic evidence function `e=f(W, x[i:j), config)` while preserving `x`. The weak label is `L=g(e, config)` and must carry `W.window_id`. Neither `e` nor `L` is expert ground truth.

**MotionLab example.** A window can be flagged or abstained while the raw channel remains unchanged and available for clinician review.

**Counterexample.** Replacing `window_id` with a timestamp string breaks stable lineage; using a detector output as a training truth creates circular validation.

**Teach-back.** Explain in two minutes what evidence is measured, which assumptions are configuration-bound, and which conclusions remain forbidden.

## Worked examples

### Example 1

Input is a stable DAY22 window and native samples. First check reference/config eligibility; second compute only the day-specific evidence; third emit a DAY21 candidate or ABSTAIN/UNKNOWN; fourth verify raw bytes/samples are unchanged. The correct answer never invents clinical meaning and never sets final session quality.

### Example 2

Input is a stable DAY22 window and native samples. First check reference/config eligibility; second compute only the day-specific evidence; third emit a DAY21 candidate or ABSTAIN/UNKNOWN; fourth verify raw bytes/samples are unchanged. The correct answer never invents clinical meaning and never sets final session quality.

### Example 3

Input is a stable DAY22 window and native samples. First check reference/config eligibility; second compute only the day-specific evidence; third emit a DAY21 candidate or ABSTAIN/UNKNOWN; fourth verify raw bytes/samples are unchanged. The correct answer never invents clinical meaning and never sets final session quality.

### Example 4

Input is a stable DAY22 window and native samples. First check reference/config eligibility; second compute only the day-specific evidence; third emit a DAY21 candidate or ABSTAIN/UNKNOWN; fourth verify raw bytes/samples are unchanged. The correct answer never invents clinical meaning and never sets final session quality.

### Example 5

Input is a stable DAY22 window and native samples. First check reference/config eligibility; second compute only the day-specific evidence; third emit a DAY21 candidate or ABSTAIN/UNKNOWN; fourth verify raw bytes/samples are unchanged. The correct answer never invents clinical meaning and never sets final session quality.

### Example 6

Input is a stable DAY22 window and native samples. First check reference/config eligibility; second compute only the day-specific evidence; third emit a DAY21 candidate or ABSTAIN/UNKNOWN; fourth verify raw bytes/samples are unchanged. The correct answer never invents clinical meaning and never sets final session quality.

## Common junior mistakes

- Rebuilding window boundaries inside the detector.
- Resampling to make implementation easier.
- Treating `PASS_CANDIDATE` as final PASS.
- Treating synthetic truth as expert truth.
- Hiding a threshold without a version/evidence status.
- Using diagnosis or healthy-vs-pathology identity as a QC label.
- Deleting or replacing bad raw samples instead of masking metadata.

## Debugging thought process

When a test fails, first ask whether the failure is coordinate/contract, evidence computation, configuration, candidate mapping, or packaging. Do not immediately adjust thresholds. A threshold change is a configuration/version change and must not be used to conceal a contract bug. Verify the window ID, sample range, source length, reason-code registry, LF schema, provenance versions, and raw immutability in that order.

## What not to learn yet

No neural QC model, no label model training, no active-learning acquisition algorithm, no OOD score, no clinical diagnosis, no final aggregation, no preprocessing/filter design, and no metric extraction. Those belong to later days.

## Flashcards

1. **Q:** What is the DAY23 invariant #1? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
2. **Q:** What is the DAY23 invariant #2? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
3. **Q:** What is the DAY23 invariant #3? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
4. **Q:** What is the DAY23 invariant #4? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
5. **Q:** What is the DAY23 invariant #5? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
6. **Q:** What is the DAY23 invariant #6? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
7. **Q:** What is the DAY23 invariant #7? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
8. **Q:** What is the DAY23 invariant #8? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
9. **Q:** What is the DAY23 invariant #9? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
10. **Q:** What is the DAY23 invariant #10? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
11. **Q:** What is the DAY23 invariant #11? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
12. **Q:** What is the DAY23 invariant #12? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
13. **Q:** What is the DAY23 invariant #13? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
14. **Q:** What is the DAY23 invariant #14? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
15. **Q:** What is the DAY23 invariant #15? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
16. **Q:** What is the DAY23 invariant #16? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
17. **Q:** What is the DAY23 invariant #17? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
18. **Q:** What is the DAY23 invariant #18? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
19. **Q:** What is the DAY23 invariant #19? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
20. **Q:** What is the DAY23 invariant #20? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
21. **Q:** What is the DAY23 invariant #21? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
22. **Q:** What is the DAY23 invariant #22? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
23. **Q:** What is the DAY23 invariant #23? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
24. **Q:** What is the DAY23 invariant #24? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.
25. **Q:** What is the DAY23 invariant #25? **A:** Preserve DAY22 identity, DAY21 candidate semantics, raw immutability, explicit evidence status, and defer final QC.

## Exercises

### Exercise 1
Given a window, a native sample array, and an incomplete configuration, decide whether the correct output is candidate evidence, UNKNOWN, ABSTAIN, or typed failure. Then name the exact provenance fields and explain why raw data must remain unchanged.

### Exercise 2
Given a window, a native sample array, and an incomplete configuration, decide whether the correct output is candidate evidence, UNKNOWN, ABSTAIN, or typed failure. Then name the exact provenance fields and explain why raw data must remain unchanged.

### Exercise 3
Given a window, a native sample array, and an incomplete configuration, decide whether the correct output is candidate evidence, UNKNOWN, ABSTAIN, or typed failure. Then name the exact provenance fields and explain why raw data must remain unchanged.

### Exercise 4
Given a window, a native sample array, and an incomplete configuration, decide whether the correct output is candidate evidence, UNKNOWN, ABSTAIN, or typed failure. Then name the exact provenance fields and explain why raw data must remain unchanged.

### Exercise 5
Given a window, a native sample array, and an incomplete configuration, decide whether the correct output is candidate evidence, UNKNOWN, ABSTAIN, or typed failure. Then name the exact provenance fields and explain why raw data must remain unchanged.

### Exercise 6
Given a window, a native sample array, and an incomplete configuration, decide whether the correct output is candidate evidence, UNKNOWN, ABSTAIN, or typed failure. Then name the exact provenance fields and explain why raw data must remain unchanged.

## Quiz

1. Why must detector result #1 remain a weak-label candidate rather than expert ground truth?
2. Why must detector result #2 remain a weak-label candidate rather than expert ground truth?
3. Why must detector result #3 remain a weak-label candidate rather than expert ground truth?
4. Why must detector result #4 remain a weak-label candidate rather than expert ground truth?
5. Why must detector result #5 remain a weak-label candidate rather than expert ground truth?
6. Why must detector result #6 remain a weak-label candidate rather than expert ground truth?
7. Why must detector result #7 remain a weak-label candidate rather than expert ground truth?
8. Why must detector result #8 remain a weak-label candidate rather than expert ground truth?
9. Why must detector result #9 remain a weak-label candidate rather than expert ground truth?
10. Why must detector result #10 remain a weak-label candidate rather than expert ground truth?
11. Why must detector result #11 remain a weak-label candidate rather than expert ground truth?
12. Why must detector result #12 remain a weak-label candidate rather than expert ground truth?
13. Why must detector result #13 remain a weak-label candidate rather than expert ground truth?
14. Why must detector result #14 remain a weak-label candidate rather than expert ground truth?
15. Why must detector result #15 remain a weak-label candidate rather than expert ground truth?

## Explained answers

All answers reduce to the same safety architecture: the detector observes limited technical evidence under a versioned configuration. Expert truth arrives later; missing evidence must not become PASS; and downstream policy must remain separately versioned and reviewable.

## Final mental model

`DAY22 WindowIdentity → DAY23 evidence/rule → DAY21 LabelingFunctionOutput → later DAY30 aggregation → later clinician adjudication`. Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.

## Readiness checklist

- [ ] Can explain measurement fact vs inference vs clinical interpretation.
- [ ] Can point to `window_id` provenance.
- [ ] Can explain ABSTAIN/UNKNOWN behavior.
- [ ] Can show raw is unchanged.
- [ ] Can explain why weak labels are not truth.
- [ ] Can state what belongs to later days.
