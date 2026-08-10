# DAY 20 — Real Data Contract Freeze & GATE B

> **DAY20 Engineering Execution Specification & Integration Runbook**  
> Phase 1 closure / M1 / Gate B  
> Engineering pack can be complete while evidence gate remains blocked.

## 0. Document Control

| Field | Value |
|---|---|
| Day | DAY20 |
| Task | Real Data Contract Freeze & GATE B |
| Phase | Phase 1 — Real Data Contract & Ingestion Hardening |
| Milestone | M1 — Real Data Contract Frozen |
| Gate | B |
| Gate outcomes | REAL_DATA_READY / BLOCKED_PRIVACY / BLOCKED_SCHEMA |
| Current isolated-pack gate | BLOCKED_PRIVACY |
| Training | false |
| Clinical claims | prohibited |
| Production code mandatory | No; contract/evidence/decision artifacts are primary |

## 1. Executive Intent

DAY20 không phải ngày “viết code cuối Phase 1”. Nó là ngày chuyển toàn bộ work DAY09–19 thành một **evidence-signed configuration baseline**. Parser chỉ được xem là nền đáng tin cho Phase 2 khi contract, live integration, privacy boundary và approved real/sample export đều có bằng chứng tương ứng. Nếu một trong các evidence bắt buộc thiếu, decision phải block ngay cả khi 100% synthetic tests xanh.

## 2. Why This Day Exists

Không có Gate B, nhóm dễ mắc lỗi phổ biến: synthetic fixture chạy tốt → coi site format đã verified; documentation privacy tồn tại → coi data class đã approved; DomainContext schema tồn tại → gọi OOD capability; event contract tồn tại → gọi Clinical Event Store; 16 Ultium sensors → gọi MFCV eligible. DAY20 ngăn các promotion không có evidence này.

## 3. Position in the 90-Day Critical Path

```text
DAY09-10 contracts
→ DAY11 provenance
→ DAY12 canonical/context
→ DAY13 validation
→ DAY14 ontology/layout
→ DAY15 property safety
→ DAY16-17 MR4 parsers
→ DAY18 optional Vicon
→ DAY19 unified ingestion/events
→ DAY20 contract freeze + Gate B
→ only after PASS: DAY21 QC taxonomy
```

## 4. Relationship With Previous Day

DAY19 tạo facade thống nhất, retry/idempotency, source lineage và minimum ingestion events. DAY20 **không mở rộng facade**; nó yêu cầu current live facade pass và freeze semantics. Nếu DAY19 current monorepo không được verify, GB-01 phải `NOT_VERIFIED`.

## 5. What Must Be True Before Starting

- DAY19 artifacts đã được tích hợp hoặc ít nhất available để review.
- Current repo không có unreviewed parser rewrite.
- Privacy evidence class được xác định trước khi mở real patient-derived export.
- Raw patient data không được commit.
- Training remains disabled.
- Gate A/Phase 1 source hierarchy vẫn hiệu lực.

Nếu các điều kiện này chưa đạt, vẫn có thể build DAY20 pack, nhưng không được pass Gate B.

## 6. Objectives

1. Freeze ingestion/data contracts v1.0.
2. Validate approved de-identified real/sample exports when available.
3. Freeze unresolved fields explicitly.
4. Freeze process correlation/event emission minimum.
5. Freeze DomainContext minimum for later distribution-support analysis.
6. Re-confirm property-safety invariants.
7. Map exact 25 existing requirements.
8. Produce formal Gate B decision from evidence.

## 7. Non-Goals / Explicitly Out of Scope

- Không viết QC detector.
- Không đặt clinical threshold.
- Không train model/SSL/shared embedding.
- Không implement OOD detector/reference distribution.
- Không implement persistent Clinical Event Store.
- Không enable MFCV.
- Không implement preprocessing/metrics.
- Không mở generic Vicon/mocap project.
- Không gọi public healthy data là site validation.

## 8. Source-of-Truth for This Day

1. SRS MotionLab current.
2. PRD MotionLab current.
3. Observed CSV architecture/approved real export evidence.
4. 90-Day Re-baselined Roadmap.
5. Technology Augmentation Plan as additive delta.
6. Integrated DAY09–19 artifacts/tests.
7. Assumption, always explicit.

## 9. Requirements Addressed Today

Roadmap shorthand `FR-001..025` is resolved to actual SRS IDs, not a fabricated continuous sequence. Denominator:

```text
FR: 16 = FR-001..010 + FR-020..025
NFR: 6 = NFR-001..004 + NFR-011 + NFR-012
AC: 3 = AC-01 + AC-02 + AC-09
TOTAL = 25
```

## 10. Inputs

