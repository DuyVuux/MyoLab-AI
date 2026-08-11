# DAY34 FEYNMAN LEARNING GUIDE — Weak Labels, Known Truth, Disagreement & Coverage

## 1. The simple story

Imagine six smoke alarms looking at the same room. One alarm detects heat, one smoke density, one electrical current, and another depends on a neighboring sensor. If two alarms disagree, that does not mean one human reviewer disagreed with another. It only tells us the engineering rules respond differently to the same situation.

DAY34 asks three questions: **Did each detector have enough evidence to speak? When synthetic truth is genuinely inside the window it inspected, did it react appropriately? Which rules tend to fire together or disagree?**

The fourth question is even more important: **Is the benchmark itself honest?** A perfect detector cannot detect an artifact that is outside the window it was asked to inspect.

## 2. Four objects you must never confuse

### Synthetic known truth

We generated the corruption ourselves. We know what transform was applied. This is technical truth about the generator, not clinical truth about human physiology.

### Weak label

A rule observes signal evidence and emits a candidate such as PASS, WARNING, FAIL, UNKNOWN, or ABSTAIN. The candidate is not ground truth.

### QC policy decision

DAY30 can combine evidence into operational PASS/WARNING/FAIL. That is a system decision, not a clinician label.

### Expert annotation

A qualified human reviewer can provide an opinion under an annotation protocol. No such evidence exists in DAY34.

## 3. Why disagreement is useful

Suppose power-line says WARNING but motion says PASS. This may be entirely correct: a 50-Hz sine wave is not necessarily a movement artifact. Disagreement helps us identify information diversity. If every rule always fires together, we may have redundant evidence rather than six independent signals.

But “agreement” between rules is not inter-rater agreement. Cohen's kappa was designed for raters classifying items under a reference labeling task. A frequency-domain heuristic and a dropout rule are algorithms with different target constructs. Calling their kappa “reviewer agreement” would create a false clinical narrative.

## 4. Coverage before accuracy

A detector can be highly accurate on the small set of windows where it speaks, while abstaining on most difficult cases. Therefore DAY34 records coverage separately.

For a family:

```text
coverage = number of binary PASS/positive outputs / scorable items
```

UNKNOWN and ABSTAIN are unresolved. They are not quietly removed and then forgotten.

For positive truth we also distinguish:

```text
selective recall = TP / evaluated positive cases
```

and

```text
effective recall = TP / all scorable positive truth cases
```

If every positive case abstains, selective recall has no denominator while effective recall is zero. This distinction prevents selective systems from appearing better by refusing all hard cases.

## 5. The benchmark-window alignment lesson

DAY33 uses 2000-sample signals at 2000 Hz. Its core window is samples `[1000,1500)`. Several local corruptions were inserted near one-third of the signal, approximately samples 666–866. That means MISSING, ZERO_DROPOUT, FLATLINE, and CLIPPING are outside the core. They may be visible in context, but the detector functions consume the core window.

A naive evaluator would say “the detector missed the artifact.” That conclusion would be wrong. The truth label describes the full signal while the prediction describes a different time interval.

DAY34 therefore introduces the concept of **truth applicability**:

```text
truth exists in full signal
        ≠
truth overlaps evaluated core window
```

Only the second one authorizes window-level supervised scoring.

This is a general machine-learning lesson. Label granularity must match prediction granularity. Session labels cannot automatically become window labels. Patient labels cannot automatically become sample labels. File-level corruption cannot automatically become every-window corruption.

## 6. Why baseline noise remains UNKNOWN

The DAY25 baseline-noise detector requires a protocol-specific threshold. DAY34 deliberately does not invent one because DAY35 owns threshold sensitivity. The synthetic baseline noise is truly present across the window, but the detector cannot convert descriptors into PASS/WARNING without an operative threshold.

Returning UNKNOWN is good safety behavior. It means:

> “I can compute descriptors, but I do not have authorized evidence to convert them into a quality decision.”

This is different from a false negative. A false negative would be a confident PASS on a scorable positive case.

## 7. Why clipping is special

Clipping has two levels of evidence:

1. heuristic repeated extrema/plateau;
2. verified device ADC saturation semantics.

