# DAY34 EXECUTION PLAN — Weak-Label Disagreement & Known-Truth Evaluation

## 0. Document Control

- Program: MyoLab-AI / sEMG Quality Intelligence
- Day: DAY34
- Mode: Independent Research Portfolio
- Upstream hard dependency: DAY33 Research Benchmark Corpus v1
- Claim scope: `RESEARCH_ONLY`
- Allowed final claim: `WEAK_LABEL_ANALYTICAL_EVIDENCE_READY`
- Expert agreement: `NOT_PERFORMED`
- Clinical validation: `NOT_PERFORMED`
- Model training: forbidden
- Threshold tuning: forbidden; DAY35 owns threshold sensitivity.

## 1. Executive Intent

DAY34 replaces the original clinician agreement/adjudication day with an engineering evaluation that can be executed honestly without clinicians. The objective is not to manufacture a new ground truth. It is to determine how the six weak-label families behave on the DAY33 synthetic known-truth development corpus, how often they abstain or disagree, where two rules are correlated, and which cases are high-value candidates for future expert review if expert access ever becomes available.

The central safety rule is simple: machine rules are not reviewers. Therefore pairwise rule correlation or disagreement must never be called inter-rater agreement, Cohen's kappa, consensus, adjudication, or clinical validation. The only authorized supervised reference in DAY34 is `SYNTHETIC_KNOWN_TRUTH`, and only when the known injected truth is applicable to the exact WindowIdentity core evaluated by the detector.

## 2. Why DAY34 Exists

A unit test can prove that a detector behaves as intended on a hand-written fixture. It cannot reveal how multiple detectors interact on the same corpus, how abstention changes coverage, whether two rules fire on the same windows, or whether the benchmark itself is incorrectly aligned. DAY34 therefore acts as a bridge between detector implementation and DAY35 threshold sensitivity.

This bridge is especially important because threshold tuning on an invalid benchmark would produce precise but meaningless numbers. DAY34 must first prove that the reference signal, truth label, evaluated window, detector applicability, and evidence tier agree.

## 3. Critical Path

```text
DAY33 manifest + synthetic signals
        ↓
partition/evidence guard
        ↓
WindowIdentity reconstruction
        ↓
DAY23–28 detector execution
        +
DAY29 timestamp integrity execution
        ↓
truth/window applicability gate
        ↓
window-level known-truth metrics
        ↓
LF coverage / abstention / disagreement / correlation
        ↓
high-value review candidate ranking
        ↓
DAY35 threshold-sensitivity readiness
```

## 4. Preconditions

1. DAY33 status is PASS.
2. `research-benchmark-corpus-v0.1.manifest.yaml` exists.
3. 12 `benchmark-development` items expose synthetic truth.
4. 6 `benchmark-locked` items retain hidden truth and are not consumed.
5. DAY22 WindowIdentity semantics are importable in the live repository.
6. DAY23–28 detectors and DAY29 data-integrity evaluator are present.
7. DAY30/31 safety semantics remain unchanged.

## 5. Objectives

1. Execute six canonical weak-label families on every development item.
2. Preserve raw sub-rule outputs where one canonical family combines more than one detector rule.
3. Execute DAY29 timestamp integrity separately from weak-label correlation.
4. Produce coverage-aware synthetic metrics.
5. Compute pairwise machine-rule disagreement and phi/Pearson correlation only on co-evaluated binary outputs.
6. Rank high-value future review candidates without pretending expert review occurred.
7. Detect corpus-quality problems before DAY35.
8. Keep locked truth completely outside evaluation.

## 6. Explicit Non-Goals

DAY34 does not train a label model, fit a classifier, tune detector thresholds, calculate clinician agreement, reveal locked labels, convert weak labels to expert truth, infer pathology, download public raw data, or change final QC aggregation policy. It does not report event-localization accuracy because the current LF contracts emit window-level candidates rather than event bounds.

## 7. Canonical Weak-Label Families

DAY34 normalizes detector implementation history into six analytical families:

