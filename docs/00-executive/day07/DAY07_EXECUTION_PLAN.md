# DAY 07 — Legacy Asset Audit & Disposition Matrix
## Engineering Execution Specification & Integration Runbook

## 0. Document Control

| Field | Value |
|---|---|
| Day | 07 |
| Official task | Legacy Asset Audit & Disposition Matrix |
| Phase | Phase 0 — Re-baseline & Clinical Discovery |
| Product | MotionLab Data Intelligence & Automation Platform — Vinmec MotionLab × VSF |
| Version | v1.0 |
| Language | Vietnamese with technical English terms |
| Primary owner | VSF Engineering / Clinical AI / DSP / QA |
| Clinical role | Governance and engineering re-baseline only; no clinical interpretation |
| Production code required | No |
| Supporting QA/tooling | Yes |
| Upstream dependency | DAY06 accepted/integrated evidence inventory and access package |
| Downstream consumer | DAY08 Requirements v0.2 Freeze & GATE A |

This file is intentionally a runbook, not a management summary. A junior engineer should be able to execute DAY07 from preflight to handoff without guessing a critical technical step.

---

## 1. Executive Intent

DAY07 answers one dangerous question before the project freezes requirements in DAY08:

> **What should we do with all engineering work created before the MotionLab problem was re-baselined?**

The answer cannot be “delete everything” because the repository contains valuable generic parsers, DSP primitives, metrics, UI infrastructure, tests, reproducibility assets and research evidence. It also cannot be “reuse everything” because legacy code may encode old assumptions: classifier-first product framing, public-healthy thresholds, gesture-specific schemas, binary-fatigue claims, mandatory MFCV assumptions, or a lower-limb schedule that has been superseded.

DAY07 therefore creates an explicit, versioned disposition for each legacy asset family:

```text
REUSE_AS_IS
ADAPT
REVALIDATE
PARK
DEPRECATE
```

The main output is not a refactor. It is a **decision boundary** that tells future days what may be reused, what must be changed, what requires new evidence, what should remain parked, and what is no longer active product direction.

---

## 2. Why This Day Exists

The re-baselined roadmap explicitly states that previous engineering assets remain useful but do not automatically become site-validated clinical assets. Without DAY07, three failure modes become likely:

1. A mature old component is reused because “it already works,” even though its contract conflicts with the current SRS.
2. A public-dataset threshold/model is silently promoted into MotionLab site logic.
3. Engineers continue the old gesture/fatigue/lower-limb roadmap due to sunk-cost momentum instead of the current North Star: automation of data-processing toil.

DAY07 prevents these by converting historical work into a controlled inventory with current semantics.

---

## 3. Position in the 90-Day Critical Path

```text
DAY01 requirements/source-of-truth
  ↓
DAY02 workflow measurement design
  ↓
DAY03 observation/baseline evidence
  ↓
DAY04 artifact-vs-physiology taxonomy
  ↓
DAY05 privacy/de-identification gate
  ↓
DAY06 real-data evidence inventory/access package
  ↓
DAY07 legacy asset audit & disposition
  ↓
DAY08 requirements v0.2 freeze / GATE A
  ↓
DAY09+ real data contracts and implementation
```

DAY07 is the last major “what from the old system is still allowed?” checkpoint before requirements freeze.

---

## 4. Relationship With Previous Day

DAY06 establishes evidence classes, governance status and the rule that public/sample data cannot silently substitute for governed MotionLab evidence. DAY07 consumes that logic when reviewing legacy models, thresholds, datasets and experiments.

For example:

```text
Old gesture classifier
+ strong public-dataset accuracy
≠ site clinical evidence
```

and:

```text
Old QC threshold
+ synthetic/public validation
≠ approved MotionLab threshold
```

DAY07 must preserve the evidence-tier boundary from DAY06.

### What DAY07 may do if DAY06 is integrated but not fully site-approved

It may prepare the disposition matrix, regression scope and technical-debt register. It may not promote an asset to site-validated simply because the previous day is present in Git.

---

## 5. What Must Be True Before Starting

Before STEP 0, confirm:

- the current repository contains the integrated DAY06 artifacts or the operator has a documented reason why they are temporarily unavailable;
- current PRD and SRS are available;
- the re-baselined 90-day roadmap is available;
- the current skeleton or equivalent repository architecture is available;
- the operator understands that DAY07 is an audit/disposition day, not a feature-development day;
- no raw patient data needs to be opened for this task.

If current PRD/SRS are unavailable, **STOP**. Legacy code cannot be classified without the current authority it is being compared against.

---

## 6. Objectives

DAY07 is complete only when all of the following are addressed:

1. Identify the important legacy asset families from Days 2–40/PRE-DAY41_01.
2. Bind each family to one allowed disposition.
3. Explain why the disposition is correct under current PRD/SRS.
4. Separate reusable engineering behavior from stale clinical/product meaning.
5. Define regression scope for behavior worth preserving.
6. Register technical debt required before future reuse.
7. Mark site-dependent assumptions as `NOT_VERIFIED`, `REVALIDATE` or equivalent.
8. Provide tooling to scan the actual current monorepo and bind family decisions to real paths.
9. Update traceability for PRD Product Principles, NFR-001 and NFR-011.
10. Produce a clear handoff to DAY08 without implementing DAY08 freeze logic.

---

## 7. Non-Goals / Explicitly Out of Scope

DAY07 must **not**:

- refactor all legacy code;
- retrain or benchmark models;
- choose new clinical thresholds;
- declare MotionLab MFCV eligibility;
- revive gesture recognition as P0;
- implement the new MR4 parser scheduled for DAY16–17;
- implement QC detectors scheduled for DAY21–39;
- implement preprocessing profiles scheduled for DAY40+;
- remove historical evidence from Git solely because it is deprecated;
- rewrite the entire repository structure;
- decide DAY08 Gate A prematurely.

Remember:

```text
MORE DETAIL != MORE SCOPE
```

---

## 8. Source-of-Truth for This Day

Apply the hierarchy in this order:

1. Current SRS MotionLab Data Intelligence.
2. Current PRD MotionLab Data Intelligence.
3. Observed MotionLab CSV Architecture / real data reality.
4. Re-baselined 90-Day Roadmap.
5. Current Project Skeleton.
6. Integrated DAY01–DAY06 artifacts.
7. Historical Days 2–40 / PRE-DAY41_01 artifacts.
8. Legacy implementation plans/research.
9. Assumption.

If an old model card says “fatigue classifier is the primary product” and current PRD says binary fatigue classifier is out of scope as the product center, the current PRD wins. Do not silently average the two positions.

---

## 9. Requirements Addressed Today

| Requirement | Meaning for DAY07 |
|---|---|
| PRD Product Principles | Every legacy disposition must respect Quality before intelligence, Preserve physiology, Human final authority, Abstain over hallucinate, Traceable by design, Automation of toil first, Modality-neutral foundation. |
| NFR-001 Reproducibility | Reusable behavior must have an explicit regression/replay strategy. |
| NFR-011 Versioning | Data schema, QC config, preprocessing, metric registry and model/rule reuse must be versioned rather than silently inherited. |

Supporting safety requirements are relevant as constraints, but DAY07 should not falsely claim to implement them.

---

## 10. Inputs

### Mandatory project inputs

```text
PRD_MotionLab_Data_Intelligence_v0.1
SRS_MotionLab_Data_Intelligence_v0.1
Motion_Lab_CSV_Architecture
MotionLab_Data_Intelligence_90_Day_Rebaselined_Execution_Roadmap_v1.0
current project skeleton
DAY06 artifacts in the real repo
```

### Historical inputs to inspect

At minimum, look for families representing:

```text
generic parser / canonical signal objects
QC / abstention
generic DSP / preprocessing / windowing
RMS / MAV / MDF / MNF
14-feature gesture pipeline
classical gesture models
personalization / few-shot
confidence calibration
fatigue context / fatigue classifier
MFCV
Task C quantitative metrics
cross-dataset transfer
offline integrated pipeline
schemas / OpenAPI
web portal / UI
human review / audit
model governance / reproducibility
public healthy datasets
old post-PRE-DAY41 lower-limb schedule
PRE-DAY41_01 governance checkpoint
```

---

## 11. Mandatory Outputs

Exactly the roadmap outputs:

```text
docs/00-executive/rebaseline/legacy-asset-disposition.v1.0.md
qa-validation/regression/legacy-regression-scope.v1.0.yaml
docs/00-executive/rebaseline/technical-debt-register.v1.0.md
```

### Output content contract

#### `legacy-asset-disposition.v1.0.md`
Must contain:

- disposition vocabulary;
- explicit rationale per family;
- reuse boundary;
- prohibited reuse;
- evidence status;
- downstream owning day(s);
- current PRD/SRS alignment;
- actual-repo confirmation requirement.

#### `legacy-regression-scope.v1.0.yaml`
Must contain:

- suite ID;
- asset family;
- disposition;
- purpose;
- includes;
- excludes;
- trigger days;
- statement that regression success does **not** establish site validity.

#### `technical-debt-register.v1.0.md`
Must contain:

- debt ID;
- severity;
- legacy family;
- exact risk;
- owning future day;
- evidence required to close;
- prohibited shortcut where clinically/safety relevant.

---

## 12. Supporting Outputs

DAY07 also uses supporting governance/QA artifacts:

```text
data-platform/catalog/legacy-asset-inventory.v1.0.yaml
docs/00-executive/decisions/day07-legacy-disposition-decision-record.v1.0.yaml
docs/03-architecture/traceability/day07-legacy-asset-traceability.v1.0.csv
qa-validation/requirements/day07-acceptance-criteria.md
qa-validation/evidence/day07-validation-report.json
qa-validation/evidence/day07-source-hash-ledger.json
qa-validation/evidence/day07-artifact-manifest.json
qa-validation/test-data/day07/synthetic-repo-asset-cases.yaml
packages/common-schemas/json/legacy-asset-inventory.schema.json
packages/common-schemas/json/legacy-regression-scope.schema.json
scripts/dev/day07_asset_audit.py
scripts/dev/validate_day07_legacy_assets.py
scripts/dev/check_day07_artifacts.py
scripts/dev/run_day07_checks.sh
```

These are QA/governance tooling, not production clinical code.

---

## 13. Target Repo Tree After This Day

