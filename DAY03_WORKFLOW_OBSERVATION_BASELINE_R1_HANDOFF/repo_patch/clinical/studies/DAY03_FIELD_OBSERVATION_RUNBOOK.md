# DAY03 Field Observation Runbook

## Purpose

This runbook tells the observer how to create evidence that can populate `time-motion-baseline-round1.csv` without changing the MotionLab workflow.

## STEP 0 — Governance preflight

**Input:** local approval / observation permission.  
**Output:** governance reference or `BLOCKED_WITH_EVIDENCE`.

Do not observe/record data outside the approved boundary. This DAY03 pack does not authorize raw patient-data access.

## STEP 1 — Create one observation copy

**Input:** DAY02 `time-motion-observation-form.v0.1.yaml`.  
**Output:** one de-identified observation YAML stored in an approved local working area.

Use an analysis-only identifier. Do not enter patient name, MRN, DOB, contact data, raw signals, screenshots or unnecessary clinical-note text.

## STEP 2 — Declare the observation boundary

**Input:** current case/workflow.  
**Output:** explicit start/end boundary and `partial_case` state.

Never extrapolate an observed partial segment into a full case.

## STEP 3 — Record event intervals

**Input:** direct observation.  
**Output:** timestamped events with actor, activity code, time class and evidence status.

Split events when actor/activity/time-class changes. Preserve concurrency.

## STEP 4 — Record rework / remeasurement

**Input:** observed decision/episode.  
**Output:** remeasurement flag, episode ID and operator-reported reason.

Do not infer a QC category; DAY04 owns artifact-vs-physiology taxonomy.

## STEP 5 — Review the observation

**Input:** completed observation YAML.  
**Output:** accepted/excluded decision for Round-1 baseline.

A record cannot be baseline eligible if it is interview-only, synthetic, lacks required boundary evidence, contains prohibited PHI/raw data, or is not reviewed.

## STEP 6 — Add the aggregate row

**Input:** reviewed observation.  
**Output:** one row in `clinical/studies/time-motion-baseline-round1.csv`.

Use interval-union durations, not naive addition of overlapping intervals.

## STEP 7 — Run DAY03 gate

```bash
bash scripts/dev/run_day03_checks.sh
```

**Output:** `qa-validation/evidence/day03-validation-report.json`.

`GO_FOR_DAY_04` requires at least one reviewed baseline-eligible site/approved retrospective case. The first Round-1 observations are descriptive discovery evidence; they do not by themselves establish representativeness or a powered pilot baseline.

## Optional safe helper — prepare a candidate row

After a de-identified observation YAML has been reviewed for basic completeness, you may generate a **candidate** CSV row:

```bash
python3 scripts/dev/prepare_day03_candidate_row.py \
  /approved/local/path/observation.yaml \
  --row-id D03-R1-001 \
  --partial-case false \
  --start-boundary "post-acquisition data handling begins" \
  --end-boundary "data handling handed off for interpretation" \
  --output /tmp/day03-candidate-row.csv
```

The helper deliberately outputs `baseline_eligible=false` and `reviewer_status=PENDING_REVIEW`. It never auto-approves evidence.