| Canonical family | Raw detector source |
|---|---|
| `LF_MISSING_DROPOUT` | DAY23 dropout/missing + flatline sub-rule |
| `LF_CLIPPING_SATURATION` | DAY24 clipping |
| `LF_BASELINE_NOISE` | DAY25 baseline/noise |
| `LF_POWERLINE` | DAY26 power-line |
| `LF_LOW_FREQUENCY_CONTAMINATION` | DAY27 motion/low-frequency |
| `LF_POOR_CONTACT` | DAY28 channel-abnormality/poor-contact |

The normalization is explicit. It is not a hidden voting model. DAY23's dropout and flatline sub-rules are preserved in raw IDs/reasons, while a deterministic max-severity family candidate is used for the six-family analysis table.

## 8. DAY29 Integrity Is Not a Seventh Weak Label

Timestamp duplicate/non-monotonic checks are evaluated through DAY29 `DataIntegrityQcResult`. They are safety/integrity evidence and can block downstream processing. They are not included in LF correlation as though they were another labeling function. This separation prevents a hard data-integrity gate from being diluted by weak-label statistics.

## 9. Evaluation Semantics

Candidates are mapped to binary analytical votes only when their result is evaluable:

```text
WARNING_CANDIDATE / FAIL_CANDIDATE → 1
PASS_CANDIDATE                    → 0
UNKNOWN / ABSTAIN                 → unresolved / null
not applicable                    → null
```

UNKNOWN and ABSTAIN are never converted to PASS. This matters for baseline noise, whose threshold remains `NOT_VERIFIED`, and for poor-contact analysis, which lacks cross-channel peers in the DAY33 one-channel synthetic corpus.

## 10. Truth Applicability Gate

DAY34 discovered an upstream corpus issue that must not be hidden. DAY33 generated several localized corruptions around `n/3`, while the selected core WindowIdentity is `[1000,1500)` for a 2000-sample signal. Consequently:

- `MISSING`
- `ZERO_DROPOUT`
- `FLATLINE`
- `CLIPPING`

are injected outside the detector's core window, although they remain inside the wider context. These fixtures cannot be used as positive window-level truth for the corresponding detector. DAY34 marks them `LOCAL_TRUTH_OUTSIDE_WINDOW_CORE_NOT_SCORABLE` and treats them as corpus-repair findings rather than detector false negatives.

`MOTION_TRANSIENT` is injected at `n/2`, so it overlaps the core. Global transforms such as power-line, drift, broadband noise, and amplitude scaling apply to the core by construction.

This finding is one of DAY34's most important outputs because it prevents DAY35 from tuning dropout/clipping thresholds against mislabeled windows.

## 11. Detector-Specific Context Policy

### Dropout / Flatline

The family executes both DAY23 sub-rules. Positive synthetic truth is scorable only if the local corruption overlaps the core. In current DAY33 v0.1 it does not, so positive recall is intentionally `N/A`, not zero.

### Clipping

DAY24 ADC semantics remain unverified for the DAY33 arbitrary synthetic amplitude scale. DAY34 does not invent device rails. The current clipping-positive fixture is additionally outside the core, so no clipping recall claim is allowed.

### Baseline Noise

The synthetic baseline-noise transform is global and therefore truth-localized correctly. However the operative threshold remains `NOT_VERIFIED`. The detector returns `UNKNOWN`, which is recorded as unresolved fail-closed behavior. DAY35 is the first day allowed to study threshold sensitivity.

### Power-Line

The synthetic fixture environment explicitly uses a 50-Hz injected grid component. DAY34 supplies 50 Hz as verified synthetic metadata only; this is not a site mains-frequency claim. The existing rule thresholds are not tuned.

### Motion / Low-Frequency

Drift is global; transient overlaps the core. Both are valid window-level known-truth cases under current generator semantics.

### Poor Contact

The DAY33 corpus is single-channel. DAY28 poor-contact evidence fundamentally depends on cross-channel context/corroboration. The raw detector is executed for traceability, but DAY34 refuses to score or correlate the family as if adjacent channels existed. `SYNTHETIC_LOW_AMPLITUDE_STRESS` remains a physiology-preservation sentinel and is explicitly not poor-contact truth.

## 12. Metrics

For every family DAY34 records declared positives, truth-localization gaps, scorable positives/negatives, binary coverage, unresolved positives/negatives, TP/FP/TN/FN, selective precision/recall/specificity, and effective recall. Effective recall treats unresolved positive truth as not positively detected, while selective recall only describes evaluated positives. Both are reported to avoid coverage hiding.

