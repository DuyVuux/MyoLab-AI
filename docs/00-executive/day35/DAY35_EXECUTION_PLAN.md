# DAY35 EXECUTION PLAN — Research-Only Threshold Sensitivity & Configuration Study

## 0. Document Control

- **Program:** MyoLab-AI / sEMG Quality Intelligence.
- **Day:** DAY35.
- **Mode:** Independent research / portfolio continuation.
- **Claim scope:** `RESEARCH_ONLY`.
- **Highest allowed outcome:** `RESEARCH_THRESHOLDS_FROZEN_V0.1`.
- **Clinical/site threshold status:** `NOT_VERIFIED`.
- **Upstream:** DAY34 `WEAK_LABEL_ANALYTICAL_EVIDENCE_READY`, with truth-window limitations.
- **Downstream:** DAY36 physiology-preserving stress/domain challenge.

## 1. Executive Intent

DAY35 is not a clinical threshold-lock day. The organizational project no longer has the site data, clinician review process, or deployment authority required to turn a detector operating point into a hospital policy. The purpose of this day is narrower and technically defensible: establish a reproducible **research-only sensitivity study** that shows how detector decisions move when thresholds move, repair the DAY33 synthetic localization problem without rewriting history, choose a reversible research profile on development evidence only, and keep the site template explicitly empty.

The most important invariant is therefore not the numerical threshold itself. It is the authority boundary around that number. Every selected value must remain tagged `RESEARCH_HEURISTIC`; the `site-template` must remain `SITE_NOT_VERIFIED` with null thresholds; no locked outcomes may be consumed; and no result may be described as a clinical optimum. This day implements the re-based roadmap requirement to study parameter sensitivity while preserving evidence class and leakage controls. The independent roadmap requires parameter sweeps, Fs/window robustness, evidence classes, reversible research defaults, and a frozen provenance decision. It also explicitly prohibits selecting thresholds using locked evaluation data or describing them as site/clinician validated.

## 2. Why DAY35 Exists

DAY23–28 created detector contracts conservatively. DAY34 then showed why direct threshold tuning would have been unsafe: four localized DAY33 corruption labels were outside the detector core window. A naïve workflow would have converted those into false negatives and tuned the algorithm to compensate for a benchmark-label error. DAY35 therefore starts with **scorable-truth readiness**, not with grid search.

The day has four engineering goals:

1. create valid, core-aligned synthetic development evidence for detector families blocked by DAY34;
2. sweep only dimensions that have positive and negative scorable truth;
3. choose a deterministic research operating point under an explicit objective;
4. preserve a hard separation between a research profile and the unverified site profile.

## 3. Critical Path

```text
DAY34 analytical evidence
  ↓
Scorable-truth readiness matrix
  ↓
DAY35 versioned aligned fixtures (no DAY33 mutation)
  ↓
Detector-specific parameter grids
  ↓
Primary synthetic development sweep
  ↓
Sensitivity / specificity / weighted-error analysis
  ↓
Fs × window-duration robustness check
  ↓
Research operating-point decision
  ↓
thresholds.research-v0.1.yaml
  ↓
Claim + leakage + site-template guards
  ↓
DAY36 handoff
```

## 4. Previous-Day Handoff

DAY34 evaluated 12 DAY33 development items across six weak-label families and isolated DAY29 integrity evidence. It found:

- power-line positive truth was scorable;
- motion drift/transient positives were scorable;
- baseline-noise truth was scorable, but its threshold remained `NOT_VERIFIED`;
- missing/zero-dropout/flatline/clipping positives were not scorable because local transforms were outside the target WindowIdentity core;
- poor contact was not scorable because the corpus had no multi-channel peer context;
- locked items consumed: zero.

DAY35 must not reinterpret the four localization defects as detector failures. It must either use aligned fixtures or keep the corresponding threshold branch blocked. This package chooses the first option for dropout/flatline and clipping by creating a **new DAY35 fixture version**; DAY33 history remains untouched.

