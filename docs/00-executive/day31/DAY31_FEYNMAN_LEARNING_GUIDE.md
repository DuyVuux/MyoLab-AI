# DAY31 FEYNMAN LEARNING GUIDE — From QC Result to Safe Downstream Permission

## 1. The one-sentence idea

DAY30 tells us **what the quality state is**. DAY31 tells downstream code **what it is allowed to do with that state**.

That distinction sounds small, but it is one of the most important architectural boundaries in a safety-sensitive signal-processing system.

## 2. Analogy: airport security versus weather forecast

Imagine you are boarding a flight. QC is airport security. If security says a bag is blocked, a weather forecast cannot overrule security. Distribution support is more like the question “is this aircraft operating in conditions represented by its approved experience?” Uncertainty tells you whether a prediction is a rough rule, a calibrated probability, or a formal prediction set.

Three different questions:
1. Is the input technically acceptable?
2. Is the operating context supported?
3. What uncertainty evidence do we truly have?

Combining them into one “confidence=0.82” number destroys meaning.

## 3. Why QC FAIL must be first

Suppose a signal has `UNIT_MISMATCH`. A model later says it is “99% confident”. That model confidence cannot repair the unit contract. The signal may be numerically scaled by 1000x. Therefore QC FAIL must block before uncertainty is considered.

Formal invariant:

`QC_FAIL => metric_handoff_status = BLOCKED`.

Not “usually blocked”. Not “blocked unless model confidence is high”. Always blocked for unsupported downstream metrics.

## 4. PASS, WARNING, FAIL, and null are not four grades

`PASS`, `WARNING`, and `FAIL` are evaluated QC states. `null` paired with `NOT_EVALUATED` or `INSUFFICIENT_EVIDENCE` means the system lacks enough evidence to decide. Null is not between WARNING and FAIL. It is an epistemic state.

A beginner error is to sort them numerically:

`PASS=2, WARNING=1, FAIL=0, null=-1`.

That encourages averaging. DAY31 instead maps them to permissions:

- PASS -> quality permits profiled processing;
- WARNING -> hold for review;
- FAIL -> block;
- null -> abstain.

## 5. Why WARNING is not “continue with a log”

In ordinary software a warning often means the program continues. In this clinical-quality pipeline, WARNING means review is part of the workflow. If you silently compute and publish a metric first, review becomes ceremonial rather than protective.

Thus DAY31 emits `REVIEW_REQUIRED` and `HOLD_FOR_REVIEW`.

## 6. Distribution support is orthogonal to QC

A clean sEMG recording can be outside the domain supported by a learned model. Conversely, a familiar healthy-domain recording can be corrupted by dropout. These axes are independent.

Think of a 2D grid:

```text
                   Distribution support
                supported        unknown/shifted
QC PASS          maybe proceed    model may abstain/review
QC FAIL          BLOCK            BLOCK
```

The bottom row never changes.

## 7. Why deterministic DSP should not be held hostage by nonexistent OOD AI

Suppose we want RMS on a QC-PASS native window. RMS is a deterministic mathematical operation. If its contract only requires signal quality and units, it does not need a trained distribution detector. Forcing `distribution_support=SUPPORTED` would create a fake dependency and tempt engineers to invent an OOD score.

Therefore each downstream capability declares `distribution_support_required`.

For a distribution-independent deterministic metric:

`QC PASS + distribution UNKNOWN -> ELIGIBLE` can be valid.

This does **not** mean distribution is supported. It means this capability did not require that evidence axis.

## 8. When distribution support should gate

A model trained on specific protocols, channel layouts or cohorts may depend strongly on reference-domain coverage. That capability can declare distribution support required.

Then:
- SUPPORTED -> may proceed if QC passes;
- SHIFTED -> review;
- UNKNOWN -> abstain;
- NOT_EVALUATED -> abstain.

This is selective use, not diagnosis.

## 9. SHIFTED does not mean pathology

A stroke patient may differ from a healthy reference distribution because of physiology. A new electrode layout may also create a shift. A new sampling configuration may create shift. None of these observations alone diagnoses disease.