A metric is left null when its denominator does not exist. For example, poor-contact has no positive known-truth fixture, so recall is not zero; it is unavailable.

## 13. Pairwise Correlation

Correlation is calculated only on windows where both families emit binary votes. Binary Pearson correlation is equivalent to the phi coefficient for binary variables. If one rule never varies or too few co-evaluated samples exist, correlation remains null with an explicit status.

The companion disagreement rate is often more interpretable than correlation in this tiny corpus. Every correlation row carries `MACHINE_RULE_RELATION_ONLY_NOT_INTER_RATER`.

## 14. High-Value Candidate Ranking

Candidate ranking uses deterministic, transparent signals:

- known-truth target false-allow;
- known-truth target unresolved fail-closed;
- DAY29 hard-integrity override;
- physiology-preservation sentinel;
- machine-rule disagreement;
- unresolved LF count;
- cross-family positive evidence.

Corpus truth/window misalignment has the highest engineering repair priority, but these cases are **not** selected for future expert review because a reviewer should not be asked to adjudicate a benchmark construction defect.

## 15. Mandatory Outputs

1. `ai-core/notebooks/05_rule_disagreement_analysis.ipynb`
2. `qa-validation/evidence/lf-performance-synthetic-v0.1.csv`
3. `qa-validation/evidence/lf-correlation-v0.1.csv`
4. `qa-validation/evidence/research-review-candidate-list-v0.1.csv`

Supporting outputs include raw LF-window outputs, disagreement matrix, timestamp-integrity performance, analysis summary, evaluation profile, tests, validation report, traceability, and DAY35 handoff.

## 16. Actual Analytical Findings

On the 12 development items:

- six LF families produce 72 family-level rows;
- DAY29 produces 12 timestamp-integrity rows;
- locked items consumed = 0;
- four development items have truth/window misalignment;
- power-line has 1 scorable positive and detects it;
- motion/low-frequency has 2 scorable positives and detects both;
- timestamp integrity has 2 positives and blocks both;
- baseline-noise has one scorable positive but remains unresolved because threshold is not verified;
- dropout and clipping positive recall are not reportable because the positive injections lie outside the core;
- poor-contact supervised performance is not reportable because there is no cross-channel context and no positive poor-contact truth fixture.

These are engineering observations on a tiny synthetic corpus. They are not performance claims for public data, clinical data, a hospital, or a patient population.

## 17. Automated Validation

Focused DAY34 tests cover locked-partition rejection, evidence-tier rejection, WindowIdentity anchoring, six-family coverage, truth localization, fail-closed semantics, timestamp integrity, correlation determinism, candidate ranking, output reproducibility, no pathology promotion, and forbidden claim language.

Full upstream regression is run with one historical DAY21 guard deselected: `test_43_no_day22_window_implementation`. That test intentionally asserted DAY22 must not exist when executing DAY21 alone; it is no longer a valid global regression invariant after DAY22 has legitimately been integrated. The deselection is explicit rather than modifying historical evidence.

## 18. Failure Injection / Negative Checks

- Attempt to analyze a locked item → hard error.
- Change development evidence tier from synthetic known-truth → hard error.
- Remove visible synthetic truth → hard error.
- Set `clinical_truth_claim=true` → hard error.
- Tamper a signal file → SHA mismatch hard error.
- Use an unknown corpus partition → hard error.
- Attempt clinical-validation wording → claim validator rejects it.
- Treat poor-contact as scorable without peers → tests fail.

## 19. Acceptance Criteria

DAY34 is complete when mandatory outputs exist, 12 development items are evaluated without locked leakage, all six families are represented, machine-rule correlation is deterministic, truth localization defects are surfaced rather than mis-scored, review candidates are deterministic, and all focused/regression/integrity checks pass.

## 20. Stop / Block Conditions

DAY35 must not tune dropout/clipping thresholds against the current misaligned DAY33 positive fixtures. It must first either use detector-specific aligned known-truth fixtures already available from DAY23/24 or create a versioned corpus localization patch with new WindowIdentity references. Site/clinical threshold claims remain forbidden.