## 5. Preconditions

- DAY34 evidence files are available in the live repository.
- DAY23–27 detector modules are available and unchanged unless an approved version update exists.
- DAY22 `WindowIdentity` semantics remain authoritative for detector target scope.
- DAY33 locked manifest entries remain sealed.
- No public raw payload is required for this day.
- Training, label-model fitting, calibration-model fitting, and clinical threshold selection remain disabled.

## 6. Objectives

- Build a machine-readable detector readiness matrix.
- Create aligned positive/negative synthetic threshold-study fixtures.
- Sweep dropout/flatline, clipping, baseline-noise, power-line, and motion warning thresholds.
- Hold poor-contact threshold selection.
- Evaluate selected operating points over synthetic Fs/window strata.
- Freeze a research profile and an empty site profile.
- Produce an ADR and validation report that distinguish `RESEARCH_HEURISTIC` from `SITE_NOT_VERIFIED`.

## 7. Non-Goals

DAY35 does **not**:

- establish a clinical optimum;
- establish a Vinmec/MotionLab site threshold;
- evaluate patient data;
- evaluate the DAY33 locked set;
- train a label model;
- train a classifier;
- infer pathology;
- promote poor-contact logic without multi-channel evidence;
- rewrite DAY33 manifests or fixture truth;
- claim real-world sensitivity or specificity from the synthetic results.

## 8. Source of Truth

For this day the priority order is:

1. DAY32–90 Independent Research Roadmap v2.0 DAY35 definition;
2. DAY34 handoff findings and analytical evidence;
3. frozen detector implementation/config contracts from DAY23–28;
4. DAY22 WindowIdentity;
5. DAY35 synthetic engineering fixture definitions;
6. assumptions, always tagged `RESEARCH_HEURISTIC` or `NOT_VERIFIED`.

A lower layer cannot promote a claim beyond the authority of a higher layer.

## 9. Evidence-Class Model

DAY35 uses four threshold evidence classes:

- `DEVICE_KNOWN`: a device fact independently established from trusted device metadata. DAY35 selects **no site threshold** in this class.
- `ANALYTICAL`: a mathematical or implementation property whose validity does not depend on a patient cohort. DAY35 uses analytical checks, but the selected detector operating points are not elevated to this class.
- `RESEARCH_HEURISTIC`: a reversible operating point selected from synthetic development evidence. This is the class of all five selected detector families.
- `SITE_NOT_VERIFIED`: site-specific applicability or thresholds not established. The entire `site-template`, and poor-contact threshold selection, remain here.

## 10. Detector-by-Detector Readiness

| Family | DAY34 state | DAY35 action |
|---|---|---|
| `LF_MISSING_DROPOUT` | Positive truth mislocalized | Create aligned core fixtures; sweep missing/zero-run/flatline parameters |
| `LF_CLIPPING_SATURATION` | Positive truth mislocalized | Create aligned synthetic ADC fixtures; sweep repeated-extrema fraction |
| `LF_BASELINE_NOISE` | Scorable, threshold unresolved | Sweep RMS/MAD research thresholds |
| `LF_POWERLINE` | Scorable | Sweep warning band-power ratio using synthetic 50 Hz metadata |
| `LF_LOW_FREQUENCY_CONTAMINATION` | Scorable | Sweep low-band ratio, drift, transient thresholds |
| `LF_POOR_CONTACT` | No cross-channel truth | `HOLD_NOT_SCORABLE` |

## 11. Synthetic Fixture Contract

The DAY35 fixture manifest is separate from DAY33. Positive localized corruptions must overlap the core window. Each item records:

- family and subtype;
- truth label;
- exact event bounds for local corruptions;
- sampling rate;
- window duration;
- WindowIdentity-style sample/context bounds;
- deterministic seed;
- file SHA-256;
- `clinical_evidence=false`;
- `claim_scope=RESEARCH_ONLY`.

