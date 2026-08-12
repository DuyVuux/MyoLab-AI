# DAY40 FEYNMAN LEARNING GUIDE — Processing Profile Contracts for sEMG

## 1. Explain DAY40 Like You Are Teaching a Junior Engineer

Imagine you inherit an EMG notebook containing:

```python
x = bandpass(x, 20, 450, fs=2000)
x = notch(x, 50)
x = abs(x)
```

The notebook may run, but it hides many decisions:

- Why 20 Hz?
- Why 450 Hz?
- What if the signal is sampled at 1000 Hz?
- Why 50 Hz rather than 60 Hz?
- Was the signal already filtered?
- Was a dropout masked before filtering?
- Which code version produced the result?
- Did somebody tune those settings on the evaluation set?

DAY40 does not try to answer all the DSP questions at once. It first forces every decision to become **explicit, versioned, testable configuration**.

That is the central idea.

## 2. Analogy: A Laboratory Recipe

A processing profile is like a laboratory recipe.

A bad recipe says:

> “Filter the sample as usual.”

A reproducible recipe says:

> “Use profile X version Y. Input sampling rate is read from the sample metadata. Apply method M with parameters P. Preserve mask Q. Record the output hash.”

If two researchers get different outputs, the second recipe gives enough evidence to ask why.

## 3. Why Configuration Is Part of Scientific Evidence

In biomedical signal processing, code alone is not the experiment. The experiment is roughly:

```text
input data
+ selection rules
+ preprocessing configuration
+ code version
+ environment
= output evidence
```

Changing one cutoff can change MDF, MNF, amplitude, onset timing or even whether a downstream feature exists.

Therefore processing configuration is not “just settings.” It is part of provenance.

## 4. Profile ID versus Fingerprint

Two different concepts are needed.

### Profile ID

Human/logical identity:

```text
research-native-grid-preserve-v0.1
```

### Fingerprint

Exact configuration identity:

```text
pprof_sha256_...
```

Why both?

A profile ID is readable. A fingerprint tells you whether the content is bit-for-bit semantically identical after canonicalization.

If somebody modifies a field but forgets to rename the profile, the fingerprint catches the difference.

## 5. Why Hash Canonical JSON Instead of YAML Bytes

YAML allows formatting differences:

```yaml
a: 1
b: 2
```

and:

```yaml
b: 2
a: 1
```

These should represent the same configuration.

DAY40 therefore hashes canonical JSON after sorting keys. Whitespace and YAML key order do not matter, but semantic values do.

## 6. Raw Grid and Processed Grid

Suppose an EMG signal has:

```text
Fs = 2048 Hz
```

and later somebody resamples it to:

```text
Fs = 1000 Hz
```

If the system stores only “Fs=1000,” you lose acquisition truth.

DAY40 requires both:

```text
native_fs_hz = 2048
processed_fs_hz = 1000
is_resampled = true
```

Raw/native information is historical fact. Processed grid is transformation output.

## 7. Nyquist in One Minute

If sampling rate is `Fs`, frequencies at or above:

\[
F_N = F_s/2
\]

cannot be represented uniquely.

For `Fs=1000 Hz`, Nyquist is `500 Hz`.

Therefore a proposed band-pass high cutoff of `600 Hz` is impossible. DAY40 runtime binding rejects it before a filter is run.

The contract does not yet prove whether 450 Hz is a good cutoff. It only proves whether the proposed cutoff is structurally possible for the input Fs.

## 8. Why 20–450 Hz Is Not Automatically Wrong

A subtle point: DAY40 does **not** say 20–450 Hz is scientifically invalid.

It says:

> Historical familiarity is not sufficient authority to make it a global default.

DAY41 may later verify a 20–450 Hz profile for some research context. The difference is provenance and evidence.

## 9. Why Notch Needs Explicit Mains Frequency

Power-line contamination may be associated with local mains frequency, but signal processing must still know what it is doing.

Bad behavior:

```text
mains unknown
→ assume 50 Hz
→ notch 50 Hz
```

DAY40 behavior:

```text
mains unknown
→ notch disabled
```

or later:

```text
mains explicitly configured = 50 Hz
→ notch profile may be eligible
```

No inference is silently converted into signal modification.

## 10. Q Factor versus Bandwidth

A notch filter needs a width. One way is Q factor:

\[
Q = \frac{f_0}{BW}
\]

where `f0` is the notch center and `BW` is bandwidth.

DAY40 requires either Q or bandwidth, not both, because redundant inconsistent specifications can create ambiguity.

## 11. Why Resampling Is Not “Just Change Array Length”

Downsampling from 2000 Hz to 1000 Hz can fold high-frequency components into the lower band if anti-alias filtering is not used.

This is aliasing.

So a profile that requests decimation must explicitly state an anti-aliasing policy.

DAY40 does not implement the filter. It guarantees the request cannot pretend anti-aliasing is irrelevant.

## 12. Rectification Changes Signal Meaning

Full-wave rectification computes:

\[
y[n] = |x[n]|
\]

After rectification, the waveform is no longer a zero-centered raw sEMG signal. Its amplitude distribution and frequency content have changed.

Therefore rectification must be represented as a processing step, not a hidden helper function.

## 13. Smoothing Is Also a Filter

A moving average may look harmless:

\[
y[n] = \frac{1}{M}\sum_{k=0}^{M-1}x[n-k]
\]

but it changes timing and frequency response.

If you use it to estimate activation envelopes, the window length becomes an experimental parameter.

DAY40 therefore makes `window_ms` explicit.

## 14. Why Normalization Is More Dangerous Than It Looks

Suppose you normalize by MVC:

\[
x_{norm}(t) = \frac{x(t)}{MVC}
\]

What exactly is MVC?

- same participant?
- same day?
- same muscle?
- same electrode placement?
- valid reference trial?

If the denominator is invalid, normalized output can be meaningless.

DAY40 therefore says normalization is disabled and fitting is forbidden. DAY44 will decide eligibility.

## 15. QC and Processing Are Different Layers

A common mistake is:

> “The signal failed QC, but after filtering it looks okay.”

That does not repair the acquisition evidence.

DAY40 preserves:

```text
QC FAIL
→ automatic processing is not authorized
```

Processing may produce a different representation, but it cannot rewrite history and say the raw acquisition was good.

## 16. WARNING Is Not PASS

DAY31 maps WARNING to `HOLD_FOR_REVIEW`.

Therefore DAY40 automatic binding rejects it.

This is not because filtering a warning signal is mathematically impossible. It is because the **workflow authority** has not authorized automatic processing.

Technical possibility and workflow permission are different concepts.

## 17. UNKNOWN Is Not Normal

If upstream says `ABSTAIN`, a processing system must not say:

> “No problem detected, continue with defaults.”

The absence of evidence is not evidence of quality.

DAY40 treats ABSTAIN as no automatic processing authorization.

## 18. Distribution Shift Is Not Artifact

DAY36 established that changed sampling rate, layout or protocol context can mean distribution shift without meaning bad signal.

For deterministic DSP that does not require validated domain support:

```text
QC PASS + SHIFTED
→ processing can still be structurally allowed
```

For a future distribution-sensitive capability:

```text
SHIFTED
→ review
```

That is why `distribution_support_required` belongs to a capability/profile contract rather than global QC.

## 19. Why No OOD Score Exists Here

A common temptation is to compute a distance and call it confidence.

DAY39 explicitly says no validated OOD method exists.

So DAY40 carries only categorical distribution status and never invents:

```text
OOD probability = 0.83
```

without a validated method.

## 20. Masks Protect Evidence

Imagine samples 100–200 are dropout.

Deleting them changes timestamps and can make the signal appear continuous.

Instead:

```text
samples remain
mask marks invalid region
```

Later filtering may cause edge contamination around the masked segment. The processed mask may need to expand, but raw samples and original mask must remain traceable.

## 21. Worked Example A — Safe Native Profile

Input:

```text
Fs = 2048 Hz
unit = uV
QC = PASS
permission = ALLOW_PROFILED_PROCESSING
distribution = SHIFTED
```

Profile:

```text
all transforms disabled
distribution support required = false
```

Result:

```text
native Fs = 2048
processed Fs = 2048
unit remains uV
is_resampled = false
binding allowed
```

Why is SHIFTED allowed? Because this profile performs deterministic identity/preserve behavior and does not claim domain-dependent inference.

## 22. Worked Example B — QC FAIL

Input:

```text
QC = FAIL
processing permission = BLOCK_UNSUPPORTED_METRIC
```

Even if the requested profile is safe:

```text
bind_profile_to_runtime(...)
→ ProcessingProfileAuthorizationError
```

No processed artifact should be created automatically.

## 23. Worked Example C — Invalid Band-Pass for Fs=1000

Proposed:

```text
low = 20 Hz
high = 600 Hz
Fs = 1000 Hz
```

Nyquist:

```text
500 Hz
```

Since 600 >= 500, binding fails.

This is a structural validation, not a clinical decision.

## 24. Worked Example D — Notch with Unknown Mains

Profile:

```text
notch.enabled = true
mains_frequency_hz = null
```

JSON Schema rejects it before runtime.

This is an example of fail-fast configuration validation.

## 25. Worked Example E — Locked Evaluation

A fixed, pre-registered processing profile may be *applied* to locked evaluation data.

What is forbidden is:

```text
look at locked outcome
→ change filter cutoff
→ rerun
```

So:

```text
locked processing != locked fitting
```

DAY40 encodes `locked_partition_fitting_allowed=false`.

## 26. Counterexample — Why Global “EMG Standard Filter” Is Dangerous

Suppose dataset A is 1000 Hz and dataset B is 4000 Hz.

A global 20–450 Hz filter is structurally possible for A because 450 < 500, but only barely leaves transition room. It is also structurally possible for B. Yet the same filter may not be optimal or justified for both tasks.

Protocol-specific configuration allows both commonality and explicit exceptions.

## 27. Counterexample — Cleaning Dropout into Smooth Signal

If a dropout region is interpolated before QC evidence is preserved, downstream users may see a smooth waveform and assume it was observed.

DAY40 prevents this architectural mistake by requiring masks and provenance, even though interpolation itself is not implemented here.

## 28. Separation of Concerns

DAY40 uses a deliberately small architecture:

```text
JSON Schema
→ static structural validation

profile_contract.py
→ semantic + runtime-dependent validation

later DSP modules
→ actual numeric transformation
```

Why not put everything in JSON Schema?

Because constraints like `high_cut < Fs/2` depend on runtime input.

Why not put everything in filter code?

Because then invalid configuration is discovered too late and configuration semantics become coupled to numerical implementation.

## 29. What Does “Protocol-Specific” Mean Today?

It does not mean hard-code “Vinmec protocol A.”

It means profiles require explicit runtime context and are versionable by protocol when evidence becomes available.

DAY40 chooses a portable base profile because the project is now an independent research continuation and does not possess validated site protocol authority.

## 30. What Not to Learn from DAY40

Do not conclude:

- “No preprocessing is best.”
- “20–450 Hz is bad.”
- “Notch filters should never be used.”
- “Resampling should never happen.”
- “Distribution shift does not matter.”

The correct conclusion is:

> Every transformation needs explicit authority, parameters, provenance and verification.

## 31. Flashcards

1. **Q:** Highest DAY40 claim? **A:** `PROCESSING_PROFILE_CONTRACT_READY`.
2. **Q:** Does DAY40 implement band-pass? **A:** No.
3. **Q:** Why fingerprint a profile? **A:** Exact reproducibility/identity.
4. **Q:** Silent Fs default allowed? **A:** No.
5. **Q:** Silent mains frequency allowed? **A:** No.
6. **Q:** Can QC FAIL be auto-processed? **A:** No.
7. **Q:** Can WARNING auto-process? **A:** No, hold for review.
8. **Q:** Can locked data be processed with a fixed profile? **A:** Yes.
9. **Q:** Can locked data be used to fit/tune the profile? **A:** No.
10. **Q:** Does SHIFTED mean artifact? **A:** No.
11. **Q:** Does SHIFTED always block deterministic DSP? **A:** No.
12. **Q:** Is OOD score produced? **A:** No.
13. **Q:** Raw data deleted after masking? **A:** Never.
14. **Q:** Is normalization reference inferred? **A:** No.
15. **Q:** What must enabled notch declare? **A:** Mains frequency and Q or bandwidth.
16. **Q:** Runtime band-pass safety bound? **A:** `high_cut < Fs/2`.
17. **Q:** Resampling must record what? **A:** native Fs, processed Fs, resampling flag.
18. **Q:** Why canonical JSON? **A:** Formatting-independent fingerprint.
19. **Q:** Is public data clinical evidence? **A:** No.
20. **Q:** What day verifies band-pass analytically? **A:** DAY41.

