# DAY21 Engineering Execution Specification & Integration Runbook
## QC Taxonomy & Machine-Readable Reason-Code Contract

## 0. Document Control
- **Day:** DAY21
- **Phase:** Phase 2 — sEMG Quality Intelligence Foundation
- **Primary task:** QC Taxonomy & Machine-Readable Reason-Code Contract
- **Augmentation:** Active Learning + Weak Supervision — contract/registry only
- **Traceability:** FR-030, FR-037..041, NFR-009, NFR-011
- **Safety:** quality support, not diagnosis; preserve physiology; fail closed on unknown configuration
- **Training:** not authorized / not required
- **Patient data in package:** none

## 1. Executive Intent
DAY21 begins the QC phase by solving a semantic problem before a signal-processing problem. Later detectors can each be technically correct yet collectively unsafe if they emit incompatible labels, hide uncertainty, or transform a quality observation into a clinical statement. DAY21 therefore defines the machine-readable language that every later QC component must speak.

The day creates a versioned taxonomy, a common QC result schema, a reason-code registry, and the first weak-supervision labeling-function contract. It deliberately creates no clinical threshold and no detector.

## 2. Why This Day Exists
Phase 1 established how data enter the system. Phase 2 must establish what “quality evidence” means. Without DAY21, later days could implement incompatible PASS/WARNING/FAIL semantics or collapse acquisition artifacts and physiological variation into the same label.

The roadmap requires clinician taxonomy to become machine-readable categories, evidence fields, PASS/WARNING/FAIL semantics and technical action suggestions. Technology Augmentation additionally requires `labeling_function_candidate`, `evidence_type`, `severity`, `supportability`, plus a common schema for rule/detector output.

## 3. Position in the 90-Day Critical Path
```text
DAY20 Gate B / frozen ingestion
        ↓
DAY21 QC language + reason contract
        ↓
DAY22 window identity / aggregation architecture
        ↓
DAY23–28 controlled detectors
        ↓
DAY29–31 integrated QC / blocking
        ↓
DAY32–35 expert evidence / thresholds
        ↓
DAY36–39 edge cases / regression / Gate C
```
DAY21 cannot perform DAY22 windowing or DAY23 detector implementation.

## 4. Relationship With DAY20
The supplied report says DAY20 reference artifacts are integrated, traceability now uses `requirements-manifest.yaml`, the evaluator is unified in `scripts/dev/day20_gate_evaluator.py`, and all 40 governance tests pass. DAY21 preserves this Option B architecture: its requirement impact lives in YAML, while Python reads configuration instead of encoding requirement counts.

The report does **not** state the current Gate-B decision. DAY21 therefore records phase entry as user-reported upstream state, permits contract-only engineering, and does not claim site-real-data QC authorization until the live evaluator returns `REAL_DATA_READY`.

## 5. What Must Be True Before Starting
**Input:** current monorepo after DAY20 integration.  
**Output:** engineer knows whether the work is contract/synthetic only or phase-entry/site evidence is authorized.  
**Stop:** if anyone attempts to use real clinical windows while privacy/Gate B is not authorized.

## 6. Objectives
1. Upgrade DAY04 taxonomy v0.1 into QC taxonomy v0.2 without losing physiology-preservation semantics.
2. Define strict QC result JSON Schema.
3. Define reason-code registry with evidence, severity, supportability and technical actions.
4. Define weak-supervision output schema where weak labels cannot claim expert truth.
5. Register DAY23–28 LF candidates without implementing them early.
6. Preserve configuration-driven traceability from DAY20.
7. Provide negative tests for unsafe semantic combinations.

## 7. Non-Goals / Out of Scope
No dropout/clipping/noise/power-line/motion/poor-contact detector. No window length or overlap. No aggregation. No numerical threshold freeze. No weak-supervision label model. No Active Learning selection. No OOD score/model. No clinical diagnosis.

## 8. Source of Truth
SRS → PRD → observed data reality → authoritative roadmap → Technology Augmentation as additive delta → accepted prior-day artifacts → legacy research. DAY04 taxonomy is a useful engineering baseline but cannot override current SRS.