The builder creates 90 fixtures: 30 primary fixtures at 2000 Hz/250 ms and 60 robustness fixtures across 1000, 2000 and 4000 Hz and 250/500 ms windows. These are intentionally simple engineering challenges. They are useful for detecting implementation sensitivity and regressions, not for estimating real clinical operating characteristics.

## 12. Selection Objective

The primary selection objective is explicit:

```text
weighted_error = 3 × false_negative + 1 × false_positive
```

This is **not a clinical risk ratio**. It is a research-engineering preference to avoid a sensitivity study that rewards false allows merely because the corpus is small. Ties are resolved by minimum normalized distance from the upstream provisional operating point, then a deterministic lexicographic rule. The tie-break deliberately avoids unnecessary config churn when several candidates separate the synthetic fixtures equally well.

## 13. Selected Research Operating Points

The deterministic sweep selected the same values as the upstream provisional defaults for all five scorable families:

- Dropout: missing warning fraction `0.01`; zero-run warning fraction `0.25`; flatline peak-to-peak epsilon `1e-12`.
- Clipping: repeated-extrema fraction `0.10` under **synthetic ADC semantics only** (`[-1,+1]`).
- Baseline noise: RMS warning `0.00020`; MAD warning `0.00010` for the synthetic reference profile.
- Power-line: warning ratio `0.08` with 50 Hz **synthetic metadata**.
- Motion/low-frequency: low-frequency ratio `0.22`; normalized drift `0.20`; transient z `6.0`.

This is not evidence that the original values were universally correct. It means that under the DAY35 fixture definitions and explicit tie-break policy, there was no research justification to move them.

## 14. Primary Synthetic Results

Each selected operating point separated the deliberately constructed primary positive/negative engineering fixtures without error. The result must be read with its denominator:

- dropout/flatline family: 6 synthetic positives + 6 negatives;
- clipping: 2 positives + 3 negatives;
- baseline noise: 2 positives + 2 negatives;
- power-line: 2 positives + 2 negatives;
- motion: 2 positives + 2 negatives.

A displayed sensitivity of 1.0 on these tiny synthetic strata is a **fixture check**, not an external performance estimate. The report must never say “100% accurate detector” without this qualifier.

## 15. Fs / Window Robustness Study

Selected research defaults were replayed at 1000, 2000 and 4000 Hz and at 250/500 ms windows on versioned synthetic fixtures. All tested strata produced the expected synthetic binary separation. This evidence only supports the claim that the implementation behaves consistently on these constructed frequencies/durations. It does not prove invariance to real device transfer functions, electrode geometry, patient physiology, or protocol differences.

## 16. Safety Invariants

1. `benchmark-locked` outcome consumption must remain zero.
2. The DAY33 corpus history must not be rewritten.
3. Positive local truth must overlap the target core.
4. `UNKNOWN` and `ABSTAIN` are not converted to PASS.
5. Poor-contact remains HOLD without peer-channel truth.
6. Synthetic ADC limits are not vendor/site ADC facts.
7. Synthetic 50 Hz metadata is not a site mains-frequency claim.
8. The site-template contains no operative numerical threshold.
9. Research selected values have `clinical_threshold_claim=false`.
10. No threshold result is described as diagnostic or clinically validated.

## 17. Environment

Recommended:

```bash
python >= 3.11
numpy
PyYAML
pytest
```

For live repository verification:

```bash
export PYTHONPATH="$PWD/packages/semg-core${PYTHONPATH:+:$PYTHONPATH}"
```

No Internet access is required after upstream artifacts are present.

## 18. Preflight

**Input:** DAY34 evidence, detector modules, DAY33 sealed manifest.

**Action:** verify file presence, count six locked entries without reading any hidden truth, verify detector family readiness, and confirm `site_threshold_status=NOT_VERIFIED` before study execution.

**Expected output:** preflight PASS; locked-consumed counter remains zero.

**Stop:** any locked item exposes non-null truth or a site threshold is already promoted without approved evidence.

## 19. STEP 1 — Build Scorable-Truth Readiness Matrix

