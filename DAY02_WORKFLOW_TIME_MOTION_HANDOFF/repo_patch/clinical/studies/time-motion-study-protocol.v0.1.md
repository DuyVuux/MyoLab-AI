# MotionLab Time-Motion Study Protocol v0.1

**Artifact:** `clinical/studies/time-motion-study-protocol.v0.1.md`  
**Day:** DAY02  
**Protocol status:** `DESIGNED_FOR_ROUND1_OBSERVATION`  
**Baseline status:** `NOT_MEASURED`  
**Clinical claim status:** none  
**Training/model activity:** prohibited/not applicable for DAY02

## 1. Purpose

Design a reproducible, low-burden observation method for measuring the current MotionLab workflow before attempting automation. The protocol exists to make DAY03 evidence interpretable and to support later paired manual-vs-copilot evaluation without turning the current team estimate (`>=60 min/case`) into a fabricated baseline.

## 2. Source requirements

Primary traceability targets:

- PRD `JTBD-01..05`;
- PRD KPI framework (`PRD-KPI-01..07` in the DAY01 registry);
- SRS `AC-10` — pilot must demonstrate reduction versus a **measured** baseline and the official target must be fixed before pilot.

Supporting open questions:

- `OQ-001` volume/case mix;
- `OQ-002` manual processing time by step/case;
- `OQ-003` remeasurement rate/reasons;
- `OQ-004` current filter/normalization/window/protocol;
- `OQ-005` final sEMG output/decision context;
- `OQ-007` privacy/de-identification pathway.

None of these questions are silently closed by this design artifact.

## 3. Study questions

### Q1 — Workflow structure
What activities actually occur from preparation/acquisition through data handling, remeasurement and interpretation?

### Q2 — Human toil
How much **active hands-on time** is spent by doctor and KTV on each workflow category?

### Q3 — Waiting/system time
How much time is machine-active or blocked/waiting, and how often does it overlap human work?

### Q4 — Rework/remeasurement
When does rework or remeasurement occur, how much burden does it add, and what reason is reported by the operator?

### Q5 — Decision context
What output/evidence does the clinician actually use before professional interpretation or approval?

## 4. Design type

`Prospective non-interventional workflow observation` is the preferred mode for DAY03 when permitted. A retrospective workflow reconstruction or interview may be used as a lower evidence tier when direct observation is unavailable, but it must not be reported as the same evidence class.

The observer does not change device setup, processing choices, thresholds, signal handling, clinical decisions or remeasurement decisions.

## 5. Unit of observation

Primary unit: one workflow case/session from a defined start boundary to a defined end boundary.

The case ID in this instrument is an **analysis ID only** and must not contain direct identifiers.

### Recommended boundary for Round 1

- Start: first workflow action included in the observation scope (record exact boundary).
- End: completion/handoff of the observed workflow scope (record exact boundary).

If a full end-to-end case cannot be observed, record `partial_case=true` in a derived Day03 dataset and state the observed boundary. Do not normalize it to a full case by assumption.

## 6. No invented sample size

DAY02 does not define `n=20`, `n=30`, or any other statistically powered sample size because case volume/distribution is `OQ-001 = UNKNOWN` and the first goal is discovery/baseline characterization. DAY03 Round 1 should capture available approved cases and explicitly report sampling limitations.

A representative/powered cohort, if needed for pilot claims, is a later design decision after volume, variability and governance are known.

## 7. Observation modes and evidence tiers

| Mode | Allowed DAY03 use | Evidence interpretation |
|---|---|---|
| `DIRECT_OBSERVATION` | Preferred under approved site conditions | Can support `SITE_VERIFIED` workflow facts if complete and traceable. |
| `RETROSPECTIVE_WORKFLOW_RECONSTRUCTION` | When timestamped operational evidence exists | Site evidence with reconstruction limitations. |
| `INTERVIEW_ONLY` | Discovery fallback | Captures reported workflow; not a measured time-motion baseline. |
| `SYNTHETIC_QA` | Test the form/scripts only | Never clinical/site evidence; never baseline eligible. |

## 8. Data minimization boundary

Until the dedicated DAY05 privacy gate is closed, this protocol is intentionally designed to avoid needing raw patient data.

Do not record in this form:

- patient name;
- MRN/hospital identifier;
- email/phone/address;
- date of birth;
- screenshots containing identifiers;
- raw sEMG/pressure/Vicon signal;
- clinical note text not required for workflow timing.

Record roles and workflow events only. If direct observation itself requires local approval, that approval is a prerequisite. If it is unavailable, mark `BLOCKED_WITH_EVIDENCE` for measured baseline rather than bypassing governance.

## 9. Timing method

Use timestamped event intervals.

Each event has:

