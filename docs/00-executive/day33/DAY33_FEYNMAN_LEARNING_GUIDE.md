# DAY33 FEYNMAN LEARNING GUIDE — Research Benchmark Corpus Engineering

## 1. DAY33 in one sentence

DAY33 teaches you how to build a **research corpus whose evidence authority, licensing, provenance,
partitions and synthetic truth are explicit before any model or detector evaluation starts**.

A junior engineer often thinks a dataset is simply a folder containing arrays. In a serious
biomedical project, a dataset is closer to a legal-and-scientific contract. You need to know where it
came from, what the labels mean, what license permits, what was transformed, whether the same person
leaks into train/evaluation, whether a sample is synthetic, and exactly what you are allowed to
claim from the result.

## 2. The central analogy: evidence passports

Imagine every signal window crossing a border. The waveform is the traveler; the manifest is its
passport. A passport does not say the traveler is healthy or sick. It says identity, origin and
permission. Likewise, a dataset DOI/license tells you source/provenance, not clinical truth.

DAY32 created the **authority ladder**. DAY33 gives each research source a passport and prevents
engineers from stamping a stronger authority level onto it just because the data looks convenient.

## 3. Four concepts that must never be merged

### 3.1 Source provenance

This answers: *Where did the signal originate?* Examples are public external dataset, synthetic
fixture or organizational engineering sample.

### 3.2 License/governance

This answers: *What are we allowed to do with it?* Open download does not automatically mean
redistribution, commercial reuse or unrestricted derivatives.

### 3.3 Annotation authority

This answers: *Who/what supports this label?* DAY32 defines synthetic known-truth, weak-label
candidate, expert annotation and adjudicated reference.

### 3.4 Claim scope

This answers: *What may a report say?* DAY33 is research-only. Even a perfect detector on synthetic
fault injection does not justify a hospital effectiveness claim.

## 4. Why public data does not become an evidence tier

Suppose GRABMyo has a label saying gesture 7. That label is authoritative for the original gesture
protocol according to its dataset documentation. It is **not** an expert annotation that a window is
free from power-line noise. If your QC rule later calls the same window `POWERLINE_SUSPECTED`, that is
`WEAK_LABEL_CANDIDATE`. If a qualified human reviews the signal, that new act may create
`EXPERT_ANNOTATION`. Dataset provenance and QC annotation authority are orthogonal dimensions.

This is why DAY33 keeps public sources in `public_sources` and uses the four DAY32 tiers only for
actual annotation/corpus items.

## 5. Why we do not put 9 GB or 135 GB into Git

Source data is not source code. GRABMyo is roughly gigabyte-scale; Hyser is much larger. Copying raw
payload into Git causes slow clones, duplicate storage, accidental redistribution and difficult
license management. A better architecture stores raw public data in an external data root and puts
only a source ledger into the repository.

The ledger contains relative file name, file size and SHA-256. Thus the project can prove exactly
which bytes were used without publishing those bytes.

## 6. Hashing explained simply

A SHA-256 hash is like a content fingerprint. If one bit changes, the fingerprint should change.
Therefore:

```text
source file bytes
      ↓ SHA-256
64-hex digest
```

The hash does not tell whether the data is correct; it tells whether the data being used now is the
same byte sequence that was registered earlier. Provenance and semantic validation remain separate.

## 7. Why deterministic synthetic data is valuable

Real sEMG has unknown mixtures of physiology, contact conditions, motion and environmental noise.
That makes it difficult to say with certainty where a fault begins and ends. Synthetic corruption
solves a different problem: it gives **known construction truth**.

For example, if you explicitly set samples 700:900 to NaN, you know that a missing-data segment was
injected there. The truth comes from construction, not from a doctor. This makes it excellent for
unit, property and threshold-sensitivity engineering.

But synthetic truth has a strict ceiling: it cannot establish clinical realism.

## 8. Counterexample: low amplitude is not synthetic stroke

