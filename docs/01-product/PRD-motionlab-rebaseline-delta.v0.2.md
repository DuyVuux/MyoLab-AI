# PRD MotionLab Re-baseline Delta v0.2

## 0. Document Control

| Field | Value |
|---|---|
| Program | MotionLab Data Intelligence & Automation Platform — Vinmec MotionLab × VSF |
| Artifact | `docs/01-product/PRD-motionlab-rebaseline-delta.v0.2.md` |
| Baseline being refined | PRD MotionLab Data Intelligence v0.1 — 07/08/2026 |
| Day / Gate | DAY08 / GATE A / M0 |
| Status | `PROPOSED_REQUIREMENTS_FREEZE` until Gate A = `REQUIREMENTS_READY` |
| Scope | Phase 0 synthesis only; no production implementation |
| Change control | Any scope/threshold/claim change after freeze requires decision record + requirement impact + version bump |

## 1. Purpose

Tài liệu này không thay thế PRD v0.1 bằng một sản phẩm mới. Nó ghi **delta và freeze semantics** sau Phase 0: workflow/time-motion design, early observation/baseline evidence boundary, artifact-vs-physiology taxonomy, privacy/de-identification design, evidence inventory/data-request package và legacy-asset disposition. Mục tiêu là đưa product framing sang một baseline đủ rõ để Phase 1 thiết kế data contract mà không phải tự đoán requirement.

`PROPOSED_REQUIREMENTS_FREEZE` không đồng nghĩa site validated. Freeze ở đây có nghĩa: product direction, safety boundary, requirement text và mapping được khóa ở mức đủ cho downstream design; mọi `UNKNOWN/TBD/NOT_VERIFIED/DISCOVERY_REQUIRED` vẫn phải hiển thị.

## 2. North Star — giữ nguyên

> **Giảm thời gian bác sĩ MotionLab phải trực tiếp xử lý dữ liệu, đồng thời tăng tính nhất quán và độ tin cậy của dữ liệu đủ điều kiện cho diễn giải lâm sàng.**

DAY08 không thay North Star thành “đạt accuracy cao” hoặc “xây classifier”. Model chỉ được dùng sau này nếu nó trực tiếp phục vụ toil reduction, quality, evidence hoặc exception review và có evidence phù hợp.

## 3. Product Operating Model — freeze ở mức thiết kế

```text
Machine:
ingest → validate → QC → versioned processing → eligibility → evidence → exception surfacing

Doctor/KTV:
review exceptions → override/reprocess/remeasure/inconclusive → approve → clinical interpretation
```

Quyền quyết định cuối của bác sĩ/KTV không được xóa khỏi workflow. `Draft technical analysis` không được trở thành final clinical conclusion nếu chưa có clinician approval.

## 4. P0 Success Definition v0.2

P0 thành công **không** được định nghĩa bằng một model metric duy nhất. Success phải được đo ở năm lớp.

### 4.1 Toil reduction

- đo `manual processing time / case` bằng protocol time-motion đã versioned;
- tách clinician hands-on, technician hands-on, waiting, system-active và remeasurement;
- so sánh pilot với **baseline đo thực tế** khi đủ evidence;
- `>=50%` chỉ là research target ban đầu, không phải commitment tại Gate A.

### 4.2 Quality supportability

- critical acquisition/data problems phải được surface với reason/evidence;
- low-quality hoặc unsupported data phải được block/abstain thay vì tạo output có vẻ chắc chắn;
- physiological variation/pathology không được tự động coi là artifact chỉ vì khác người khỏe.

### 4.3 Traceability

Mọi output chính downstream phải có khả năng truy vết tới source, window/channel khi applicable, processing/config/version, eligibility và reason/limitation.

### 4.4 Human review efficiency

Mục tiêu workflow là exception-first review: bác sĩ tập trung vào các trường hợp cần xem, không phải review lại toàn bộ pipeline một cách mù quáng. Đây là intended operating model; hiệu quả thực tế cần pilot evidence.

### 4.5 Failure safety

Parser/QC/rule/model failure phải fail closed. `Missing metric != 0`, `insufficient data != normal`, `MFCV unavailable != system failure`.

## 5. Phase 0 Evidence Synthesis

| Domain | Phase 0 result | Evidence interpretation at Gate A |
|---|---|---|
| Workflow/time-motion | measurement model + observation/baseline pathway designed | site workflow/baseline facts only when actual reviewed observations exist |
| QC semantics | artifact vs physiological variation taxonomy designed | taxonomy is design evidence; site thresholds are not frozen here |
| Privacy | data classification/de-identification/access design created | site policy/approval remains evidence-gated |
| Real-data access | evidence tiers + request package defined | request readiness does not equal data receipt |
| Legacy assets | disposition/regression strategy defined | historical benchmark performance is not site validation |
| Requirements | 57 FR + 12 NFR + 10 AC mapped at DESIGN | implementation/validation remains future work |