### Goal
Prevent an invalid threshold branch from entering the sweep.

### Input
`lf-performance-synthetic-v0.1.csv`, DAY34 candidate list, DAY34 summary.

### Action
Assign each family one of `GO_RESEARCH_SWEEP`, `GO_AFTER_ALIGNED_FIXTURE_REPAIR`, or `HOLD_NOT_SCORABLE`.

### Output
`qa-validation/evidence/day35-scorable-truth-readiness-matrix.csv`.

### Verification
Exactly six families; site status remains `NOT_VERIFIED` for all.

### Negative Check
Poor-contact must not become GO.

### Pass
Five families can enter research evaluation; poor-contact remains HOLD.

## 20. STEP 2 — Freeze DAY35 Fixture Specification

### Goal
Repair truth localization without altering DAY33 history.

### Input
DAY34 truth-window defect report; DAY22 WindowIdentity semantics.

### Action
Create a new fixture factory with exact event bounds and a target core at 0.5 s into the synthetic signal. Store seeds, transforms, WindowIdentity fields and hashes.

### Output
`day35-threshold-study-fixtures.v0.1.manifest.yaml` plus synthetic `.npz` fixtures.

### Verification
Every positive local event overlaps the core; regeneration reproduces hashes.

### Negative Check
A positive event outside the core must fail generation.

### Pass
Aligned dropout/flatline/clipping truth is available without DAY33 mutation.

## 21. STEP 3 — Configure Sweep Grids

### Goal
Make threshold search finite, inspectable and reproducible.

### Action
Freeze parameter grids in `day35-threshold-study-profile.v0.1.yaml` rather than searching continuous parameters or optimizer-driven values.

### Verification
All candidate values are explicit; upstream provisional values are included.

### Pass
Grid fingerprint is stable and code can enumerate candidate counts deterministically.

## 22. STEP 4 — Dropout / Flatline Sweep

### Input
Aligned missing, zero-run, flatline positives and controls.

### Action
Sweep missing warning fraction, zero-run warning fraction and flatline epsilon while preserving upstream fail thresholds.

### Output
Rows in `day35-threshold-sensitivity-results-v0.1.csv`.

### Negative Check
Do not use original misaligned DAY33 positives.

### Pass
Selected parameters are supported by valid core-aligned synthetic evidence and remain `RESEARCH_HEURISTIC`.

## 23. STEP 5 — Clipping Sweep

Clipping uses synthetic verified ADC semantics only. The fixture's rails `-1/+1` exist solely to test detector mechanics. DAY35 must not infer Noraxon ADC limits from them. Sweep repeated-extrema fraction, preserve plateau rule, and select only against DAY35 aligned positives/negatives.

## 24. STEP 6 — Baseline-Noise Sweep

Baseline evaluation is protocol/reference dependent. DAY35 creates a **synthetic reference profile** and never infers rest from low amplitude. Sweep RMS/MAD warning thresholds. The output establishes a research profile only; the site profile remains threshold-null.

## 25. STEP 7 — Power-Line Sweep

Power-line evaluation is enabled with `site_config_status=VERIFIED` only within the synthetic fixture's metadata context and `mains_frequency_hz=50`. This is not a statement about any physical site. Sweep warning band-power ratios and retain high-ratio behavior from the upstream rule.

## 26. STEP 8 — Motion / Low-Frequency Sweep

Sweep warning low-frequency ratio, normalized drift and transient-z thresholds. Retain the detector's no-auto-clean and no-pathology semantics. A motion warning is an acquisition/artifact evidence candidate, not a diagnosis.

## 27. STEP 9 — Poor-Contact HOLD Decision

No parameter sweep is allowed. The rule uses adjacent-channel RMS and corroborating evidence; a single-channel corpus cannot produce a valid positive/negative threshold study. DAY35 records `HOLD_NOT_SCORABLE` and carries this limitation to DAY36/37.

## 28. STEP 10 — Select Research Profile

