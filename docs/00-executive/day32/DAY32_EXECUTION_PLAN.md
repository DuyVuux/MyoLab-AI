# DAY32 EXECUTION PLAN — Annotation Readiness Protocol & Evidence-Tier Design

## 0. Document Control

- Program: MyoLab-AI — Safety-Aware sEMG Quality Intelligence Research Prototype
- Repository: MyoLab-AI
- Roadmap: DAY32–DAY90 Independent Research & Portfolio Roadmap v2.0
- Phase: Phase 2R — QC Research Validation & Evidence Engineering
- Day: DAY32
- Continuation mode: independent research/portfolio continuation
- Upstream hard dependencies: DAY21, DAY22, DAY30, DAY31 contracts; DAY23–29 evidence vocabulary
- Clinical validation status: NOT PERFORMED
- Production deployment status: NOT FOR CLINICAL USE
- Primary role of DAY32: annotation-readiness engineering, not annotation execution
- Package status: reference implementation requiring live merge/review

## 1. Executive Intent

DAY32 exists to prevent the project from entering an evidence dead-end after the organizational initiative ended before clinical-data validation. The day does not attempt to manufacture replacement clinical evidence. Instead, it freezes the language, hierarchy, reviewer rubric, acquisition policy, budget method and data-readiness gate needed for future research annotation. The engineering goal is simple: if qualified reviewers or new research data become available later, they should be able to start annotation without redesigning evidence semantics.

This rebase is deliberately conservative. Synthetic fixtures remain synthetic. Machine rules remain weak labels. One qualified expert remains one expert annotation. An adjudicated reference requires multiple independent expert annotations plus an explicit adjudication action. Public data remains external research evidence, not site evidence. None of these states may be promoted by changing a filename, editing a status string or passing a unit test.

## 2. Why This Day Exists

DAY21–31 built a mature QC stack: machine-readable taxonomy, stable WindowIdentity, six weak-label detector families, hard data-integrity gates, hierarchical aggregation, abstention and metric-handoff safety. The original roadmap expected clinician annotation next. That assumption is no longer valid after the organizational project ended. If the project simply skipped annotation semantics, later public-data evaluation would mix incompatible evidence tiers. If it fabricated expert labels from synthetic/public data, the portfolio would become less credible.

DAY32 solves this by turning annotation into a governed interface between evidence classes. It is therefore an architecture and research-governance day, not a data-volume day.

## 3. Position on the Critical Path

```text
DAY21 taxonomy / weak-label contract
        +
DAY22 WindowIdentity
        +
DAY23–29 evidence
        +
DAY30 QC aggregation
        +
DAY31 metric handoff
        ↓
DAY32 annotation-readiness contract
        ↓
DAY33 public + synthetic research benchmark corpus
        ↓
DAY34 disagreement / known-truth evaluation
```

DAY32 must not depend on real clinical data. DAY33 may proceed with verified public research data and/or synthetic known-truth; it must expose limitations if public evidence is not yet available.

## 4. Relationship to DAY31

DAY31 is a runtime safety boundary. DAY32 is an evidence-authority boundary. Annotation must never bypass DAY31 metric eligibility and must never automatically rewrite DAY30 QC. Future expert review may generate new evidence for research, but any change to runtime policy remains a separately versioned configuration/decision.

## 5. Preconditions

**Input:** accepted live semantics for DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, DAY30 `QcAggregationResult`, DAY31 eligibility; detector/reason vocabulary from DAY23–29.

**Output of preflight:** the repository can identify a stable window; machine evidence can be tied to that window; unavailable clinical/expert evidence is represented explicitly rather than guessed.

**Do not stop DAY32 because no clinician or hospital data exists.** Stop only if upstream schemas are internally contradictory or if the team tries to use confidential/proprietary data without permission.

## 6. Objectives

1. Freeze a four-tier evidence ladder.
2. Define a non-diagnostic reviewer rubric with explicit ambiguity.
3. Require DAY22 WindowIdentity and surrounding context for every item.
4. Prevent random/contextless crop annotation.
5. Define Active-Learning acquisition strata without running a trained selection model.
6. Define annotation budget from measured time rather than arbitrary sample count.
7. Define DAY33 research-data readiness states.
8. Provide positive/negative fixtures and machine validation.
9. Preserve the project claim boundary: research/portfolio prototype, no clinical validation claim.

