# DAY35 FEYNMAN LEARNING GUIDE — Threshold Sensitivity Without Fake Clinical Validation

## 1. The One-Sentence Idea

A detector threshold is not “true” because a grid search found a number. DAY35 teaches how to ask a safer question: **given a clearly defined research fixture set, how does detector behavior change as the operating point changes, and which reversible research setting is least surprising while preserving safety constraints?**

## 2. Simple Mental Model

Imagine a smoke alarm. Turning the sensitivity up catches smaller amounts of smoke but may alarm on cooking steam. Turning it down reduces nuisance alarms but may miss a real fire. There is no universal correct dial position independent of building, sensor, environment and consequence. sEMG artifact thresholds behave similarly. A number such as `powerline_warning_ratio = 0.08` is an operating point, not a biological law.

DAY35 therefore separates three things:

```text
Detector feature
≠ Threshold
≠ Evidence authority of the threshold
```

A power-line band-power ratio is a measured feature. `0.08` is a policy boundary. `RESEARCH_HEURISTIC` tells us how much authority the boundary has.

## 3. Why DAY34 Had To Come First

Suppose your benchmark says a 250 ms window contains clipping, but the injected clipping is actually 150 ms earlier than the window. The detector returns PASS. If you call that a false negative and lower the clipping threshold, you are optimizing the detector to compensate for a mislabeled benchmark. This is worse than having no threshold study at all.

DAY34 caught exactly this type of problem for missing/zero-dropout/flatline/clipping. DAY35 does not edit DAY33. It creates a new versioned fixture family with exact event bounds overlapping the target core. This is a practical lesson in ML/DSP engineering: **data quality of the benchmark is part of algorithm quality.**

## 4. Vocabulary

- **Operating point:** one chosen threshold configuration.
- **Sensitivity:** among positives, fraction detected.
- **Specificity:** among negatives, fraction correctly left negative.
- **Precision:** among predicted positives, fraction that are positive.
- **False allow:** a bad/positive engineering condition incorrectly allowed as negative.
- **False block:** a negative/acceptable engineering condition incorrectly flagged.
- **Scorable truth:** a reference label valid for the detector target scope.
- **Truth localization:** where the injected condition occurs relative to the evaluation window.
- **Research heuristic:** a reversible engineering setting supported only for research/prototyping.
- **Site-not-verified:** a setting not justified for a real acquisition site.
- **Locked evaluation:** data whose outcomes are intentionally not used during tuning.

## 5. Thresholds Are Policy, Not Physics

Some quantities are physical or mathematical. Sampling rate is measured in Hz. A time interval is measured in seconds. A spectral ratio can be computed deterministically. The decision that a ratio above 0.08 should produce a warning is a policy decision layered on top of the measurement.

This distinction matters because policy depends on intended use and error costs. A research demo can explore operating points. A clinical workflow would need representative evidence, review of false-allow/false-block consequences, device/protocol context and formal approval. DAY35 only has the former.

## 6. The Evidence Ladder for Thresholds

DAY35 uses:

### `DEVICE_KNOWN`
A hardware fact verified from trusted device metadata. Example: a truly verified ADC rail. DAY35's `-1/+1` clipping rails are **not** device-known; they belong only to the synthetic fixture.

### `ANALYTICAL`
A property proven by mathematics or controlled numerical verification. Example: a filter's gain at a frequency under a specified implementation.

### `RESEARCH_HEURISTIC`
A setting chosen from research development evidence. All selected DAY35 detector thresholds live here.

### `SITE_NOT_VERIFIED`
No site-specific authority exists. Every site-template threshold remains here.

## 7. Development vs Locked Evaluation

The temptation in a small project is to inspect every example because there are so few. That destroys the meaning of final evaluation. DAY33 created six locked items with hidden truth commitments. DAY35 may count that six sealed items exist, but it may not consume outcomes.

Think of the locked set like the answer key to an exam. You are allowed to verify that the envelope exists. You are not allowed to open it while choosing your method.

## 8. Why We Created DAY35 Fixtures Instead of “Fixing” DAY33

Historical evidence should be immutable. If DAY33 had a geometry defect, rewriting it would erase the provenance of DAY34's finding. Instead:

```text
DAY33 v0.1
  retained as historical evidence

DAY34
  detects truth-window defect

DAY35 aligned fixture v0.1
  new evidence source
```

This is the same principle as database migrations and model versioning: repair by adding a new version, not by silently rewriting the past.

## 9. Worked Example 1 — Missing Samples

A 250 ms core at 2000 Hz contains 500 samples. A missing-warning threshold of 1% means roughly five non-finite samples can trigger warning evidence. DAY35 creates controls below its engineering positive definition and positives at larger fractions, all inside the core.

The sweep tests multiple warning fractions. If several values produce the same confusion counts, the tie-break chooses the value closest to the upstream provisional configuration. That is conservative configuration management, not proof that the upstream number is universally correct.

## 10. Worked Example 2 — Zero-Run Dropout

A zero run is different from scattered missing values. The detector uses the longest zero run divided by core length. A 25% warning threshold on a 500-sample core corresponds to a run of about 125 samples.

A zero can be physiologically plausible after preprocessing or in certain device behaviors, so this remains heuristic evidence. The important property is deterministic behavior under a declared contract.

## 11. Worked Example 3 — Flatline

Flatline uses peak-to-peak amplitude. If peak-to-peak is below epsilon, the rule emits a fail candidate. Epsilon is especially scale-sensitive: V vs uV or prior normalization can change its interpretation dramatically. That is why DAY35's value cannot be promoted to a generic site threshold.

## 12. Worked Example 4 — Clipping

DAY24 correctly refuses strong device-truth clipping claims when ADC semantics are unknown. For DAY35 engineering study we deliberately create synthetic rails `[-1,+1]` and set ADC semantics VERIFIED **inside that synthetic universe only**. The detector can then test whether repeated extrema and plateaus are detected.

The lesson: sometimes you need a controlled artificial universe to test logic, but you must not confuse its constants with real hardware constants.

## 13. Worked Example 5 — Baseline Noise

Baseline noise is protocol-dependent. A low-amplitude active muscle is not automatically rest. DAY35 creates a synthetic baseline reference explicitly, so the detector is allowed to compute descriptors and apply synthetic thresholds.

The selected RMS/MAD values happen to match the earlier synthetic profile. This means the DAY35 synthetic study provides no reason to change them. It does not mean those values should be applied to every muscle, task, device or patient.

## 14. Worked Example 6 — Power-Line

Power-line evidence uses spectral energy around the known mains frequency and harmonics relative to total band power. In DAY35 the fixture explicitly declares 50 Hz. The detector is configured `site_config_status=VERIFIED` only because the **synthetic generator itself** is the source of truth.

If a real site frequency were unknown, the correct result would remain abstention/unknown rather than guessing 50 Hz from geography.

## 15. Worked Example 7 — Motion Artifact

Motion detection combines low-frequency spectral ratio, normalized drift and derivative transient evidence. The decision is an OR-like warning: any sufficiently strong component can trigger suspicion. This creates a multidimensional threshold surface rather than a single scalar threshold.

DAY35 sweeps a small explicit grid. It does not use Bayesian optimization or a neural model because the goal is inspectability.

## 16. Why Poor Contact Is Different

Poor contact is causal ambiguity. Low RMS could mean bad electrode contact, but it could also mean low activation, muscle weakness, anatomy, task execution or physiology. DAY28 therefore asks for peer-channel and corroborating artifact context. DAY35's single-channel synthetic corpus cannot supply that context.

The correct engineering result is:

```text
HOLD_NOT_SCORABLE
```

This is stronger work than inventing a threshold just to fill a YAML file.

## 17. False-Allow vs False-Block

In QC research:

- false allow = a known synthetic artifact passes;
- false block = a synthetic control is flagged.

But those terms are evidence-tier specific. A false allow on synthetic clipping is not automatically a clinical safety event. It is an engineering proxy used to understand detector behavior.

## 18. Why DAY35 Weights FN Higher

The selection formula weights synthetic false negatives three times more than false positives. This encourages sensitivity in a QC research context. However, `3:1` is not a medically validated loss ratio. It is simply written down so the engineering choice is inspectable and replayable.

A future clinical study might choose a different policy after studying consequences and workflow burden.

## 19. What Does “1.0 Sensitivity” Mean Here?

If a family has two positive synthetic fixtures and catches both, sensitivity is 1.0. Mathematically true. Scientifically, the denominator is tiny and narrow.