## 6. Scope Freeze

### 6.1 P0 — sEMG Data Processing & Quality Intelligence

In scope remains: MR4 single/separated ingestion; immutable raw/hash/provenance; metadata validation; session/channel/window QC; profile-specific versioned preprocessing; metric eligibility; RMS/MAV/MDF/MNF and conditional metrics; evidence bundle; raw-vs-processed review; clinician actions/audit; clinician approval gate.

### 6.2 P1 — Plantar Pressure Left/Right Auto-Correction

Remains a later decision track. Gate A does not implement pressure correction and does not expand it to fall-risk/diabetic-foot diagnosis.

### 6.3 Knee/ACL

Remains discovery-gated. `DR-K01..DR-K08` must be sufficiently completed before choosing a correction solution class. Gate A does not authorize Knee ML/model development.

### 6.4 MFCV

MFCV remains optional. Site eligibility is `NOT_VERIFIED` unless electrode geometry, IED, alignment, sampling/config and propagation-supporting evidence are explicitly verified. “16 sensors” is not eligibility evidence.

## 7. Product Principles Frozen for Downstream Design

1. QUALITY BEFORE INTELLIGENCE.
2. PRESERVE PHYSIOLOGY.
3. HUMAN FINAL AUTHORITY.
4. ABSTAIN OVER HALLUCINATE.
5. TRACEABLE BY DESIGN.
6. AUTOMATION OF TOIL FIRST.
7. MODALITY-NEUTRAL FOUNDATION.
8. FAIL CLOSED as system safety behavior from the SRS/roadmap.

## 8. KPI Semantics at Gate A

| KPI | Gate A interpretation |
|---|---|
| Manual processing time / case | baseline must be measured; team estimate is not baseline |
| Full-manual-review rate | baseline/pilot evidence pending |
| Re-measurement rate | observed/reviewed evidence required |
| QC critical-artifact recall | sensitivity-first concept; threshold/site reference not frozen at DAY08 |
| Doctor acceptance rate | future pilot metric |
| Abstention appropriateness | future validation metric with reason/evidence |
| Traceability completeness | design target 100% for primary outputs; implementation evidence later |

## 9. AC-10 Freeze Semantics

AC-10 remains:

> Pilot cho thấy giảm manual processing time so với baseline đo thực tế; target chính thức được chốt trước pilot.

DAY08 freezes this **requirement text**, not the numeric outcome. It is prohibited to convert the 50% research target into an approved pilot commitment solely because PRD mentioned it.

## 10. Data & Evidence Boundary

- raw patient data must not be committed to Git;
- public healthy datasets may support engineering regression/research but not Vinmec clinical-effectiveness claims;
- vendor sample can support format reasoning only within its evidence tier;
- missing governance/de-identification status blocks evidence promotion;
- source fact, observed fact, engineering design, inference and assumption must remain distinguishable.

## 11. Open Evidence Carried Forward

Gate A does not erase open questions. In particular, actual site workflow/time-motion evidence, privacy approval details, exact metadata completeness, pressure semantics, MFCV eligibility and Knee failure semantics remain governed by their planned discovery/validation days. A requirement can be frozen while supporting evidence remains `TBD` if the uncertainty is explicit and does not make downstream design unsafe.

## 12. Change Control After Gate A

After `REQUIREMENTS_READY`, any change to P0 scope, intended use, clinical claim, threshold policy, evidence interpretation or safety boundary must include:

1. decision record;
2. source/evidence that triggered the change;
3. affected requirement IDs;
4. affected artifacts/tests;
5. version bump;
6. reviewer/approval appropriate to the change;
7. migration/revalidation impact when applicable.

No lower-priority legacy document may silently override SRS/PRD.

## 13. Gate A Dependency

This document becomes an **effective freeze** only when `docs/00-executive/gates/GATE-A-requirements-readiness.md` concludes `REQUIREMENTS_READY` using reviewed evidence. Until then the status remains `PROPOSED_REQUIREMENTS_FREEZE`.

## 14. Explicit Non-Claims

DAY08 does not claim:

- clinical diagnosis/treatment effectiveness;
- autonomous use;
- universal generalization across pathologies/body types/protocols;
- MFCV site eligibility;
- Knee/ACL correction readiness;
- pressure diagnostic capability;
- measured >=50% manual-time reduction;
- real-data parser validity before Phase 1 contract/ingestion work.

## 15. Traceability

Machine-readable mapping is maintained in:

- `data-platform/contracts/requirements-freeze.v0.2.yaml`;
- `qa-validation/traceability/day08-requirement-freeze-matrix.csv`;
- `docs/03-architecture/SRS-traceability-baseline.v0.2.md`.

Gate decision is maintained separately so product text cannot self-approve its own readiness.