## 7. Non-Goals

DAY32 does not collect clinician labels, compute Cohen's kappa, perform adjudication, train a label model, train an Active Learning model, create a clinical gold standard, validate thresholds, compute clinical sensitivity/specificity, diagnose pathology, change DAY30 aggregation or calculate downstream metrics.

It also does not fabricate “stroke”, “paresis”, “atrophy” or other pathology by amplitude scaling. A scaled waveform may be a `SYNTHETIC_LOW_AMPLITUDE_STRESS` fixture only.

## 8. Source of Truth

Priority for DAY32:

1. independent continuation roadmap v2.0 DAY32;
2. accepted live DAY21/22/30/31 contracts;
3. ICR-002, ICR-003, ICR-004, ICR-012;
4. this reference package.

Historical clinical-roadmap assumptions are informative only where they do not conflict with the new evidence boundary.

## 9. Requirements and Safety Claims

- **ICR-002:** no clinical/site claims without evidence.
- **ICR-003:** continuation data is synthetic/public/governed research data only.
- **ICR-004:** synthetic artifact/low amplitude is not pathology.
- **ICR-012:** non-clinical review cannot be called clinician usability/expert evidence.

DAY32 additionally preserves upstream invariants: weak label != ground truth, unknown != normal, physiology != artifact, raw remains immutable, and no fake calibrated probability.

## 10. Inputs

Required logical inputs:

- `labeling-function-output.schema.json` semantics;
- `qc-window-identity.schema.json` semantics;
- machine evidence reason codes from DAY23–29;
- DAY30 QC reasons/supportability;
- DAY31 distribution/uncertainty separation.

Physical raw signal is not required to execute DAY32 contract tests.

## 11. Mandatory Outputs

1. `clinical/labels/qc-annotation-protocol.v0.2-research.md`
2. `clinical/labels/qc-annotation-schema.v0.2-research.yaml`
3. `clinical/review-templates/qc-adjudication-policy.v0.2-research.md`
4. `clinical/labels/annotation-acquisition-policy.v0.2-research.yaml`
5. `clinical/labels/annotation-budget-policy.v0.2-research.md`
6. `qa-validation/evidence/day32-data-readiness.template.yaml`

## 12. Supporting Outputs

- JSON Schema for research annotation items;
- current reference readiness state;
- positive/negative fixtures;
- semantic transition validator;
- automated tests;
- traceability/phase-entry evidence;
- peer-review template;
- runner, artifact manifest, validation report and learning guide.

## 13. Target Repository Tree

```text
clinical/labels/
├── qc-annotation-protocol.v0.2-research.md
├── qc-annotation-schema.v0.2-research.yaml
├── annotation-acquisition-policy.v0.2-research.yaml
└── annotation-budget-policy.v0.2-research.md
clinical/review-templates/
└── qc-adjudication-policy.v0.2-research.md
packages/common-schemas/json/
└── qc-annotation-item.research.v0.2.schema.json
qa-validation/
├── automated-tests/qc/test_day32_annotation_readiness.py
├── evidence/day32-data-readiness.template.yaml
├── evidence/day32-data-readiness.reference.yaml
├── lib/day32_annotation_semantics.py
└── test-data/day32/*.json
scripts/dev/
├── day32_annotation_contract_validator.py
└── run_day32_checks.sh
```

## 14. Data and Evidence Boundaries

The core distinction is **authority**, not file format. `SYNTHETIC_KNOWN_TRUTH` is authoritative only about what the generator injected. It cannot establish patient physiology. `WEAK_LABEL_CANDIDATE` is a machine proposal. `EXPERT_ANNOTATION` requires a new qualified human judgment. `ADJUDICATED_REFERENCE` requires at least two independent expert annotations plus an adjudication action.

A public dataset can provide real waveform variation, but its clinical labels and acquisition semantics are only as trustworthy as its documentation. Public external evidence is never silently rebranded as organizational/site validation.

## 15. Safety and Governance Invariants