## 9. Requirements Addressed
- **FR-030:** taxonomy defines SESSION/CHANNEL/WINDOW scopes.
- **FR-037:** QC result schema defines PASS/WARNING/FAIL plus typed reasons.
- **FR-038:** `QUALITY_BLOCKED` and technical blocking action are defined, but execution is later.
- **FR-039:** warning/review semantics are typed.
- **FR-040:** scope semantics prepare later usable-window/bad-window aggregation without implementing it today.
- **FR-041 / NFR-011:** taxonomy/config/rules are versioned.
- **NFR-009:** reason codes carry explainable evidence/action semantics.

## 10. Inputs
DAY20 integrated monorepo; live `requirements-manifest.yaml` when available; DAY04 taxonomy v0.1; SRS QC requirements; Technology Augmentation DAY21 delta. No raw patient signal is needed.

## 11. Mandatory Outputs
```text
clinical/quality/qc-taxonomy.v0.2.yaml
packages/common-schemas/json/qc-result.schema.json
services/quality-gate-service/config/reason-codes.v0.1.yaml
```
Augmentation:
```text
packages/common-schemas/json/labeling-function-output.schema.json
clinical/labels/qc-labeling-function-registry.v0.1.yaml
```

## 12. Supporting Outputs
Traceability YAML/CSV, phase-entry evidence, synthetic contract fixtures, validator, semantic checker, pytest suite, peer-review template, acceptance checklist and integration notes.

## 13. Target Repo Tree
Only existing domains are used: `clinical/`, `packages/common-schemas/`, `services/quality-gate-service/config/`, `qa-validation/`, `docs/`, `scripts/dev/`. No new service or repository.

## 14. Data/Evidence Boundaries
Fixtures are `TEST_FIXTURE_ONLY`. No PHI/patient signal. `EXPERT_REVIEW` and `SITE_VERIFIED` are allowed schema values for future evidence, not claims that DAY21 possesses those evidence classes.

## 15. Safety/Governance Invariants
**A — quality evidence is not diagnosis.** A reason may say suspected poor contact; it cannot assign disease.  
**B — physiology context cannot fail QC by itself.** Stroke, paresis, atrophy or body habitus are context tags.  
**C — no-evaluation cannot look normal.** If `evaluation_status != EVALUATED`, `signal_quality` must be null.  
**D — weak label != ground truth.** JSON Schema forces both ground-truth and expert-label claims false.  
**E — no threshold by invention.** The reason registry contains no numeric detector threshold.

## 16. Environment/Tooling
Python 3.11 recommended. QA uses PyYAML, jsonschema and pytest. `run_day21_checks.sh` prefers `uv run` in a project managed by uv and otherwise falls back to Python.

## 17. Preflight
### STEP 01 — Confirm repo root
**Input:** live monorepo.  
**Action:** `git rev-parse --show-toplevel && git status --short`.  
**Output:** one known root and understood unrelated changes.  
**Stop:** no repository root.

### STEP 02 — Inspect live Gate B
**Input:** `scripts/dev/day20_gate_evaluator.py`.  
**Command:** `uv run python scripts/dev/day20_gate_evaluator.py --root "$(git rev-parse --show-toplevel)"`.  
**Output:** structured gate decision.  
**Stop:** site-real-data work requested while gate is blocked.

## 18. Detailed Execution Procedure
### STEP 03 — Collision review
Check the five core paths before copy. Use semantic diff; never blindly overwrite an independently approved version.

### STEP 04 — Review taxonomy v0.2
**Goal:** preserve DAY04 safety while adding machine fields.  
**Verify:** three scopes, semantic classes, evidence types, severity, supportability and `numeric_thresholds_frozen=false`.  
**Negative:** no disease-severity or diagnosis field.

### STEP 05 — Review reason registry
Inspect every code for definition, allowed scope, evidence candidates, default effect, supportability, action and forbidden inference. `QUALITY_BLOCKED` is a disposition, not an LF candidate.  
**Stop:** any reason can be mistaken for a diagnosis without additional clinical interpretation.

### STEP 06 — Validate QC result schema
**Critical rule:** `NOT_EVALUATED` and `INSUFFICIENT_EVIDENCE` require null `signal_quality`.  
**Negative:** an added `diagnosis` property is rejected because schema is closed.