Apply the explicit weighted-error and tie-break policy. Write exact selected parameters, counts, evidence class, and limitations. Selection is deterministic and reversible.

## 29. STEP 11 — Robustness Replay

Replay selected thresholds across Fs/window strata. Do not retune per stratum. The purpose is to find obvious sampling/window sensitivity. Any degradation must be reported rather than compensated by stratum-specific hidden defaults.

## 30. STEP 12 — Freeze Research vs Site Configuration

The final `thresholds.research-v0.1.yaml` contains two visibly separate profiles:

```text
site-template
  status = SITE_NOT_VERIFIED
  all thresholds = null

research-synthetic-v0.1
  status = RESEARCH_HEURISTIC
  selected synthetic-development values
```

This separation is the main governance deliverable.

## 31. STEP 13 — Validation, Claim Audit and Release Evidence

Run focused tests, regression, config validation, artifact hashing and claim-language checks. Any site promotion, locked-set consumption, or poor-contact selection fails the day.

## 32. Automated Validation

Required test classes:

- `SCHEMA`: threshold profile fields and constants.
- `UNIT`: score, candidate grids, detector calls.
- `CONTRACT`: site profile null, evidence classes, no clinical claim.
- `NEGATIVE`: locked item rejection, site threshold injection, poor-contact promotion.
- `GOLDEN`: deterministic fixture regeneration and selected decision replay.
- `INTEGRATION`: current detector modules + WindowIdentity.
- `REGRESSION`: DAY33/DAY34 and QC safety suites when available.
- `EVIDENCE`: hashes and report/CSV consistency.

## 33. Manual / Research Review

A reviewer should inspect at least:

1. one DAY33 misaligned case from DAY34;
2. its DAY35 aligned replacement;
3. the site-template showing null values;
4. a sweep with multiple equal-performing candidates to understand the upstream-distance tie-break;
5. the poor-contact HOLD decision.

The reviewer is not asked to approve a clinical threshold.

## 34. Failure Injection

- Change a fixture partition to `benchmark-locked` → loader must reject.
- Put a numeric value into site-template → validator must reject.
- Promote `site_threshold_status` → validator must reject.
- Promote poor-contact to selected → validator must reject.
- Move a positive local event outside core and regenerate → fixture builder must fail.
- Change a fixture payload after manifest generation → hash verification must fail.

## 35. Traceability

```text
DAY34 analytical finding
→ readiness matrix
→ DAY35 fixture generation specification
→ fixture SHA + WindowIdentity
→ detector module/version
→ candidate config
→ confusion counts / weighted error
→ selected research parameter
→ thresholds.research-v0.1.yaml
→ ADR + validation report
```

## 36. Acceptance Criteria

DAY35 passes when:

- all five scorable detector families have reproducible research sensitivity evidence;
- poor-contact is explicitly HOLD;
- DAY33 history is preserved;
- locked outcomes consumed = 0;
- selected thresholds are versioned/reversible;
- every selected threshold is `RESEARCH_HEURISTIC`;
- site threshold status is still `NOT_VERIFIED`;
- site-template numbers are null;
- robustness study is reproducible;
- no forbidden clinical/site claim appears.

## 37. Definition of Done

The day is complete only when code, fixtures, config, notebook, report, ADR, tests, manifest, SHA file and DAY36 handoff are frozen together. A numerical YAML file without its provenance evidence is not DoD.

## 38. Stop / Block Conditions

- Any locked truth is evaluated.
- Any DAY33 history is rewritten instead of versioned repair.
- A detector lacks valid positive/negative evidence but still receives a selected threshold.
- Poor-contact receives an operative research threshold without multi-channel truth.
- Site-template receives an operative threshold.
- Research threshold is described as clinical/site validated.
- Reproducibility breaks.

## 39. Known Limitations

- Synthetic fixture boundaries are engineering definitions, not clinical nuisance distributions.
- Small positive denominators make 1.0 sensitivity numerically true but externally weak.
- No public raw dataset has been run through these threshold studies yet.
- No expert annotation exists.
- No site/device ADC or mains setting is inferred.
- Poor-contact threshold remains unresolved.
- Research false-negative weighting is an engineering design choice, not a medical risk estimate.