Take a waveform and multiply every sample by 0.1. You now know the amplitude is ten times smaller.
You do **not** know that it represents paresis, stroke, atrophy or weak voluntary recruitment. Those
conditions are biological/clinical phenomena involving neural drive, motor-unit recruitment,
anatomy, electrode placement and task context.

Therefore DAY33 names the case `SYNTHETIC_LOW_AMPLITUDE_STRESS`. The signal asks the safety question:
“Will the system wrongly label low amplitude as bad electrode?” It does not ask the clinical
question “Is this stroke?”

## 9. Why WindowIdentity matters in a dataset day

A typical ML tutorial cuts arrays into windows and numbers them 0, 1, 2. That is insufficient for a
traceable signal system. DAY22 creates a deterministic identity from session, channel, source, sample
range, sampling rate and window profile. Context bounds are also carried.

This means an annotation can always say exactly which samples it refers to, and the same input plus
profile reconstructs the same window ID. Random contextless crop IDs are forbidden.

## 10. Native sample grid

DAY33 does not resample, interpolate or filter before creating identity. Synthetic sources use their
native 2000 Hz grid. Later public datasets may be 2048 Hz, 1259 Hz or other rates. The architecture
must preserve the native grid first. Processing profiles belong downstream.

This is important because changing Fs before provenance/window identity can erase facts about the
original acquisition and create hidden alignment assumptions.

## 11. Development versus locked partition

Why do we need a locked partition when we are not training a model yet? Because threshold tuning is
also a form of learning from data. If you repeatedly inspect every synthetic case and choose a
threshold that handles them perfectly, those cases no longer provide an unbiased final check.

DAY33 therefore creates:

```text
benchmark-development → visible truth
benchmark-locked      → hidden truth + commitment
```

The locked partition is a governance rehearsal for DAY81's final evaluation lock.

## 12. What a truth commitment does

For a locked item, DAY33 hashes a canonical tuple containing item ID, hidden scenario and hidden truth
class. The manifest stores only that hash. Later, if the truth is revealed from the controlled source,
we can recompute the hash and show it was not silently changed after seeing algorithm outcomes.

A commitment is not encryption. Anyone reading generator source could infer the schedule. The value
here is **process discipline and tamper evidence**, not adversarial secrecy.

## 13. Worked Example 1 — Missing segment

Input base signal: 2000 samples, 2000 Hz. We inject NaNs over a known sample interval. The source hash
changes. DAY22 WindowIdentity is built on sample coordinates and the item enters the development
partition with:

```text
evidence_tier = SYNTHETIC_KNOWN_TRUTH
scenario      = MISSING
clinical_evidence = false
```

A DAY23 detector may later emit a weak-label candidate. That candidate does not replace the synthetic
truth; they are two evidence objects serving different purposes.

## 14. Worked Example 2 — 50 Hz power line

We add a deterministic 50 Hz sinusoid to the base signal. The construction truth is “a 50 Hz
component was injected.” It is **not** “the signal is unusable.” DAY26 already established that
power-line evidence alone does not automatically block a session. DAY34 can compare whether the
power-line LF notices the injected component while preserving the decision-layer separation.

## 15. Worked Example 3 — Motion drift

A 2 Hz baseline component is added. The truth is low-frequency drift injection. In real clinical
signals, low-frequency power may also occur because of task/physiology. Therefore synthetic success
only tells us the detector recognizes the constructed pattern. DAY36 later asks whether the same rule
false-blocks physiology-preserving stress cases.

## 16. Worked Example 4 — Timestamp duplicate

The signal samples are unchanged; one timestamp is duplicated. This illustrates why signal quality
and data integrity are distinct. A waveform could look beautiful while its timeline is invalid.
DAY29 should detect this structural failure. DAY33 stores the corrupted synthetic time array alongside
the signal without pretending the problem is a spectral artifact.

## 17. Worked Example 5 — Public GRABMyo source

The catalog records DOI, version, CC BY license, subject/session metadata and a canonical source URL.
DAY33 does **not** create a QC truth label from those facts. When raw files are later acquired outside
Git, the registrar hashes them. A future adapter maps verified fields into the canonical session
contract. Only then can WindowIdentity and QC rules produce project-specific evidence.

