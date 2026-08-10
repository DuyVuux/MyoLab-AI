# GATE A — Requirements Readiness

## 0. Gate Identity

| Field | Value |
|---|---|
| Gate | GATE A / M0 |
| Day | DAY08 |
| Purpose | close Phase 0 requirements/readiness before Phase 1 real-data contracts |
| Allowed gate decisions | `REQUIREMENTS_READY` or `BLOCKED_DISCOVERY` |
| Allowed day statuses | `GO_FOR_DAY_09`, `READY_WITH_LIMITATIONS`, `BLOCKED_WITH_EVIDENCE` |
| Current pack decision | `BLOCKED_DISCOVERY` |
| Current pack day status | `BLOCKED_WITH_EVIDENCE` |

## 1. Why Gate A Exists

Gate A prevents the calendar from becoming an authorization mechanism. DAY09 begins a real-data contract workstream; therefore Phase 0 must prove that product scope, privacy path, workflow understanding, evidence request, QC semantics and legacy disposition are sufficient for safe design. A green pytest suite cannot replace missing workflow/site/governance evidence.

## 2. Binary Gate Decision

### `REQUIREMENTS_READY`

May be selected only when all critical criteria GA-01..GA-12 are verified with appropriate evidence **and** manual peer/expert review is approved.

### `BLOCKED_DISCOVERY`

Must be selected when any critical criterion lacks adequate evidence, source conflict is unresolved, privacy path is insufficient for planned data use, or review is pending/rejected.

`READY_WITH_LIMITATIONS` is a **day status**, not a third Gate A decision. It can describe an engineering pack with noncritical limitations, but it cannot be used to bypass a critical Gate A failure.

## 3. Gate Criteria

| ID | Critical | Criterion | Pass evidence |
|---|---:|---|---|
| GA-01 | yes | DAY07 accepted + regression protected | integrated DAY07 validation/human-review evidence |
| GA-02 | yes | current workflow map/evidence boundary adequate | reviewed workflow artifacts |
| GA-03 | yes | privacy/de-identification path adequate for next data class | governance evidence/approval appropriate to data |
| GA-04 | yes | minimum real-data request package defined | DAY06 inventory + request pack |
| GA-05 | yes | artifact-vs-physiology taxonomy available | DAY04 taxonomy/guidance |
| GA-06 | yes | P0 success definition explicit, measurable, no invented baseline | PRD delta v0.2 |
| GA-07 | yes | 79/79 FR/NFR/AC have DESIGN mapping | freeze YAML + matrix |
| GA-08 | yes | AC-10 remains evidence-gated | traceability baseline |
| GA-09 | yes | legacy public-data/model results not promoted to site evidence | DAY07 disposition + human review |
| GA-10 | yes | no silent critical source conflict | decision/change review |
| GA-11 | yes | MFCV optional/site-gated | PRD/SRS delta + FR-064 mapping |
| GA-12 | yes | Knee remains discovery-gated | PRD/SRS + DR-K rule |

Machine state is stored in `qa-validation/evidence/day08-gate-a-evidence.yaml` and validated against `packages/common-schemas/json/gate-a-readiness.schema.json`.

## 4. Current Pack Decision

The handoff package itself **cannot prove the current integrated repository or site evidence**. Therefore it deliberately ships with:

```text
Gate A = BLOCKED_DISCOVERY
DAY08 status = BLOCKED_WITH_EVIDENCE
```

This is not an engineering failure. Automated tests may pass while the evidence gate remains blocked. To promote the gate, the integrated repository must provide evidence refs for currently `NOT_VERIFIED` critical criteria and a human reviewer must approve the review checklist.

## 5. Promotion Rule

A promotion to `REQUIREMENTS_READY` is valid only if:

```text
ALL critical GA criteria ∈ {VERIFIED_DOCUMENTED, SITE_VERIFIED}
AND manual_review.status == APPROVED
AND unresolved critical source conflicts == 0
AND no unsafe evidence promotion is present
```

Then:

```text
Gate A = REQUIREMENTS_READY
DAY08 status = GO_FOR_DAY_09
```

No script may infer `SITE_VERIFIED` from file existence alone.

## 6. Explicit Blocks

Gate A must block if any of the following occurs:

- privacy/governance evidence missing for real patient data planned next;
- current workflow is represented only by an unverified candidate map;
- DAY07 legacy disposition has unreviewed candidates that could alter P0 scope;
- an SRS/PRD conflict is silently resolved using a legacy plan;
- a public healthy dataset is substituted for missing Vinmec evidence while preserving a clinical claim;
- `>=50%` is written as approved pilot target without measured baseline/approved study definition;
- MFCV is enabled because “there are 16 sensors”;
- Knee correction/model is authorized before DR-K01..08 sufficiency;
- test pass is used as evidence of clinical validation.

## 7. Change Control

After Gate A is `REQUIREMENTS_READY`, requirement changes are not forbidden. They become controlled changes. Each material change must identify source trigger, affected requirement IDs, affected artifacts/tests, safety/evidence impact and required revalidation. A version bump and decision record are mandatory for scope/threshold/claim changes.

## 8. Review Signature Semantics

The peer-review template intentionally ships `PENDING`. A reviewer must inspect the actual integrated artifacts and evidence references. Setting `APPROVED` without performing the review is a process violation; the validator checks structure, not reviewer honesty.

## 9. DAY09 Handoff

When Gate A passes, DAY09 receives a frozen product/requirement baseline and may begin **Noraxon Single-CSV Golden Contract** work. DAY09 still must preserve unknown fields and observed-data reality; Gate A does not authorize guessing vendor fields or parsing behavior not supported by actual samples.
