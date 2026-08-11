# QC Annotation Protocol v0.2 — Independent Research Continuation

## 1. Purpose

Protocol này định nghĩa **cách một annotation item phải được trình bày và ghi nhận** trong MyoLab-AI sau khi dự án tổ chức dừng trước clinical-data validation. DAY32 là annotation-readiness engineering; nó không tạo expert labels và không tuyên bố clinician validation.

## 2. Evidence ladder

```text
SYNTHETIC_KNOWN_TRUTH
        │ new qualified human review only
        ▼
EXPERT_ANNOTATION
        │ at least two independent expert annotations + adjudication
        ▼
ADJUDICATED_REFERENCE

WEAK_LABEL_CANDIDATE
        │ new qualified human review only
        └──────────────────────────────► EXPERT_ANNOTATION
```

Không có mũi tên automatic. Một detector không thể trở thành expert. Một fixture không thể trở thành patient physiology. Một annotation của một reviewer không thể trở thành adjudicated reference.

## 3. Annotation unit

Mọi item phải dùng DAY22 `WindowIdentity` với `annotation_unit_type=QC_WINDOW_WITH_CONTEXT`. Reviewer phải có target window và surrounding context. Random crop không gắn WindowIdentity bị cấm vì có thể che giấu activation trước/sau và làm sai phân biệt artifact-vs-physiology.

## 4. Rubric

Reviewer đánh giá các dimension tách biệt:

1. **Artifact category:** no obvious artifact, missing/dropout, flatline, clipping suspected, baseline noise, power-line, low-frequency contamination, poor contact suspected, multiple artifacts, unresolved.
2. **Severity:** INFO / LOW / MODERATE / HIGH / CRITICAL / UNKNOWN.
3. **Supportability:** SUPPORTABLE / REVIEW_REQUIRED / BLOCKED / UNKNOWN / NOT_EVALUATED.
4. **Artifact-vs-physiology:** ARTIFACT_SUPPORTED / PHYSIOLOGY_POSSIBLE / BOTH_POSSIBLE / INSUFFICIENT_EVIDENCE / NOT_APPLICABLE.
5. **Technical action:** continue QC, flag review, request remeasurement, check electrode contact, check mains/earthing, verify protocol context, verify metadata, no automated action.
6. **Reviewer confidence:** ordinal LOW/MODERATE/HIGH/UNKNOWN. Đây không phải calibrated probability.

Không có trường chẩn đoán. Không có `stroke severity`, `neuropathy`, `muscle disease` hoặc treatment recommendation.

## 5. Preserve-physiology rule

Low amplitude, atypical morphology hoặc slow activation **không tự động** đồng nghĩa poor contact/motion artifact. Nếu acquisition evidence không đủ, reviewer dùng `PHYSIOLOGY_POSSIBLE`, `BOTH_POSSIBLE` hoặc `INSUFFICIENT_EVIDENCE` thay vì bị ép binary.

## 6. Machine evidence and anchoring bias

Weak-label evidence có thể được lưu cùng item để audit nhưng presentation mặc định `HIDDEN_UNTIL_INITIAL_JUDGMENT`. Reviewer nên ghi judgment ban đầu trước khi xem proposed machine label. Sau đó có thể reveal objective rule evidence để phân tích disagreement. Việc này giúp tránh biến annotation thành “approve AI suggestion”.

## 7. Source/evidence classes

- `SYNTHETIC_FIXTURE`: engineering fixture, clinical_evidence=false.
- `PUBLIC_EXTERNAL`: public research data với source/license manifest.
- `ORGANIZATIONAL_ENGINEERING`: engineering evidence từ giai đoạn tổ chức nếu được phép giữ và không confidential.
- `APPROVED_RESEARCH_DATA`: future independent data với governance phù hợp.

DAY32 không yêu cầu hoặc tạo `APPROVED_CLINICAL_DATA`.

## 8. Annotation workflow

1. Resolve WindowIdentity and source manifest.
2. Verify governance/evidence tier.
3. Render core + context waveform and verified metadata only.
4. Capture independent initial judgment.
5. Optionally reveal weak-label/objective evidence.
6. Capture annotation dimensions and rationale.
7. Validate schema and semantic guards.
8. Store immutable annotation event/reference; never modify raw signal.

## 9. Dry-run mode

Synthetic/public dry-run dùng để test schema, renderer, selection logic và reviewer ergonomics. Dry-run output must set `claim_scope=RESEARCH_ONLY` and cannot be promoted to expert evidence by renaming a file or changing one enum.

## 10. DAY32 completion

DAY32 engineering PASS không phụ thuộc clinician availability. Required output is a coherent protocol + schema + acquisition/budget policies + DAY33 data-readiness decision. Expert validation remains `NOT_PERFORMED`.