- No automatic evidence-tier promotion.
- No random crop without WindowIdentity/context.
- No direct identifiers in annotation items.
- No diagnostic suggestion in annotation UI contract.
- No numeric reviewer “probability”; reviewer confidence is ordinal.
- Machine evidence cannot claim ground truth/expert status.
- Non-clinical reviewer cannot create expert annotation tier.
- Single expert cannot create adjudicated reference.
- Synthetic truth cannot claim clinical truth.
- Annotation cannot automatically override DAY30 QC or DAY31 eligibility.
- Missing public/clinical data is surfaced as readiness limitation, not filled with fabricated evidence.

## 16. Environment and Tooling

Python 3.11+ compatible syntax, pytest, PyYAML and `jsonschema` Draft 2020-12. No production ML dependency is required. Use `PYTHONDONTWRITEBYTECODE=1` and disable pytest cache for release runs.

## 17. Preflight

Run from repository root:

```bash
git status --short
python -V
python -c 'import yaml, jsonschema; print("deps-ok")'
test -f packages/common-schemas/json/qc-window-identity.schema.json
test -f packages/common-schemas/json/labeling-function-output.schema.json
```

If live file names differ because Option-B versioning was adopted, resolve them explicitly; do not copy an older schema over the live one.

## 18. Detailed Procedure

### STEP 1 — Freeze continuation/evidence authority

**Goal:** establish what can and cannot count as evidence after the project discontinuation.

**Input:** independent continuation ICRs.

**Action:** encode the four evidence tiers and their authority in `qc-annotation-schema.v0.2-research.yaml`.

**Expected output:** machine-readable evidence ladder.

**Verification:** validator sees exactly four tiers in order.

**Negative check:** no tier has `may_claim_clinical_truth=true` in DAY32 contract.

**Evidence:** schema hash + contract validation report.

**Stop:** any automatic synthetic/weak → expert promotion rule exists.

**Pass:** authority transitions require new human/adjudication actions.

### STEP 2 — Bind annotation to DAY22 WindowIdentity

**Goal:** preserve temporal/protocol context.

**Input:** DAY22 `window_id`, sample boundaries and context boundaries.

**Action:** every annotation item requires `QC_WINDOW_WITH_CONTEXT`, stable `window_id` and surrounding context.

**Expected output:** no ad-hoc timestamps or random crop IDs.

**Verification:** negative random-crop fixture rejected.

**Negative check:** context bounds cannot begin after the target window start or end before target end.

**Pass:** item can be traced to the exact DAY22 annotation unit.

### STEP 3 — Define non-diagnostic rubric

**Goal:** let a human describe quality evidence without being forced into diagnosis.

**Input:** DAY21 taxonomy and DAY23–29 reason vocabulary.

**Action:** define artifact category, severity, supportability, artifact-vs-physiology, technical action and ordinal reviewer confidence.

**Expected output:** ambiguity is first-class (`BOTH_POSSIBLE`, `INSUFFICIENT_EVIDENCE`, `UNRESOLVED`).

**Negative check:** `PATHOLOGY`, `STROKE_SEVERITY`, diagnosis/treatment labels are not enum values.

### STEP 4 — Separate machine evidence from human judgment

**Goal:** prevent anchoring and evidence laundering.

**Input:** DAY21 `LabelingFunctionOutput` semantics.

**Action:** machine evidence records `lf_id`, reason, candidate label and WindowIdentity reference, with `ground_truth_claim=false`, `expert_label_claim=false`.

**Expected output:** machine evidence can be shown after independent initial judgment.

**Negative check:** weak-label ground-truth fixture rejected.

### STEP 5 — Define expert annotation creation

**Goal:** ensure expert tier actually requires an expert.

**Input:** reviewer class and new human action.

**Action:** only `CLINICAL_EXPERT` or `BIOMEDICAL_SIGNAL_EXPERT` may create `EXPERT_ANNOTATION` under this research schema.

**Expected output:** non-clinical reviewer stays `NON_CLINICAL_REVIEW` outside expert tier.

**Negative check:** changing `evidence_tier` string without human annotation is rejected.

### STEP 6 — Define adjudication semantics

**Goal:** prevent fake gold standard.