Correct statement:

> The selected research configuration detected all 2/2 constructed positive fixtures in this synthetic stratum.

Incorrect statement:

> The detector has 100% sensitivity.

The second sentence hides the population and would mislead a reader.

## 20. Fs and Window Duration

Detector features can depend on sample count, FFT resolution and temporal structure. Therefore DAY35 replays selected thresholds at 1000/2000/4000 Hz and 250/500 ms. The exercise is not to retune each stratum; it is to see whether the same configuration breaks obviously.

The synthetic robustness results are clean, but they remain constructed data. Real electrodes, device filters and movement spectra can behave differently.

## 21. Why the Selected Values Did Not Change

Every selected research value equals the earlier provisional value. This could look suspicious until you inspect the tie-break rule. Several thresholds can perfectly separate the deliberately spaced synthetic levels. Among equal-risk candidates, DAY35 chooses the closest upstream value to avoid unnecessary configuration drift.

This is a **configuration-management decision**, not circular validation. The actual evidence is the entire sensitivity table, not just the final point.

## 22. Counterexample — Optimizing on Misaligned Truth

Suppose clipping is injected outside the core. Every threshold appears to miss it. An optimizer would drive `repeated_extrema_fraction` downward, perhaps until clean waveforms are falsely flagged. The true problem was scope mismatch, not sensitivity. This demonstrates why a truth-applicability gate should precede threshold tuning.

## 23. Counterexample — Guessing Site Mains Frequency

A 50 Hz fixture is not evidence that every future site is 50 Hz. If configuration is unknown, abstention is safer than automatic geographic inference. Metadata should provide the setting.

## 24. Counterexample — Treating Low Amplitude as Poor Contact

If a very weak signal is flagged poor contact solely because RMS is low, a patient with genuine low activation could be mislabeled as acquisition failure. DAY35 refuses to select poor-contact thresholds without multi-channel corroboration.

## 25. Counterexample — Tuning the Locked Set

If you inspect locked outcomes to choose `0.06` instead of `0.08`, later evaluation no longer measures generalization. It measures your memory of the answer key. DAY35 has a hard zero-consumption rule.

## 26. Common Junior Mistakes

1. Reporting percentage without numerator/denominator.
2. Treating a synthetic constant as a device specification.
3. Calling a parameter grid “ROC validation” without explaining truth definition.
4. Converting UNKNOWN to PASS to simplify metrics.
5. Tuning every available example.
6. Changing historical fixtures in place.
7. Assuming a best threshold is unique.
8. Ignoring unit scale.
9. Using clinician words like “validated” for engineer-selected values.
10. Filling unsupported poor-contact parameters because the config schema has a field.

## 27. What Not To Learn From DAY35

Do not learn that `0.08`, `0.22`, or `0.0002` are universal sEMG constants. Do not learn that synthetic 1.0 metrics predict hospital performance. Do not learn that threshold tuning replaces expert review. The lesson is governance and reproducible sensitivity analysis.

## 28. Exercise — Manual Threshold Table

Given truth `[0,0,1,1]` and feature values `[0.02,0.05,0.09,0.20]`, evaluate thresholds 0.04, 0.08, 0.15. Compute TP/FP/TN/FN, sensitivity and specificity. Then apply weighted error `3×FN + FP`. Notice that multiple thresholds may tie depending on spacing.

## 29. Exercise — Window Localization

Draw a 2000-sample timeline, core `[1000,1500)`, and event `[666,866)`. Explain why the event is in context but not valid core truth. Move it to `[1100,1300)` and repeat.

## 30. Exercise — Evidence Classification

Classify each statement:

- “The synthetic generator clipped at +1.” → synthetic fixture fact.
- “The Noraxon ADC rail is +1.” → unsupported unless vendor/device evidence exists.
- “0.10 repeated-extrema fraction separates our DAY35 fixtures.” → research heuristic evidence.
- “0.10 is clinically safe.” → unsupported.

## 31. Exercise — Leakage Review

Design a command-line guard that rejects `partition=benchmark-locked`. Explain why merely promising not to tune is weaker than enforcing the rule in code.

## 32. Exercise — Poor Contact