## 18. Worked Example 6 — Hyser source mismatch

Hyser has 256-channel HD-sEMG. Your MotionLab pipeline may eventually process sparse bipolar
channels. A parser successfully reading Hyser does not prove hardware equivalence. Instead, Hyser is a
useful domain challenge: different layout, channel density and protocol can test supportability and
cross-domain assumptions.

## 19. Counterexample — downloadability is not license verification

A URL returning a ZIP proves access, not legal reuse. A dataset might require attribution,
non-commercial use, a DUA, or prohibit redistribution. DAY33 therefore uses an explicit
`license_status`. `NOT_VERIFIED` is not converted to `VERIFIED` because a browser can download it.

## 20. Counterexample — CC BY is not clinical validation

A permissive license answers a legal reuse question. It says nothing about whether the cohort matches
MotionLab patients, whether the electrode layout is comparable or whether a detector is clinically
safe. Legal permission and external validity are independent axes.

## 21. Counterexample — public fatigue rating is not diagnosis

The Cerqueira source contains self-perceived fatigue ratings. These are useful research context. They
are not a diagnosis of neuromuscular fatigue and are not a site-specific threshold reference for
MotionLab. A future analysis must preserve the exact label semantics and evaluate what inference is
actually supported.

## 22. Common junior mistakes

1. Put every dataset in one folder named `raw/` inside Git.
2. Call dataset labels “ground truth” without defining which task the truth refers to.
3. Mix synthetic and public windows then report one pooled accuracy.
4. Create random windows without source/sample identity.
5. Use one subject's windows in both development and evaluation.
6. Tune thresholds on the locked set because “it is not ML training.”
7. Convert unknown unit/Fs metadata into a convenient default.
8. Call scaled amplitude “stroke simulation.”
9. Treat open access and open license as synonyms.
10. Forget that attribution/version/DOI belong in the evidence chain.
11. Report accuracy on public data without a compatible QC reference label.
12. Hide abstentions/missing evidence by replacing them with PASS or zero.

## 23. What not to learn from DAY33

Do not learn a universal QC threshold. Do not learn a disease classifier. Do not infer electrode
contact from amplitude alone. Do not select an SSL architecture. Do not benchmark a model. DAY33 is
primarily about **data authority and benchmark mechanics**.

## 24. A useful mental model: three ledgers

Think of the research corpus as three ledgers:

### Source ledger
Dataset ID, version, DOI, license and source hashes.

### Transformation ledger
What deterministic corruption or processing changed the data?

### Evidence ledger
Who/what supports a label and at what authority tier?

A trustworthy result needs all three.

## 25. Why `null + reason` appears in dataset engineering

Suppose a public dataset card does not verify sampling rate from the primary page inspected today.
The correct field is `null` plus a note such as `NOT_VERIFIED_IN_DAY33`, not a value copied from memory.
The project has already used this fail-closed principle for metrics; DAY33 applies it to metadata.

## 26. Why public payload acquisition is deliberately deferred

Downloading Hyser would bring more than a hundred GB into the workspace. DAY33's goal can be achieved
without that operational cost: verify source/legal metadata, design the acquisition ledger, generate
synthetic corpus and test the contracts. Later public benchmark phases can acquire only the required
subsets with exact hashes.

This is an optimization: **evidence first, bytes second**.

## 27. Flashcards