- accepted/integrated outputs DAY19;
- DAY09–19 contracts/parsers/invariants;
- observed MR4/Vicon architecture;
- privacy/de-identification artifacts;
- approved de-identified source evidence, if site permits;
- Technology Augmentation contracts for DomainContext/process correlation.

## 11. Mandatory Outputs

```text
data-platform/contracts/noraxon/contract-freeze-v1.0.md
qa-validation/validation-reports/ingestion-real-data-validation-v1.0.md
docs/00-executive/gates/GATE-B-real-data-readiness.md
```

## 12. Supporting Outputs

```text
data-platform/contracts/gate-b-technology-freeze.v1.0.yaml
packages/common-schemas/json/gate-b-readiness.schema.json
qa-validation/evidence/day20-gate-b-evidence.yaml
qa-validation/evidence/day20-real-data-validation-ledger.template.yaml
qa-validation/traceability/day20-requirement-freeze-matrix.csv
qa-validation/automated-tests/governance/test_day20_gate_b.py
scripts/dev/evaluate_day20_gate_b.py
scripts/dev/run_day20_checks.sh
```

## 13. Target Repo Tree After This Day

```text
MyoLab-AI/
├── data-platform/contracts/noraxon/contract-freeze-v1.0.md
├── data-platform/contracts/gate-b-technology-freeze.v1.0.yaml
├── docs/00-executive/gates/GATE-B-real-data-readiness.md
├── packages/common-schemas/json/gate-b-readiness.schema.json
├── qa-validation/validation-reports/ingestion-real-data-validation-v1.0.md
├── qa-validation/evidence/day20-*.{yaml,json,md}
├── qa-validation/traceability/day20-requirement-freeze-matrix.csv
├── qa-validation/automated-tests/governance/test_day20_gate_b.py
└── scripts/dev/{evaluate,validate,check,run}_day20*
```

## 14. Data / Evidence Boundaries

**Synthetic:** engineering behavior only.  
**Vendor/observed architecture:** structure evidence, not site approval.  
**De-identified real/sample export:** can become `SITE_VERIFIED` only when governance-approved and reviewed.  
**Public healthy dataset:** research/regression only; cannot substitute for Vinmec site evidence.  
**Raw patient values:** never enter repository evidence bundle.

## 15. Safety & Governance Invariants

```text
raw immutable
unknown unit never inferred
parser/facade error fail closed
no silent crash
heterogeneous Fs supported
missing raw values preserved
unknown fields preserved
deterministic replay
no final-looking result on failure
no OOD model required at Gate B
MFCV remains optional/site-gated
```

## 16. Environment / Tooling Requirements

- Python >=3.11 recommended.
- `pytest`, `PyYAML`, `jsonschema` available in project environment.
- `uv` preferred when project uses `pyproject.toml`; runner falls back to Python.
- Git available for collision/diff review.
- Approved storage/access only for any patient-derived export.

## 17. Preflight Checklist

```bash
cd /path/to/MyoLab-AI
git status --short
git branch --show-current
python3 --version
command -v uv || true
test -f data-platform/contracts/noraxon/contract-freeze-v1.0.md || true
test -x scripts/dev/run_day19_checks.sh
```

Fail preflight if working tree contains unreviewed raw data or Day19 regression is unavailable in strict mode.

## 18. Detailed Execution Procedure

### STEP 0 — Preflight và branch

**Goal**  
Xác nhận working tree, Day19 runner, source hierarchy và training=false trước khi thay đổi artifact Gate B.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
git status --short; git branch --show-current; test -x scripts/dev/run_day19_checks.sh
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 1 — Chạy strict upstream regression

**Goal**  
Bảo vệ live DAY19 facade/parser bindings trước khi freeze contract.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
DAY20_STRICT_UPSTREAM=1 bash scripts/dev/run_day20_checks.sh  # lần đầu có thể block Gate, nhưng upstream test phải xanh
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 2 — Chốt evidence class và privacy boundary

