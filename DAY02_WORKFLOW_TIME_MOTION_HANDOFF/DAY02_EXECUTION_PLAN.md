# DAY02 Execution Plan — Real MotionLab Workflow Mapping & Time-Motion Study Design

## 0. Document Control

| Field | Value |
|---|---|
| Day | DAY02 |
| Phase | Phase 0 — Re-baseline & Clinical Discovery |
| Input gate | Accepted DAY01 handoff (`GO_FOR_DAY_02`) |
| Output gate | `GO_FOR_DAY_03` / `READY_WITH_LIMITATIONS` / `BLOCKED_WITH_EVIDENCE` |
| Production code | Not required by roadmap |
| QA code | Required in this handoff for reproducibility |
| Patient/raw data | Not included |
| Training/model fitting | Not allowed/not needed |

## 1. Objective

Build a **reviewable current-state candidate workflow** and a **reproducible time-motion measurement contract** that DAY03 can use without treating estimates as facts.

### Input

- accepted DAY01 governance baseline;
- PRD `JTBD-01..05`, KPI framework;
- SRS `AC-10`;
- frozen evidence taxonomy;
- OQ-001..005/OQ-007 relevant discovery gaps;
- re-baselined roadmap DAY02 definition.

### Output

Mandatory roadmap outputs:

```text
clinical/workflows/motionlab-current-state.v0.1.md
clinical/studies/time-motion-study-protocol.v0.1.md
clinical/studies/time-motion-observation-form.v0.1.yaml
```

Supporting QA/traceability outputs are included in the pack.

## 2. Non-goals

DAY02 does **not**:

- collect a measured baseline;
- observe/inspect raw patient sEMG;
- define an artifact taxonomy;
- choose signal-processing filters;
- implement QC detectors;
- calculate RMS/MAV/MDF/MNF/MFCV;
- train/tune/evaluate a model;
- solve plantar pressure or Knee/ACL;
- close site privacy governance;
- claim `>=60 min/case` as baseline;
- claim `>=50%` as a committed target.

## 3. Artifact tree

```text
DAY02_WORKFLOW_TIME_MOTION_HANDOFF/
├── README.md
├── DAY02_EXECUTION_PLAN.md
├── DAY02_FEYNMAN_LEARNING_GUIDE.md
├── INTEGRATION_MANIFEST.json
├── SHA256SUMS
└── repo_patch/
    ├── clinical/
    │   ├── workflows/motionlab-current-state.v0.1.md
    │   └── studies/
    │       ├── time-motion-study-protocol.v0.1.md
    │       └── time-motion-observation-form.v0.1.yaml
    ├── docs/
    │   ├── 00-executive/day02/day02-closeout-summary.v0.1.md
    │   ├── 00-executive/decisions/day02-decision-impact-review.v0.1.yaml
    │   ├── 01-product/motionlab-rebaseline/day02-open-question-status-update.v0.1.yaml
    │   └── 03-architecture/traceability/day02-workflow-time-motion-traceability.v0.1.csv
    ├── packages/common-schemas/json/time-motion-observation.schema.json
    ├── qa-validation/
    │   ├── automated-tests/governance/test_day02_workflow_time_motion.py
    │   ├── evidence/
    │   ├── requirements/day02-acceptance-criteria.md
    │   ├── test-data/day02/synthetic-time-motion-observation.v0.1.yaml
    │   └── traceability/day02-requirement-test-matrix.csv
    └── scripts/dev/
        ├── validate_day02_workflow_time_motion.py
        ├── check_day02_artifacts.py
        └── run_day02_checks.sh
```

---

# 4. STEP 0 — Preflight DAY01 handoff

### Input
DAY01 handoff pack / integrated DAY01 repo state.

### Why
DAY02 may not invent a new product baseline. It depends on the source hierarchy, evidence taxonomy, requirement registry and open questions frozen on DAY01.

### Action
Confirm DAY01 result says `GO_FOR_DAY_02` and key open questions remain unresolved.

### Command

```bash
unzip -p DAY01_REQUIREMENTS_REBASELINE_HANDOFF.zip \
  DAY01_REQUIREMENTS_REBASELINE_HANDOFF/repo_patch/qa-validation/evidence/day01-validation-report.json
```

### Expected output

- `status = GO_FOR_DAY_02`
- `training_executed = false`
- `raw_patient_data_read = false`

### Validation
Do not continue from an unaccepted/modified DAY01 baseline without review.

### Stop condition
DAY01 gate fails or source hierarchy is missing → `BLOCKED_WITH_EVIDENCE`.

---

# 5. STEP 1 — Lock DAY02 scope

### Input
Roadmap DAY02 section.

### Why
The most common failure is to “improve” workflow while trying to measure it, or to start signal processing too early.