List at least four alternative causes of low channel amplitude. Then design a minimal multi-channel synthetic fixture that could provide stronger evidence for poor contact without pretending to model pathology.

## 33. Flashcards

1. **Q:** What is the highest DAY35 claim? **A:** `RESEARCH_THRESHOLDS_FROZEN_V0.1`.
2. **Q:** Site threshold status? **A:** `NOT_VERIFIED`.
3. **Q:** Locked items consumed? **A:** Zero.
4. **Q:** Why not mutate DAY33? **A:** Preserve evidence history/provenance.
5. **Q:** Threshold evidence class? **A:** `RESEARCH_HEURISTIC` for selected research values.
6. **Q:** Poor-contact status? **A:** `HOLD_NOT_SCORABLE`.
7. **Q:** Synthetic ADC rail equals device rail? **A:** No.
8. **Q:** Synthetic 50 Hz equals site frequency? **A:** No.
9. **Q:** UNKNOWN equals PASS? **A:** No.
10. **Q:** Why Fs robustness? **A:** Features can depend on sample rate/resolution.
11. **Q:** Why window-duration robustness? **A:** Temporal/spectral statistics change with window length.
12. **Q:** Why weighted error? **A:** Explicit research preference for false-allow avoidance.
13. **Q:** Is 3×FN a clinical cost? **A:** No.
14. **Q:** Why tie-break toward upstream? **A:** Avoid needless configuration churn when evidence ties.
15. **Q:** Can public data be tuned now? **A:** Not until payload/adapters and partition governance exist.
16. **Q:** What makes truth scorable? **A:** Correct evidence tier and valid scope/localization/applicability.
17. **Q:** What is a false block? **A:** Negative control flagged positive within the defined evidence tier.
18. **Q:** What is a false allow? **A:** Positive engineering condition not flagged.
19. **Q:** Does DAY35 train ML? **A:** No.
20. **Q:** Does DAY35 validate clinical effectiveness? **A:** No.

## 34. Quiz

1. Why is threshold authority separate from threshold value?
2. Why are DAY35 repaired fixtures versioned separately?
3. What would invalidate the locked evaluation?
4. Why can clipping use synthetic verified ADC semantics without becoming device verified?
5. Why is baseline noise protocol-specific?
6. Why is poor contact held?
7. What does the sensitivity table prove?
8. Why is the site-template all null?
9. Why replay across Fs/window duration without retuning?
10. What is the meaning of `RESEARCH_HEURISTIC`?
11. Why does 1.0 sensitivity need denominator context?
12. What happens if UNKNOWN is mapped to PASS?
13. What is the primary DAY34→35 lesson?
14. Why avoid “clinical optimum” wording?
15. What does the tie-break accomplish?

### Answers

1. A number can be reproducible without being clinically/site authorized.
2. To preserve historical evidence and make the repair traceable.
3. Looking at outcomes while choosing thresholds.
4. The fixture defines its own artificial universe; no real-device claim is made.
5. Noise depends on task/reference/acquisition conditions.
6. Current evidence lacks multi-channel peer context and positive truth.
7. Behavior on declared synthetic development fixtures only.
8. There is no site validation authority after project discontinuation.
9. To detect obvious implementation sensitivity without hiding it by per-stratum tuning.
10. A reversible research operating point, not clinical policy.
11. Small constructed denominators do not support broad generalization.
12. Fail-closed semantics are destroyed and performance is biased.
13. Validate truth applicability before threshold tuning.
14. No clinical cohort/clinician/site approval exists.
15. It keeps stable upstream defaults when several candidates are equally supported.

## 35. Teach-Back Checklist

You are ready to leave DAY35 when you can explain, without notes:

- why DAY34's misalignment changed the DAY35 execution order;
- why a threshold can be selected and still remain unverified clinically;
- how locked evaluation differs from development evidence;
- why the site-template contains no numbers;
- why poor-contact cannot be filled in;
- what the sensitivity table and robustness table do and do not prove;
- how the same code can support future stronger evidence without changing the claim hierarchy.

## 36. Final Mental Model

```text
Correct target scope
    +
Known evidence authority
    +
Development-only sensitivity study
    +
Explicit error preference
    +
Reproducible selection
    +
Locked-set isolation
    =
Useful research threshold

Useful research threshold
    ≠
Clinical/site threshold
```