## 21. DAY35 Handoff

DAY35 receives:

- coverage-aware performance table;
- correlation/disagreement evidence;
- unresolved baseline-noise evidence;
- scorable power-line/motion evidence;
- timestamp-integrity validation;
- four corpus-repair cases;
- review-candidate ranking;
- explicit rule that locked outcomes remain unseen.

The correct DAY35 question is not “which threshold maximizes accuracy on all 12 windows?” It is “for each detector, which development fixtures have valid target truth, which threshold dimensions are authorized to vary, and how do false-allow/false-block trade-offs change without touching locked evaluation?”

## 22. Final Status Vocabulary

Highest allowed status for DAY34:

```text
WEAK_LABEL_ANALYTICAL_EVIDENCE_READY
```

with limitations:

```text
EXPERT_AGREEMENT = NOT_PERFORMED
CLINICAL_VALIDATION = NOT_PERFORMED
LABEL_MODEL_TRAINING = false
THRESHOLD_TUNING = false
LOCKED_TRUTH_CONSUMED = false
DAY33_CORPUS_LOCALIZATION_GAP = 4 ITEMS
```

## 23. Detailed Execution Procedure

### STEP 01 — Preflight DAY33 corpus authority

**Goal:** prove DAY34 is looking at the correct DAY33 evidence artifact before any detector is executed.  
**Input:** `research-benchmark-corpus-v0.1.manifest.yaml`.  
**Action:** validate `claim_scope=RESEARCH_ONLY`, development partition name, evidence tier, visible synthetic truth for development items, and hidden truth for locked items.  
**Output:** an in-memory tuple of exactly 12 authorized development items.  
**Verification:** 12 development and 6 locked items must exist.  
**Negative check:** an unknown partition, missing truth, or `clinical_truth_claim=true` raises `Day34AnalysisError`.  
**Stop:** any locked item entering the authorized tuple.

### STEP 02 — Verify signal artifact integrity

**Goal:** ensure predictions are attached to the exact bytes frozen by DAY33.  
**Input:** each development item's relative NPZ path and SHA-256.  
**Action:** resolve under the DAY33 corpus root, hash the file, then load `samples` and `time_seconds` with `allow_pickle=False`.  
**Output:** immutable analytical arrays in memory.  
**Verification:** dimensions are one-dimensional and equal length; hash matches manifest.  
**Negative check:** append a byte to a copied NPZ and assert the loader rejects it.  
**Evidence:** `test_signal_hash_mismatch_rejected`.

### STEP 03 — Reconstruct the WindowIdentity scope

**Goal:** guarantee detector prediction scope equals the frozen DAY33 window.  
**Input:** manifest `window_context`, signal sample count and Fs.  
**Action:** reconstruct the DAY22 `WindowIdentity` object using the exact frozen IDs, sample bounds, profile fingerprint and context.  
**Output:** a detector-compatible WindowIdentity.  
**Verification:** `evidence_refs[0]` from every family output equals the manifest window ID.  
**Negative check:** context outside the signal payload is rejected.

### STEP 04 — Run DAY23 dropout/flatline sub-rules

**Goal:** preserve both raw sub-rule semantics while producing the six-family analytical view requested by DAY34.  
**Input:** raw samples + WindowIdentity.  
**Action:** execute `evaluate_dropout_missing` and `evaluate_flatline`; retain both raw LF IDs and both reasons. Apply explicit candidate precedence only to construct canonical family `LF_MISSING_DROPOUT`.  
**Output:** one family row plus raw source IDs.  
**Verification:** clean windows remain negative; no ground-truth/expert claim is created.  
**Negative check:** local positive truth outside the core is excluded from recall calculation.

### STEP 05 — Run DAY24–28 weak-label detectors

**Goal:** execute the remaining five canonical families with their existing semantics.  
**Input:** same sample/window pair plus detector-specific research context.  
**Action:** execute clipping, baseline, power-line, motion and channel-abnormality detectors.  
**Output:** five additional family rows.  
**Special rules:** clipping keeps ADC semantics unverified; baseline keeps threshold unverified; power-line receives synthetic 50-Hz environment metadata; poor-contact is run but marked non-scorable without adjacent-channel peers.  
**Stop:** any code path modifies a shared detector threshold.