**Input:** independent expert annotations.

**Action:** require >=2 unique expert refs and explicit adjudication record/rationale.

**Expected output:** `ADJUDICATED_REFERENCE` is a multi-review research reference.

**Negative check:** one expert + machine label is rejected.

### STEP 7 — Design acquisition strata

**Goal:** prepare Active Learning without requiring a trained model.

**Input:** weak-label disagreement, QC states, distribution context.

**Action:** define representative-random, disagreement, domain novelty, high-risk false-allow, high-workflow-impact and artifact-vs-physiology ambiguity strata.

**Expected output:** each selected item will later record why it was selected.

**Negative check:** no diagnosis-based quota unless real verified metadata exists.

### STEP 8 — Define time-based budget

**Goal:** avoid arbitrary “300 windows” planning.

**Input:** future available review minutes and measured pilot seconds/item.

**Action:** document formula for capacity after pilot.

**Expected output:** no hard quota in acquisition YAML.

**Negative check:** absence of reviewer today does not block DAY32.

### STEP 9 — Define DAY33 data readiness

**Goal:** make next-day evidence availability explicit.

**Input:** synthetic fixture availability and public-source/license verification.

**Action:** choose among `RESEARCH_READY`, `SYNTHETIC_ONLY_READY_WITH_LIMITATIONS`, `BLOCKED_DATA_GOVERNANCE`.

**Current reference:** synthetic fixtures are user-reported from DAY23–28; public source/license not independently verified in builder → `SYNTHETIC_ONLY_READY_WITH_LIMITATIONS`.

**Negative check:** clinical data availability is not required to pass DAY32.

### STEP 10 — Create dry-run fixtures

**Goal:** prove schemas before real annotation.

**Input:** synthetic WindowIdentity-like metadata.

**Action:** create valid synthetic, weak, expert-schema-only and adjudication-schema-only fixtures plus attacks.

**Expected output:** 4 positive fixtures and 10 negative fixtures.

**Boundary:** expert/adjudication fixtures are schema fixtures, not actual expert evidence.

### STEP 11 — Automate contract validation

**Goal:** prevent documentation drift.

**Action:** cross-check YAML contract, acquisition policy, readiness states, JSON Schema and fixtures.

**Expected output:** deterministic PASS report.

**Negative check:** if any negative fixture is accepted by both schema and semantics, validation fails.

### STEP 12 — Integrate without overwriting shared Option-B artifacts

**Goal:** keep live source of truth safe.

**Action:** add DAY32 files side-by-side and only add continuation impact metadata.

**Negative check:** do not overwrite DAY21 registry, reason-code registry or shared requirements manifest.

### STEP 13 — Review and close DAY32

**Goal:** distinguish engineering completeness from expert/clinical validation.

**Action:** run contract validator, focused tests, optional DAY31 regression, artifact integrity and human peer review.

**Expected output:** engineering PASS with peer review separately `PENDING/APPROVED`.

**Allowed final engineering claim:** `ANNOTATION_READINESS_ENGINEERING_READY`.

## 19. Automated Validation

The release runner validates contract structure, positive/negative examples, evidence transitions and optional DAY31 focused/property regressions. It does **not** simulate a clinician and does not mark peer review approved.

## 20. Manual / Expert Review

DAY32 manual review is a protocol-quality review, not clinical annotation. Recommended roles: DSP engineer, data-governance reviewer, QA reviewer and human-factors reviewer. If a clinician happens to review the rubric, record that separately; DAY32 engineering pass must not depend on it.

## 21. Failure Injection / Negative Tests

Mandatory attacks include random crop, synthetic auto-promotion, non-clinical expert impersonation, single-reviewer adjudication, hidden context, weak-label ground-truth hijack, numeric probability-like reviewer confidence, direct identifier field, inconsistent context bounds and forced pathology label.

## 22. Traceability

DAY32 is traced primarily to ICR-002/003/004/012 and to upstream DAY21/22/30/31 contracts. No legacy clinical acceptance criterion is silently carried forward as if the partner still existed.

## 23. Acceptance Criteria