Thus `SHIFTED` belongs to supportability, not clinical diagnosis.

Counterexample:

Bad logic: `OOD high -> abnormal patient`.

Correct logic: `support evidence differs from validated reference -> capability support needs review/abstention`.

## 10. What is an OOD score?

An OOD score is a numeric output of a specific method. A number is meaningful only if the method, reference distribution, preprocessing, thresholds and validation are known. DAY31 intentionally ships no validated OOD method.

So the default is:

`ood_method_status=NOT_IMPLEMENTED`, `ood_score=null`.

This is better science than inventing `0.0` to mean “not OOD”. Zero would falsely look like measured evidence.

## 11. Four uncertainty types

DAY31 separates four forms.

### RULE_CONFIDENCE
An ordinal statement about a deterministic rule's evidence strength. Example: HIGH evidence that repeated extrema match a clipping heuristic. It is not probability.

### CALIBRATED_PROBABILITY
A numeric probability is allowed only after a calibration procedure has been validated and referenced.

### CONFORMAL_SET
A set-valued prediction generated under a conformal procedure with calibration evidence. It is not a probability and must not be displayed as one.

### NOT_APPLICABLE
The safest default when no uncertainty mechanism applies. It carries no hidden confidence number.

## 12. Rule confidence versus probability

If a rule says “line-noise ratio exceeds configured threshold”, someone may want to report 90% confidence. Where did 90% come from? Unless calibrated against reference labels, it is invented.

DAY31 therefore uses ordinal levels such as LOW/MODERATE/HIGH for rule confidence. Numeric probability is a different type with stronger evidence requirements.

## 13. Why mixing uncertainty types is dangerous

Suppose an object says:

- `uncertainty_type=RULE_CONFIDENCE`
- `calibrated_probability=0.91`
- `conformal_set=[PASS, WARNING]`

A consumer cannot know what 0.91 means. The schema rejects mixed representations. One handoff instance uses one uncertainty representation.

## 14. Abstention is an output, not a failure of courage

Abstention means the system knows it lacks support to make a safe automatic decision. Examples:
- QC incomplete;
- distribution support unknown for a required model;
- a selective model rejects the case;
- required calibration evidence is unavailable.

In medical-support software, abstention is often safer than forcing a label.

## 15. Worked Example 1 — Hard QC failure

Input:
- QC = FAIL;
- reason = UNIT_MISMATCH;
- distribution = SUPPORTED;
- uncertainty = rule confidence HIGH.

Reasoning:
1. Unit mismatch is hard quality/integrity evidence.
2. QC precedence executes first.
3. Distribution and uncertainty cannot repair units.

Output:
- BLOCKED;
- BLOCK_UNSUPPORTED_METRIC;
- metric value null.

## 16. Worked Example 2 — Warning with familiar domain

Input:
- QC = WARNING due power-line evidence;
- distribution = SUPPORTED.

Reasoning:
1. QC has been evaluated but requires review.
2. Familiar domain does not cancel quality warning.

Output: REVIEW_REQUIRED / HOLD_FOR_REVIEW.

## 17. Worked Example 3 — Clean deterministic RMS with unknown distribution

Input:
- QC = PASS;
- metric = RMS;
- distribution required = false;
- distribution status = UNKNOWN.

Output: ELIGIBLE for profiled processing.

Interpretation: the system is not claiming domain support. RMS simply does not require that support dimension under this contract.

## 18. Worked Example 4 — Clean learned model with shifted domain

Input:
- QC PASS;
- distribution-sensitive model;
- status SHIFTED.

Output: REVIEW_REQUIRED.

No pathology label is produced.

## 19. Worked Example 5 — Clean model but support not evaluated

Input:
- QC PASS;
- model requires distribution support;
- distribution NOT_EVALUATED.

Output: ABSTAINED.

This demonstrates why `NOT_EVALUATED` must be valid. Otherwise engineers feel pressure to manufacture an OOD score.

## 20. Worked Example 6 — Calibrated probability