### Action
Write down the one-day question:

> How will we observe and measure current workflow accurately enough to build a baseline later?

### Output
Explicit non-goals and acceptance criteria.

### Validation
No parser/DSP/QC/model feature is required for DAY02.

### Stop condition
If a proposed task cannot improve workflow measurement/traceability, defer it.

---

# 6. STEP 2 — Build evidence-aware candidate workflow

### Input
PRD problem framing + roadmap phrase `thu đo → inspect → clean → normalize → process → remeasure → interpret`.

### Why
We need a coding scaffold, but we must not call it site truth.

### Action
Use `motionlab-current-state.v0.1.md` and keep every site-specific node `DISCOVERY_REQUIRED` until observed.

### Output
Candidate workflow with actor/input/output/rework fields.

### Validation
The file must contain `CANDIDATE_CURRENT_STATE_TO_VERIFY` and `NOT SITE-VERIFIED`.

### Stop condition
Any node is presented as a verified site SOP without evidence → fail review.

---

# 7. STEP 3 — Separate actors

### Input
Candidate workflow.

### Why
If doctor and KTV time are merged, later optimization can appear successful while simply transferring burden.

### Action
Code actor as `DOCTOR`, `KTV`, `SOFTWARE`, `DEVICE`, `OTHER`, `UNKNOWN`.

### Output
Actor-resolved events.

### Validation
Doctor/KTV hands-on classes must be distinct.

### Stop condition
Observer cannot distinguish actor role for a quantitative event → mark `UNKNOWN`; do not guess.

---

# 8. STEP 4 — Define time classes

### Input
PRD manual-time KPI and operational North Star.

### Why
Elapsed time, hands-on time, waiting and machine time answer different questions.

### Action
Use the frozen DAY02 classes:

- `CLINICIAN_DATA_HANDS_ON`
- `TECHNICIAN_DATA_HANDS_ON`
- `ACQUISITION_HANDS_ON`
- `SYSTEM_ACTIVE`
- `WAITING_BLOCKED`
- `REMEASUREMENT`
- `CLINICAL_INTERPRETATION`
- `OTHER` / `UNKNOWN`

### Output
Operational definitions in protocol and form.

### Validation
Interpretation is not silently counted as post-acquisition processing.

### Stop condition
If hands-on/waiting/remeasurement cannot be distinguished, roadmap says baseline is not usable.

---

# 9. STEP 5 — Design interval/event capture

### Input
Time classes + actor model.

### Why
Parallel work makes a scalar “duration” field unsafe.

### Action
Record start/end intervals for every event. Use `parallel_group_id` only as a convenience; timestamps remain source of truth.

### Output
Machine-readable event contract.

### Validation
Synthetic fixture must contain overlapping software/doctor intervals.

### Stop condition
If the instrument only stores summed minutes and loses timeline overlap, redesign before DAY03.

---

# 10. STEP 6 — Design remeasurement representation

### Input
OQ-003 + PRD qualitative statement that remeasurement occurs.

### Why
Remeasurement is a separate operational burden and potential QC benefit; hiding it inside acquisition destroys the metric.

### Action
Capture:

- remeasure decision/request;
- `remeasurement_episode_id`;
- remeasurement intervals;
- operator-reported reason;
- observer note separately.

### Output
Remeasurement-capable observation contract.

### Validation
Synthetic fixture exercises `RM-001`.

### Stop condition
No distinct remeasurement episode is representable → block.

---

# 11. STEP 7 — Protect measurement fact from inference

### Input
Evidence taxonomy.

### Why
A workflow observer is not a signal-quality ground-truth annotator.

### Action
Keep these fields distinct:

```text
observed_action
reason_reported_by_operator
observer_note
```

### Output
No hidden clinical/QC relabeling.

### Validation
DAY02 must not create “motion artifact”, “pathology”, or other machine labels from free text.

### Stop condition
If an inference is needed, mark `INFERRED`; never rewrite it as observation fact.

---

# 12. STEP 8 — Apply conservative privacy boundary

### Input
OQ-007 = `DISCOVERY_REQUIRED`.

### Why
DAY05 owns the formal privacy/de-identification gate. DAY02/03 measurement design should not require raw patient data.

### Action
Observation template prohibits:

- direct identifiers;
- raw signal;
- screenshots;
- free-text clinical details not required for timing.

### Output
No-direct-PHI workflow instrument.

### Validation
Automated test #3.

### Stop condition
If actual observation requires unavailable governance approval → measured baseline is blocked, not bypassed.

---

# 13. STEP 9 — Map requirements and open questions

### Input
DAY01 requirement registry + OQ register.

### Action
Review:

```text
JTBD-01..05
PRD-KPI-01..07
AC-10
OQ-001/002/003/004/005/007
```