### STEP 07 — Validate weak-supervision schema
**Expected:** only candidate labels; no probability field; `ground_truth_claim=false`; `expert_label_claim=false`.  
**Negative:** ground-truth fixture must fail.

### STEP 08 — Review LF registry
Entries are future `PLANNED_DAY23..28`; DAY21 does not implement detector code.  
**Stop:** actual detector/model source appears in DAY21 patch.

### STEP 09 — Reconcile configuration-driven traceability
Validator reads `day21-requirement-impact.yaml` and, when live `requirements-manifest.yaml` exists, checks subset membership.  
**Negative:** no hard-coded requirement count in validator.

### STEP 10 — Run automated validation
```bash
bash scripts/dev/run_day21_checks.sh
```
**Expected:** contract validator PASS + 48 pytest cases PASS + managed artifact hashes PASS.

### STEP 11 — Strict phase-entry check for promotion
```bash
DAY21_STRICT_PHASE_ENTRY=1 bash scripts/dev/run_day21_checks.sh
```
**Expected:** live Gate B = `REAL_DATA_READY`. Green contract tests never override a blocked upstream gate.

### STEP 12 — Manual expert/QA review
Complete `day21-peer-review.template.yaml`; review non-diagnostic language, ambiguity handling, LF truth boundary, no threshold/site assumptions.

### STEP 13 — Closeout/Git handoff
Run `git diff --check`, review targeted diff, commit only DAY21-managed changes.

## 19. Automated Validation Strategy
STATIC artifact checks; Draft 2020-12 SCHEMA tests; cross-contract consistency; NEGATIVE unsafe-shape tests; configuration-driven TRACEABILITY; SAFETY semantic tests. Detector accuracy is intentionally absent because no detector exists today.

## 20. Manual/Expert Review
A DSP/clinical reviewer challenges terms such as poor contact, physiology possible, quality blocked and review required. The reviewer is not asked to approve thresholds. The central question is whether each reason reports measurement/evidence state without claiming pathology.

## 21. Failure Injection / Negative Tests
Attempt weak-label ground truth, diagnosis field in QC output, PASS for not-evaluated, PASS with review-required evidence, FAIL without blocking evidence, unknown reason, numeric threshold, and premature detector files.

## 22. Requirement Traceability
Configuration-driven: `day21-requirement-impact.yaml` carries the roadmap IDs; validator reconciles against live authoritative manifest when present. No Python constant encodes the expected count.

## 23. Acceptance Criteria
Mandatory + augmentation artifacts exist; schemas pass; negative fixtures fail as expected; no hidden threshold/site fact; weak labels cannot claim ground truth; traceability reconciles; tests pass; human review is approved before `GO_FOR_DAY_22`.

## 24. Definition of Done
Engineering DoD = coherent machine-readable QC semantic contract, testable and safely limited. Site validation is not a DAY21 DoD. Promotion additionally requires acceptable phase-entry state and manual review.

## 25. Stop / Block Conditions
Block if reason embeds diagnosis/pathology from quality feature, unknown becomes PASS, weak label becomes expert truth, unsupported threshold is frozen, authoritative manifest conflicts, or real-data work occurs without approved privacy/evidence tier.

## 26. Known Limitations
No detector performance, expert-window dataset, site threshold, aggregation policy or OOD model. These are later work; do not fill by assumption.

## 27. Open Questions
Live Gate-B decision; expert annotation workflow; threshold evidence tiers; later detector disagreement prioritization; required protocol context per detector.

## 28. Integration
Use `rsync -avni` for dry run. Copy only `repo_patch/` to root. Do not overwrite DAY20 `requirements-manifest.yaml` or evaluator. Run checks after copy.

## 29. Git Workflow
Focused branch/commit; no detector/UI work mixed in. Run `git diff --check` and review collisions.

## 30. Rollback
Restore/remove only DAY21-managed files from its commit. Do not roll back DAY20 Gate-B configuration. If v0.2 is consumed by another branch, coordinate a version rollback instead of silently reverting to v0.1.

## 31. Evidence/Provenance
Package evidence is synthetic/configuration evidence. DAY20 report is user-reported upstream context, not independently verified filesystem evidence. Validation report records contract maturity, not clinical validation.