- `start_timestamp`;
- `end_timestamp`;
- actor role;
- activity code;
- time class;
- candidate workflow step;
- rework/remeasurement flags;
- optional parallel group;
- measurement fact;
- operator-reported reason;
- observer note;
- evidence status.

### Clock resolution

Use the highest practical resolution of the observation tool (seconds are sufficient for Round 1 unless actual workflow shows sub-second activities matter). Do not fabricate precision beyond the recording method.

## 10. Event segmentation rule

Create a new event when any of the following changes:

- actor;
- activity code;
- time class;
- workflow step;
- remeasurement episode;
- the observed action materially changes.

If a doctor transitions from data inspection to clinical interpretation, split the event. This is essential because interpretation must not be silently counted as data-processing toil.

## 11. Time classes

### 11.1 `CLINICIAN_DATA_HANDS_ON`
Doctor actively performs post-acquisition data handling: inspect, manipulate, correct, select, process, review processing evidence, or similar operational data actions.

### 11.2 `TECHNICIAN_DATA_HANDS_ON`
KTV actively performs export/retrieval/data handling/operational support.

### 11.3 `ACQUISITION_HANDS_ON`
Human setup/acquisition work. Kept separately from post-acquisition data-processing KPI.

### 11.4 `SYSTEM_ACTIVE`
Software/device actively computes, exports or loads without continuous human work.

### 11.5 `WAITING_BLOCKED`
Workflow cannot progress due to system/person/dependency wait.

### 11.6 `REMEASUREMENT`
Time specifically associated with a repeat measurement episode. If the same interval is also acquisition hands-on, store the remeasurement episode flag and preserve the underlying actor/activity; downstream analysis can produce both views without double-counting elapsed time.

### 11.7 `CLINICAL_INTERPRETATION`
Professional interpretation/decision activity, separate from the data-processing endpoint.

### 11.8 `OTHER` / `UNKNOWN`
Use explicitly rather than guessing.

## 12. Activity codes

`PREPARE_OR_SETUP`, `ACQUIRE`, `EXPORT_OR_RETRIEVE`, `INSPECT_DATA`, `IDENTIFY_DATA_ISSUE`, `MANUAL_CLEAN_OR_CORRECT`, `NORMALIZE_OR_REFERENCE`, `PROCESS_OR_COMPUTE`, `REMEASURE_DECISION`, `REMEASURE`, `INTERPRET`, `DOCUMENT_OR_HANDOFF`, `WAIT`, `SYSTEM_PROCESS`, `OTHER`, `UNKNOWN`.

These are **observation codes**, not a site-validated SOP and not a QC taxonomy.

## 13. Measurement facts vs inference vs interpretation

### Measurement fact
“Doctor inspected the displayed data from 10:03:30 to 10:06:20.”

### Operator report
“Doctor stated that this part needed re-checking.”

### Observer inference
“Likely due to motion artifact.” — **do not record as fact unless independently evidenced.**

### Clinical interpretation
“This pattern indicates pathology.” — outside the observer’s task unless quoted as a clinician-reported decision context; never relabel it as ground truth in DAY02/03 by default.

The form therefore keeps `observed_action`, `reason_reported_by_operator`, and `observer_note` separate.

## 14. Concurrent work and interval-union rule

Suppose software exports from 08:02:00–08:02:45 while the doctor reviews another record from 08:02:10–08:03:30.

Incorrect:

`case time = 45 s + 80 s = 125 s`

Correct concept:

- elapsed time is determined by the case timeline boundaries;
- human hands-on is measured from the doctor interval;
- system-active is measured from the software interval;
- overlapping intervals remain overlapping and are not transformed into extra elapsed time.

For a set of intervals `I`, class time is the duration of the **union** of intervals for that class, not the naive sum if intervals overlap.

No final baseline calculation is performed in DAY02; the storage contract merely makes correct calculation possible later.

## 15. Primary and supporting endpoints

### Primary designed endpoint

`doctor_data_hands_on_union_sec_per_case`

Definition: union duration of doctor post-acquisition events coded `CLINICIAN_DATA_HANDS_ON` within the declared observation boundary.

Status in DAY02: `DESIGNED`, value `NOT_MEASURED`.

### Supporting endpoints

- `technician_data_hands_on_union_sec_per_case`;
- `acquisition_hands_on_union_sec_per_case`;
- `system_active_union_sec_per_case`;
- `waiting_blocked_union_sec_per_case`;
- `remeasurement_union_sec_per_case`;
- `clinical_interpretation_union_sec_per_case`;
- `elapsed_time_sec_per_case`;
- `remeasurement_occurred`;
- `remeasurement_episode_count`;
- `full_manual_review_required` (operational definition to be confirmed in observed workflow).