```text
repo-root/
├── data-platform/
│   └── catalog/
│       └── legacy-asset-inventory.v1.0.yaml
├── docs/
│   ├── 00-executive/
│   │   ├── decisions/
│   │   │   └── day07-legacy-disposition-decision-record.v1.0.yaml
│   │   ├── day07/
│   │   │   └── day07-closeout-summary.v1.0.md
│   │   └── rebaseline/
│   │       ├── legacy-asset-disposition.v1.0.md
│   │       └── technical-debt-register.v1.0.md
│   └── 03-architecture/
│       └── traceability/
│           └── day07-legacy-asset-traceability.v1.0.csv
├── packages/common-schemas/json/
│   ├── legacy-asset-inventory.schema.json
│   └── legacy-regression-scope.schema.json
├── qa-validation/
│   ├── automated-tests/governance/test_day07_legacy_asset_audit.py
│   ├── evidence/
│   ├── regression/legacy-regression-scope.v1.0.yaml
│   ├── requirements/day07-acceptance-criteria.md
│   └── test-data/day07/synthetic-repo-asset-cases.yaml
└── scripts/dev/
    ├── day07_asset_audit.py
    ├── validate_day07_legacy_assets.py
    ├── check_day07_artifacts.py
    └── run_day07_checks.sh
```

No new production service/package is justified today.

---

## 14. Data / Evidence Boundaries

DAY07 should inspect **code, configs, manifests, docs, tests and path metadata**. It does not need to inspect patient signal values.

Safe inputs:

- tracked source-code paths;
- YAML/JSON/Markdown configs and manifests;
- model cards and experiment metadata;
- public dataset metadata;
- existing test names;
- Git history/diff if available.

Do not open patient raw data merely to decide whether a parser or model should be parked.

### Important distinction

```text
Asset exists in repo
≠ asset is validated

Asset has tests
≠ asset matches current SRS

Model has strong accuracy
≠ model belongs on current critical path
```

---

## 15. Safety & Governance Invariants

The following statements must remain true throughout DAY07:

- pathology != noise;
- physiological variation != acquisition artifact;
- unavailable metric != zero;
- public healthy data != MotionLab clinical effectiveness evidence;
- 16 sensors != MFCV eligibility;
- old schedule != current authority;
- regression PASS != site validation;
- test PASS != clinician approval;
- parked != deleted;
- deprecated != erased historical provenance.

---

## 16. Environment / Tooling Requirements

Minimum:

```text
Python >= 3.11
Git
pytest
PyYAML
jsonschema
bash
```

Recommended commands:

```bash
python3 --version
git --version
python3 -c 'import yaml, jsonschema; print("deps-ok")'
```

Expected exit code: `0`.

No NumPy/SciPy/scikit-learn/PyTorch is required for DAY07.

---

## 17. Preflight Checklist

Run from repository root:

```bash
git status --short
git branch --show-current
python3 --version
```

Check expected folders:

```bash
test -d docs
test -d qa-validation
test -d scripts
```

Check DAY06 inputs if integrated:

```bash
test -f data-platform/catalog/motionlab-evidence-inventory.v0.1.yaml
test -f data-platform/governance/evidence-tier-policy.v0.1.md
```

If the exact DAY06 paths differ because of a reviewed integration decision, document that change instead of fabricating files.

---

# 18. Detailed Execution Procedure

## STEP 0 — Freeze the DAY07 scope before touching legacy assets

### Goal
Create a written mental boundary: DAY07 classifies legacy assets; it does not modernize them.

### Input
- roadmap DAY07 section;
- current PRD/SRS;
- this runbook.

### Why
Without scope lock, the engineer will see old code and start “fixing” it, accidentally doing DAY09–60 work early.

### Concepts used
Source-of-truth, scope boundary, disposition, technical debt.

### Action
Read roadmap DAY07 and DAY08 sections. Write down the three mandatory DAY07 outputs and the five allowed dispositions.

### Files to create / modify
None yet.

### Code / Command

```bash
grep -n -A70 'DAY 07 — Legacy Asset Audit' path/to/roadmap.md
```

If your roadmap filename differs, use the actual path.

### Expected Output
You should see the DAY07 objective, three output paths, product-principle/NFR traceability and the prohibition against reusing threshold/model/clinical claims from public healthy data.

### Verification
You can explain in one sentence why “improve old model accuracy” is out of scope.

### Negative Check
If your task list contains “retrain gesture model,” scope has leaked.

### Evidence Produced
No artifact; preflight knowledge only.

### Stop Condition
Current roadmap unavailable or conflicts with the copy in this handoff.

### Pass Condition
Scope statement is unambiguous.

---

## STEP 1 — Confirm source-of-truth and upstream evidence boundaries

### Goal
Ensure legacy audit compares against current authority, not historical momentum.

### Input
PRD, SRS, DAY06 evidence-tier policy.

### Why
Disposition is meaningless unless you know what “current correct behavior” means.

### Concepts used
Authority hierarchy, evidence tier, site validation.

### Action
Review current Product Principles and SRS NFR-001/NFR-011. Review DAY06 rule preventing ungoverned/public evidence from being promoted.

### Files to create / modify
No new files; notes may remain local.

### Code / Command

```bash
grep -Rni 'Quality before intelligence\|Automation of toil first' docs clinical data-platform 2>/dev/null | head -n 30
```

### Expected Output
At least the integrated PRD-derived/current governance sources should be discoverable.

### Verification
You can state why old QC thresholds are `REVALIDATE`, not `REUSE_AS_IS`.

### Negative Check
If “previous benchmark > X%” is used as the only reason to reuse a clinical threshold, fail the review.

### Evidence Produced
Decision rationale later captured in the disposition matrix.

### Stop Condition
Current PRD/SRS cannot be located.

### Pass Condition
Authority hierarchy is documented and understood.

---

## STEP 2 — Generate actual current-repository legacy path inventory

### Goal
Bind documented asset families to real tracked paths in the post-DAY06 repository.

### Input
Current Git repository.

### Why
The handoff package cannot see your current monorepo filesystem. Skeleton documentation alone cannot prove a path currently exists.