## 32. Closeout
Close with validator/tests, peer review, traceability review and live Gate-B state. Engineering PASS can coexist with `READY_WITH_LIMITATIONS`.

## 33. Next-day Handoff
DAY22 receives a frozen semantic vocabulary and QC result contract. It defines stable window identity, overlap/profile policy and aggregation architecture without redefining reason semantics.

## 34. Final Status Rules
- `GO_FOR_DAY_22`: tests + manual review PASS and live phase-entry state acceptable.
- `READY_WITH_LIMITATIONS`: engineering-complete but Gate B decision/site phase-entry evidence is not demonstrated in the supplied report, or a non-safety limitation remains.
- `BLOCKED_WITH_EVIDENCE`: privacy/governance/evidence insufficient for data class or safety conflict remains.

Never use `CLINICALLY_VALIDATED`, `SITE_VALIDATED` or `PRODUCTION_READY`.

# Appendix A — Formal QC Semantic Model

DAY21 is intentionally a semantic-contract day. The central engineering object is not a detector score but a **typed statement about quality evidence**. The minimum state model is:

```text
QCResult
├── evaluation_status
│   ├── EVALUATED
│   ├── NOT_EVALUATED
│   └── INSUFFICIENT_EVIDENCE
├── scope
│   ├── SESSION
│   ├── CHANNEL
│   └── WINDOW
├── signal_quality
│   ├── PASS
│   ├── WARNING
│   ├── FAIL
│   └── null when no supportable evaluation exists
├── reasons[]
│   ├── reason_code
│   ├── semantic_class
│   ├── severity
│   ├── supportability
│   ├── evidence_type[]
│   ├── evidence_status
│   ├── evidence_refs[]
│   └── technical_action
└── provenance
    ├── contract version
    ├── configuration version
    ├── evaluator version
    └── source references
```

The model deliberately separates three questions that are frequently collapsed in early QC systems:

1. **Was the quality assessment actually performed?** This is `evaluation_status`.
2. **If performed, what is the operational quality state?** This is `signal_quality`.
3. **Why is that state justified?** This is the list of reason/evidence objects.

This separation prevents an unsafe default such as `detector unavailable → PASS`. A missing detector, missing protocol reference, missing device metadata, or unsupported context is not evidence of a good signal. In DAY21, `NOT_EVALUATED` and `INSUFFICIENT_EVIDENCE` are therefore structurally incompatible with a non-null PASS/WARNING/FAIL value.

The same separation also helps later analytics. At DAY37, a false-allow analysis must distinguish “system evaluated and incorrectly passed” from “system never had enough evidence to evaluate.” Those are different failure modes with different mitigations.

# Appendix B — Taxonomy Migration v0.1 → v0.2

DAY04 created the first clinical data-quality taxonomy. DAY21 does not discard it. The migration follows a **preserve-and-formalize** strategy:

```text
DAY04 v0.1
human-readable safety taxonomy
        ↓ preserve principles
DAY21 v0.2
machine-readable QC semantic contract
        ↓
DAY23–28 detectors
        ↓
DAY30 aggregation
```

The following DAY04 invariants are preserved without weakening:

- physiological variation is not automatically artifact;
- pathology is not noise;
- body habitus alone is not a QC failure;
- measurement facts and clinical interpretations are different evidence classes;
- ambiguous states should surface for review rather than be forced into a clean/noisy binary;
- raw data remain immutable;
- numerical QC thresholds are not invented before evidence.

DAY21 adds structures required by production software: scope enums, evaluation state, severity, supportability, evidence type, technical action, registry versioning, JSON Schemas, labeling-function candidacy, and explicit weak-supervision boundaries.

A migration review must therefore ask two questions. First, **did v0.2 preserve every safety distinction from v0.1?** Second, **did v0.2 add only machine semantics, rather than silently adding new site facts?** If a new field requires a number such as an amplitude threshold, ADC limit, mains frequency, or acceptable dropout duration and that number is not supported by approved evidence, the field must remain policy-dependent/TBD rather than filled with a plausible value.

# Appendix C — Reason-Code Lifecycle and Change Control