- Mandatory six outputs exist.
- Four evidence tiers are exact and non-automatic.
- WindowIdentity context is mandatory.
- Ambiguous artifact-vs-physiology states exist.
- No hard annotation quota.
- No clinical diagnosis label.
- Current DAY33 readiness is explicit.
- All positive fixtures accepted and negative fixtures rejected.
- No shared Option-B source-of-truth artifact overwritten.

## 24. Definition of Done

Engineering DoD is achieved when automated tests PASS, artifact hashes match, package hygiene passes and the protocol can be understood by a new reviewer without guessing evidence authority. Expert validation remains separate.

## 25. Stop / Block Conditions

- Binary artifact/pathology rubric with no ambiguity state.
- Synthetic pathology presented as real pathology.
- Weak label called ground truth.
- Contextless/random annotation crop accepted.
- Non-clinical reviewer accepted as expert evidence.
- One reviewer accepted as adjudication.
- Public dataset included without license/provenance decision.
- Confidential/PHI artifact included in handoff.

## 26. Known Limitations

No real expert annotation is included. No public dataset license is independently verified in this DAY32 builder. No clinical/site threshold or patient cohort evidence exists. The protocol has not been tested for clinician usability. These are expected limitations, not engineering failures.

## 27. Open Questions

Primary question for DAY33 is which public datasets can be legally and semantically admitted to the benchmark corpus. A secondary question is whether any qualified expert will later be available; if not, expert/adjudicated tiers remain unused and the project continues with synthetic known-truth + public external evidence.

## 28. Integration

Copy `repo_patch` into the live monorepo after collision review. Keep side-by-side versioning. Then run:

```bash
bash scripts/dev/run_day32_checks.sh
```

If upstream file locations differ in the live refactor, update imports/scripts deliberately; do not copy old upstream files from this handoff.

## 29. Git Workflow

Recommended:

```bash
git checkout -b feature/day32-annotation-readiness
git status --short
# copy reviewed repo_patch
git diff --check
bash scripts/dev/run_day32_checks.sh
git add clinical packages qa-validation scripts docs
git commit -m "day32: add research annotation readiness contracts"
```

## 30. Rollback

Rollback DAY32 by reverting only files listed in the integration manifest. Do not revert accepted DAY21–31 artifacts. Because DAY32 is mostly additive contracts/tests, rollback should not mutate raw data or runtime QC state.

## 31. Evidence / Provenance

Every fixture is `SCHEMA_FIXTURE` or synthetic research evidence. Builder validation results are not live-monorepo proof until rerun after integration. The current readiness status is intentionally conservative.

## 32. Closeout

Record automated results, peer-review status, any contract changes, public-data open questions and exact final status. Never close with `clinically validated`.

## 33. Handoff to DAY33

DAY33 receives:

- evidence-tier contract;
- research annotation item schema;
- acquisition strata;
- time-budget method;
- DAY33 readiness decision;
- dry-run fixtures.

DAY33 then builds a **Public + Synthetic Research Benchmark Corpus**, not a clinician-annotated hospital cohort.

## 34. Final Status Model

Highest engineering state available at DAY32:

```text
ENGINEERING_VALIDATION = PASS
ANNOTATION_READINESS = ENGINEERING_READY
EXPERT_VALIDATION = NOT_PERFORMED
CLINICAL_VALIDATION = NOT_PERFORMED
ACTIVE_LEARNING_SELECTION = NOT_RUNNING
LABEL_MODEL_TRAINED = false
DAY33_DATA_READINESS = SYNTHETIC_ONLY_READY_WITH_LIMITATIONS
FINAL_STATUS = READY_WITH_LIMITATIONS
```

Promotion to DAY33 requires DAY32 automated validation plus protocol peer review appropriate to the research project. It does not require a clinician or hospital dataset.

## 35. Evidence Authority Matrix

DAY32 cần một bảng quyền lực rõ để tránh việc cùng một JSON được hiểu khác nhau bởi từng engineer.