### Concepts used
Path inventory, tracked file, discovery vs semantic review.

### Action
Run the DAY07 audit helper after integrating the patch.

### Files to create / modify

```text
qa-validation/evidence/day07-repo-scan.json
```

### Implementation details
The helper:

1. prefers `git ls-files` so it audits version-controlled assets without crawling `.venv`/`node_modules`;
2. falls back to `os.walk` with pruning when Git metadata is unavailable;
3. classifies candidate paths into `LA-*` families using path patterns;
4. reports unclassified legacy-looking candidates;
5. does **not** claim semantic correctness from path matching.

### Code / Command

```bash
python3 scripts/dev/day07_asset_audit.py \
  --root . \
  --output qa-validation/evidence/day07-repo-scan.json
```

Expected exit code without `--strict`: `0`.

### Expected Output
A JSON object containing:

```json
{
  "candidate_count": 123,
  "classified_family_count": 12,
  "unclassified_count": 4,
  "repo_confirmation_complete": false
}
```

Numbers are examples only; do not copy them into evidence.

### Verification
Open the report and sample paths from at least five families.

### Negative Check
A path containing `day37_taskc` classified as gesture-only would indicate a rule problem.

### Evidence Produced
`day07-repo-scan.json`.

### Stop Condition
The helper returns malformed JSON, audits the wrong repository root, or path count is zero despite a known populated repo.

### Pass Condition
Repository scan is explainable and representative; path triage can begin.

---

## STEP 3 — Review unclassified candidates before accepting automated classification

### Goal
Prevent path heuristics from silently becoming disposition decisions.

### Input
`day07-repo-scan.json`.

### Why
A filename can be ambiguous. `fatigue_context_policy.yaml` may contain reusable reason semantics, while `fatigue_classifier.pkl` represents a deprecated product direction. Both include the word “fatigue.”

### Concepts used
Heuristic triage, semantic review, false classification.

### Action
For each unclassified or high-risk candidate:

- open only code/config/docs needed for semantic inspection;
- identify responsibility;
- map to an existing `LA-*` family or create a proposed new family entry;
- if a new family is needed, update the inventory and disposition matrix through review rather than hiding it.

### Files to create / modify

```text
data-platform/catalog/legacy-asset-inventory.v1.0.yaml
docs/00-executive/rebaseline/legacy-asset-disposition.v1.0.md
```

### Code / Command

```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path('qa-validation/evidence/day07-repo-scan.json')
d = json.loads(p.read_text())
for item in d['unclassified_candidates']:
    print(item)
PY
```

### Expected Output
A finite list requiring review, ideally zero after disposition update.

### Verification
Every legacy-looking candidate is either mapped or explicitly marked for review.

### Negative Check
Do not add a catch-all `LA-99 = OTHER` solely to force zero unclassified paths.

### Evidence Produced
Reviewed path-family mapping.

### Stop Condition
A high-risk asset has unclear purpose and no owner/source evidence.

### Pass Condition
No high-risk asset remains silently unclassified.

---

## STEP 4 — Audit generic ingestion assets

### Goal
Decide what parser/data-contract code can survive the re-baseline.

### Input
Paths mapped to LA-01.

### Why
Generic parsers are high-value reuse candidates but can hide dangerous assumptions about sampling rate, units and raw preservation.

### Concepts used
Data contract, heterogeneous sampling, raw immutability, provenance.

### Action
For representative ingestion modules, inspect:

- whether input format is hard-coded;
- whether missing values are preserved;
- whether units are explicit;
- whether source identity/hash exists;
- whether a single sampling rate is assumed;
- whether unknown metadata is silently dropped.

### Files to create / modify
Disposition and debt register only.

### Code / Command

```bash
grep -Rni 'sampling_rate\|frequency\|units\|source_hash\|read_csv' \
  ai-core data-platform packages services 2>/dev/null | head -n 100
```

### Expected Output
Evidence supporting `ADAPT`, not a full parser refactor.

### Verification
At least one concrete reuse boundary and one adaptation requirement are recorded.

### Negative Check
“Parser works on Mendeley CSV” cannot prove MR4 compatibility.

### Evidence Produced
LA-01 section + TD-001.

### Stop Condition
You start modifying parser production behavior. That belongs to later days.

### Pass Condition
Disposition rationale is complete.

---

## STEP 5 — Audit QC, preprocessing and metrics separately

### Goal
Prevent three different layers from being collapsed into “signal processing.”

### Input
LA-02, LA-03, LA-04 paths.

### Why
QC asks whether data is supportable; preprocessing transforms eligible data; metrics summarize/measure. Reuse safety differs by layer.

### Concepts used
QC vs preprocessing vs metric, analytical validity vs site validity.

### Action
Review representative configs/tests/modules and classify:

- QC architecture: `REVALIDATE` for thresholds/site semantics;
- DSP primitives: `ADAPT` around profile/provenance;
- RMS/MAV/MDF/MNF math: `ADAPT` with eligibility and analytical verification.

Read Feynman Guide sections on “same math, different evidence scope” before this step.

### Files to create / modify

```text
legacy-asset-disposition.v1.0.md
technical-debt-register.v1.0.md
legacy-regression-scope.v1.0.yaml
```

### Code / Command

```bash
grep -Rni 'threshold\|bandpass\|notch\|RMS\|MDF\|MNF' \
  ai-core packages services configs qa-validation 2>/dev/null | head -n 150
```

### Expected Output
Three clearly different dispositions/reuse conditions.