If a future validated model provides a calibrated probability, DAY31 can represent it only with:
- `uncertainty_type=CALIBRATED_PROBABILITY`;
- `calibration_status=CALIBRATED`;
- probability in [0,1];
- calibration reference.

Without those fields, construction fails.

## 21. Property-based safety thinking

A unit test checks one scenario. A safety property asks whether an invariant holds over a whole state space.

Example property:

For every distribution status in `{SUPPORTED, SHIFTED, UNKNOWN, NOT_EVALUATED}`, if QC is FAIL, the output must be BLOCKED.

Another property:

For every QC state and distribution state, `metric_value` remains null on DAY31.

The package implements deterministic loops and seeded randomized invalid-score attacks because an external property library is not required for the core idea.

## 22. Model-based state table

Think of the handoff as a state machine:

```text
QC FAIL ----------------------------> BLOCKED
QC null ----------------------------> ABSTAINED
QC WARNING -------------------------> REVIEW_REQUIRED
QC PASS + no distribution need ----> ELIGIBLE (unless uncertainty abstains)
QC PASS + required + SUPPORTED ----> ELIGIBLE
QC PASS + required + SHIFTED ------> REVIEW_REQUIRED
QC PASS + required + UNKNOWN ------> ABSTAINED
```

Any transition outside this table deserves suspicion.

## 23. False-allow versus false-block

False-allow: corrupted or unsupported data reaches a metric as valid. This can produce authoritative-looking nonsense.

False-block: a valid deterministic metric is prevented solely because an unrelated distribution model does not exist. That wastes clinical workflow and encourages fake OOD evidence.

The `distribution_support_required` flag is designed to reduce both risks.

## 24. Why metric_value is null

If DAY31 emitted a value, eligibility and computation would become coupled. A future developer might accidentally compute before checking eligibility. By forcing `metric_value=null`, the data model makes sequencing explicit:

1. determine eligibility;
2. only then invoke a Phase-3 metric engine;
3. that engine must still record provenance and reasons when unavailable.

## 25. Common junior mistakes

1. Treat WARNING as log-only and continue.
2. Treat UNKNOWN distribution as SUPPORTED.
3. Treat OOD as disease.
4. Use sigmoid output as probability without calibration.
5. Call a heuristic score “confidence=0.9”.
6. Average QC and OOD scores.
7. Recompute QC inside the metric engine.
8. Let exceptions fall through to a default PASS.
9. Put metric values in the eligibility object.
10. Assume deterministic DSP needs a learned distribution detector.

## 26. What not to learn deeply today

Do not spend DAY31 implementing Mahalanobis OOD, deep ensembles, temperature scaling, conformal algorithms, TTA or domain adaptation. Learn their contract implications only. Their algorithms belong later and only if decision gates justify them.

## 27. Flashcards

1. Q: What does DAY31 output? A: Downstream permission/eligibility, not metric values.
2. Q: QC FAIL precedence? A: Absolute block.
3. Q: WARNING action? A: Review required.
4. Q: Null QC action? A: Abstain.
5. Q: Is SHIFTED pathology? A: No.
6. Q: Is UNKNOWN distribution normal? A: No.
7. Q: Is NOT_EVALUATED valid? A: Yes.
8. Q: Default OOD score? A: Null.
9. Q: When may OOD score be numeric? A: Only validated method + provenance.
10. Q: Rule confidence numeric probability? A: No.
11. Q: Probability requirement? A: Calibration status and ref.
12. Q: Conformal set requirement? A: Valid calibration ref.
13. Q: Can uncertainty override QC FAIL? A: No.
14. Q: Can SUPPORTED distribution override WARNING? A: No.
15. Q: Who declares distribution requirement? A: The downstream capability contract.
16. Q: DAY31 compute RMS? A: No.
17. Q: Can metric_value be non-null? A: No.
18. Q: `continue_on_error` allowed? A: No.
19. Q: Does PASS guarantee every model is supported? A: No.
20. Q: Does SHIFTED automatically block deterministic DSP? A: Not unless its capability contract requires support.
21. Q: Why preserve source refs? A: Reproducibility/audit.
22. Q: What is abstention? A: Explicit decision not to automate due insufficient support.
23. Q: Why mutually exclusive uncertainty? A: Prevent semantic laundering.
24. Q: What follows DAY31? A: Expert QC annotation protocol.
25. Q: Ground truth created here? A: No.