1. **Q:** What does a DOI prove? **A:** Stable scholarly/resource identity, not clinical validity.
2. **Q:** What does CC BY require? **A:** Reuse under attribution conditions; preserve exact license terms.
3. **Q:** Does open access imply open license? **A:** No.
4. **Q:** What is DAY33's actual payload evidence tier? **A:** `SYNTHETIC_KNOWN_TRUTH`.
5. **Q:** Why not `PUBLIC_EXTERNAL_EVIDENCE` as a DAY32 tier? **A:** It is a source/evidence class, not one of the frozen annotation-authority tiers.
6. **Q:** What identifies a QC window? **A:** DAY22 WindowIdentity and profile fingerprint.
7. **Q:** Why context? **A:** Artifact/physiology interpretation can depend on surrounding signal/task.
8. **Q:** What is a source hash? **A:** Content fingerprint for exact-byte provenance.
9. **Q:** Can synthetic truth be expert truth? **A:** No.
10. **Q:** Is amplitude scaling a stroke simulator? **A:** No.
11. **Q:** Why hide locked truth? **A:** Prevent tuning/selection leakage.
12. **Q:** Is a truth commitment encryption? **A:** No; it is tamper/process evidence.
13. **Q:** Can public healthy data prove clinical effectiveness? **A:** No.
14. **Q:** What happens to unverified license? **A:** Source is not default corpus-eligible.
15. **Q:** Why keep raw public data external? **A:** Storage, licensing, reproducibility and repository hygiene.
16. **Q:** Can DAY33 train? **A:** No.
17. **Q:** Can DAY33 tune thresholds? **A:** No; DAY35 research threshold study uses development evidence.
18. **Q:** Can locked data be used in DAY35? **A:** No.
19. **Q:** What should missing metadata be? **A:** Unknown/null with explicit reason/status.
20. **Q:** What is the highest DAY33 claim? **A:** Research corpus/source governance engineering readiness.
21. **Q:** What does `clinical_evidence=false` mean? **A:** Do not use the item as clinical validation/reference evidence.
22. **Q:** Does Hyser match Noraxon? **A:** No; it is a different external domain.
23. **Q:** Can source labels be preserved? **A:** Yes, with original semantics/provenance; do not promote authority.
24. **Q:** What is leakage? **A:** Information from evaluation/locked data influencing development decisions.
25. **Q:** Why deterministic seeds? **A:** Exact regeneration and audit.

## 28. Beginner Exercise 1

You find a public dataset page with a download button but cannot find a license. Decide whether to add
it to the default corpus. Correct answer: keep it in discovery/deferred status and record license as
not verified; do not ingest it as default portfolio evidence.

## 29. Beginner Exercise 2

A synthetic waveform is multiplied by 0.05. Write the allowed label. Correct:
`SYNTHETIC_LOW_AMPLITUDE_STRESS`. Incorrect: `SEVERE_PARESIS`.

## 30. Beginner Exercise 3

A window has no context samples. Can it become a DAY33 item? No. Regenerate it through DAY22
windowing with `QC_WINDOW_WITH_CONTEXT` or reject it.

## 31. Intermediate Exercise 1

Design a manifest entry for a locally acquired GRABMyo file. Include dataset ID/version, relative file
path inside the external root, SHA-256, file size, acquisition timestamp and adapter version. Do not
include absolute `/home/user/...` paths in repository evidence.

## 32. Intermediate Exercise 2

Suppose a power-line detector reports WARNING on 90% of synthetic 50 Hz cases and 30% of clean cases.
What can you conclude? You may discuss behavior on the synthetic construction distribution and false
warning rate there. You cannot infer clinical sensitivity/specificity.

## 33. Integration Exercise

Build the complete evidence path for one synthetic missing-data fixture:

```text
seed
→ base signal
→ missing injection
→ source hash
→ DAY22 WindowIdentity
→ corpus item / SYNTHETIC_KNOWN_TRUTH
→ DAY23 LF output / WEAK_LABEL_CANDIDATE
→ DAY30 aggregation
→ DAY31 metric handoff
```

Explain why each arrow changes representation/authority but never turns the synthetic sample into a
patient case.

## 34. Quiz

