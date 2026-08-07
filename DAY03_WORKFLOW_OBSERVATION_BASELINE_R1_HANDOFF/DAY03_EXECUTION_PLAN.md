# DAY03 Execution Plan — Workflow Observation & Baseline Capture, Round 1

## 0. Mission

Build a traceable Round-1 operational baseline from **approved real MotionLab observation or approved retrospective operational evidence** without changing workflow and without converting estimates into facts.

Current packaged evidence status: `NO_SITE_OBSERVATION_SUPPLIED_TO_BUILDER`.

Therefore this handoff is **field-ready but evidence-blocked** until real/retrospective evidence is added.

## 1. Inputs

- accepted DAY02 workflow map;
- DAY02 time-motion protocol;
- DAY02 observation form;
- PRD §10 KPI framework;
- PRD §14 open questions;
- SRS AC-10.

## 2. Outputs

Mandatory roadmap outputs:

- `clinical/studies/time-motion-baseline-round1.csv`;
- `clinical/workflows/current-workflow-evidence-log.md`;
- `docs/02-clinical/discovery/open-questions-burndown.md`.

Supporting outputs include schema, runbook, traceability, tests, evidence ledger and single-command gate.

## 3. Execution steps

### STEP 0 — DAY02 preflight
**Input:** DAY02 validation report.  
**Action:** confirm `GO_FOR_DAY_03`, baseline not yet measured, no silent OQ closure.  
**Output:** accepted handoff.  
**Stop:** DAY02 invalid → stop.

### STEP 1 — Governance permission check
**Input:** local/site observation permission.  
**Action:** record governance reference; do not bypass privacy controls.  
**Output:** observation allowed or `BLOCKED_WITH_EVIDENCE`.  
**Stop:** no valid path for the evidence type → do not collect it.

### STEP 2 — Select observation mode
**Input:** available evidence.  
**Action:** choose `DIRECT_OBSERVATION`, `RETROSPECTIVE_WORKFLOW_RECONSTRUCTION`, `INTERVIEW_ONLY`, or `SYNTHETIC_QA`.  
**Output:** explicit evidence class.  
**Stop:** interview/synthetic cannot become measured baseline.

### STEP 3 — Declare case boundary
**Input:** observed workflow scope.  
**Action:** record exact start/end; mark partial case if needed.  
**Output:** bounded observation.  
**Stop:** never extrapolate partial case to full case.

### STEP 4 — Capture event intervals
**Input:** workflow observation.  
**Action:** record actor/activity/time class and timestamps; preserve concurrency.  
**Output:** event ledger.  
**Validation:** doctor, KTV, system, waiting, remeasurement and interpretation remain distinct.

### STEP 5 — Capture rework/remeasurement evidence
**Input:** observed remeasurement decision/episode.  
**Action:** record episode/count and operator-reported reason.  
**Output:** provenance-bearing remeasurement evidence.  
**Stop:** do not map reason to QC/pathology taxonomy in DAY03.

### STEP 6 — Peer review observation
**Input:** completed observation.  
**Action:** check privacy, completeness, evidence tier, boundary, concurrency and notes.  
**Output:** accepted/excluded baseline decision.

### STEP 7 — Populate Round-1 baseline CSV
**Input:** reviewed observations.  
**Action:** add one aggregate row per observation using interval-union durations.  
**Output:** Round-1 dataset.  
**Stop:** no invented duration or denominator.

### STEP 8 — Update workflow evidence log
**Input:** site evidence.  
**Action:** upgrade only facts directly supported by evidence.  
**Output:** versioned evidence log.

### STEP 9 — Burn down open questions
**Input:** Round-1 evidence.  
**Action:** update OQ progress; do not close without closure criterion.  
**Output:** burndown document.

### STEP 10 — Traceability
**Input:** PRD §10, §14, SRS AC-10.  
**Action:** map evidence artifact and validation.  
**Output:** traceability CSV.

### STEP 11 — Automated gate
**Input:** repo patch.  
**Command:** `bash scripts/dev/run_day03_checks.sh`.  
**Output:** validation report + pytest result.  
**Stop:** semantic failure → fix before review.

### STEP 12 — DAY03 close
**Input:** validation report + evidence review.  
**Output:** one of:

- `GO_FOR_DAY_04` — reviewed baseline-eligible Round-1 evidence exists;
- `READY_WITH_LIMITATIONS` — evidence exists but limitations do not invalidate the next activity;
- `BLOCKED_WITH_EVIDENCE` — evidence dependency is missing/invalid.

## 4. Current packaged result

The code/contracts/tests are complete, but no site observation was supplied. The truthful packaged state is:

`BLOCKED_WITH_EVIDENCE / READY_FOR_FIELD_OBSERVATION`.

## 5. Integration

Copy `repo_patch/` into the already-integrated project root using collision review; do not blindly overwrite existing DAY01/DAY02 assets.

Suggested branch:

`day03/workflow-observation-baseline-r1`

Suggested commit after site evidence is added and reviewed:

`day03: capture round1 MotionLab workflow baseline evidence`

## 6. Rollback

Prefer selective `git restore` / removal of confirmed DAY03-added files. Do not default to `git reset --hard` on a shared repository.