## 40. Open Questions Carried Forward

- How will public datasets alter detector feature distributions after canonical adapters exist?
- Which thresholds are scale-sensitive to unit/profile differences?
- How should DAY36 define physiology-preservation sentinel cases without creating pathology truth?
- What multi-channel synthetic design is adequate for poor-contact research evaluation?

## 41. Integration Into Main Repository

Use Option-B style additive integration. Copy DAY35 files; do not overwrite site config or shared governance registries without reconciliation. Run the DAY35 runner in the integrated repo so it imports the actual current detector modules.

## 42. Git Workflow

Suggested branch: `research/day35-threshold-sensitivity`. Review generated evidence before commit. Do not add external public raw data, caches or secrets.

## 43. Rollback

Rollback means disable/remove `research-synthetic-v0.1`; it must not require changing the site-template because DAY35 never promotes it. Retain evidence and ADR for audit history.

## 44. Evidence & Provenance Capture

Primary evidence files are the fixture manifest, sensitivity CSV, robustness CSV, selection decision JSON, readiness matrix, repair evidence YAML, threshold config and validation report.

## 45. Closeout Checklist

- [ ] Five scorable families selected as research heuristics.
- [ ] Poor-contact HOLD.
- [ ] Locked consumed = 0.
- [ ] Site thresholds null.
- [ ] DAY33 unchanged.
- [ ] Focused tests pass.
- [ ] Regression pass/known historical exclusions documented.
- [ ] Artifact hashes verified.
- [ ] Peer review template completed later by a human.

## 46. DAY36 Handoff

DAY36 receives a research profile and explicit evidence classes. It may use these research values to construct physiology-preservation/domain challenges, but must not reinterpret them as site thresholds. The most important downstream rule is: **a domain/physiology challenge is allowed to expose unsupported behavior; it is not allowed to redefine pathology as artifact.**

## 47. Final Status Rule

Highest allowed status is `RESEARCH_THRESHOLDS_FROZEN_V0.1`. Site/clinical threshold remains `NOT_VERIFIED`, regardless of synthetic results.

## 48. Detector-Specific Interpretation Notes

### 48.1 Missing samples and explicit zero runs
The missing branch uses a fraction of non-finite values, while the zero-run branch uses the longest consecutive run of exact zero values. These are intentionally separate because scattered missing samples and contiguous acquisition dropout have different structural signatures. DAY35 keeps the upstream fail thresholds fixed and studies the warning operating points. This choice constrains the scope of the experiment: the day is not redesigning detector semantics; it is testing the sensitivity of the existing contract.

### 48.2 Flatline epsilon and unit dependence
The flatline epsilon is numerically tiny and therefore especially dependent on representation scale. If an upstream pipeline converted V to uV before the detector without updating the config, the same epsilon would mean something different by orders of magnitude. DAY35 therefore treats the value as valid only within the declared raw/synthetic representation. DAY40+ processing profiles must never silently reuse this threshold after scaling or normalization without explicit contract mapping.

### 48.3 Clipping and device semantics
Clipping is unique because a plateau at an observed extremum is not sufficient proof of ADC saturation. A physiological or preprocessing plateau can repeat extrema too. The DAY24 detector correctly distinguishes heuristic plateau evidence from verified device-limit evidence. DAY35 exercises the verified branch only because the synthetic generator controls the rails. This test proves code behavior, not device truth.

### 48.4 Baseline noise and protocol role
A baseline/noise detector is not a generic low-amplitude detector. The caller must provide a valid baseline/reference role. DAY35's synthetic reference is explicitly tagged as eligible. This prevents a dangerous shortcut where a weak active signal is silently reclassified as rest and compared against an inappropriate threshold.