Reason codes are API semantics, not disposable labels. Once downstream UI, evidence bundles, audit events, or clinician workflows consume a code, changing its meaning can silently invalidate historical replay. For that reason, use the following lifecycle:

```text
PROPOSED
→ machine schema added
→ semantic review
→ detector implementation references it
→ validation evidence accumulates
→ FROZEN for a release/config version
→ DEPRECATED only through change record
```

A reason code may change wording without changing meaning, but semantic changes require version impact review. For example, changing `POOR_CONTACT_SUSPECTED` from “evidence suggests possible contact/acquisition abnormality” to “electrode contact is bad” is not cosmetic. It converts uncertainty into a measurement fact and can cause a patient-specific physiological pattern to be discarded. Such a change must be rejected unless a higher-quality evidence source and approved requirement change justify it.

Reason codes are also divided by responsibility. **Evidence reasons** explain observed/derived quality evidence. **Disposition reasons** such as `QUALITY_BLOCKED` or `CLINICIAN_REVIEW_REQUIRED` describe what the current policy does with evidence. A disposition must not erase the underlying evidence reason. A future evidence bundle should be able to answer both “what was observed?” and “what did the policy decide?”

# Appendix D — Evidence Hierarchy for DAY21 Semantics

DAY21 introduces evidence fields but does not pretend all evidence has equal authority. A practical hierarchy for QC development is:

```text
SYNTHETIC_KNOWN_TRUTH
  useful for exact injected conditions and analytical detector tests

DEVICE / PROTOCOL DOCUMENTED EVIDENCE
  useful for what a device/profile is documented to support

OBSERVED SAMPLE / SITE DATA EVIDENCE
  useful for real export and acquisition behavior

EXPERT ANNOTATION
  useful for interpretation of real QC windows under a rubric

ADJUDICATED EXPERT REFERENCE
  stronger reference for disputed categories
```

These evidence classes answer different questions. Synthetic data can prove that a dropout detector detects a known 400 ms gap under a controlled fixture, but it cannot prove clinical robustness on pathological signals. Expert annotation can judge a real signal, but an expert label does not replace exact byte-level source provenance. Device documentation can state sampling or saturation properties, but does not demonstrate that a specific site configuration used those settings.

For this reason, the QC schema stores **evidence type** and **evidence status** separately. A future detector may emit `evidence_type=SPECTRAL` while the reference supporting its threshold remains `NOT_VERIFIED`; those fields should not collapse into one ambiguous status.

# Appendix E — Weak Supervision Contract: What Is Allowed and Forbidden

DAY21 marks the first official weak-supervision/Active-Learning work in the augmented roadmap, but its maturity is deliberately limited to **CONTRACT_AND_REGISTRY_ONLY**.

Allowed today:

```text
- define a common labeling-function output schema;
- define future labeling-function IDs and versions;
- map each LF candidate to a reason code and planned day;
- require evidence/provenance in every LF output;
- allow ABSTAIN/UNKNOWN candidate states;
- define ordinal evidence strength if useful;
- explicitly prohibit ground-truth/expert-label claims.
```

Forbidden today:

```text
- train a label model;
- learn LF weights;
- fit probabilistic aggregation;
- select real windows for clinicians;
- claim LF accuracy;
- attach a calibrated probability to a deterministic rule;
- use weak labels as clinician adjudication;
- implement DAY23–28 detectors early.
```

The distinction matters because multiple deterministic rules can be correlated. A future dropout rule and a poor-contact rule may both react to the same flat segment. Counting them as two independent votes would create false certainty. DAY34 explicitly evaluates LF correlation on adjudicated evidence; DAY21 should therefore preserve LF identity and provenance so this later analysis is possible.

# Appendix F — Negative-Test Matrix

The DAY21 QA suite should be understood as a safety contract rather than only schema syntax testing.