| Evidence tier | Ai/điều gì tạo ra | Được chứng minh | Không được chứng minh | Có thể tự promote? |
|---|---|---|---|---|
| `SYNTHETIC_KNOWN_TRUTH` | deterministic generator | transformation/injected fault đã được tạo đúng như manifest | pathology, clinical severity, site prevalence | Không |
| `WEAK_LABEL_CANDIDATE` | rule/detector | machine observation/candidate theo config/version | expert truth, diagnosis, calibrated probability | Không |
| `EXPERT_ANNOTATION` | qualified human review | opinion của reviewer có provenance | consensus/gold standard | Không |
| `ADJUDICATED_REFERENCE` | >=2 independent expert annotations + adjudication | research reference có multi-review provenance | clinical gold standard nếu chưa có governance riêng | Không |

Điểm quan trọng là **authority không phải accuracy**. Một synthetic fixture có thể có truth chắc chắn hơn một expert opinion đối với câu hỏi “generator đã inject gì?”, nhưng nó không có authority về patient physiology. Một expert annotation có authority về expert judgment nhưng không có nghĩa luôn đúng tuyệt đối. DAY32 giữ hai khái niệm này tách biệt.

## 36. Reviewer Qualification Contract

DAY32 không tạo hệ thống credentialing đầy đủ nhưng phải định nghĩa qualification boundary.

### `CLINICAL_EXPERT`

Reviewer có chuyên môn lâm sàng liên quan và được governance tương lai xác định. DAY32 không tự gán ai vào class này.

### `BIOMEDICAL_SIGNAL_EXPERT`

Reviewer có chuyên môn sEMG/DSP/biomedical signal đủ để đánh giá artifact/technical supportability trong research context. Class này vẫn **không tự tạo clinical truth**.

### `NON_CLINICAL_REVIEWER`

Engineer, QA, UX reviewer hoặc người dùng thử tool. Evidence của họ có thể hữu ích cho usability/workflow nhưng không được serialize dưới `EXPERT_ANNOTATION`.

**Stop condition:** nếu hệ thống chỉ dựa vào một boolean `is_expert=true` không provenance/role semantics, không promote DAY32.

## 37. Annotation Item Data-Minimization Contract

Một annotation item chỉ nên chứa dữ liệu cần thiết để review chất lượng tín hiệu:

- WindowIdentity;
- verified channel/muscle/side/protocol context nếu có;
- waveform core/context hoặc reference tới waveform service;
- machine evidence refs;
- evidence source class/license status;
- reviewer annotation fields;
- provenance.

Không nên chứa:

- patient name;
- MRN/hospital ID;
- address/phone/email;
- free-text note copied từ medical record;
- diagnosis fields chỉ để “làm context phong phú”;
- local absolute paths.

Trong independent portfolio mode, data minimization còn giúp public-release hygiene dễ hơn.

## 38. Machine Evidence Presentation Modes

DAY32 định nghĩa ba mode nhưng freeze default là `HIDDEN_UNTIL_INITIAL_JUDGMENT`.

### Mode A — HIDDEN_UNTIL_INITIAL_JUDGMENT

Reviewer thấy waveform/context trước. Sau khi lưu judgment ban đầu, tool có thể reveal reason codes/weak labels. Đây là mode ưu tiên khi muốn nghiên cứu disagreement mà giảm anchoring bias.

### Mode B — VISIBLE_WITH_DISCLOSURE

Machine evidence hiển thị ngay nhưng phải ghi rõ `RULE/WEAK LABEL — NOT GROUND TRUTH`. Mode này phù hợp demo assisted-review hoặc workflow efficiency, không phù hợp đo independent judgment.

### Mode C — HIDDEN

Không hiện machine evidence; hữu ích khi muốn blind review hoặc test human interpretation. Machine evidence vẫn có thể tồn tại trong backend provenance.

UI implementation tương lai phải record mode nào đã được dùng, vì annotation distribution có thể khác giữa blinded và assisted review.

## 39. Acquisition-Stratum Semantics

### Representative Random

Mục đích là chống selection bias. Random control không nhất thiết “healthy” hay “normal”; nó chỉ đại diện cho eligible pool theo sampling policy.

### Detector Disagreement

Không dùng count vote đơn giản. Disagreement có thể bao gồm:

- PASS vs FAIL;
- WARNING vs ABSTAIN;
- artifact family A vs B;
- QC aggregation PASS nhưng weak high-risk candidate tồn tại;
- multiple rules cùng flag nhưng supportability khác nhau.