The DAY33 synthetic amplitude scale is arbitrary research scale, not verified Noraxon ADC rails. DAY34 therefore refuses to invent hardware limits. Even if the local clipping truth were correctly aligned, a heuristic suspicion would not automatically become verified device saturation.

This teaches an important biomedical DSP principle: a waveform shape can suggest clipping, but hardware saturation is a hardware claim.

## 8. Why power-line is scorable

The power-line transform is global: a 50-Hz sinusoid is added to the entire signal. Therefore it exists inside the core. DAY34 knows 50 Hz because the synthetic generator itself specifies the engineering fixture environment. Supplying 50 Hz is not a Vinmec/site claim; it is synthetic metadata.

The result demonstrates only that the current DAY26 rule detects this specific injected 50-Hz engineering fixture. It does not prove sensitivity on real electrode recordings, different SNRs, 60-Hz environments, or clinical sessions.

## 9. Why motion has two valid positives

The 2-Hz drift is global, so every core contains it. The transient is injected at `n/2`, exactly where the selected core begins. Both truth events therefore overlap the detector target.

This is why DAY34 can report valid window-level synthetic evidence for the motion/low-frequency family, while refusing the same claim for misaligned dropout/clipping fixtures.

## 10. Poor contact: the missing dimension

Poor contact is not simply “small amplitude.” DAY28 intentionally needs corroboration and cross-channel context. The DAY33 corpus contains one synthetic channel per item. No neighboring channels exist.

If we forced a poor-contact accuracy number anyway, we would be evaluating an amputated version of the task. DAY34 instead executes the detector for traceability, records its raw output, then marks supervised scoring as `NOT_SCORABLE_NO_CROSS_CHANNEL_PEERS`.

This is a strong portfolio lesson: **not every missing benchmark number is a weakness. Sometimes refusing an invalid metric is evidence of better system design.**

## 11. Low amplitude is a safety sentinel

`SYNTHETIC_LOW_AMPLITUDE_STRESS` is intentionally not labeled stroke, paresis, atrophy, or poor contact. It exists to test whether the system overreacts to amplitude reduction.

A healthy signal multiplied by 0.1 remains an engineering amplitude transform. It does not reproduce recruitment changes, motor-unit physiology, altered coordination, tissue conductivity, or disease mechanisms.

The correct question is:

> “Does the QC system avoid fabricating an acquisition-failure/pathology claim from amplitude alone?”

not:

> “Can this synthetic signal represent stroke?”

## 12. Phi correlation in plain language

For two binary rules A and B, phi correlation summarizes whether they tend to be positive on the same windows. It ranges roughly from -1 to +1 when defined:

- +1: they move together perfectly;
- 0: no linear association in this sample;
- -1: one is positive whenever the other is negative.

With only 12 windows, correlation is descriptive, not a stable population estimate. If one rule never changes value, correlation is undefined because there is no variance.

DAY34 therefore reports both the coefficient and a status such as `INSUFFICIENT_VARIABILITY`.

## 13. Disagreement rate can be more useful

If A and B are both evaluable on 12 windows and differ on 3:

```text
disagreement_rate = 3 / 12 = 0.25
```

This is simple and operationally meaningful. It tells us how often future reviewers might see different machine evidence streams.

But again: it is algorithm disagreement, not doctor disagreement.

## 14. Correlated weak labels and double counting

Suppose two detectors use almost the same low-frequency feature. If both fire, a naive majority vote may treat that as two independent votes. In reality it may be one physical phenomenon counted twice.

This is why correlation and shared evidence types matter before any label model or aggregation scheme. DAY34 explicitly does not train a label model; it only prepares evidence that could inform a later decision.

## 15. Candidate ranking is not active-learning magic

DAY34 does not run a trained Active Learning model. It uses transparent acquisition signals:

- disagreement;
- unresolved evidence;
- known-truth target failure;
- hard-integrity override;
- physiology-preservation sentinel;
- workflow impact.

This is enough to prioritize future review candidates without pretending a neural acquisition function exists.

## 16. Why corpus-repair items should not go to a doctor

If a fixture label and its evaluated window are misaligned, asking a doctor to review it wastes expert time. The correct owner is engineering. DAY34 therefore routes those items to `ENGINEERING_CORPUS_REPAIR` and explicitly sets future expert selection to false.