## 28. Exercises

### Beginner 1
Given QC FAIL and distribution SUPPORTED, write the handoff. Expected: BLOCKED.

### Beginner 2
Given QC WARNING and distribution UNKNOWN, decide permission. Expected: REVIEW_REQUIRED, not PASS.

### Beginner 3
Explain why `ood_score=0` is not a safe default. Answer: it looks like measured evidence and falsely implies support.

### Intermediate 1
A deterministic RMS metric has QC PASS but distribution NOT_EVALUATED. Should it proceed? Answer: it may proceed if its metric contract does not require distribution support.

### Intermediate 2
A learned classifier has QC PASS, distribution SHIFTED. What is safe? Review/abstention per capability policy, never pathology inference.

### Integration exercise
Sketch the call order for DAY30 aggregate -> DAY31 eligibility -> Phase-3 metric. Explain where each layer may fail closed.

## 29. Quiz

1. Can model confidence override `UNIT_MISMATCH`?
2. What status represents missing QC evidence?
3. Why is WARNING held for review?
4. What are the four distribution-support states?
5. Is a numeric OOD score required?
6. What evidence is required before emitting calibrated probability?
7. What is the difference between rule confidence and probability?
8. Can conformal set and probability coexist in one uncertainty object?
9. Why can deterministic RMS ignore unknown distribution support under some contracts?
10. Why can a learned model not necessarily do the same?
11. What does `SHIFTED` mean clinically?
12. What is `metric_value` on DAY31?
13. What does `ABSTAINED` protect against?
14. What property test should always hold for QC FAIL?
15. What must happen before GO_FOR_DAY_32?

## 30. Quiz Answers

1. No.
2. NOT_EVALUATED/INSUFFICIENT_EVIDENCE with null quality, leading to abstention.
3. Because FR-039 makes review part of the safety workflow.
4. SUPPORTED, SHIFTED, UNKNOWN, NOT_EVALUATED.
5. No; null is correct without a validated method.
6. CALIBRATED status and a calibration reference.
7. Rule confidence is ordinal evidence strength; probability is a calibrated numeric claim.
8. No.
9. It is deterministic and may not depend on learned reference-domain coverage.
10. Learned behavior may depend on the training/reference domain.
11. Support evidence differs or may not cover the operating context; it is not diagnosis.
12. Null.
13. Forced decisions under missing/unsupported evidence.
14. FAIL must always produce BLOCKED regardless of distribution/uncertainty.
15. Live regression, Option-B reconciliation and peer review must pass.

## 31. Troubleshooting

If QC FAIL becomes ELIGIBLE, inspect precedence ordering first. If UNKNOWN distribution blocks all deterministic metrics, inspect the request's `distribution_support_required`. If schema rejects a valid uncertainty object, ensure only one uncertainty representation is populated. If a developer wants `confidence=0.95`, ask where calibration evidence lives. If a model needs OOD support but DAY31 has none, the correct result is NOT_EVALUATED/ABSTAIN, not a fabricated score.

## 32. Teach-back

A junior is ready when they can explain, without notes:
- why QC and distribution support are orthogonal;
- why QC FAIL precedes uncertainty;
- why WARNING is not continue-on-error;
- why null/NOT_EVALUATED is safer than fake PASS;
- why deterministic DSP and learned models may have different distribution requirements;
- why rule confidence is not probability;
- why DAY31 contains no metric value.

## 33. Readiness Checklist

- I can enumerate the state machine.
- I know which states block, review, abstain and allow.
- I can spot fake OOD/probability claims.
- I can explain the role of capability-specific distribution requirements.
- I can write a property test for QC FAIL precedence.
- I understand why DAY31 is a boundary, not a metric implementation.

## 34. Final Mental Model

Keep this sentence:

**Quality says whether the evidence is technically usable; distribution support says whether a capability is supported in this context; uncertainty says what uncertainty evidence is justified; permission is computed from these contracts without allowing any later signal to erase an earlier hard QC failure.**