### STEP 06 — Execute DAY29 timestamp integrity

**Goal:** evaluate structural time-axis corruption without pretending it is another weak label.  
**Input:** full `time_seconds`, WindowIdentity/session refs.  
**Action:** derive duplicate/non-monotonic anomalies and pass them to DAY29 `evaluate_data_integrity`. Sampling/unit status is marked verified only for the synthetic engineering fixture context; no site claim is made.  
**Output:** 12 integrity rows.  
**Verification:** duplicate and non-monotonic fixtures are blocked; clean and other signal-only transforms do not receive timestamp blocks.

### STEP 07 — Apply truth-localization gate

**Goal:** ensure reference granularity matches prediction granularity.  
**Input:** development scenario, generator version, sample count, WindowIdentity core bounds.  
**Action:** derive local transform interval from the frozen DAY33 generator contract where applicable and test core overlap.  
**Output:** `GLOBAL_OR_NONLOCAL_TRUTH_APPLIES_TO_CORE`, `LOCAL_TRUTH_OVERLAPS_WINDOW_CORE`, or `LOCAL_TRUTH_OUTSIDE_WINDOW_CORE_NOT_SCORABLE`.  
**Verification:** four local scenarios are outside the core; motion transient overlaps.  
**Stop:** never silently count an out-of-core local truth as a detector miss.

### STEP 08 — Build coverage-aware performance table

**Goal:** create metrics that expose abstention and missing applicability rather than hiding them.  
**Input:** 72 family rows + truth map.  
**Action:** calculate declared/scorable positives, localization gaps, unresolved counts, TP/FP/TN/FN, coverage, selective/effective recall and specificity.  
**Output:** `lf-performance-synthetic-v0.1.csv`.  
**Verification:** null metrics remain blank rather than zero when the denominator does not exist.  
**Stop:** no aggregate “accuracy” column is introduced because families have different truth coverage.

### STEP 09 — Build pairwise disagreement/correlation evidence

**Goal:** characterize machine-rule dependence.  
**Input:** binary votes from scorable/evaluable family outputs.  
**Action:** pair windows where both families have 0/1 votes, calculate disagreement rate, and compute binary Pearson/phi only when both variables have variance.  
**Output:** long-form `lf-correlation-v0.1.csv` and matrix `lf-disagreement-matrix-v0.1.csv`.  
**Verification:** all 36 ordered family pairs exist; poor-contact pairs have zero co-evaluation.  
**Negative check:** no statistic is named reviewer agreement.

### STEP 10 — Build high-value review candidate list

**Goal:** turn disagreement/error evidence into a future acquisition queue without consuming expert time today.  
**Input:** family rows + integrity rows + synthetic truth.  
**Action:** rank deterministic signals including corpus defects, true false-allows, unresolved truth, hard integrity, physiology-preservation sentinel, and disagreement.  
**Output:** `research-review-candidate-list-v0.1.csv`.  
**Verification:** four corpus-repair cases are explicitly not selected for expert review.  
**Stop:** candidate ranking is not presented as trained Active Learning.

### STEP 11 — Reproducibility replay

**Goal:** prove the evaluation is deterministic.  
**Input:** unchanged DAY33 bytes and detector/config versions.  
**Action:** write all DAY34 analytical outputs twice in separate temp directories and compute a stable digest over file names and bytes.  
**Output:** identical evidence artifacts.  
**Verification:** `test_written_outputs_are_deterministic` PASS.

### STEP 12 — Functional and regression verification

**Goal:** prove DAY34 did not alter upstream safety behavior.  
**Input:** DAY34 focused suite, DAY33 corpus tests, QC tests, property tests.  
**Action:** execute `run_day34_checks.sh`.  
**Output:** focused + upstream PASS counts.  
**Historical guard handling:** deselect only the DAY21 anti-future-scope assertion that requires the DAY22 schema to be absent. This is documented, narrow, and does not suppress functional QC behavior.

### STEP 13 — Evidence freeze and handoff

**Goal:** make DAY35 consume exactly what DAY34 proved.  
**Input:** all final DAY34 files.  
**Action:** compute artifact manifest, SHA256SUMS, validation report, quality audit and handoff.  
**Output:** immutable DAY34 release ZIP.  
**Stop:** regenerate manifest/SHA files after any content change.