| Unsafe case | Expected behavior | Safety reason |
|---|---|---|
| `NOT_EVALUATED` with `PASS` | Reject | unknown cannot look normal |
| QC result contains `diagnosis` | Reject | quality layer is non-diagnostic |
| LF output sets `ground_truth_claim=true` | Reject | weak label is not truth |
| unregistered reason code | Semantic failure | no silent configuration fallback |
| `PASS` includes review-required reason | Semantic failure | internally contradictory state |
| `FAIL` lacks blocking rationale | Semantic failure | fail must be evidence/policy explainable |
| physiology context alone maps to failure | Peer-review blocker | preserve physiology |
| numeric threshold appears in registry | QA blocker | thresholds are future evidence-gated work |
| detector source appears in DAY21 | Scope blocker | DAY23–28 ownership |
| window identity schema appears in DAY21 | Scope blocker | DAY22 ownership |
| model weight/artifact appears | Scope blocker | no model training in DAY21 |

These tests prevent two classes of error: **false certainty** and **scope leakage**. Both are dangerous in medical-data software because they are often invisible during happy-path demos.

# Appendix G — Configuration-Driven Traceability Under Option B

The DAY20 report states that the live monorepo moved requirement traceability to `qa-validation/traceability/requirements-manifest.yaml` and centralized Gate-B evaluation. DAY21 must integrate with this architecture rather than restoring Python constants.

The intended relationship is:

```text
requirements-manifest.yaml        # authoritative live list
        ↑ subset reconciliation
DAY21 requirement-impact.yaml     # requirements touched today
        ↓
day21 validator
        ↓
traceability report / tests
```

The validator must not encode `EXPECTED_REQUIREMENT_COUNT = 8` as a substitute for the manifest. It may validate that DAY21 declares the expected roadmap IDs, but when the live authoritative manifest exists it should read and reconcile against that source. This protects the project if the requirement baseline changes through an approved change record.

The same rule applies to Gate B. `run_day21_checks.sh` can query the live DAY20 evaluator when present. In normal mode it can validate DAY21 engineering artifacts even if the supplied report did not state the gate decision. In strict promotion mode, `DAY21_STRICT_PHASE_ENTRY=1` requires the actual live gate to return `REAL_DATA_READY`. This preserves decision-gated execution without preventing harmless contract development on synthetic/configuration evidence.

# Appendix H — Troubleshooting Playbook

### H.1 JSON Schema passes but semantic tests fail
Likely cause: the object is structurally legal but internally contradictory, for example PASS plus review-required reason. Fix the producer/fixture semantics; do not weaken the semantic checker merely because Draft 2020-12 validation is green.

### H.2 Authoritative requirement reconciliation fails
Check whether the live `requirements-manifest.yaml` changed through an approved DAY20 integration. Compare IDs, not hard-coded counts. If a requirement was renamed/removed, open a decision/change record rather than editing DAY21 impact YAML silently.

### H.3 Gate B strict phase-entry fails while all 48 tests pass
This is expected when the live Gate-B decision is blocked/not demonstrated. Engineering validation and program authorization are different states. Do not set an environment variable or patch evaluator output simply to continue.

### H.4 A reviewer requests an exact clipping/noise threshold in DAY21
Record the request as future evidence/threshold work. DAY24/25 and DAY35 own detector/threshold evidence. DAY21 may define the parameter location and evidence status but not invent the value.

### H.5 A clinician says a waveform “looks pathological”
Keep that statement in clinical/expert context, not as an acquisition-artifact reason unless the evidence specifically supports a measurement issue. Use `PHYSIOLOGICAL_VARIATION_POSSIBLE` or `ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED` when appropriate.

### H.6 LF candidate appears to have very high confidence
Do not convert confidence language into probability. Preserve rule evidence and use ordinal strength if needed. Calibration/label-model evaluation belongs later and requires validation.

# Appendix I — Integration and Rollback Runbook

**Input:** clean/reviewed working tree or a branch where unrelated work is understood.  
**Output:** DAY21 artifacts integrated without modifying DAY20-owned source-of-truth files.

1. From repo root, record `git status --short` and branch name.
2. Compare `repo_patch/` paths against tracked files with `git ls-files`.
3. Run a dry copy such as `rsync -avni <DAY21>/repo_patch/ ./`.
4. Inspect collisions, especially `clinical/quality/`, `packages/common-schemas/json/`, `services/quality-gate-service/config/`, and traceability paths.
5. Copy only after collision review.
6. Run `bash scripts/dev/run_day21_checks.sh`.
7. If Gate B is known to be ready and promotion is intended, run strict mode.
8. Complete peer-review template and record reviewer/evidence state.
9. Run `git diff --check` and inspect the diff for detector/windowing/model scope leakage.
10. Commit DAY21 changes in one focused change or a small controlled series.