## 35. A deeper mental model: three axes, one permission

It helps to draw three orthogonal axes rather than one score.

Axis A is quality: PASS, WARNING, FAIL or unknown. This comes from the QC system and asks whether the signal/data evidence is technically supportable.

Axis B is distribution support: SUPPORTED, SHIFTED, UNKNOWN or NOT_EVALUATED. This asks whether a downstream capability has evidence that its operating context is represented or supported.

Axis C is uncertainty representation: rule confidence, calibrated probability, conformal set or not applicable. This asks what kind of uncertainty statement is justified.

DAY31 computes a permission from these axes according to a declared capability contract. Permission is not another clinical label. It is an operational state: eligible, review required, blocked or abstained.

## 36. Why a single “confidence score” is so tempting

A single number is easy to sort, plot and show in a UI. That convenience makes it dangerous. Imagine a developer combines QC quality, OOD distance and classifier confidence into `confidence=0.74`. What does 0.74 mean? Is it probability of good signal, probability of correct diagnosis, similarity to training data, or rule agreement? Nobody can audit it.

Typed contracts force the system to answer these questions separately. More fields can actually make the system simpler because each field has one meaning.

## 37. Selective prediction without a selective model

DAY31 prepares for selective prediction but does not pretend one exists. Selective prediction means a model may choose not to predict when its confidence/support conditions are not met. The contract supports an `abstention` field inside uncertainty so a future validated model can express that decision.

However, QC blocking, quality abstention and distribution abstention are represented at the metric-handoff layer. They are not fabricated as model abstention. This distinction is subtle but valuable: a future audit can tell whether automation stopped because the signal failed QC, because domain support was unknown, or because the model itself abstained.

## 38. Example: same waveform, two downstream capabilities

Suppose a window has QC PASS and distribution status UNKNOWN.

Capability A is RMS. Its mathematical operation is deterministic and its contract says distribution support is not required. DAY31 may mark it ELIGIBLE.

Capability B is a learned fatigue classifier trained only on a specific acquisition protocol. Its contract says distribution support is required. The same window must ABSTAIN for Capability B until support is evaluated.

Nothing contradictory happened. Eligibility belongs to the pair `(evidence, capability)`, not to the waveform alone.

## 39. Why supportability belongs in the request

If supportability requiredness were a global boolean in the quality service, all capabilities would share one policy. That would either over-block simple DSP or under-protect learned algorithms. By putting requiredness in the request/profile, the architecture follows dependency inversion: the downstream capability states what evidence it requires; the quality gate enforces that declaration.

## 40. A clinical counterexample to OOD=pathology

Imagine a stroke rehabilitation session. The patient's activation pattern differs strongly from a healthy volunteer reference set. A distribution detector may flag SHIFTED. If the system translates this into “abnormal pathology detected,” it has confused population difference with diagnosis.

Now imagine a healthy volunteer recorded after the electrode layout changed. That can also be SHIFTED. Or the same patient recorded at a new sampling rate. Therefore shift must remain an engineering supportability concept until a separate clinical model with explicit intended use and validation exists.

## 41. A DSP counterexample to quality=distribution support

A clean sine-like calibration signal may have perfect timestamps, units and noise quality but be unlike the biological data on which a model was trained. QC can PASS while distribution support is UNKNOWN. Conversely, a common training-domain waveform can have a duplicated timestamp and should FAIL QC. These examples prove the axes are logically independent.

## 42. Why null beats zero

Suppose no OOD method exists. If the API returns `ood_score=0`, a chart may display “OOD risk 0%.” That is false. Null communicates “not measured/not available.” In evidence-sensitive software, absence must remain absence.

The same principle appears throughout the project: unavailable metric is null plus reason, missing evidence is not normal, MFCV unavailable is not zero, and now OOD not evaluated is not zero.

## 43. Calibration explained with a weather analogy

A weather model may say “70% chance of rain.” Calibration asks: among many cases where the model said 70%, did it rain roughly 70% of the time under the relevant validation setup? Without such evidence, a score between zero and one is not automatically a probability.