## 24. Metric Interpretation Table

| Field | Meaning | Important caveat |
|---|---|---|
| `declared_truth_positive_count` | Positive scenarios according to full synthetic item truth | Does not guarantee truth is inside core |
| `truth_localization_gap_count` | Positive truth outside core | Must not become FN |
| `scorable_truth_positive_count` | Positive truth aligned to evaluated core | Valid denominator for window recall |
| `evaluated_binary_count` | PASS or WARNING/FAIL outputs | UNKNOWN/ABSTAIN excluded but reported separately |
| `coverage_on_scorable` | Fraction of scorable items with binary output | Not accuracy |
| `recall_selective` | TP among evaluated positives | Can hide abstention if used alone |
| `recall_effective` | TP among all scorable positives | More conservative coverage-aware view |
| `binary_phi_correlation` | Association between two binary machine rules | Not independence, causality, or reviewer agreement |

## 25. Analytical Risk Register

| Risk | Failure mode | DAY34 control |
|---|---|---|
| Truth leakage | Locked outcome enters analysis | Partition guard + tests |
| Scope mismatch | File-level truth scored against unrelated core | Truth-localization gate |
| Abstention laundering | UNKNOWN silently treated as PASS | Binary vote remains null |
| Clinical overclaim | Synthetic result described clinically | Claim boundary + wording tests |
| Rule double-counting | Correlated LFs treated independent | Pairwise correlation/disagreement evidence |
| Poor-contact overclaim | Single-channel corpus used for cross-channel task | Non-scorable applicability status |
| Threshold leakage | DAY34 chooses thresholds based on truth | `threshold_tuning=false`; config remains frozen |
| Expert-time waste | Corpus defects queued for physician | Engineering repair routing |
| Historical test misuse | DAY21 anti-future test interpreted as regression failure | Explicit single-test deselection |

## 26. Why No Overall Accuracy Is Reported

An overall accuracy across the 72 family rows would be mathematically easy and scientifically poor. The six families target different phenomena, have different positive prevalence, different applicability, and different abstention behavior. Baseline has zero binary coverage under unverified thresholds; poor contact has no valid cross-channel context; dropout/clipping positive truth is mislocalized. Pooling all of those into one number would reward abundant negative cases and hide unsupported capabilities. DAY34 therefore reports family-specific evidence only.

## 27. Why DAY34 Does Not Patch DAY33 Silently

The evaluator could regenerate windows around the injected local corruption and produce attractive positive metrics. That would silently change the benchmark after seeing its behavior. Instead, DAY34 freezes the finding: four items require engineering corpus repair. A later versioned patch can create new WindowIdentity items with explicit truth localization and new hashes. This preserves provenance: DAY33 v0.1 remains what it was; the repair becomes a new evidence artifact rather than history being rewritten.

## 28. DAY35 Readiness Classification

DAY35 is **partially research-ready**:

- Power-line threshold sensitivity can use a correctly localized global fixture, but must still remain research-only.
- Motion/low-frequency sensitivity can use drift/transient development fixtures.
- Baseline sensitivity can proceed because truth is global, but must establish a research threshold profile without calling it site validated.
- Dropout/clipping sensitivity must use aligned detector-specific fixtures or a versioned corpus localization repair first.
- Poor-contact threshold sensitivity cannot be meaningfully assessed from the current one-channel corpus.

This prevents DAY35 from pretending every detector has equal benchmark maturity.

## 29. Definition of Done Checklist

- [x] DAY33 development-only loader.
- [x] Locked access rejected.
- [x] Six canonical families executed.
- [x] DAY29 integrity evaluated separately.
- [x] Raw family outputs preserved.
- [x] Truth localization verified.
- [x] Four corpus defects surfaced.
- [x] Coverage-aware metrics generated.
- [x] Pairwise disagreement/correlation generated.
- [x] High-value candidate list generated.
- [x] No clinician agreement claim.
- [x] No label model.
- [x] No threshold tuning.
- [x] No pathology fabrication.
- [x] Reproducibility tests.
- [x] Upstream regression.
- [ ] Independent peer review/sign-off — remains `PENDING` until performed.