1. Why are public raw datasets excluded from the ZIP?
2. What distinguishes source provenance from annotation authority?
3. What is the DAY33 readiness state after license verification?
4. Why can the public payload still be not acquired?
5. Why is Hyser valuable despite hardware mismatch?
6. Why is `sampling_rate_hz=null` safer than guessing?
7. What makes locked truth leakage harmful even without ML?
8. What evidence supports a synthetic known-truth label?
9. Why can a 50 Hz injection not automatically mean QC FAIL?
10. What prevents direct identifiers from entering the corpus?
11. What is required before a public source becomes a window-level corpus item?
12. What does `clinical_evidence=false` protect against?
13. Why is source hashing necessary but insufficient?
14. What would invalidate the development/locked split?
15. Why does DAY33 have no accuracy metric?

## 35. Answers

1. Raw datasets are data assets, often large and license-governed; repository stores provenance, not
bulk payload.
2. Provenance states origin; authority states what actor/process supports a label.
3. `RESEARCH_READY`, because verified public source governance and reproducible synthetic fixtures
exist.
4. Readiness concerns usable source governance, not whether all bytes are bundled in Git.
5. It provides a deliberately different HD-sEMG/cross-day domain for future supportability research.
6. Guessing creates false evidence and potentially invalid DSP assumptions.
7. Engineers can still tune deterministic thresholds/rules to evaluation examples.
8. The deterministic generator and transform provenance.
9. DAY26 semantics distinguish artifact evidence from final usability decision.
10. Schema/semantic guards plus synthetic-only committed payload and path scans.
11. External acquisition, hash registration, verified canonical adapter and DAY22 windowization.
12. It prevents research/synthetic evidence from becoming clinical validation evidence.
13. Hash proves byte identity, not semantic correctness/license/task compatibility.
14. Seed/subject/source overlap or inspection/tuning using locked truth.
15. No QC labels have been produced/evaluated yet; that is DAY34, and external public QC truth may be
absent.

## 36. Teach-back Readiness

You are ready for DAY34 when you can explain, without notes:

- why open access is not enough;
- why DAY32 tiers and public source classes are orthogonal;
- how a source hash differs from a window ID;
- why synthetic low amplitude is not pathology;
- how development/locked leakage can happen without neural-network training;
- why public raw bytes stay outside Git;
- what evidence DAY34 is allowed to compute and what it must not call expert agreement.

## 37. Final mental model

```text
Rights + provenance
        ↓
Source eligibility
        ↓
Deterministic synthetic truth / external raw registration
        ↓
Canonical WindowIdentity
        ↓
Research partition
        ↓
Only then: detector evaluation
```

DAY33 is successful when the project knows exactly **which bytes it could use, why it may use them,
what each label means, what remains hidden, and what it is forbidden to claim**.


## 38. Deep Dive — Internal Validity vs External Validity

Two experiments can be perfectly reproducible yet answer different questions. **Internal validity** asks whether the experiment correctly measures behavior inside its defined setup. Synthetic known-truth is strong here because the corruption is known exactly. **External validity** asks whether the result transfers to real-world populations/devices/protocols. Synthetic fixtures are weak here.

Public data improves external diversity but still does not solve clinical validity automatically. GRABMyo may show that a pipeline can ingest multi-day healthy forearm/wrist data. It does not show that the same QC threshold works for a neurological rehabilitation patient recorded with a different electrode setup.

This distinction explains why DAY33 deliberately uses multiple evidence sources rather than declaring one “ground-truth dataset.”

## 39. Deep Dive — Dataset Labels Have Task-Local Meaning

A label should always be read as a sentence with a hidden suffix: **“according to this dataset's protocol.”**

`gesture = wrist_flexion` means a participant performed the protocol's wrist-flexion instruction. It does not mean the window is artifact-free, clinically normal, or comparable to a different acquisition. Similarly `fatigue_rating = 2` in an external dataset means the source's self-perceived scale reached level 2 under its protocol. It does not mean a universal physiological fatigue state exists.

When combining datasets, semantic mapping is therefore a research operation requiring documentation, not a string-replacement operation.

## 40. Deep Dive — Why Subject IDs Still Matter When De-Identified

A de-identified subject ID can be essential for preventing leakage. Suppose one participant contributes 100 windows. If 80 windows go into development and 20 into evaluation, the algorithm may exploit person-specific electrode/anatomy characteristics. Performance can look excellent while failing on unseen people.