## 32. Beginner Exercises

### Exercise 1

A signal has Fs=800 Hz. Can a profile request high cutoff 450 Hz?

**Answer:** No. Nyquist is 400 Hz.

### Exercise 2

QC permission is `HOLD_FOR_REVIEW`. The filter parameters are valid. Can automatic processing run?

**Answer:** No. Workflow authorization precedes numerical validity.

### Exercise 3

The active profile receives unit `mV`, but allowed units are V/uV. What should happen?

**Answer:** Fail closed with unsupported input-unit error unless an explicit unit-conversion contract exists upstream.

## 33. Intermediate Exercises

### Exercise 4

Design a notch profile for a known 60 Hz environment. What fields must be explicit?

**Expected:** enabled, method, 60 Hz center, Q or bandwidth, version, parameter origin, effect metadata, fingerprint.

### Exercise 5

Why is `processed_fs_hz` needed when resampling is disabled?

**Expected:** downstream consumers can use a uniform output contract and verify that native and processed grids are identical.

## 34. Integration Exercise

You want to enable band-pass on DAY41.

List what must change without breaking DAY40.

**Expected answer:**

1. create new profile version;
2. enable band-pass explicitly;
3. fill method/cutoffs/order/phase;
4. set evidence/parameter authority from DAY41 analytical results;
5. update effect metadata;
6. recompute fingerprint;
7. validate against each runtime Fs/Nyquist;
8. preserve QC authorization, masks and raw immutability;
9. keep old DAY40 profile reproducible.

## 35. Quiz

1. Why does DAY40 use a no-op active profile?
2. What is the difference between static schema validation and runtime semantic validation?
3. Why can a fixed profile be applied to locked data but not fitted on it?
4. Why is a filter cutoff a provenance field?
5. Why must a disabled step keep parameters null?
6. Why is mask deletion forbidden?
7. When can SHIFTED still process?
8. Why is a 50 Hz default forbidden?
9. What makes a profile site-specific?
10. What does a fingerprint protect against?

### Answers

1. To avoid promoting unverified legacy DSP settings into defaults.
2. Schema checks structure; runtime validation checks input-dependent constraints such as Nyquist and authorization.
3. Evaluation requires applying pre-registered logic, but fitting on outcomes causes leakage.
4. It changes numerical/physiological representation and downstream metrics.
5. To prevent dormant hidden defaults from becoming active accidentally.
6. It changes time alignment and destroys evidence.
7. When the capability/profile does not require validated distribution support and QC permits processing.
8. Mains frequency must be explicit evidence/config, not assumption.
9. Embedding a site name/config/threshold without authorized site evidence.
10. Unrecorded semantic configuration drift.

## 36. Teach-Back Checklist

You are ready for DAY41 if you can explain without notes:

- why processing permission is separate from DSP validity;
- why native and processed grids are separate;
- how profile fingerprints work;
- why disabled transform parameters are null;
- how Nyquist validation depends on runtime Fs;
- why locked processing is different from locked fitting;
- why SHIFTED is not QC FAIL;
- why DAY40 does not make any filter performance claim.

## 37. Final Mental Model

Remember this chain:

```text
QC tells us whether processing is authorized.
Profile tells us exactly what processing is requested.
Runtime context tells us whether that request is structurally valid.
DSP implementation later proves whether the transform is numerically correct.
Provenance tells us exactly what happened.
```

DAY40 freezes the second and third parts of that chain so later DSP work cannot silently rewrite the rules.