### Domain Novelty

Dựa trên metadata/supportability context như protocol, layout, Fs, unit, session/day. DAY32 không tạo OOD probability.

### High-Risk False-Allow

Đây là những case machine policy có thể cho downstream tiếp tục nhưng có evidence đáng kiểm tra. Stratum này quan trọng hơn “uncertain score cao” khi chưa có model calibrated.

### High Workflow Impact

Ưu tiên item có thể dẫn tới remeasure/reprocess/review. Đây là product/workflow value, không phải clinical severity.

### Artifact-vs-Physiology Ambiguity

Stratum chuyên bảo vệ `Preserve Physiology`. Không cần pathology label thật để tạo synthetic stress, nhưng nếu dùng synthetic thì phải ghi rõ stress-only evidence.

## 40. Selection-Bias Logging Requirements

Mỗi future selected item nên lưu tối thiểu:

```text
selection_policy_version
selection_strata[]
selection_reason_codes[]
selection_rank_basis
pool_snapshot_id
pool_size_at_selection
selected_at
```

Nếu item được chọn vì rule disagreement, phải lưu rule IDs/versions. Nếu do domain novelty, phải lưu domain axes. Nếu random control, phải lưu seed/pool snapshot. Điều này cho phép DAY34/37 phân tích whether annotation sample itself is biased.

## 41. Time-Budget Worked Scenarios

### Scenario A — fast engineering review

- available time: 90 min;
- measured median: 30 sec/item;
- raw capacity: 180;
- effective review fraction measured/selected after pilot: 0.70;
- usable capacity: 126.

Con số 126 không phải target chuẩn; nó chỉ minh họa formula.

### Scenario B — difficult expert review

- available time: 120 min;
- median: 90 sec/item;
- effective fraction: 0.65;
- usable capacity: 52.

Nếu roadmap cố giữ quota 150 trong scenario này, reviewer sẽ vội hoặc bỏ rationale. Time-based policy tránh vấn đề đó.

## 42. DAY33 Readiness Decision Table

| Synthetic corpus | Public source | License/provenance | DAY33 decision |
|---|---|---|---|
| available | verified | verified | `RESEARCH_READY` |
| available | absent/not verified | not verified | `SYNTHETIC_ONLY_READY_WITH_LIMITATIONS` |
| absent | verified public | verified | `RESEARCH_READY` nếu public corpus đáp ứng technical needs |
| absent | unavailable | unavailable | `BLOCKED_DATA_GOVERNANCE` |
| available | candidate public | license unclear | synthetic-only; candidate public excluded |

Clinical data không xuất hiện như một precondition trong bảng này.

## 43. Negative-Test Threat Model

DAY32 coi evidence laundering như một security/safety problem. Threats:

1. **Enum laundering:** đổi `WEAK_LABEL_CANDIDATE` thành `EXPERT_ANNOTATION`.
2. **Role laundering:** non-clinical reviewer gắn class expert.
3. **Consensus laundering:** one reviewer + machine vote gọi adjudicated.
4. **Pathology laundering:** synthetic low amplitude gọi stroke.
5. **Context stripping:** export screenshot không WindowIdentity.
6. **Probability laundering:** ordinal confidence biến thành 0–1 score.
7. **Governance laundering:** public dataset license unknown nhưng vẫn vào corpus.
8. **Clinical-claim laundering:** research adjudication gọi “gold standard clinical”.

Test suite không thể bắt mọi câu chữ trong future UI, vì vậy peer review/claim audit vẫn bắt buộc ở release milestones.

## 44. Troubleshooting Runbook

### Validator báo positive fixture invalid

Kiểm tra schema version, `annotation_unit_type`, WindowIdentity regex, context bounds và tier-specific required blocks. Không sửa schema bằng cách nới `additionalProperties` chỉ để fixture pass.

### Negative fixture unexpectedly passes

Xác định invariant nằm ở JSON Schema hay semantic validator. Nếu invariant là cross-field authority transition, semantic validator có thể là đúng nơi. Add regression test trước khi sửa.

### Live repo dùng schema filename khác