Rollback should remove/revert only DAY21-owned artifacts. It must **not** restore an older DAY20 evaluator or overwrite the live requirement manifest. If another branch has already consumed taxonomy v0.2, use an explicit version rollback/change record rather than silently replacing v0.2 with DAY04 v0.1.

# Appendix J — Adversarial Review Before Handoff

**Junior engineer:** Can I run the commands without guessing paths, expected results, or stop conditions?  
**Senior engineer:** Are semantics separated from implementation and future detector scope?  
**Clinical safety reviewer:** Can any reason code accidentally diagnose disease or erase physiological variation?  
**QA reviewer:** Do negative tests exercise unsafe combinations rather than only happy paths?  
**Product/PM reviewer:** Does DAY21 advance the critical path without claiming site validation?  
**Next-day engineer:** Can DAY22 create window identity/aggregation architecture without redefining QC meanings?

DAY21 is acceptable only if all six views can answer yes. A green pytest suite alone is necessary but not sufficient for promotion.

# Appendix K — Requirement-to-Test Verification Matrix

DAY21 should be reviewed requirement-by-requirement rather than by file count. The minimum verification logic is:

| Requirement | DAY21 interpretation | Primary artifact | Verification |
|---|---|---|---|
| FR-030 | QC semantics support SESSION/CHANNEL/WINDOW | taxonomy + QC schema | enum/schema tests |
| FR-037 | evaluated QC uses PASS/WARNING/FAIL + reasons | QC schema + reason registry | positive/negative fixtures + semantic checks |
| FR-038 | blocking state/reason exists and is explainable | `QUALITY_BLOCKED` | FAIL-without-block negative test; later execution owned by DAY31 |
| FR-039 | review-required warning semantics exist | `CHANNEL_WARNING`, `CLINICIAN_REVIEW_REQUIRED` | PASS-with-review contradiction test |
| FR-040 | semantics are ready for bad-window/channel accounting | scopes + provenance | design traceability only; aggregation deliberately deferred |
| FR-041 | QC contract/rules are versioned | versioned YAML/JSON | version assertions and manifest hashes |
| NFR-009 | reason/evidence/action are human-explainable | reason registry + QC schema | field completeness + peer review |
| NFR-011 | schema/rule evolution is controlled | version fields/change notes | deterministic artifact/version tests |

The matrix prevents a common mistake: marking FR-040 “implemented” merely because WINDOW exists as an enum. DAY21 contributes design semantics, while usable-window ratio and bad-window aggregation are implemented later. Traceability must therefore record lifecycle state accurately instead of turning every touched requirement into IMPLEMENTED.

# Appendix L — Release Evidence Checklist

Before handing DAY21 to DAY22, capture the following evidence in the package/live repository:

```text
[ ] qc-taxonomy.v0.2.yaml parses and passes semantic checks
[ ] qc-result.schema.json is valid Draft 2020-12
[ ] reason-codes.v0.1.yaml has unique codes and no diagnosis/numeric threshold leakage
[ ] labeling-function-output.schema.json rejects truth claims
[ ] LF registry contains only PLANNED_DAY23..28 implementations
[ ] requirement impact reconciles against live requirements-manifest.yaml when present
[ ] synthetic positive fixtures validate
[ ] negative fixtures fail for the intended reason
[ ] semantic contradiction tests pass
[ ] no DAY22 window object was implemented
[ ] no DAY23–28 detector was implemented
[ ] no model/training artifact exists
[ ] DAY20-owned evaluator/manifest were not overwritten
[ ] peer review records non-diagnostic language and physiology-preservation review
[ ] strict phase-entry check is used before GO_FOR_DAY_22
```

The expected final engineering claim is narrow: **QC semantics and weak-supervision interface are engineered and testable**. It is not “QC detector validated,” “site thresholds validated,” “Active Learning operational,” or “clinical QC validated.” Preserving this claim boundary is part of the deliverable, not a disclaimer added after the fact.