Human time should be spent resolving genuine ambiguity, not fixing benchmark bookkeeping.

## 17. Worked example: power-line

1. DAY33 truth: `POWERLINE_50HZ_INJECTED`.
2. Transform is global.
3. Truth overlaps core.
4. DAY26 receives synthetic-grid frequency 50 Hz.
5. Rule returns `POWERLINE_INTERFERENCE_SUSPECTED`.
6. Candidate becomes binary positive.
7. Window-level synthetic TP = 1.

Allowed conclusion:

> Current rule detected the single scorable 50-Hz synthetic fixture in DAY33 development corpus.

Forbidden conclusion:

> Power-line detector is clinically 100% accurate.

## 18. Worked example: baseline noise

1. Truth: broadband baseline noise injected globally.
2. Truth overlaps core.
3. Baseline descriptors can be calculated.
4. Operative threshold is `NOT_VERIFIED`.
5. Output = UNKNOWN.
6. Positive truth remains unresolved.

This is a good candidate for DAY35 sensitivity study, not a reason to secretly choose a threshold in DAY34.

## 19. Worked example: dropout misalignment

1. Missing segment is injected around samples 666–866.
2. Core is 1000–1500.
3. The core contains no missing segment.
4. Dropout returns PASS for the core.
5. Evaluator checks truth localization.
6. Positive window metric is disallowed.
7. Item goes to corpus repair.

Without step 5, we would falsely punish the detector.

## 20. Worked example: timestamp corruption

Timestamp duplicate/non-monotonic corruption occurs outside the core, but DAY29 integrity operates at the session/source structure level rather than only the signal core. The full time array is therefore the correct target. Both timestamp corruptions are valid positive integrity cases and are blocked.

This demonstrates why scope matters: the same corruption can be irrelevant to a window detector yet critical to a session integrity gate.

## 21. Common junior mistakes

1. Calling weak-label agreement “doctor agreement.”
2. Treating UNKNOWN as PASS.
3. Computing recall when no positive truth is scorable.
4. Calling null metric zero.
5. Using full-file truth as every-window truth.
6. Treating a synthetic low-amplitude transform as pathology.
7. Tuning thresholds while evaluating them.
8. Looking at locked labels “just once for debugging.”
9. Treating rule correlation as causal independence.
10. Sending corpus construction bugs to expert review.

## 22. What not to learn from DAY34

Do not learn that power-line or motion detectors are generally accurate from 1–2 synthetic positives. Do not learn a site threshold. Do not learn a clinical artifact prevalence. Do not learn poor-contact performance. Do not learn clinician agreement. Do not infer public-dataset behavior because public raw payloads are not yet in the corpus.

## 23. Flashcards

1. **Q:** Weak label equals truth? **A:** No; it is a machine candidate.
2. **Q:** What authorizes supervised scoring in DAY34? **A:** `SYNTHETIC_KNOWN_TRUTH` plus truth applicability to the evaluated scope.
3. **Q:** UNKNOWN equals negative? **A:** No.
4. **Q:** Why can poor contact not be scored? **A:** No cross-channel peers/positive truth fixture.
5. **Q:** Why can baseline noise not produce a thresholded decision? **A:** Threshold remains unverified.
6. **Q:** What partition is used? **A:** `benchmark-development` only.
7. **Q:** What happens to locked truth? **A:** It remains unseen.
8. **Q:** Correlation between LFs means reviewer agreement? **A:** No.
9. **Q:** Local corruption outside core is FN? **A:** No; it is not scorable for that window.
10. **Q:** Is 50 Hz a site claim? **A:** No; synthetic fixture metadata only.
11. **Q:** Is low amplitude poor contact? **A:** Not by itself.
12. **Q:** Who owns threshold tuning? **A:** DAY35.
13. **Q:** Who owns hard timestamp integrity? **A:** DAY29.
14. **Q:** Does DAY34 train a label model? **A:** No.
15. **Q:** What is effective recall? **A:** TP divided by all scorable positive truth cases.
16. **Q:** What is selective recall? **A:** TP divided by evaluated positive cases.
17. **Q:** Why report coverage? **A:** To expose abstention/unknown behavior.
18. **Q:** What is `ENGINEERING_CORPUS_REPAIR`? **A:** A benchmark construction issue, not an expert annotation task.
19. **Q:** Highest DAY34 claim? **A:** `WEAK_LABEL_ANALYTICAL_EVIDENCE_READY`.
20. **Q:** Clinical validation status? **A:** `NOT_PERFORMED`.

