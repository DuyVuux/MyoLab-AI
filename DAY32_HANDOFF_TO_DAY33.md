# DAY32 → DAY33 HANDOFF CONTEXT PACK

## 0. Handoff Metadata

```yaml
current_day: DAY32
next_day: DAY33

dependency_type: HARD_HANDOFF

current_day_status: PASS

direct_handoff_required: true

generated_from_actual_outputs: true
```

---

## 1. Executive Handoff

* DAY32 solved the annotation readiness contract and evidence authority ladder for the independent research portfolio (DAY32–DAY90 Roadmap v2.0).
* End status: PASS. All 50 focused unit/contract tests, 60 upstream DAY31 regression tests, contract schema validator, and 38 managed artifact SHA256 integrity checks passed cleanly.
* Frozen elements: 4-tier evidence ladder (`SYNTHETIC_KNOWN_TRUTH`, `WEAK_LABEL_CANDIDATE`, `EXPERT_ANNOTATION`, `ADJUDICATED_REFERENCE`), WindowIdentity selection unit (`QC_WINDOW_WITH_CONTEXT`), strict de-identification rules, non-diagnostic reviewer rubric, and time-based annotation budget policy.
* Automatic promotion of synthetic data or machine weak labels to expert annotation/ground truth is explicitly forbidden by code semantics and schema invariants.
* DAY33 may begin immediately.

---

## 2. What DAY32 Was Supposed To Achieve

### Objective
Freeze the evidence authority ladder, reviewer rubric, acquisition strata, annotation budget policy, and DAY33 research data readiness checklist required for future research annotation without claiming clinical access or fabricating clinical gold-standards.

### Inputs
- DAY21 taxonomy + `LabelingFunctionOutput`
- DAY22 `WindowIdentity`
- DAY23–29 detector/integrity evidence
- DAY30 aggregation semantics
- DAY31 metric-handoff safety boundary

### Mandatory Outputs
- `clinical/labels/qc-annotation-protocol.v0.2-research.md`
- `clinical/labels/qc-annotation-schema.v0.2-research.yaml`
- `clinical/review-templates/qc-adjudication-policy.v0.2-research.md`
- `clinical/labels/annotation-acquisition-policy.v0.2-research.yaml`
- `clinical/labels/annotation-budget-policy.v0.2-research.md`
- `qa-validation/evidence/day32-data-readiness.template.yaml`

### Acceptance Criteria
- Protocol is sufficient for a new reviewer to annotate without asking engineers about semantics.
- Unavailable expert/site evidence is explicitly recorded as `NOT_AVAILABLE` / `NOT_VERIFIED`.
- No real clinical data required to PASS the engineering day.
- Claim scope restricted to `RESEARCH_ONLY` with claim status `ANNOTATION_READINESS_ENGINEERING_READY`.

---

## 3. Actual Completion Status