### Verification
No QC threshold is marked `REUSE_AS_IS` merely because it has tests.

### Negative Check
A rule “amplitude below X = bad channel” without site/protocol evidence must not be promoted.

### Evidence Produced
LA-02..04 + TD-002..04.

### Stop Condition
A threshold appears site-specific but source/evidence cannot be located.

### Pass Condition
It is explicitly `REVALIDATE`/debt, not guessed.

---

## STEP 6 — Audit model-centric legacy work against the new North Star

### Goal
Separate valuable research assets from product-critical assets.

### Input
LA-05..09, LA-12.

### Why
These are the strongest sources of sunk-cost bias.

### Concepts used
Technical debt, sunk-cost bias, domain shift, regression-only asset, product scope.

### Action
Review gesture, personalization, confidence, fatigue and transfer assets. Ask:

1. Does it reduce current P0 data toil?
2. Does it depend on public healthy data?
3. Does it imply diagnosis/classification as product center?
4. Is any generic infrastructure reusable independently of the old task?

### Files to create / modify
Main disposition and debt register.

### Code / Command

```bash
grep -Rni 'gesture\|personalization\|fatigue\|cross-dataset\|transfer' \
  ai-core apps docs qa-validation 2>/dev/null | head -n 200
```

### Expected Output
Gesture/personalization/transfer mostly `PARK`; binary fatigue product center `DEPRECATE`; abstention infrastructure selectively `ADAPT`.

### Verification
No old classifier becomes a DAY08 P0 requirement by inertia.

### Negative Check
Do not delete research outputs merely because they are parked.

### Evidence Produced
LA-05..09, LA-12 + TD-005..07.

### Stop Condition
You discover an active current requirement that genuinely depends on one of these assets but is absent from PRD/SRS. Open a decision/change record; do not silently override scope.

### Pass Condition
Product scope and regression scope are separated.

---

## STEP 7 — Audit MFCV and Task C quantitative assets

### Goal
Keep useful scientific work without overclaiming site eligibility or interpretation.

### Input
LA-10 and LA-11 paths.

### Why
MFCV is explicitly optional/not verified; Task C metrics can be useful but need protocol and eligibility.

### Concepts used
Eligibility, conditional capability, bilateral/longitudinal compatibility.

### Action
For MFCV, identify whether code assumes geometry/IED/alignment. Mark site use `REVALIDATE`. For Task C, identify reusable math vs old task assumptions and mark `ADAPT`.

### Files to create / modify
Disposition and technical debt.

### Code / Command

```bash
grep -Rni 'mfcv\|conduction.velocity\|taskc\|symmetry\|co-contraction' \
  ai-core packages docs qa-validation 2>/dev/null | head -n 150
```

### Expected Output
No MFCV default enablement; quantitative metrics have eligibility debt.

### Verification
The phrase “16 sensors therefore MFCV-ready” does not appear as an accepted claim.

### Negative Check
A metric existing in a parquet/report file does not establish current protocol supportability.

### Evidence Produced
LA-10..11 + TD-008/TD-004.

### Stop Condition
Site geometry evidence is unexpectedly found and appears to contradict current `NOT_VERIFIED`. Open evidence review/change record rather than silently updating the claim.

### Pass Condition
Conditional capability remains explicit.

---

## STEP 8 — Audit pipeline, schemas, UI and human-review infrastructure

### Goal
Preserve reusable platform infrastructure while removing old semantic hierarchy.

### Input
LA-13..16.

### Why
These are high-value reuse areas, but old screens and orchestration can make the wrong thing look primary or final.

### Concepts used
Contract-driven architecture, fail closed, exception-first UX, clinician approval.

### Action
Inspect representative orchestration/API/UI/review assets and document:

- infrastructure worth retaining;
- old task-specific contracts to change;
- final-looking outputs to prohibit;
- future-day owner.

### Files to create / modify
Disposition + debt + regression scope.

### Code / Command

```bash
grep -Rni 'final\|approve\|override\|FatigueStatus\|GestureHistory\|offline_pipeline' \
  apps services packages ai-core 2>/dev/null | head -n 200
```

### Expected Output
UI shell/HITL concepts `ADAPT`; no automatic finalization preserved.

### Verification
Reuse notes point to DAY52–63 rather than implementing them now.

### Negative Check
A “Fatigue score 82/100” card must not be preserved as a generic clinical output if eligibility is absent.

### Evidence Produced
LA-13..16 + TD-009..12.

### Stop Condition
An active UI path currently auto-finalizes clinical output. Mark CRITICAL debt; do not hide it.

### Pass Condition
Risk and owner are explicit.

---

## STEP 9 — Audit governance, public datasets and old schedules

### Goal
Protect reproducibility assets while de-authorizing stale schedules and evidence misuse.

### Input
LA-17..20.

### Why
Governance code can be reusable almost as-is; old schedules and public data can be misleading even if technically sound.

### Concepts used
Versioning, reproducibility, historical provenance, deprecation.

### Action
Review model-agnostic manifests/versioning utilities separately from task-specific model registry assumptions. Mark public datasets research/regression-only. Mark old post-PRE-DAY41 schedule deprecated as schedule. Preserve PRE-DAY41_01 governance provenance but adapt priorities.

### Files to create / modify
All three mandatory outputs.

### Code / Command

```bash
grep -Rni 'model_registry\|environment-lock\|pre-day41\|lower-limb.*roadmap' \
  ai-core docs qa-validation configs 2>/dev/null | head -n 200
```