## 24. Exercises

### Beginner 1
Given outputs PASS, UNKNOWN, WARNING on three windows, map them to binary analytical votes. Explain why UNKNOWN remains null.

### Beginner 2
A clipping event exists in samples 200–300 while the core is 500–750. Should a PASS be a false negative? Explain.

### Beginner 3
A detector has 1 positive truth case and abstains on it. What are selective recall and effective recall?

### Intermediate 1
Design a 2×2 confusion matrix that keeps unresolved cases outside the binary matrix while still reporting positive coverage.

### Intermediate 2
Explain why two highly correlated weak-label rules should not automatically receive two independent votes in an aggregation model.

### Integration
Design a corrected DAY33 v0.1.1 window-selection strategy for localized corruption. Preserve WindowIdentity determinism, locked partition governance, and truth commitments.

## 25. Quiz

1. Why is DAY34 not clinician adjudication?
2. Which four local scenarios are misaligned in DAY33 v0.1?
3. Why is the power-line positive scorable?
4. Why is motion transient scorable?
5. Why does baseline remain unresolved?
6. Why is poor-contact not scorable?
7. What is the difference between coverage and recall?
8. What does phi correlation measure here?
9. Why is a correlation coefficient sometimes null?
10. Why is timestamp corruption scored separately from LF correlation?
11. What does `truth_localization_gap_count` protect against?
12. Why must corpus-repair items not consume expert time?
13. What does a low-amplitude stress fixture prove?
14. What is forbidden in DAY34 regarding thresholds?
15. What is forbidden regarding locked truth?

### Answers

1. No expert reviewers exist; DAY34 evaluates machine rules and synthetic truth only.
2. MISSING, ZERO_DROPOUT, FLATLINE, CLIPPING.
3. The 50-Hz transform affects the whole signal and overlaps the core.
4. It is injected at the start of the core window.
5. No authorized baseline-noise threshold exists yet.
6. Cross-channel context and a positive poor-contact truth fixture are absent.
7. Coverage tells how often the detector gives a binary answer; recall tells how many scorable positives were detected.
8. Pairwise association of binary machine-rule outputs.
9. Too few paired observations or no variance.
10. DAY29 integrity is a hard structural gate, not a weak labeling function.
11. Scoring truth against a window where that truth is absent.
12. The issue is engineering provenance/alignment, not clinical ambiguity.
13. Safety against overinterpreting amplitude; not pathology.
14. No threshold tuning.
15. No locked truth access.

## 26. Readiness Teach-Back

You are ready for DAY35 when you can explain, without notes:

- why a detector can be correct even when a file-level truth label says artifact;
- why UNKNOWN is not a false negative but still reduces effective detection capability;
- why 100% on one synthetic positive is not a meaningful generalization claim;
- why poor-contact needs another data dimension;
- why DAY35 must repair or replace misaligned positives before threshold sweep;
- why the locked partition remains untouched.

## 27. Vocabulary you should be able to define precisely

**Applicability:** whether a detector has the contextual prerequisites needed to produce interpretable evidence.  
**Coverage:** how often an applicable detector returns a binary/evaluable output.  
**Abstention:** deliberate non-decision due to missing support; not a negative prediction.  
**Known truth:** a property deliberately created by the synthetic generator.  
**Truth localization:** where that property exists relative to the prediction target.  
**Weak supervision:** using heuristic/rule outputs as candidate labels or evidence, without claiming expert truth.  
**Correlation:** statistical co-variation between rule outputs.  
**Disagreement:** fraction of co-evaluated items where binary outputs differ.  
**False allow:** a scorable harmful/positive condition receiving an allowed/negative result rather than being blocked/reviewed.  
**False block:** a scorable acceptable condition being incorrectly blocked.  
**Corpus repair:** engineering correction to benchmark construction or provenance.  
**Selective metric:** performance calculated only on cases where a system chooses to answer.  
**Effective metric:** performance accounting for unresolved/abstained scorable cases in the denominator where appropriate.