DAY33 does not yet create public subject-wise splits because public raw data is not acquired, but it preserves subject/session metadata requirements so DAY66 can freeze leakage-safe partitions. De-identification means removing direct identity, not destroying grouping information needed for valid science.

## 41. Deep Dive — Versioning a Dataset

A dataset name without a version is incomplete provenance. GRABMyo has multiple releases; Hyser has multiple versions. A later release may add files, fix metadata or change licensing. Therefore a reproducible record should include:

```text
dataset_id
version
DOI for that version
canonical source
license observed for that version
file hashes actually used
```

This is analogous to pinning a Python dependency rather than writing `numpy=latest`.

## 42. Deep Dive — Why `source_id` and `item_id` Are Different

A source can contain many windows. `source_id` identifies the source bytes. `window_id` identifies a deterministic slice/context under a versioned profile. `item_id` identifies how that window participates in the benchmark, including partition and seed provenance.

If the same source window is intentionally used in two different benchmark roles, its source/window identities can remain the same while its corpus item identity should differ. This separation prevents provenance semantics from becoming overloaded.

## 43. Deep Dive — Missing Values Are Data, Not Empty Space

In biomedical signals, NaN or missing segments can be the phenomenon you need to detect. Automatically interpolating them during corpus creation destroys construction truth. DAY33 therefore stores missing values directly in synthetic arrays and leaves repair/processing out of scope.

The same principle later applies to public data: preserve raw missingness first, decide downstream handling later through a versioned processing profile.

## 44. Deep Dive — Why a Clean Synthetic Case Is Necessary

If every fixture contains an injected artifact, a detector can simply warn on everything and still appear sensitive. A clean/no-injection control is required to examine false warning behavior. However, call it `NO_INJECTED_ARTIFACT`, not “healthy,” because the base waveform is not a validated physiological simulator.

Language discipline is part of technical correctness.

## 45. Deep Dive — Attribution Is Part of Reproducibility

A public dataset can be technically reproducible while being cited incorrectly. Dataset cards ensure attribution survives into reports, notebooks and final portfolio documentation. DOI/version/license are not administrative decoration; they are part of the scientific dependency graph.

A strong final project should allow another engineer to answer: “Which exact external resources did this result depend on?” without searching old browser history.

## 46. Deep Dive — Why We Verify Current Sources Again

The project already had a pre-DAY25 dataset study. Why verify sources again? Because access pages, versions and licensing are external state and can change. DAY33 is the moment public data becomes an execution dependency, so it performs a fresh primary-source check rather than treating an older research note as immutable truth.

This is the same principle used with software dependencies: a prior note guides discovery; the execution gate verifies what is current.

## 47. More Counterexamples

### Counterexample A — Great model, invalid split

A classifier reaches 98% window accuracy, but windows from every subject appear in both train and test. The number can be reproducible and still not measure unseen-subject generalization.

### Counterexample B — Good license, wrong semantics

A dataset is CC BY 4.0 and easy to download, but contains only preprocessed envelopes with no raw timing/unit metadata needed for QC. Legal eligibility does not guarantee technical eligibility.

### Counterexample C — Correct detector, wrong claim

A power-line detector perfectly identifies every constructed 50-Hz injection. Reporting “100% clinical power-line detection” is still wrong because the test distribution is synthetic.

### Counterexample D — Public clinical cohort, restricted reuse

A dataset may contain clinically valuable stroke cases but be governed by a DUA. Scientific relevance cannot override data-use terms.

## 48. Practical Exercise — Audit a New Dataset

Given a new sEMG dataset link, fill this table before downloading anything:

| Question | Answer |
|---|---|
| Canonical repository | ? |
| Dataset version | ? |
| DOI/version DOI | ? |
| Explicit license | ? |
| Redistribution allowed | ? |
| Registration/DUA | ? |
| Subjects/sessions | ? |
| Channel layout | ? |
| Sampling rate | ? |
| Raw vs processed | ? |
| Label semantics | ? |
| Clinical cohort | ? |
| Direct identifiers possible | ? |
| Fit to DAY33/DAY64 purpose | ? |
| Main limitation | ? |