That distinction is the core lesson of DAY35.

## 37. A Deeper Look at Threshold Curves

When a detector produces one scalar feature, a threshold sweep can be pictured as moving a vertical line across the feature axis. Every time the line crosses an example, the confusion matrix can change. With a tiny dataset, the curve is a staircase, not a smooth estimate of a population distribution. This is why DAY35 stores every candidate row instead of only the selected one. The table lets you see whether the “best” value is a broad stable region or a knife-edge choice.

For the multidimensional motion detector, there is not one line but a decision surface. A warning occurs when any of several criteria is exceeded. Grid search samples a few surfaces. The same caution applies: an attractive point on four synthetic items is a test of logic, not an estimate of real-world optimum.

## 38. Stable Region vs Lucky Point

Suppose thresholds 0.06, 0.08 and 0.10 all produce identical TP/FP/TN/FN. Selecting 0.08 because it matches the previous config is safer than claiming the data “estimated 0.08.” The data only tell you that this interval is indistinguishable on the current fixtures. The tie-break contributes the final choice. A mature report states both facts.

By contrast, if only one exact candidate works and adjacent values fail badly, the operating point is brittle. That should trigger more fixture design before freezing even a research profile.

## 39. Why Known-Truth Synthetic Data Is Still Valuable

Synthetic data is weak for external validity but strong for controlled causality. When you inject exactly 30% zero run into the core, you know what changed and where. When you add 50 Hz sinusoidal interference, the generator controls the cause. This makes synthetic data excellent for known-answer, metamorphic and boundary tests.

The mistake is not using synthetic data. The mistake is asking synthetic data to answer a question it cannot answer, such as prevalence, clinical acceptability or patient-specific artifact distribution.

## 40. Metamorphic Thinking for Thresholds

A metamorphic test asks how output should change when input is transformed in a controlled way. Examples:

- increase missing fraction while all else stays fixed → dropout evidence should not become less severe;
- increase repeated clipping plateau fraction → clipping suspicion should not disappear;
- increase 50 Hz amplitude → power-line ratio should generally increase under the same signal background;
- increase baseline noise sigma → RMS/MAD descriptors should increase statistically;
- increase slow drift amplitude → motion evidence should not systematically decrease.

These properties can catch implementation bugs even when an exact threshold is not validated.

## 41. Threshold Monotonicity Is Not Always Simple

Do not assume every spectral metric is perfectly monotonic with an injected amplitude. Windowing, spectral leakage, harmonics and normalization can cause non-linear behavior. The correct approach is to test the feature and decision under controlled increments, not to hard-code a mathematical expectation that the implementation does not guarantee.

## 42. Units as a Hidden Threshold Dimension

Consider an amplitude threshold stored as `0.0002`. Is that volts, millivolts, microvolts, normalized units, or arbitrary synthetic amplitude? Without a unit/provenance contract the number is meaningless. DAY13 already established controlled unit handling; DAY35 depends on that discipline. Threshold files should never be copied between raw representations by visual similarity.

## 43. Window Duration as a Statistical Parameter

A 250 ms window at 2000 Hz has 500 samples. A 500 ms window has 1000. Longer windows can stabilize spectral estimates but blur short events. Shorter windows improve temporal localization but can reduce frequency resolution. Therefore the “threshold” is really part of a larger detector configuration that includes windowing. DAY35's robustness replay reminds us not to isolate the scalar from its context.

## 44. Sampling Rate and Nyquist Context

Power-line and motion spectral features depend on the available frequency axis. At 1000 Hz, Nyquist is 500 Hz; at 4000 Hz it is 2000 Hz, although the detector may cap total-band analysis at 450 Hz. Changing Fs alters bin spacing and number of samples. If a threshold works at multiple Fs in synthetic replay, that is useful regression evidence, but the device anti-aliasing/filter chain still matters in real data.

## 45. Why We Do Not Tune Fail Thresholds Today

The dropout rule has warning and fail thresholds. DAY35 holds existing fail boundaries fixed and studies warning sensitivity. This reduces dimensionality and prevents the day from redesigning safety semantics under insufficient evidence. A later error-analysis phase could justify studying fail boundaries if it has stronger evidence and explicit risk objectives.

## 46. Confidence Intervals and Why They Are Not the Main Story Here