Likewise, a neural network's sigmoid output of 0.9 may be a score. DAY31 allows `CALIBRATED_PROBABILITY` only when calibration evidence is explicitly referenced.

## 44. Conformal prediction explained simply

Conformal methods can output a set such as `{PASS, WARNING}` rather than a single class, under assumptions and calibration procedures. The useful point for DAY31 is not the algorithm. The useful point is semantic: a set is not a probability. The contract therefore gives conformal output its own type and requires a calibration reference.

## 45. Property testing as “laws of physics” for software

Example-based tests are like checking three bridges. Property tests are like stating a structural law every bridge must obey. DAY31's most important law is:

`for all distribution states D: QC_FAIL + D -> BLOCKED`.

Another law is:

`for all inputs: DAY31.metric_value = null`.

These laws protect the architecture when new cases are added later.

## 46. Why deterministic replay matters here

Eligibility decisions may be audited months later. If the same QC result, distribution object, uncertainty object and request produce different permission because of unordered sets, random IDs or current wall-clock state, reproduction becomes difficult.

DAY31 canonicalizes reason codes and preserves stable evidence refs. It does not call random functions or system time during evaluation. Identical immutable inputs produce identical serialized output.

## 47. What “fail closed” really means

Fail closed is not “return FAIL for everything unexpected.” That would create false evidence. It means an unexpected or insufficient state cannot silently become permission to proceed.

Sometimes fail closed means BLOCKED, such as QC FAIL. Sometimes it means ABSTAINED, such as unknown required distribution support. Sometimes a contract violation raises an exception and emits no final-looking result. The safe state depends on semantics.

## 48. Distinguishing BLOCKED and ABSTAINED

BLOCKED means there is sufficient evidence that this downstream action is not allowed under the current quality contract. Example: UNIT_MISMATCH.

ABSTAINED means the system does not have enough support to make the automatic downstream decision. Example: a model requires distribution support but that support has not been evaluated.

This difference matters for workflow. A blocked case may require remediation/re-measurement; an abstained model may still allow a clinician to inspect other evidence or use a deterministic metric.

## 49. Why WARNING is distinct from ABSTAINED

WARNING means the QC system has evaluated the signal and found evidence that requires human review. ABSTAINED often means evidence is incomplete or a required support mechanism is unavailable. Both prevent automatic progression, but for different reasons. Preserving the distinction helps clinicians and engineers understand the next action.

## 50. Hidden bypasses to search for during code review

Even if `quality_gate.py` is correct, bypasses can appear elsewhere:

- a metric worker imports DAY30 directly and ignores DAY31;
- a batch job computes metrics before checking eligibility;
- an exception handler catches `QualityGateContractError` and continues;
- a UI marks a metric valid based only on non-null value;
- a developer treats WARNING as PASS to improve throughput;
- a model-serving endpoint assumes `distribution_support_status` defaults to SUPPORTED.

The architecture becomes safe only when downstream consumers actually require the DAY31 permission.

## 51. Worked Example 7 — critical flag survives migration bug

Imagine an adapter accidentally serializes `signal_quality=PASS`, but `critical_failure=true` remains from a hard timestamp failure. DAY31 checks the critical flag independently and blocks. This is defense in depth, not permission for inconsistent upstream objects.

## 52. Worked Example 8 — physiology warning plus deterministic metric

A window is marked WARNING because `PHYSIOLOGICAL_VARIATION_POSSIBLE` requires review. Even though this is not an artifact failure and the window was counted usable at DAY30, DAY31 still holds automatic metric execution because the workflow says WARNING routes review. This shows “usable for aggregation” and “automatically eligible downstream” are different concepts.

## 53. Worked Example 9 — supported domain but failed QC

A learned model has excellent validated domain coverage, `SUPPORTED`, and a calibrated probability mechanism. The source has `TIMESTAMP_NON_MONOTONIC`. DAY31 blocks. No amount of downstream model evidence can restore broken input integrity.

## 54. Worked Example 10 — high probability cannot fix missing QC