## 30. Git / Integration Recommendation

Recommended branch/commit sequence:

```text
feat/day34-weak-label-analysis
  1. analysis library + evaluation policy
  2. generated analytical evidence
  3. tests + validators
  4. docs + handoff
  5. artifact hashes
```

Do not overwrite DAY33 manifest or signal files during merge. DAY34 is an analytical layer on top of frozen DAY33 evidence.

## 31. Rollback

Rollback DAY34 by removing day34-owned analysis files only. No DAY23–33 detector, manifest, taxonomy, threshold, or signal artifact is modified by this patch. Therefore rollback does not require data migration.

## 32. Evidence Maturity

```text
Synthetic analytical evidence    = READY_WITH_LIMITATIONS
Machine-rule relation map        = READY
Expert annotation                = NOT_PERFORMED
Adjudicated reference            = NOT_PERFORMED
Public raw-data benchmark        = NOT_PERFORMED
Clinical/site validation         = NOT_PERFORMED
```

## 33. Final Decision

DAY34 can close as `WEAK_LABEL_ANALYTICAL_EVIDENCE_READY` while explicitly carrying the four truth/window alignment defects and capability-specific limitations forward. The value of the day is not a flattering accuracy number; it is a trustworthy map of what can and cannot yet be scored.

## 34. Reviewer Checklist for Research Evidence

A senior engineer reviewing DAY34 should inspect at least one example from each evidence class rather than approving only test counts. For a clean window, verify that scorable rules remain negative while unsupported baseline/poor-contact evidence remains unresolved. For the power-line fixture, open the raw LF row and confirm that the first evidence reference is the exact WindowIdentity and that the reason is spectral interference rather than a generic quality failure. For motion drift/transient, verify that the known transform overlaps the core and that the rule remains warning-oriented rather than autonomous session failure. For timestamp corruption, verify that DAY29 integrity—not weak-label voting—owns the hard block. For low-amplitude stress, confirm that no truth map or candidate reason introduces stroke, paresis, atrophy, or poor-contact truth.

The reviewer must also inspect one of the four corpus-repair cases. The key question is not whether the detector output is plausible, but whether the reference label is valid for the target scope. The expected answer is no: the local transform lies outside the core. If a future implementation changes the generator/windowing geometry, this assumption must be recomputed rather than hard-coded from this report.

## 35. Provenance Chain

Every analytical statement in DAY34 should be reconstructible as:

```text
DAY33 item_id
→ signal artifact SHA-256
→ DAY22 window_id
→ detector module/version/config
→ raw LF output + reason/evidence refs
→ applicability/truth-localization decision
→ family-level analytical vote
→ metric/correlation/candidate CSV row
```

This chain is intentionally longer than simply storing a final score. The extra links are what allow a future engineer to distinguish detector behavior from benchmark construction, configuration availability, or evidence-tier limitations.

## 36. Why This Day Matters for the Portfolio

DAY34 is valuable because it demonstrates that benchmark engineering is part of AI engineering. A weaker portfolio would show a confusion matrix with attractive percentages. This project instead demonstrates how to reject invalid denominators, preserve abstention, detect label granularity defects, prevent locked-set leakage, and distinguish hard integrity from heuristic QC. These are transferable skills for biomedical AI, time-series ML, safety-sensitive data systems, and production MLOps.

The most defensible portfolio statement from DAY34 is not “our artifact detector achieved high accuracy.” It is:

> Built a reproducible weak-label evaluation framework with locked-split governance, coverage-aware metrics, machine-rule dependence analysis, and truth-to-window applicability checks; detected and quarantined benchmark-label misalignment before threshold tuning.

That statement is directly supported by code and evidence in this package without implying clinical validation.

## 37. Final Handoff Rule

DAY35 may consume the **analytical evidence**, but it must not convert DAY34's descriptive findings into site policy. Any threshold selected next remains `RESEARCH_HEURISTIC` or other explicitly non-clinical evidence class. If a detector lacks scorable positive truth, its threshold branch must stay blocked or use a newly frozen aligned development fixture. Locked items remain outside the loop until the later final evaluation phase defined by the independent roadmap.