### Expected Output
NFR-001/NFR-011 regression scope is concrete; obsolete schedule cannot authorize future work.

### Verification
`DEPRECATE` is used for active direction, not as a command to destroy historical records.

### Negative Check
Do not remove hashes/manifests needed to reproduce historical results.

### Evidence Produced
LA-17..20 + TD-013..15.

### Stop Condition
A historical schedule is referenced by current code as active authority. Record high-risk debt and raise review.

### Pass Condition
Authority and provenance are separated.

---

## STEP 10 — Validate machine-readable contracts and negative cases

### Goal
Prove the inventory/regression scope is structurally consistent.

### Input
YAML inventory, regression scope, JSON schemas, synthetic path cases.

### Why
Human-readable Markdown alone cannot prevent duplicate IDs, invalid disposition or accidental clinical-claim flags.

### Concepts used
Schema validation, negative testing, deterministic QA.

### Action
Run the day validator/tests.

### Files to create / modify

```text
qa-validation/evidence/day07-validation-report.json
qa-validation/evidence/day07-artifact-manifest.json
```

The validator/test run may update only DAY07-owned evidence artifacts.

### Code / Command

```bash
PYTHONDONTWRITEBYTECODE=1 \
python3 scripts/dev/validate_day07_legacy_assets.py

PYTHONDONTWRITEBYTECODE=1 \
python3 -m pytest -q -p no:cacheprovider \
  qa-validation/automated-tests/governance/test_day07_legacy_asset_audit.py
```

### Expected Output
All tests pass. No `__pycache__` or `.pytest_cache` is created inside tracked artifacts.

### Verification
Exit code `0`.

### Negative Check
Synthetic invalid disposition `KEEP_FOREVER` must fail schema/contract validation.

### Evidence Produced
`day07-validation-report.json` after runner finalization.

### Stop Condition
Any schema/contract/safety test fails.

### Pass Condition
Automated suite passes.

---

## STEP 11 — Perform manual senior/clinical-safety review

### Goal
Check semantic correctness that path patterns and schemas cannot decide.

### Input
All DAY07 artifacts + repo scan.

### Why
A machine can identify “fatigue” in a filename; it cannot determine whether a particular component is a reusable evidence renderer or an unsafe clinical classifier without context.

### Concepts used
Human review, source authority, evidence promotion.

### Action
Reviewer must answer:

- Is every high-risk family disposition justified?
- Are any numerical thresholds incorrectly marked reusable?
- Are any public-dataset findings presented as site evidence?
- Is MFCV still optional/not verified?
- Is human final authority preserved?
- Are parked assets clearly not deleted?
- Are deprecated schedules clearly not active?
- Are NFR-001 and NFR-011 responsibilities assigned?

### Files to create / modify
May add review notes to the main disposition/debt register; do not create fake approvals.

### Code / Command
No automated command substitutes for this review.

### Expected Output
Reviewer name/approval can be recorded in your normal change-control process if available.

### Verification
No unresolved CRITICAL semantic issue is hidden.

### Negative Check
“Tests pass” is not an acceptable answer to “is this QC threshold site-valid?”

### Evidence Produced
Human review record in project workflow/change request.

### Stop Condition
Reviewer finds source conflict or unsafe reuse.

### Pass Condition
All blocking findings resolved or explicitly blocked with owner.

---

## STEP 12 — Close DAY07 and prepare DAY08 handoff

### Goal
Produce exactly one honest DAY07 status.

### Input
Automated validation + actual repo scan + human review.

### Why
DAY08 freezes requirements; it must know whether legacy ambiguity remains.

### Concepts used
Final status taxonomy, evidence gate, handoff contract, no-fake-GO principle.

### Action
Apply status rule:

```text
GO_FOR_DAY_08
  only if:
  - mandatory artifacts pass;
  - actual current-repo inventory has been reviewed;
  - no unclassified critical legacy path remains;
  - no source conflict is silently unresolved.

READY_WITH_LIMITATIONS
  if engineering artifacts are sound but repo/path or non-critical review remains incomplete.

BLOCKED_WITH_EVIDENCE
  if a critical source/evidence/governance conflict prevents safe disposition.
```

### Files to create / modify

```text
docs/00-executive/day07/day07-closeout-summary.v1.0.md
qa-validation/evidence/day07-validation-report.json
```

### Code / Command

```bash
bash scripts/dev/run_day07_checks.sh
```

### Expected Output
One deterministic engineering status plus explicit repo-confirmation/human-review limitation.

### Verification
Read the JSON report; do not infer status only from pytest output.

### Negative Check
`GO_FOR_DAY_08` with `repo_confirmation_complete=false` is invalid.

### Evidence Produced
Final validation report and closeout summary.

### Stop Condition
Status inputs disagree.

### Pass Condition
Handoff is internally consistent.

---

## 19. Automated Validation Strategy

DAY07 uses multiple layers:

| Test layer | Required | Purpose |
|---|---:|---|
| Static check | Yes | Files exist, UTF-8, no obvious placeholder/compound formatting problems. |
| Schema test | Yes | Inventory and regression YAML obey allowed enums/required fields. |
| Unit test | Yes, QA helper only | Path classifier handles known examples deterministically. |
| Contract test | Yes | Every LA ID unique; disposition allowed; future day ranges valid. |
| Negative test | Yes | Invalid disposition, clinical-claim-enabled regression, duplicate ID, unclassified legacy candidate. |
| Golden test | Limited | Synthetic path-family examples. |
| Integration test | Yes | Audit helper works in a synthetic Git repo with legacy/current assets. |
| Regression test | Yes | DAY06 evidence-tier concepts remain unmodified; DAY07 does not create raw/model training artifacts. |
| Manual review | Yes | Semantic disposition. |
| Expert review | Recommended | Clinical/DSP review for QC/MFCV/fatigue semantics. |
| Evidence gate | Yes | Repo confirmation + unresolved high-risk assets control final status. |