| Requirement | Expected | Actual | Status | Evidence |
| ----------- | -------- | ------ | ------ | -------- |
| Evidence Ladder Schema | 4 explicit tiers defined | 4 tiers (`SYNTHETIC_KNOWN_TRUTH`, `WEAK_LABEL_CANDIDATE`, `EXPERT_ANNOTATION`, `ADJUDICATED_REFERENCE`) | PASS | `clinical/labels/qc-annotation-schema.v0.2-research.yaml` |
| Reviewer Rubric | Non-diagnostic, ambiguity-aware rubric | Defined with explicit `INSUFFICIENT_EVIDENCE` and `BOTH_POSSIBLE` options | PASS | `clinical/labels/qc-annotation-protocol.v0.2-research.md` |
| Acquisition Policy | Stratified selection without hard quotas | 6 selection strata defined, hard quotas = null | PASS | `clinical/labels/annotation-acquisition-policy.v0.2-research.yaml` |
| Budget Policy | Time-based budget model | Seconds-per-window calculation (15–45s/window) | PASS | `clinical/labels/annotation-budget-policy.v0.2-research.md` |
| Adjudication Policy | Multi-reviewer consensus rules | Requires $\ge 2$ independent expert refs + explicit action | PASS | `clinical/review-templates/qc-adjudication-policy.v0.2-research.md` |
| JSON Schema | Draft 2020-12 valid schema | `qc-annotation-item.research.v0.2.schema.json` | PASS | `packages/common-schemas/json/qc-annotation-item.research.v0.2.schema.json` |
| Semantics Invariants | Enforce transitions & de-identification | `day32_annotation_semantics.py` with invariant checks | PASS | `qa-validation/lib/day32_annotation_semantics.py` |
| Contract Validator | Pass positive & reject negative fixtures | 4 positive passed, 10 negative rejected | PASS | `scripts/dev/day32_annotation_contract_validator.py` |
| Automated Test Suite | 50 focused unit/contract tests | 50/50 PASS in 0.42s | PASS | `qa-validation/automated-tests/qc/test_day32_annotation_readiness.py` |
| Upstream Regression | Upstream DAY31 tests pass | 44 unit + 16 property tests PASS | PASS | `qa-validation/automated-tests/qc/test_quality_handoff.py` |
| Artifact Integrity | All managed artifacts verified | 38/38 SHA256 hashes match | PASS | `qa-validation/evidence/day32-artifact-manifest.json` |

---

## 4. Artifacts Produced

| Artifact | Path | Role | Status | Needed by DAY33? |
| -------- | ---- | ---- | ------ | ------------------- |
| Common JSON Schema | `packages/common-schemas/json/qc-annotation-item.research.v0.2.schema.json` | SCHEMA | FOUND | YES |
| Annotation Schema Spec | `clinical/labels/qc-annotation-schema.v0.2-research.yaml` | POLICY | FOUND | YES |
| Annotation Protocol | `clinical/labels/qc-annotation-protocol.v0.2-research.md` | PROTOCOL | FOUND | NO |
| Acquisition Policy | `clinical/labels/annotation-acquisition-policy.v0.2-research.yaml` | POLICY | FOUND | YES |
| Budget Policy | `clinical/labels/annotation-budget-policy.v0.2-research.md` | POLICY | FOUND | NO |
| Adjudication Policy | `clinical/review-templates/qc-adjudication-policy.v0.2-research.md` | POLICY | FOUND | NO |
| Data Readiness Template | `qa-validation/evidence/day32-data-readiness.template.yaml` | TEMPLATE | FOUND | YES |
| Data Readiness Reference | `qa-validation/evidence/day32-data-readiness.reference.yaml` | EVIDENCE | FOUND | YES |
| Domain Semantics Library | `qa-validation/lib/day32_annotation_semantics.py` | CODE | FOUND | YES |
| Contract Validator Script | `scripts/dev/day32_annotation_contract_validator.py` | SCRIPT | FOUND | NO |
| Artifact Integrity Script | `scripts/dev/check_day32_artifacts.py` | SCRIPT | FOUND | NO |
| Master Test Runner | `scripts/dev/run_day32_checks.sh` | SCRIPT | FOUND | NO |
| Test Fixture Directory | `qa-validation/test-data/day32/*.json` | TEST_DATA | FOUND | NO |
| Focused Test Suite | `qa-validation/automated-tests/qc/test_day32_annotation_readiness.py` | TEST | FOUND | NO |
| Artifact Manifest | `qa-validation/evidence/day32-artifact-manifest.json` | MANIFEST | FOUND | NO |
| Execution Plan | `docs/00-executive/day32/DAY32_EXECUTION_PLAN.md` | DOC | FOUND | NO |

---

## 5. Frozen Contracts & Decisions