## 28. Counterexample: why “more labels” can make a benchmark worse

Suppose every one-second signal has the file-level label `CLIPPING`. You cut it into four 250-ms windows but clipping occurs only in the first. If you copy the file label to all four windows, you now have four “positive” windows even though three contain no clipping. A perfect clipping detector becomes 25% recall. Adding labels made the dataset less truthful.

The fix is not a smarter model. The fix is to align the label to the prediction scope.

## 29. Counterexample: why abstention can be safer than a high score

Detector A answers 100 easy cases and achieves 95 correct, but refuses 900 difficult cases. Detector B answers all 1000 and gets 850 correct. If you report only selective accuracy, A looks superior at 95% versus 85%. But A's coverage is 10%. For a workflow that needs broad automation, the evidence is incomplete.

DAY34 therefore refuses single-number performance reporting.

## 30. Counterexample: why rule agreement is not truth

Imagine two rules both detect high spectral power around 50 Hz, but one calls it “power-line ratio” and another calls it “spectral abnormality.” They agree on nearly every window because they reuse similar information. Agreement does not mean the label is correct twice. It means evidence is correlated.

This is why a weak-label aggregation model should understand source dependence before treating rules as independent voters.

## 31. DSP perspective: scope is part of the signal definition

In signal processing, an observation is never just an array. It is an array plus sampling rate, units, time interval, channel, preprocessing state and context. The same physical recording can yield different conclusions under different windows. A 2-Hz drift visible over one second may look nearly linear over 250 ms. A transient can disappear entirely if the window shifts 20 ms.

Therefore WindowIdentity is not bookkeeping. It is part of the mathematical input to the detector.

## 32. Why context and core are different

DAY22 deliberately stores a core window and surrounding context. The core is the segment whose QC result is being emitted. Context exists so a reviewer or algorithm can interpret transitions and neighborhood. A truth event in context does not automatically make the core positive.

This distinction is especially relevant to DAY33: localized corruption can be seen by a human inspecting the larger context while the detector correctly emits PASS for the core. Evaluation must respect which scope the output describes.

## 33. How to reason about UNKNOWN versus ABSTAIN

Both are unresolved for binary performance, but their semantics may differ:

- `ABSTAIN`: the rule intentionally refuses because required evidence is missing or the input is unsupported.
- `UNKNOWN`: evidence exists but does not authorize a categorical candidate.

DAY34 keeps both unresolved. Future workflows may route them differently, but neither is converted to PASS.

## 34. A practical formula sheet

For scorable cases:

```text
binary coverage = evaluated binary cases / scorable cases
positive coverage = evaluated positive cases / scorable positive cases
precision = TP / (TP + FP)
selective recall = TP / (TP + FN)
effective recall = TP / scorable positive cases
specificity = TN / (TN + FP)
disagreement = differing binary outputs / pairwise co-evaluated cases
```

Every denominator must be visible. If the denominator is zero, return null—not zero.

## 35. Why effective recall is useful for safety

Suppose there are ten known positive artifacts. The detector detects six, returns PASS on one, and abstains on three.

```text
selective recall = 6 / 7 ≈ 0.857
effective recall = 6 / 10 = 0.60
```

Both numbers are true. Selective recall tells you the quality of decisions when the detector speaks. Effective recall tells you how much of the known-positive workload is actually captured. For safety-sensitive automation, hiding the second number would be misleading.

## 36. Understanding the DAY34 result without overreading it

Power-line and motion currently show perfect synthetic counts on extremely small positive sets. The right interpretation is **contract execution evidence**, not statistical validation. One power-line positive cannot establish prevalence robustness, confidence intervals, cross-device transfer, or noise tolerance.

The result proves the pipeline can connect frozen synthetic truth to real detector code and compute honest metrics. That infrastructure is more important at DAY34 than the numeric score itself.

## 37. Why the baseline result is actually good news