If any legal field is unknown, do not mark the source corpus-eligible by convenience.

## 49. Practical Exercise — Diagnose a Leakage Bug

You generate 12 development cases with seeds 1–12 and six locked cases with seeds 7–12. The signals are not identical because different corruption functions are used. Is this acceptable? No. Seed overlap is itself a reproducibility/leakage smell because the same stochastic base may share noise realization. The DAY33 contract rejects partition seed overlap even if scenarios differ.

## 50. Practical Exercise — Design a Public Data Ledger

A good ledger should contain enough to reproduce the source bytes but not leak workstation details:

```json
{
  "dataset_id": "GRABMYO_V1_1_0",
  "relative_path": "Session1/.../trial.dat",
  "sha256": "...",
  "size_bytes": 655360
}
```

Do not store `/home/duy/...` or account-specific cloud mount paths. Those paths are not scientific provenance and can leak internal information.

## 51. Additional Flashcards

26. **Q:** Can a dataset have high scientific value but be excluded? **A:** Yes; license/governance or technical incompatibility may block default use.
27. **Q:** Does synthetic `CLEAN` mean healthy subject? **A:** No; it only means no selected corruption was injected.
28. **Q:** Why preserve public dataset version? **A:** Files/metadata/license can differ across releases.
29. **Q:** Can public labels be used later? **A:** Yes, only with their original task semantics and source provenance.
30. **Q:** Why not download Hyser in DAY33? **A:** Corpus governance can be completed without bringing a very large raw payload into the repo/workspace.
31. **Q:** What is technical eligibility? **A:** Whether data fields/shape/metadata support the intended processing, distinct from legal eligibility.
32. **Q:** What is external validity? **A:** How well findings transfer beyond the experiment's defined distribution.
33. **Q:** What is internal validity here? **A:** Whether constructed truth and evaluation accurately test the intended technical behavior.
34. **Q:** Why does missingness stay in synthetic raw? **A:** It may be the fault under test; interpolation would erase truth.
35. **Q:** What makes a source “current”? **A:** Re-verification of version/access/license at execution time.

## 52. Oral Exam Prompts

Explain these without using the words “because it is safer” as a shortcut:

1. Why a public-source license and an annotation evidence tier solve different problems.
2. Why public raw data can remain outside Git while experiments remain reproducible.
3. Why deterministic threshold tuning can leak against a locked set just like ML tuning.
4. Why a dataset with stroke patients may still be unusable for your public portfolio.
5. Why a synthetic low-amplitude case is an important safety test despite having no pathology truth.
6. Why a public dataset adapter must preserve unknown metadata instead of filling defaults.
7. Why cross-dataset performance should not be pooled before checking protocol compatibility.

## 53. DAY34 Readiness Self-Test

You should be able to derive the next-day analysis plan from the corpus contract:

- only development synthetic truth is eligible for construction-truth scoring;
- locked truth stays untouched;
- public source catalog can inform future domains but public windows are not yet payload items;
- six DAY21–28 labeling functions can be applied as weak-label candidates;
- correlation/disagreement describes machine rules, not reviewer agreement;
- no label model is required to perform useful weak-supervision analysis.

If any of those statements feels surprising, review DAY32 and DAY33 before moving to DAY34.

## 54. Final Feynman Explanation

If you had to teach DAY33 to a first-year engineer in sixty seconds, say:

> We are not collecting “more data.” We are building rules that tell us what data we may use and what each piece of data can prove. We verify public sources and licenses, keep their raw bytes outside Git, create small deterministic synthetic faults whose truth we know because we injected them, give every window a stable identity, and reserve some cases so future threshold decisions cannot see everything. We never call synthetic data clinical truth, and we do not train anything yet. The output is a trustworthy research corpus foundation, not an accuracy number.