With two positive fixtures, a point estimate of 1.0 sensitivity has enormous uncertainty as a population estimate. One could calculate a binomial confidence interval, but that might create a false aura of statistical generalization because the fixtures were not sampled from a target population. The more honest approach is to report counts and evidence-generation process. Statistical intervals become meaningful when evaluation items are sampled under a defensible population protocol.

## 47. Research Profile vs Default Product Profile

A research profile is opt-in evidence for experimentation. A product/site profile drives real workflow behavior. Mixing them is dangerous because a developer may think, “The number exists, so let's use it.” DAY35 prevents this by giving the site profile a structurally different state: null numerical values plus `SITE_NOT_VERIFIED`.

## 48. Why Null Is Better Than a Placeholder Number

A placeholder like `0.08` in a site config often survives longer than intended. Months later nobody remembers whether it was a guess, literature value or validated setting. `null + NOT_VERIFIED` forces downstream code to handle the absence explicitly. This is the threshold analogue of DAY31's fail-closed metric handoff.

## 49. Future Evidence Upgrade Path

A future threshold could gain stronger authority through a chain such as:

```text
RESEARCH_HEURISTIC
  ↓ external public benchmark
RESEARCH_EXTERNAL_EVIDENCE
  ↓ expert/site study under approved protocol
SITE_EVIDENCE_CANDIDATE
  ↓ formal review / intended-use scope decision
APPROVED_FOR_DEFINED_SCOPE
```

The names may evolve, but the principle is monotonic evidence authority: stronger claims require stronger evidence, not just more code.

## 50. Why DAY36 Needs DAY35 But Must Not Worship It

DAY36 uses the research thresholds to stress the system across amplitude, morphology, Fs, layout and context changes. Its job is partly to show where the threshold profile fails. Therefore DAY36 should treat DAY35 as a fixed test configuration, not as truth. If a physiology-preservation sentinel is blocked, the correct response may be to expose the limitation rather than immediately retune DAY35.

## 51. Interview Explanation in 60 Seconds

A concise explanation is:

> “We originally had provisional QC thresholds. Before tuning them I built a synthetic known-truth benchmark, and the evaluation found that some corruption labels were outside the actual target window. I quarantined those cases, created a versioned aligned fixture set, then ran detector-specific sensitivity sweeps only on development evidence. I kept a sealed locked set untouched, selected reversible research operating points with an explicit false-negative-weighted objective, tested them across sampling rates/window sizes, and deliberately left the site config null because we had no clinical/site validation.”

This tells an interviewer much more about engineering maturity than saying “I tuned thresholds.”

## 52. Advanced Exercise — Build a Stability Map

For one scalar detector, plot threshold on x-axis and weighted error on y-axis. Mark all zero-error candidates and the selected point. Answer:

- How wide is the stable region?
- Is the selected point near an edge?
- Would a small numerical change matter on the current fixtures?
- Does the answer justify more fixture density around a boundary?

## 53. Advanced Exercise — Design Better Power-Line Fixtures

Current fixtures use a few discrete interference amplitudes. Design a new set that varies:

- line amplitude;
- base EMG spectral content;
- phase;
- 50 vs 60 Hz synthetic metadata;
- harmonic content;
- window duration.

Then explain which variants test algorithm mechanics and which begin to approximate external validity.

## 54. Advanced Exercise — Multi-Channel Poor Contact

Construct four synthetic channels with similar task activation. On one channel attenuate signal amplitude while also injecting contact-like broadband/line-noise evidence. Keep a second condition with low amplitude but no corroborating artifact. The desired policy should distinguish “poor-contact suspected” from “low activation cause unresolved.” This would create a defensible future research fixture without pretending either condition is a disease model.

## 55. Advanced Exercise — Configuration Migration

Imagine v0.2 changes the power-line warning ratio after public benchmark analysis. Write a migration record that preserves:

- v0.1 result replay;
- reason for change;
- new evidence source;
- affected protocols;
- rollback path;
- statement that the change still does not imply clinical validation.

## 56. Final Feynman Test

If you can explain why `0.08` can simultaneously be:

1. reproducibly selected on synthetic development data,
2. useful in a research demo,
3. stable across the tested synthetic Fs/window strata,
4. and still **not** be an approved site threshold,

then you understand DAY35.