### Output

- `day02-workflow-time-motion-traceability.v0.1.csv`
- `day02-open-question-status-update.v0.1.yaml`

### Validation
OQ-001/002/003/005 must remain `OPEN` and `UNKNOWN`.

### Stop condition
Any unknown is “closed” only because the form has a field for it → fail.

---

# 14. STEP 10 — Synthetic dry-run

### Input
Blank observation form.

### Why
We can test instrument structure without contaminating baseline evidence.

### Action
Use:

```text
qa-validation/test-data/day02/synthetic-time-motion-observation.v0.1.yaml
```

It includes overlapping software/doctor work and a remeasurement branch.

### Output
QA evidence only.

### Validation

```yaml
baseline_eligible: false
observation_mode: SYNTHETIC_QA
```

### Stop condition
Synthetic data ever appears in baseline output → fail closed.

---

# 15. STEP 11 — Run automated gate

### Input
All DAY02 artifacts.

### Command

```bash
cd DAY02_WORKFLOW_TIME_MOTION_HANDOFF/repo_patch
bash scripts/dev/run_day02_checks.sh
```

### Expected output

```text
20 passed
[DAY02] PASS — GO_FOR_DAY_03
```

### Output
`qa-validation/evidence/day02-validation-report.json`

### Stop condition
Any pytest/control failure → do not claim `GO_FOR_DAY_03`.

---

# 16. STEP 12 — Human peer review

### Input
Three mandatory artifacts + traceability.

### Action
Reviewer answers:

1. Does the workflow map look like a useful observation scaffold rather than a claimed SOP?
2. Can the form separate doctor, KTV, system, waiting and remeasurement?
3. Can concurrent work be represented?
4. Is the primary endpoint consistent with PRD wording?
5. Are interpretation and data processing separated?
6. Could the observer accidentally record PHI or invent a QC label?
7. Are all unresolved questions still explicit?

### Output
Review notes/approval in the team’s normal change-control process.

### Stop condition
Material ambiguity affecting baseline validity → `READY_WITH_LIMITATIONS` or `BLOCKED_WITH_EVIDENCE`.

---

# 17. Integration into the main repo

## Input
A clean/known git working tree containing DAY01 artifacts.

```bash
export PROJECT_ROOT=/path/to/semg-fatigue-platform
export PACK_ROOT=/path/to/DAY02_WORKFLOW_TIME_MOTION_HANDOFF

cd "$PROJECT_ROOT"
git status --short
git branch --show-current
```

Create branch:

```bash
git switch -c day02/workflow-time-motion
```

Dry-run copy without overwrite:

```bash
rsync -avnc --ignore-existing "$PACK_ROOT/repo_patch/" "$PROJECT_ROOT/"
```

Actual add-only copy:

```bash
rsync -av --ignore-existing "$PACK_ROOT/repo_patch/" "$PROJECT_ROOT/"
```

If a destination file already exists:

```text
STOP → compare → decide merge/reuse → document → rerun tests
```

Do not use blind overwrite.

Run:

```bash
bash scripts/dev/run_day02_checks.sh
git diff --check
git status --short
git diff --stat
git diff
```

Suggested commit:

```bash
git add clinical docs packages qa-validation scripts
git commit -m "day02: design MotionLab workflow time-motion observation"
```

---

# 18. Rollback

For uncommitted added files, remove only files confirmed to belong to this patch. For modified/merged files, use selective `git restore -- <path>` only after reviewing the diff.

For a committed change, prefer:

```bash
git revert <commit_sha>
```

Do **not** use `git reset --hard` as default rollback.

---

# 19. Why there is no notebook

DAY02 is contract/workflow measurement design. A notebook would add little value and risks becoming an informal source of truth. All machine-readable semantics live in YAML/JSON Schema and all acceptance checks are executable scripts/tests.

---

# 20. DAY03 handoff

### DAY03 input

- accepted candidate workflow;
- accepted time-motion protocol;
- observation form;
- open-question delta;
- traceability;
- validation report.

### DAY03 output target

```text
clinical/studies/time-motion-baseline-round1.csv
clinical/workflows/current-workflow-evidence-log.md
docs/02-clinical/discovery/open-questions-burndown.md
```

### DAY03 rule

DAY03 may replace `UNKNOWN` with observed evidence only when evidence exists. It may not replace missing observations with the team estimate.

---

# 21. Definition of Done

DAY02 is done only when:

- 3/3 mandatory roadmap outputs exist;
- 20/20 automated controls pass;
- baseline measured = false;
- synthetic fixture baseline eligible = false;
- key OQs closed = 0;
- no direct PHI/raw patient data/model artifact exists;
- status = `GO_FOR_DAY_03` means measurement design ready, nothing more.