---

## 20. Manual / Expert Review

Minimum reviewers when available:

- engineering/architecture reviewer for LA-01, LA-13..17;
- DSP reviewer for LA-02..04, LA-10..11;
- product/clinical-safety reviewer for LA-05..09, LA-15..16, LA-18..20.

A single operator may prepare the artifacts, but high-risk semantic decisions should be surfaced for review rather than silently self-certified.

---

## 21. Failure Injection / Negative Tests

Required negative scenarios:

1. Inventory contains disposition `KEEP` → fail.
2. Two asset families use duplicate `LA-05` → fail.
3. Regression suite sets `clinical_claim_allowed: true` → fail.
4. MFCV family is `REUSE_AS_IS` with no site eligibility evidence → fail policy test.
5. Binary fatigue product center is marked P0 active → fail.
6. Public healthy dataset is marked site clinical evidence → fail.
7. Deprecated old schedule is used as higher authority than current roadmap → fail.
8. Repo scan finds `day37_*` legacy path not classifiable → review required, no GO.
9. Regression success is described as site validation → fail content check.
10. `GO_FOR_DAY_08` while repo confirmation remains false → fail final status check.

---

## 22. Requirement Traceability

| Requirement | Source | What DAY07 does | Artifact | Test/Evidence | State after DAY07 |
|---|---|---|---|---|---|
| PRD Product Principles | PRD §9 | Uses seven principles as disposition filters | legacy-asset-disposition | policy/content review | DESIGNED |
| NFR-001 | SRS | Defines protected reusable behavior and replay/regression boundaries | legacy-regression-scope | schema + suite review | DESIGNED |
| NFR-011 | SRS | Requires versioned reuse/adaptation/revalidation and assigns future owners | disposition + debt register | traceability tests | DESIGNED |

DAY07 does not claim NFR-001 or NFR-011 are fully implemented system-wide; it creates the governance contribution required by the roadmap.

---

## 23. Acceptance Criteria

DAY07 acceptance requires:

- mandatory artifact `legacy-asset-disposition.v1.0.md` exists and is reviewed;
- all assumptions/evidence gaps are explicit;
- allowed dispositions are controlled and mutually understood;
- no legacy threshold/model/clinical claim is reused solely due to public healthy performance;
- PRD Product Principles, NFR-001 and NFR-011 traceability is present;
- regression scope distinguishes behavior preservation from site validation;
- technical debt assigns owner/future day/evidence to close high-risk reuse gaps;
- actual repo scan is run before final GO;
- no raw patient data or model training is required for DAY07.

---

## 24. Definition of Done

Engineering package DoD:

```text
[ ] 3 mandatory roadmap outputs present
[ ] machine-readable inventory valid
[ ] regression scope valid
[ ] technical debt register complete
[ ] QA helper tests pass
[ ] no pycache/cache in package
[ ] source hashes recorded
[ ] integration manifest valid
[ ] ZIP integrity valid
```

Program/day DoD additionally requires:

```text
[ ] current-repo scan executed after integration
[ ] unclassified critical candidates resolved
[ ] semantic human review completed
[ ] final status honestly assigned
```

---

## 25. Stop / Block Conditions

**STOP immediately** if:

- current PRD/SRS unavailable;
- source conflict cannot be resolved by hierarchy;
- a site-specific threshold is being promoted without evidence;
- public/easy data is being substituted for blocked site evidence while preserving claim;
- actual repo scan reveals unclassified high-risk legacy assets;
- MFCV is being enabled from sensor count alone;
- a legacy model/UI automatically produces a final-looking clinical result and owner/remediation is unknown.

Use `BLOCKED_WITH_EVIDENCE` when the missing evidence affects safety/validity, not to punish ordinary cleanup debt.

---

## 26. Known Limitations

This handoff environment does not contain the user's exact post-DAY06 current monorepo. Therefore:

- family-level disposition is based on authoritative roadmap/skeleton/current requirements;
- exact path existence is **not** claimed here;
- the included repo-audit helper must be run after integration;
- path-based classifier is triage, not semantic truth;
- no clinical/site validation is created by this day.

---

## 27. Open Questions Carried Forward

DAY07 may carry:

- exact current paths for legacy families until repo scan;
- whether any model-governance schema is truly model-agnostic enough for `REUSE_AS_IS`;
- whether undocumented legacy assets exist outside skeleton/history;
- whether current Git history contains stale active links to old schedule;
- whether some Task C math can be reused unchanged after analytical review.

These questions must not be silently converted to positive claims.

---

## 28. Integration Into Main Repository

### A. Locate project root

```bash
cd /path/to/semg-fatigue-platform
export PROJECT_ROOT="$PWD"
```

### B. Inspect working tree

```bash
git status --short
git branch --show-current
```

Do not integrate into an unknown dirty state without understanding existing changes.

### C. Verify required existing folders

```bash
for d in docs qa-validation scripts data-platform packages; do
  test -d "$d" || echo "MISSING: $d"
done
```

### D. Create dedicated branch

```bash
git switch -c day07/legacy-asset-audit
```

