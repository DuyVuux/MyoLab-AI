# Current Workflow Evidence Log — DAY03 Round 1

**Artifact:** `clinical/workflows/current-workflow-evidence-log.md`  
**Day:** DAY03  
**Scope:** current-state MotionLab workflow evidence only  
**Current site-evidence state in this handoff:** `NO_SITE_OBSERVATION_SUPPLIED_TO_BUILDER`  
**Baseline claim:** none

## 1. Purpose

This log converts the DAY02 candidate workflow into an evidence ledger. It must distinguish:

1. measurement fact;
2. operator-reported explanation;
3. observer inference;
4. clinical interpretation.

DAY03 may strengthen a workflow node only when a traceable direct observation or approved retrospective reconstruction exists. Interview-only and synthetic data are not equivalent to measured site baseline evidence.

## 2. Evidence hierarchy used in Round 1

| Evidence class | May support measured baseline? | Notes |
|---|---:|---|
| `DIRECT_OBSERVATION` | Yes, if governance/review conditions are met | Preferred DAY03 evidence. |
| `RETROSPECTIVE_WORKFLOW_RECONSTRUCTION` | Conditional | Must have traceable operational evidence and declared reconstruction limits. |
| `INTERVIEW_ONLY` | No | Reported workflow only; not measured time-motion baseline. |
| `SYNTHETIC_QA` | No | Test tooling only. |

## 3. Candidate workflow evidence table

The DAY02 states remain **candidate states** until evidence is attached.

| Step | Candidate activity | Current evidence status | Round-1 evidence reference | Measurement fact | Operator report | Observer inference | Limitation / next action |
|---|---|---|---|---|---|---|---|
| CW-01 | Prepare / setup | `DISCOVERY_REQUIRED` | — | — | — | — | Observe without changing setup. |
| CW-02 | Acquire | `DISCOVERY_REQUIRED` | — | — | — | — | Capture timing/actor only; no raw signal in this pack. |
| CW-03 | Export / retrieve | `DISCOVERY_REQUIRED` | — | — | — | — | Observe data retrieval/export path. |
| CW-04 | Inspect data | `DISCOVERY_REQUIRED` | — | — | — | — | Separate doctor/KTV hands-on. |
| CW-05 | Identify data issue | `DISCOVERY_REQUIRED` | — | — | — | — | Do not convert operator wording into DAY04 QC taxonomy. |
| CW-06 | Manual clean / correct | `DISCOVERY_REQUIRED` | — | — | — | — | Record action and duration, not assumed rationale. |
| CW-07 | Normalize / reference | `DISCOVERY_REQUIRED` | — | — | — | — | Capture reported settings only; OQ-004 remains open. |
| CW-08 | Process / compute | `DISCOVERY_REQUIRED` | — | — | — | — | Separate system-active from human-active time. |
| CW-09 | Remeasure decision | `DISCOVERY_REQUIRED` | — | — | — | — | Record reason as operator report; no taxonomy inference. |
| CW-10 | Remeasure | `DISCOVERY_REQUIRED` | — | — | — | — | Record episode and burden separately. |
| CW-11 | Interpret | `DISCOVERY_REQUIRED` | — | — | — | — | Do not silently count as data-processing toil. |
| CW-12 | Document / handoff | `DISCOVERY_REQUIRED` | — | — | — | — | Capture only if inside declared boundary. |

## 4. Round-1 evidence ingestion rule

For every real/retrospective observation added later:

- assign a non-PHI `observation_id` and `analysis_case_id`;
- retain the source observation file outside raw patient-data storage boundaries defined by local governance;
- compute a SHA-256 source reference;
- record observation mode and evidence status;
- preserve partial-case boundaries;
- never infer missing event durations;
- never transform an interview estimate into a measured duration;
- never infer pathology/noise taxonomy from workflow timing notes.

## 5. Current Round-1 finding

No site observation or retrospective workflow record was supplied with the inputs used to build this DAY03 handoff. Therefore:

- `time-motion-baseline-round1.csv` contains the canonical header only;
- no case is baseline eligible;
- no monthly case volume is claimed;
- no manual-processing baseline is claimed;
- no remeasurement rate is claimed;
- no workflow node is upgraded to `SITE_VERIFIED`.

This is an intentional **evidence-safe block**, not a missing-code failure.

## 6. Review checklist before a row may become baseline eligible

- [ ] Observation mode is direct observation or approved retrospective reconstruction.
- [ ] Governance approval/reference is present when required.
- [ ] No direct PHI, raw signal, screenshot or clinical-note dump is embedded.
- [ ] Start/end boundaries are explicit.
- [ ] Event intervals are complete enough for the endpoint claimed.
- [ ] Concurrent intervals are handled by interval-union logic.
- [ ] Doctor/KTV/system/waiting/interpretation classes remain separate.
- [ ] Remeasurement reason is recorded as reported evidence, not silently relabeled.
- [ ] Reviewer status is `ACCEPTED_FOR_ROUND1_BASELINE`.
- [ ] Evidence limitations are explicit.

## 7. Handoff

DAY04 can only start with `GO_FOR_DAY_04` after the DAY03 validator sees at least one reviewed baseline-eligible Round-1 case and no blocking governance/evidence conflict. Otherwise the correct status is `BLOCKED_WITH_EVIDENCE` or `READY_WITH_LIMITATIONS` according to the evidence actually available.