**Goal**  
Xác định chính xác data class được phép dùng để Gate B validate; không dùng raw patient data khi governance chưa approve.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
review security-compliance/privacy/* and fill GB-02 only from approved evidence
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 3 — Validate approved MR4 single export

**Goal**  
Chạy production single parser trên approved de-identified source, ghi hash/shape/result nhưng không commit raw values.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
record result in day20-real-data-validation-ledger from live parser output
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 4 — Validate approved separated export

**Goal**  
Xác minh physical info.csv framing + signal/signal_2d + mixed Fs + source lineage.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
record directory/source hashes and approved site layout profile evidence
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 5 — Review optional Vicon context

**Goal**  
Xác minh minimum four-section contract; sync remains unknown unless measured.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
bash scripts/dev/run_day18_checks.sh
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 6 — Re-run property safety on live ingestion

**Goal**  
Chứng minh raw immutable, unknown unit no inference, no silent crash, fail closed sau integration.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
bash scripts/dev/run_day19_checks.sh
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 7 — Freeze process correlation/event semantics

**Goal**  
Kiểm event contract đủ cho later process mining nhưng không chứa PHI/raw payload.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
review process-correlation.schema.json + ingestion-event-emission-contract.v0.1.yaml
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 8 — Freeze DomainContext/OOD readiness semantics

**Goal**  
Khóa metadata axes và maturity METADATA_CONTRACT_ONLY; không yêu cầu OOD model.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
python3 scripts/dev/validate_day20_gate_b.py
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 9 — Freeze 25-requirement traceability

**Goal**  
Đảm bảo đúng existing SRS IDs, không phát minh FR-011..019.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
python3 scripts/dev/validate_day20_gate_b.py
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 10 — Peer/expert review

**Goal**  
Review evidence, source conflicts, privacy, event semantics, safety and no-overclaim.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
cp qa-validation/evidence/day20-peer-review.template.yaml <review-work-file>
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 11 — Evaluate Gate B

**Goal**  
Tính decision từ evidence thay vì lịch.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
python3 scripts/dev/evaluate_day20_gate_b.py --write-report qa-validation/evidence/day20-gate-b-evaluation.json
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.
### STEP 12 — Closeout / commit / handoff

**Goal**  
Chỉ khi REAL_DATA_READY mới handoff GO_FOR_DAY_21; block phải giữ blockers explicit.

**Input**  
Các artifact đã frozen trước DAY20 và current live repository state.

**Why**  
Gate B là phase boundary; lỗi ở đây sẽ biến assumption Phase 1 thành input mặc định cho QC Phase 2.

**Concepts used**  
Evidence grading, fail-closed, configuration baseline, source provenance, change control. Xem Learning Guide mục tương ứng.

**Action**  
Thực hiện đúng một đơn vị công việc của step; không đồng thời sửa production parser trừ khi phát hiện defect và mở change record riêng.

**Files**  
`data-platform/contracts/noraxon/contract-freeze-v1.0.md`, `qa-validation/evidence/day20-gate-b-evidence.yaml` và evidence artifact liên quan step.

**Implementation details**  
Không promote status bằng file existence. `SITE_VERIFIED` cần site/approved-source evidence; `LIVE_REPO_VERIFIED` cần current repository test log. Không đưa raw source values vào commit.

**Code/Command**
```bash
cd /path/to/MyoLab-AI
git diff --check; git status --short; git diff
```

**Expected Output**  
Một evidence state hoặc test result explicit; không có ambiguous “looks OK”.

**Verification**  
Kiểm hash/source reference, status enum, reviewer/evidence ref và deterministic rerun khi applicable.

**Negative Check**  
Nếu thiếu evidence, giữ `NOT_VERIFIED`; không điền `VERIFIED_*` để làm Gate xanh.

**Evidence Produced**  
Gate criterion/evidence ledger/review record tương ứng.

**Stop Condition**  
Privacy violation, source conflict, raw mutation, silent parser fallback hoặc final-looking failure state.

**Pass Condition**  
Step có evidence rõ và không làm yếu invariant Phase 1.


## 19. Automated Validation Strategy

DAY20 tests are governance/contract tests, not clinical performance tests. Required categories:

- **STATIC:** mandatory paths and forbidden artifacts.
- **SCHEMA:** Gate-B evidence JSON Schema.
- **CONTRACT:** exact allowed gate decisions and evidence statuses.
- **NEGATIVE:** privacy missing → BLOCKED_PRIVACY; schema missing → BLOCKED_SCHEMA.
- **POSITIVE TEST-ONLY:** all criteria + manual approval → REAL_DATA_READY.
- **TRACEABILITY:** exact 25 requirements.
- **REGRESSION:** strict call to DAY19; DAY19 calls relevant upstream.
- **SAFETY:** OOD model not required, training false, event store not falsely claimed.
- **EVIDENCE:** current pack cannot claim site validation.

## 20. Manual / Expert Review

Automated tests cannot verify whether site governance approval is genuine, whether source is sufficiently de-identified, whether `info.csv` profile really corresponds to current MotionLab configuration, or whether a newly observed field changes clinical semantics. Review must check evidence IDs, source hashes, privacy approval, parser logs, source conflicts and wording.

## 21. Failure Injection / Negative Tests

At minimum:

1. all engineering criteria pass but privacy `NOT_VERIFIED` → `BLOCKED_PRIVACY`;
2. privacy passes but separated physical layout missing → `BLOCKED_SCHEMA`;
3. all criteria pass but manual review pending → `BLOCKED_SCHEMA`;
4. missing OOD model alone must **not** block;
5. test fixture must be explicitly TEST_ONLY;
6. a criterion cannot pass using status outside its own `pass_statuses`.

## 22. Requirement Traceability

Machine-readable source is `day20-requirement-freeze-matrix.csv`. Validation must reject 24/26 rows and must reject invented FR-011..019.

## 23. Acceptance Criteria

- Mandatory outputs exist and reviewed.
- Every unresolved assumption explicit.
- 25/25 existing requirements mapped.
- Gate decision derived from evidence.
- Real export evidence and privacy evidence meet required grade before PASS.
- Property invariants preserved.
- Process correlation/event emission + DomainContext frozen.
- OOD model absence non-blocking.
- No raw patient data in repo/package.

## 24. Definition of Done

**Engineering DONE:** package/tests/checksums valid and current decision honestly computed.  
**Gate DONE/PASS:** evaluator returns `REAL_DATA_READY`.  
A DAY20 engineering deliverable may be complete while Gate B is blocked; this is an expected valid state.

## 25. Stop / Block Conditions

- privacy approval absent for used data class;
- actual single/separated structure contradicts frozen contract;
- live parser regression fails;
- raw mutated;
- unit inferred;
- failure returns final-looking state;
- source conflict silently reconciled;
- reviewer cannot trace evidence;
- any attempt to pass because calendar reached DAY20.

## 26. Known Limitations

Current isolated builder cannot inspect your live monorepo or approved MotionLab exports. It therefore cannot independently assign `LIVE_REPO_VERIFIED`/`SITE_VERIFIED`. OOD remains metadata-readiness only; Vicon sync and MFCV eligibility remain separate evidence questions.

## 27. Open Questions Carried Forward

See `day20-open-evidence-carry-forward.md`. The most important are privacy approval, live bindings, single real validation, separated physical `info.csv` framing, optional sync evidence and MFCV site eligibility.

## 28. Integration Into Main Repository

```bash
export PROJECT_ROOT=/path/to/MyoLab-AI
export PACK_ROOT=/path/to/DAY20_REAL_DATA_CONTRACT_FREEZE_GATE_B_HANDOFF

cd "$PROJECT_ROOT"
git status --short
git switch -c day20/real-data-contract-freeze-gate-b

cd "$PACK_ROOT/repo_patch"
find . -type f -print0 | while IFS= read -r -d '' f; do
  test -e "$PROJECT_ROOT/${f#./}" && echo "COLLISION ${f#./}"
done

rsync -avnc --ignore-existing "$PACK_ROOT/repo_patch/" "$PROJECT_ROOT/"
rsync -av --ignore-existing "$PACK_ROOT/repo_patch/" "$PROJECT_ROOT/"

cd "$PROJECT_ROOT"
DAY20_STRICT_UPSTREAM=1 bash scripts/dev/run_day20_checks.sh
```

Do not blind-overwrite an existing Gate-B evidence file; review collisions first.

## 29. Git Workflow

Prefer two commits:

```text
commit 1: DAY20 contract/evaluator/test artifacts
commit 2: actual site/live evidence updates + Gate decision
```

This separates engineering from evidence promotion.

## 30. Rollback Procedure

If Day20 artifacts cause an integration issue, revert only DAY20 paths/commit. Do not `git reset --hard` across unrelated work. A Gate decision rollback never deletes evidence; add a new decision/revision record.

## 31. Evidence & Provenance Capture

Record source hashes, tool versions, current commit, parser/config versions, privacy approval refs, opaque source IDs and reviewer. Do not store raw values. Gate decision JSON must be reproducible from evidence YAML.

## 32. Closeout Checklist

- [ ] strict upstream regression run
- [ ] mandatory docs reviewed
- [ ] 25/25 traceability
- [ ] privacy evidence graded
- [ ] single export evidence graded
- [ ] separated export evidence graded
- [ ] property safety reviewed
- [ ] event/privacy semantics reviewed
- [ ] OOD readiness correctly labelled
- [ ] manual review complete
- [ ] evaluator report generated
- [ ] `git diff --check` clean

## 33. DAY21 Handoff

Only `REAL_DATA_READY` hands Phase 2 a valid frozen ingestion baseline. DAY21 receives: frozen source/data contracts, explicit unknowns, stable reason/failure boundaries, DomainContext/process correlation minimum and safety invariants. DAY21 then works on QC taxonomy/reason codes, not ingestion rewrites.

## 34. Final Day Status Rules

```text
Gate B = REAL_DATA_READY
→ DAY20 status = GO_FOR_DAY_21

Gate B = BLOCKED_PRIVACY
→ DAY20 status = BLOCKED_WITH_EVIDENCE

Gate B = BLOCKED_SCHEMA
→ DAY20 status = BLOCKED_WITH_EVIDENCE
```

Never use `READY_WITH_LIMITATIONS` to bypass a critical Gate-B blocker.