### 48.5 Power-line feature resolution
Power-line ratio depends on FFT resolution, tapering, band width, harmonics and sample count. A 250 ms window provides coarser frequency resolution than a 500 ms window. DAY35's robustness table is therefore important even though the synthetic results are stable. A future real-data study must re-check whether the line-band feature behaves similarly under device filtering and different recording durations.

### 48.6 Motion composite feature
Motion evidence is multi-mechanism: low-frequency spectral concentration, normalized drift and transient derivative magnitude can independently trigger a warning. A single scalar “motion threshold” would hide this. The DAY35 research profile preserves all three dimensions so later error analysis can tell which mechanism produced the decision.

## 49. Why the Sweep Is Intentionally Small

A larger grid or optimizer could produce a more impressive search, but it would not produce stronger evidence. The development corpus is deliberately small and synthetic. Increasing the number of candidate parameters without increasing independent evidence would increase the risk of overfitting the fixture factory itself. The chosen grids cover meaningful neighborhoods around the upstream provisional values and boundaries seen in generated examples. This is enough for an engineering sensitivity study and leaves later public-data evaluation genuinely informative.

## 50. Why Public Data Is Not Pulled Into DAY35 Yet

DAY33 verified public source governance but did not acquire bulk raw payloads in-repo. DAY64–72 is the dedicated public benchmark phase in the independent roadmap. Pulling public data into DAY35 without canonical adapters, unit verification, protocol semantics and split governance would mix two questions: “does the detector threshold respond as designed?” and “does this detector generalize across external datasets?” The current day answers only the first. External validity is intentionally deferred rather than simulated.

## 51. Reproducibility Contract

A DAY35 result is reproducible only if all of the following match:

- fixture generator version;
- fixture seed and generation parameters;
- fixture SHA-256;
- WindowIdentity coordinates;
- detector implementation version;
- sweep profile version;
- parameter candidate set;
- selection objective and tie-break rules;
- Python/numpy environment within declared numerical tolerance.

Changing any of these should create a new study version or invalidate direct comparison. A CSV copied without its config and fixture manifest is not sufficient evidence.

## 52. Configuration Reversibility

`research-synthetic-v0.1` is not a migration of site policy. It is a named optional profile. If later evidence shows a different operating point is more useful, create `research-synthetic-v0.2` or a public-data-derived research profile and keep v0.1 for replay. Reversibility is especially important in a portfolio project because future experiments should be able to reproduce the historical result rather than merely showing the newest config.

## 53. Safety Review Questions

Before approving this day, a senior reviewer should ask:

1. Could any selected threshold be mistaken for a clinical/site policy by reading the YAML alone?
2. Are synthetic device constants visually separated from real-device metadata?
3. Is there any code path that reads locked signal payloads during sweep selection?
4. Are the four DAY33 misaligned cases preserved as historical findings?
5. Does the study distinguish lack of scorable evidence from poor detector performance?
6. Can a future developer replace `HOLD_NOT_SCORABLE` with a number without adding evidence?
7. Are performance statements always accompanied by evidence tier and denominator?

If any answer is unsafe or ambiguous, the package should remain `READY_WITH_LIMITATIONS` and not proceed as if the threshold contract were mature.

## 54. Portfolio Value

DAY35 demonstrates more than parameter tuning. It shows benchmark validation, leakage control, safety-oriented loss design, configuration governance, synthetic known-answer testing, cross-Fs/window replay, and explicit claim boundaries. A strong CV description would emphasize this systems discipline rather than quoting tiny synthetic performance percentages. For example: “Built a reproducible research-only threshold sensitivity framework for sEMG QC rules, including truth-localization repair, locked-split leakage guards, deterministic operating-point selection, and site-vs-research configuration isolation.”

## 55. Final Engineering Summary

DAY35 closes the gap between “detectors have arbitrary provisional numbers” and “detectors have a documented research operating profile.” It does not close the gap between research and clinical use. That gap remains intentionally visible. The day is successful precisely because it produces a useful configuration while preserving the statement that the site threshold is unknown.