Do Option-B side-by-side versioning, resolve live version deliberately. Không overwrite `qc-result`/`WindowIdentity` upstream. DAY32 chỉ cần semantic compatibility.

### Public dataset candidate chưa rõ license

Không tải vào managed corpus. Ghi `NOT_VERIFIED`, giữ DAY33 synthetic-only.

### Reviewer role chưa rõ

Không nâng lên expert tier. Record non-clinical review hoặc leave reviewer unavailable.

### Team muốn hiện AI pre-label để review nhanh

Cho phép `VISIBLE_WITH_DISCLOSURE` cho assisted workflow, nhưng nếu mục tiêu là independent annotation/disagreement study phải dùng hidden-until-initial-judgment và record presentation mode.

## 45. Adversarial Review Roles

### Junior engineer

Hỏi: Tôi có thể dùng synthetic fixture như example không? Có, nếu giữ evidence tier và claim boundary.

### Senior DSP engineer

Hỏi: Rubric có ép poor contact khi low amplitude không? Nếu có → reject design.

### Data governance reviewer

Hỏi: source/license/evidence class có được trace không? Direct identifiers có bị cấm không?

### QA reviewer

Hỏi: negative fixtures có thực sự test cross-field semantics hay chỉ JSON syntax?

### Human-factors reviewer

Hỏi: machine proposed label có gây anchoring? Context waveform có đủ không?

### Portfolio reviewer

Hỏi: tài liệu có khiến recruiter hiểu lầm rằng clinician đã annotate không? Nếu có → sửa trước public release.

## 46. Research Ethics / Claim Language Checklist

Allowed wording:

- annotation-readiness protocol;
- research annotation schema;
- synthetic known-truth fixtures;
- weak-label candidates;
- expert annotation tier supported by schema;
- adjudication policy defined;
- clinician validation not performed.

Forbidden wording without new evidence:

- clinician-approved rubric;
- hospital-validated annotation protocol;
- gold-standard clinical labels;
- stroke-vs-artifact validated;
- Vinmec annotation cohort;
- clinically validated Active Learning.

## 47. Reproducibility Requirements

DAY32 outputs are mostly contracts, so reproducibility means:

- exact schema/config versions;
- deterministic fixture IDs/hashes;
- validator result reproducible;
- no timestamps inside generated IDs;
- source-control review of contract changes;
- artifact manifest and SHA256SUMS;
- no cache artifacts.

Future annotations themselves may include event timestamps, but annotation identity should remain traceable to stable window/source refs.

## 48. Integration Test Matrix

| Case | Expected |
|---|---|
| DAY21 weak label + DAY22 valid window | valid weak-label annotation item |
| weak label GT claim true | reject |
| random crop | reject |
| expert tier + non-clinical reviewer | reject |
| adjudicated + one ref | reject |
| synthetic tier + human annotation | reject |
| context bounds inconsistent | reject |
| public source license unknown | allowed as candidate metadata only, not `RESEARCH_READY` |
| DAY30 FAIL annotated by reviewer | annotation may record opinion but cannot auto-unblock DAY31 |
| DAY31 BLOCKED | annotation layer cannot compute metric |

## 49. Day32-to-Day33 Contract

DAY33 must consume DAY32 without changing evidence authority. Its job is data governance/corpus construction. It may:

- admit public datasets after license/provenance verification;
- generate deterministic synthetic challenges;
- assign evidence source class;
- create benchmark development/locked splits.

DAY33 may not:

- create expert annotations from dataset labels unless label semantics truly are expert annotations and governance supports that claim;
- call task/gesture labels QC ground truth;
- call public pathological labels Vinmec/site evidence;
- unlock clinical claims.

## 50. Closure Decision

DAY32 is successful when the project can answer, for any future annotation record:

1. **What exact WindowIdentity was reviewed?**
2. **What evidence source class produced the waveform?**
3. **What evidence tier does the label have?**
4. **Who/what created it and under which version?**
5. **What can it legitimately support?**
6. **What can it not support?**
7. **Was machine evidence visible before judgment?**
8. **Can the record be replayed/audited without raw mutation?**

If any answer is ambiguous, annotation readiness is not complete.