## 16. KPI mapping

| PRD KPI | DAY02 contribution | Measured on DAY02? |
|---|---|---|
| Manual processing time / case | Primary timing definition designed | No |
| Full-manual-review rate | Case-level capture field/operational question designed | No |
| Re-measurement rate | Remeasurement event/episode capture designed | No |
| QC critical-artifact recall | Capture current operator-identified issues/actions as future reference; no QC system exists here | No |
| Doctor acceptance rate | Future-state KPI; preserved in traceability only | No |
| Abstention appropriateness | Future-state KPI; preserved in traceability only | No |
| Traceability completeness | DAY02 artifacts themselves are versioned/traceable; product KPI not measured | No |

## 17. Remeasurement coding

When remeasurement occurs:

1. record the decision/request event;
2. assign `remeasurement_episode_id`;
3. record the repeat setup/acquisition intervals;
4. capture `reason_reported_by_operator` verbatim/briefly without converting it to an unvalidated taxonomy;
5. keep the rate `UNKNOWN` until observed numerator and denominator exist.

## 18. Interruptions and multi-tasking

If the actor is interrupted:

- end the active event;
- create `WAITING_BLOCKED`, `OTHER`, or an event for the alternate task if within scope;
- resume with a new event when the original task restarts.

Do not count an unattended software wait as doctor hands-on.

## 19. Missing data

Use explicit `UNKNOWN`, `TBD`, `NOT_VERIFIED`, or `DISCOVERY_REQUIRED` states. Do not backfill from memory unless the mode is explicitly `RETROSPECTIVE_WORKFLOW_RECONSTRUCTION`, and even then record the evidence limitation.

A missing timestamp makes that event non-eligible for quantitative duration analysis; it can remain qualitative evidence.

## 20. Observer conduct

- Be non-interventional.
- Do not coach the operator to use a different workflow.
- Do not ask questions during critical clinical work if that would alter timing; collect clarifications after the event when practical.
- Do not suggest “cleaning” or QC decisions.
- Do not change software settings.
- Do not label pathology/noise.
- Record only role-level identities.

## 21. Bias controls

### Hawthorne effect
People may behave differently when observed. Record that observation occurred and avoid claiming Round 1 represents all cases.

### Sampling bias
Available cases may overrepresent easy/hard workflows. Record protocol/workflow variant without direct patient identity and report limitations.

### Observer drift
Use the same code dictionary; if two observers disagree, log disagreement rather than silently harmonize.

### Recall bias
Interview-only timing is not equivalent to timestamped observation.

## 22. Quality checks for completed forms

A completed quantitative observation is duration-eligible only if:

- observation boundary is declared;
- event IDs are unique;
- start/end timestamps are parseable;
- end >= start;
- actor/time class/activity are from the dictionary or explicit `UNKNOWN`;
- direct PHI is absent from the form;
- remeasurement episodes are identifiable if present;
- evidence status is valid;
- observation mode is not `SYNTHETIC_QA` or `INTERVIEW_ONLY` for measured baseline.

## 23. Baseline rule

The following statement is allowed:

> “The PRD records a team estimate of >=60 min/case; this is not a measured baseline.”

The following statement is prohibited before measurement:

> “MotionLab baseline = 60 minutes/case.”

Similarly, `>=50% reduction` remains a research target to be fixed after baseline, not a committed site-validated threshold.

## 24. Day03 execution handoff

DAY03 should produce:

- `clinical/studies/time-motion-baseline-round1.csv`;
- `clinical/workflows/current-workflow-evidence-log.md`;
- `docs/02-clinical/discovery/open-questions-burndown.md`.

A DAY03 `GO_FOR_DAY_04` requires evidence collection under valid conditions. If only interview/synthetic data is available, report the limitation and do not fabricate a measured operational baseline.

## 25. Stop/block rules

Return `BLOCKED_WITH_EVIDENCE` for baseline collection when:

- doctor/KTV hands-on cannot be distinguished;
- waiting/system/remeasurement cannot be distinguished enough to interpret the endpoint;
- required local governance for observation is absent;
- timestamps are unusable for the claimed quantitative result;
- a material requirement/source conflict appears and has no decision record.

`READY_WITH_LIMITATIONS` is acceptable only when limitations do not invalidate the next safe discovery step.

## 26. DAY02 acceptance

DAY02 is complete when:

- workflow map exists and is explicitly candidate/not site-verified;
- protocol exists;
- machine-readable observation form exists;
- traceability covers `JTBD-01..05`, all PRD KPIs and `AC-10`;
- OQ statuses are not silently closed;
- synthetic dry-run proves concurrency and remeasurement can be represented;
- automated controls pass;
- no raw patient data or model training artifact exists.