At first glance, “baseline positive unresolved” may look like failure. But the baseline rule refuses to apply an unverified threshold. That behavior preserves the roadmap boundary: DAY35 studies thresholds; DAY34 does not smuggle one in.

A system that produced PASS simply because no threshold exists would be more dangerous and would violate fail-closed design.

## 38. Why poor-contact needs a better future corpus

A meaningful poor-contact benchmark should include at least:

- target channel;
- two or more adjacent/reference channels;
- known acquisition perturbation or corroborating evidence;
- protocol activation context;
- clean low-activation cases to test physiology preservation;
- exact WindowIdentity for all channels aligned in time.

Only then can we evaluate whether low relative RMS plus corroboration identifies a contact problem without punishing true low activation.

## 39. Designing DAY33 corpus v0.1.1 correctly

For each localized injection:

1. Generate the clean signal.
2. Choose the target WindowIdentity first.
3. Inject the corruption inside that core or record exact event bounds.
4. Store `truth_start_sample` and `truth_end_sample_exclusive` in provenance.
5. Verify overlap automatically.
6. Create a new item ID/source hash because bytes changed.
7. Recompute locked truth commitments for new locked items without exposing the truth.
8. Never overwrite v0.1 history.

This is a reusable benchmark-engineering pattern for future ML experiments.

## 40. How DAY34 prepares Active Learning without training it

A future acquisition system can prioritize windows where:

- rules disagree;
- critical rules abstain;
- QC and distribution support conflict;
- a hard integrity gate blocks while waveform heuristics appear clean;
- low-amplitude physiology-preservation sentinels occur;
- rare domain contexts appear.

No neural uncertainty model is necessary for the first acquisition cycle. Transparent engineering scores are enough.

## 41. How DAY34 prepares weak-supervision modeling without training it

If a future label model is considered, DAY34 already provides important prerequisites:

- LF identity normalization;
- per-window LF output matrix;
- coverage;
- pairwise dependence evidence;
- known-truth subsets;
- abstention semantics;
- failure cases.

But a model should not be trained merely because this matrix exists. The corpus is tiny, some families lack valid positive truth, and no expert reference exists.

## 42. Interview explanation

A strong interview explanation of DAY34 is:

> “I built a weak-label evaluation layer that deliberately separates synthetic truth, machine candidates and operational QC. During evaluation it caught a benchmark-label granularity bug: four injected artifacts were outside the core window being scored. Instead of reporting them as false negatives, I marked them non-scorable and blocked threshold tuning on those cases. I also measured rule coverage/correlation and preserved fail-closed UNKNOWN behavior.”

This demonstrates signal-processing reasoning, ML evaluation hygiene and safety architecture simultaneously.

## 43. Advanced exercise — construct a misleading metric

Using 12 windows, create an example where a detector has 100% selective precision and recall but only 8% positive coverage. Explain why reporting “100% sensitivity” without coverage would be misleading.

## 44. Advanced exercise — correlated rules

Construct outputs for two rules over 12 windows such that disagreement is 0 but neither rule is informative about truth. What does phi correlation become? Why does agreement not establish validity?

## 45. Advanced exercise — scope conversion

You have a session-level timestamp failure and window-level waveform PASS. Is this a contradiction? No. Explain how DAY29 can block downstream even if all six signal-quality rules are negative on a particular window.

## 46. Advanced exercise — threshold governance

Suppose baseline descriptors for clean synthetic windows cluster at RMS 0.09 and noisy windows at 0.18. Why should DAY34 still not choose 0.13 as a threshold? Describe what DAY35 must add: parameter sweep, objective definition, leakage protection, evidence class, robustness across Fs/window profile, and locked exclusion.

## 47. Teach-back checklist

You should be able to answer yes to all of these:

- Can you explain why four DAY33 positives are not scorable?
- Can you distinguish unresolved from false negative?
- Can you explain why power-line 50 Hz metadata is synthetic-only?
- Can you explain why poor-contact needs cross-channel data?
- Can you compute coverage, selective recall and effective recall by hand?
- Can you explain phi correlation without calling it clinician agreement?
- Can you state why locked truth is untouched?
- Can you state exactly what DAY35 is allowed to change and what it is not?

If any answer is no, review the corresponding worked example before proceeding.