| Decision / Contract | Value / Rule | Status | Downstream consequence |
| ------------------- | ------------ | ------ | ---------------------- |
| 4-Tier Evidence Ladder | `SYNTHETIC_KNOWN_TRUTH`, `WEAK_LABEL_CANDIDATE`, `EXPERT_ANNOTATION`, `ADJUDICATED_REFERENCE` | FROZEN | DAY33 manifest items MUST assign exact `evidence_tier` from this ladder. |
| Automatic Promotion | `automatic_promotion_forbidden = true` | FROZEN | DAY33 cannot tag machine rules or synthetic transforms as expert annotation. |
| Window Selection Unit | `QC_WINDOW_WITH_CONTEXT` | FROZEN | Every corpus window MUST reference DAY22 `window_id` + context bounds. Random crop forbidden. |
| De-identification Invariant | `direct_identifiers_present = false` | FROZEN | Public/synthetic signals MUST strip any PHI or subject direct identifiers. |
| Claim Scope | `RESEARCH_ONLY` | FROZEN | Corpus items and benchmark tags MUST be restricted to research scope. |
| Non-diagnostic Rubric | `diagnostic_suggestion_present = false` | FROZEN | DAY33 synthetic scaling MUST NOT be labeled as pathology (`stroke`, `paresis`, `atrophy`). |
| Acquisition Strata | 6 strata (Random, Disagreement, Novelty, High-Risk False Allow, High Workflow Impact, Ambiguity) | FROZEN | DAY33 benchmark sampling should represent these strata. |

---

## 6. Test & Verification Evidence

* **Contract Validator**: `python3 scripts/dev/day32_annotation_contract_validator.py` $\rightarrow$ `PASS` (4 tiers, 6 strata, 4 positive fixtures valid, 10 negative fixtures rejected).
* **Focused Unit Tests**: `python3 -m pytest qa-validation/automated-tests/qc/test_day32_annotation_readiness.py` $\rightarrow$ `50 passed in 0.42s`.
* **Upstream Regression**: `qa-validation/automated-tests/qc/test_quality_handoff.py` $\rightarrow$ `44 passed in 0.37s`; `qa-validation/property-tests/test_day31_quality_handoff_properties.py` $\rightarrow$ `16 passed in 0.09s`.
* **Artifact Integrity**: `python3 scripts/dev/check_day32_artifacts.py` $\rightarrow$ `PASS` (38 managed artifacts verified via SHA256).
* **Master Verification Script**: `bash scripts/dev/run_day32_checks.sh` $\rightarrow$ `PASS`.

---

## 7. Known Limitations / Blockers

| Issue | Severity | Impact | Required handling |
| ----- | -------- | ------ | ----------------- |
| No Real Clinical Data | LOW (Expected) | Cannot claim clinical effectiveness or site validation | DAY33 uses public datasets + synthetic known-truth only. |
| Expert Reviewers Unavailable | LOW (Expected) | `EXPERT_ANNOTATION` and `ADJUDICATED_REFERENCE` tiers remain empty | Keep expert tiers unpopulated; populate `SYNTHETIC_KNOWN_TRUTH` & `WEAK_LABEL_CANDIDATE`. |
| Public Dataset Catalog Pending | MEDIUM | DAY33 needs to select and ingest open-source sEMG datasets | DAY33 WP1/WP2 must build `public-sEMG-catalog.v0.1.yaml` and dataset cards. |

---

## 8. Safety / Claim Boundaries Carried Forward

- `synthetic ≠ clinical truth`: Synthetic transforms are technical stress tests only.
- `public healthy data ≠ clinical validation`: Public datasets prove technical pipeline behavior, not clinical efficacy.
- `artifact ≠ pathology`: Signal artifacts (clipping, dropout, line noise) must not be labeled as muscle pathology.
- `null + reason ≠ 0`: Abstention or unsupported metrics must fail closed with explicit reason code.
- `synthetic amplitude scaling ≠ pathology`: Scaling waveform amplitude is `SYNTHETIC_LOW_AMPLITUDE_STRESS` only.
- `non-clinical review ≠ expert annotation`: Internal engineer testing must be tagged `NON_CLINICAL_REVIEW`.