QC is INSUFFICIENT_EVIDENCE. A model reports calibrated probability 0.999. DAY31 abstains because the input quality gate is incomplete. Calibration answers how a model's probability behaves under validation; it does not prove the current raw evidence passed QC.

## 55. Worked Example 11 — distribution shift with no model

Suppose contextual rules flag a new channel layout as SHIFTED, but the requested capability is deterministic RMS. If the request says distribution support is not required, RMS remains eligible after QC PASS. The shift stays recorded for audit. This avoids throwing away useful deterministic evidence.

## 56. Worked Example 12 — distribution-sensitive model not evaluated

QC PASS; the model contract requires distribution support; OOD machinery is not implemented. Correct output: ABSTAINED with `DISTRIBUTION_SUPPORT_NOT_EVALUATED`. Incorrect outputs include `SUPPORTED` by default, `ood_score=0`, or a guessed confidence.

## 57. Debugging thought exercise: why did a metric run?

Trace the following chain:
1. What exact DAY30 scope/result was used?
2. Did DAY31 receive the same WINDOW/CHANNEL/SESSION scope requested by the metric?
3. What was `metric_handoff_status`?
4. What was `processing_permission`?
5. Did the worker verify `ALLOW_PROFILED_PROCESSING` before running?
6. Was distribution support required for that capability?
7. Did an exception handler bypass the gate?

This sequence finds architectural bypasses faster than staring at numerical metric output.

## 58. Debugging thought exercise: where did probability come from?

Whenever you see a numeric probability, ask:
- which model generated it?
- what calibration procedure was used?
- which validation cohort and split?
- what calibration reference/version is in provenance?
- is the operating domain supported?

If these cannot be answered, the number should not use the `CALIBRATED_PROBABILITY` type.

## 59. Review exercise: design a new Phase-3 metric request

Imagine MDF. Decide whether its eligibility depends on distribution support or only on QC + preprocessing eligibility. State your assumption explicitly. Do not answer from habit. The point is that capability contracts should declare dependencies rather than inherit a global AI policy.

## 60. Review exercise: design a learned model request

Imagine a future classifier trained on one protocol and channel layout. Its request should likely declare distribution support required. Explain how SHIFTED, UNKNOWN and NOT_EVALUATED should route before any model result is treated as supported.

## 61. Extended quiz

16. Why can a critical flag be checked separately from signal quality?
17. Does an abstained metric necessarily mean QC failed?
18. Can a blocked metric still carry a non-abstaining uncertainty object?
19. Why is that not contradictory?
20. What field expresses operational permission?
21. What is the danger of a global distribution gate for all DSP metrics?
22. What is the danger of no distribution gate for learned models?
23. What should a consumer do with `metric_value=null` on DAY31?
24. Why is provenance important for supportability decisions?
25. How does property testing protect future extension points?

## 62. Extended quiz answers

16. Defense in depth against migration/serialization inconsistency; hard-stop evidence must not be lost.
17. No. It may mean QC evidence is incomplete, distribution support is unknown, or an uncertainty mechanism abstained.
18. Yes, because metric blocking and model/selective abstention are different semantics.
19. Permission is determined by QC precedence; uncertainty metadata can remain descriptive without overriding it.
20. `metric_handoff_status` together with `processing_permission`.
21. It can unnecessarily block valid deterministic calculations and incentivize fake support evidence.
22. It can apply learned behavior outside validated/supportable context.
23. Do not interpret it as zero; invoke the metric engine only after ELIGIBLE permission.
24. It lets reviewers reconstruct which QC/config/domain/calibration evidence justified the decision.
25. It states invariants over whole state combinations so new branches cannot silently violate them.

## 63. Final teach-back challenge

Explain this scenario to a clinician and an engineer using different vocabulary:

A signal is QC PASS. A deterministic RMS metric is eligible. A learned classifier is not eligible because distribution support is NOT_EVALUATED. No OOD score exists. Neither result implies pathology. The clinician should understand why some evidence remains available while another automated output abstains; the engineer should understand that requiredness belongs to the capability contract.

If you can explain that clearly without collapsing the states into a confidence score, you understand DAY31.