If branch already exists, inspect it; do not blindly recreate/overwrite.

### E. Review collisions

From handoff pack root:

```bash
PACK_ROOT=/path/to/DAY07_LEGACY_ASSET_AUDIT_DISPOSITION_HANDOFF
cd "$PROJECT_ROOT"
while IFS= read -r rel; do
  if [ -e "$PROJECT_ROOT/$rel" ]; then
    echo "COLLISION $rel"
  fi
done < <(
  cd "$PACK_ROOT/repo_patch"
  find . -type f -print | sed 's#^./##' | sort
)
```

### F. Dry-run copy

```bash
rsync -avnc --ignore-existing "$PACK_ROOT/repo_patch/" "$PROJECT_ROOT/"
```

Review output. `--ignore-existing` prevents silent overwrite.

### G. Controlled actual copy

```bash
rsync -av --ignore-existing "$PACK_ROOT/repo_patch/" "$PROJECT_ROOT/"
```

For collisions, manually diff and merge:

```bash
diff -u existing/file "$PACK_ROOT/repo_patch/existing/file" || true
```

### H. Run DAY07 current-repo scan

```bash
cd "$PROJECT_ROOT"
python3 scripts/dev/day07_asset_audit.py \
  --root . \
  --output qa-validation/evidence/day07-repo-scan.json
```

### I. Run day-specific checks

```bash
bash scripts/dev/run_day07_checks.sh
```

### J. Run relevant previous-day regression

If DAY06 runner exists:

```bash
if [ -x scripts/dev/run_day06_checks.sh ]; then
  bash scripts/dev/run_day06_checks.sh
fi
```

If DAY06 checks require their historical package context and no longer run directly, execute the project's agreed Phase-0 regression command instead. Do not invent a passing result.

### K. Inspect diff

```bash
git diff --check
git diff --stat
git diff
```

Pay special attention to existing governance files; DAY07 should not overwrite DAY06 evidence policies.

---

## 29. Git Workflow

Suggested commit sequence:

```bash
git add docs/00-executive/rebaseline \
        docs/00-executive/decisions \
        docs/00-executive/day07 \
        docs/03-architecture/traceability \
        data-platform/catalog/legacy-asset-inventory.v1.0.yaml \
        qa-validation \
        packages/common-schemas/json \
        scripts/dev

git status --short

git commit -m "day07: audit and disposition legacy MotionLab assets"
```

Do not commit raw data or generated cache.

---

## 30. Rollback Procedure

Before commit:

```bash
git status --short
```

For a newly added DAY07 file confirmed safe to remove:

```bash
rm path/to/new-day07-file
```

For an accidentally modified existing file:

```bash
git restore -- path/to/file
```

After a commit already shared or otherwise needing auditable rollback:

```bash
git revert <commit_sha>
```

Do **not** use `git reset --hard` as the default rollback; it can destroy unrelated work.

---

## 31. Evidence & Provenance Capture

Record:

- source file hashes for authoritative inputs available to the handoff;
- artifact hashes in DAY07 manifest;
- exact audit command used;
- whether scan used `git ls-files` or `os.walk` fallback;
- actual unclassified count;
- reviewer and decision record in your normal project process;
- final status and limitation.

SHA-256 helper should use Python 3.11+ `hashlib.file_digest()` where practical.

---

## 32. Closeout Checklist

```text
[ ] roadmap DAY07 scope unchanged
[ ] no production feature implemented
[ ] 20 asset families reviewed at family level
[ ] actual repo scan run after integration
[ ] unclassified high-risk paths reviewed
[ ] three mandatory outputs exist
[ ] Product Principles traceability present
[ ] NFR-001 traceability present
[ ] NFR-011 traceability present
[ ] no public-data site claim
[ ] no MFCV site claim
[ ] no binary fatigue product revival
[ ] no old schedule authority revival
[ ] automated tests pass
[ ] manual review done or explicit limitation remains
[ ] status is one allowed DAY07 status
```

---

## 33. DAY 08 Handoff

DAY08 receives:

```text
legacy-asset-disposition.v1.0.md
legacy-regression-scope.v1.0.yaml
technical-debt-register.v1.0.md
legacy-asset-inventory.v1.0.yaml
day07-repo-scan.json
DAY07 decision/review evidence
```

DAY08 uses these to freeze requirements without accidentally inheriting stale code semantics.

DAY07 does **not** create `requirements v0.2`; that is DAY08 work.

---

## 34. Final Day Status Rules

### `GO_FOR_DAY_08`
Use only when:

- automated acceptance passes;
- current-repo audit has been run;
- all critical/high-risk unclassified assets are dispositioned or explicitly blocked;
- required review is complete;
- no unresolved source conflict undermines the freeze.

### `READY_WITH_LIMITATIONS`
Use when:

- engineering artifacts are complete and consistent;
- but actual repo path confirmation or non-critical human review remains pending;
- limitation does not silently authorize unsafe reuse.

### `BLOCKED_WITH_EVIDENCE`
Use when:

- governance/evidence status is insufficient for the intended reuse;
- critical public-to-site evidence promotion is unresolved;
- source-of-truth conflict is unresolved;
- high-risk legacy asset cannot be safely classified.

### Handoff package default status

Because this generated handoff cannot inspect your current post-DAY06 monorepo filesystem, its honest pre-integration status is:

```text
READY_WITH_LIMITATIONS
REPO_CONFIRMATION_REQUIRED
```

After integration and successful current-repo audit + human review, the operator may promote to `GO_FOR_DAY_08` according to the rules above.