---

## 9. NEXT_DAY Input Dependency Map

| NEXT_DAY Input | Source Day | Artifact / Decision | Path | Status |
| -------------- | ---------: | ------------------- | ---- | ------ |
| DAY32 evidence policy | DAY32 | Evidence Ladder & Schema | `clinical/labels/qc-annotation-schema.v0.2-research.yaml` | FOUND |
| Annotation item schema | DAY32 | JSON Schema Draft 2020-12 | `packages/common-schemas/json/qc-annotation-item.research.v0.2.schema.json` | FOUND |
| Data readiness gate | DAY32 | Data Readiness Template | `qa-validation/evidence/day32-data-readiness.template.yaml` | FOUND |
| Public dataset inventory | DAY25/DAY27 | Public Dataset Inventory | `docs/05-data/public-dataset-inventory.csv` | FOUND |
| Synthetic factories | DAY23–DAY28 | QC detector test suites & signal generators | `qa-validation/automated-tests/qc/` | FOUND |
| License register | DAY25-Research | Dataset License & Access Register | `docs/05-data/day25-research/dataset-license-access-register-v0.2.csv` | FOUND |

---

## 10. Context NEXT_DAY Must Load

### MUST LOAD
1. `docs/plans/version03/MyoLab_AI_DAY32_90_Independent_Portfolio_Roadmap_v2.0.md` (DAY33 section)
2. `clinical/labels/qc-annotation-schema.v0.2-research.yaml` (Evidence tiers & rules)
3. `packages/common-schemas/json/qc-annotation-item.research.v0.2.schema.json` (JSON schema)
4. `qa-validation/evidence/day32-data-readiness.reference.yaml` (Upstream readiness state)
5. `docs/05-data/public-dataset-inventory.csv` (Public dataset candidates)

### SHOULD LOAD
1. `qa-validation/lib/day32_annotation_semantics.py` (Validation functions)
2. `docs/05-data/day25-research/dataset-license-access-register-v0.2.csv` (Licensing rules)

### DO NOT USE AS SOURCE OF TRUTH
1. Legacy clinical roadmap documents assuming Vinmec/MotionLab data access.
2. Unverified proprietary or confidential raw export files.

---

## 11. NEXT_DAY Starting State

```text
STARTING CONTEXT FOR DAY33

Upstream status:
- DAY32 Annotation Readiness Contract is complete, verified, and frozen.
- 4-Tier Evidence Ladder is active: SYNTHETIC_KNOWN_TRUTH, WEAK_LABEL_CANDIDATE, EXPERT_ANNOTATION, ADJUDICATED_REFERENCE.

Frozen contracts:
- Selection unit = QC_WINDOW_WITH_CONTEXT (DAY22 WindowIdentity).
- De-identification = direct_identifiers_present: false.
- Claim scope = RESEARCH_ONLY.
- Automatic promotion forbidden (synthetic/weak label -> expert).

Available artifacts:
- qc-annotation-item.research.v0.2.schema.json
- qc-annotation-schema.v0.2-research.yaml
- day32-data-readiness.reference.yaml

Known limitations:
- No clinical access; DAY33 must construct Research Benchmark Corpus v1 using public sEMG datasets + synthetic known-truth windows.

Do not:
- Do not fabricate clinical pathology labels from amplitude scaling.
- Do not ingest public datasets without verified open-source licenses.
- Do not violate the 4-tier evidence ladder tags in research-benchmark-corpus-v0.1.manifest.yaml.

DAY33 may begin: YES
```

---

## 12. Recommended First Action for DAY33

> **Inspect open-source sEMG dataset candidates in `docs/05-data/public-dataset-inventory.csv` and verify license compatibility before building `data-platform/datasets/public-sEMG-catalog.v0.1.yaml`.**
