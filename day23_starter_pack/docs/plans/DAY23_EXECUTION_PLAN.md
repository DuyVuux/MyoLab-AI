# DAY 23 — UC2 Đánh giá định lượng và Longitudinal Compatibility Gate

> **Mô hình thực hiện:** một người làm tuần tự Product/Clinical framing → Toán metric → Backend service → Frontend dashboard → QA/Safety.  
> **Điều kiện bắt đầu:** Day 22 đã pass, commit và tag.  
> **Phạm vi:** tạo contract và vertical slice UC2 bằng deterministic feature summaries; chưa khẳng định hiệu quả lâm sàng và chưa thay thế thang đánh giá chuẩn.

---

## 0. Kết quả cuối ngày

```text
Nhiều session cùng đối tượng
        ↓
Longitudinal Compatibility Gate
        ├── subject/side/muscles
        ├── protocol/version
        ├── gesture vocabulary
        ├── unit/sampling/channel map
        ├── preprocessing/feature version
        └── QC status
        ↓
UC2 Quantitative Metrics
        ├── gesture repertoire
        ├── repeatability CoV
        ├── symmetry ratio
        ├── co-contraction index
        ├── healthy-reference similarity
        └── fatigue/endurance change
        ↓
Assessment Dashboard + Accessible Tables
        ↓
Human review required
```

Nguyên tắc cứng:

```text
metric không đủ dữ liệu
→ not_available
→ không bịa số
```

```text
protocol/version/QC không tương thích
→ longitudinal conclusion blocked
```

---

# 1. Artifact bắt buộc

```text
packages/semg-core/semg_core/quantitative_metrics.py
packages/common-schemas/json/longitudinal-compatibility.v0.1.schema.json
packages/common-schemas/json/uc2-quantitative-assessment.v0.1.schema.json
services/api-server/src/schemas/uc2_schema.py
services/api-server/src/services/longitudinal_service.py
services/api-server/src/mock_api/day23_app.py
apps/web-portal/src/schemas/uc2-assessment.schema.ts
apps/web-portal/src/lib/uc2-assessment-client.ts
apps/web-portal/src/components/uc2/*
apps/web-portal/src/app/uc2/assessment/Day23UC2AssessmentPage.tsx
apps/web-portal/src/app/uc2/longitudinal/Day23UC2LongitudinalPage.tsx
```

---

# 2. Day 23 làm gì và không làm gì

## Làm

- Định nghĩa metric UC2 có công thức và version.
- Tạo status `computed | experimental | not_available | blocked`.
- Tạo compatibility gate trước longitudinal comparison.
- Tạo deterministic scenarios gồm positive và failure paths.
- Bảo tồn module UC2 cũ bằng adapter contract.
- Cung cấp chart đơn giản có table alternative.
- Kiểm thử baseline zero, bilateral missing, protocol mismatch, QC fail.

## Không làm

- Không gọi metric là “điểm phục hồi lâm sàng”.
- Không khẳng định tương quan Fugl-Meyer khi chưa có dữ liệu.
- Không so sánh session khác protocol rồi chỉ thêm cảnh báo nhỏ.
- Không coi symmetry 100% là bình thường phổ quát.
- Không chọn một CCI formula mà không version hóa.
- Không bịa healthy-reference score khi thiếu reference.
- Không dùng raw signal trong assessment API.

---

# 3. Phần cần học kỹ

## 3.1. Longitudinal comparison

Longitudinal không chỉ là “vẽ nhiều điểm theo thời gian”. Hai session phải đo cùng một construct.

Tối thiểu kiểm tra:

```text
same subject
same affected/reference side
same muscles
same protocol ID/version
same gesture vocabulary
same unit
compatible sampling rate
same channel mapping
same preprocessing version
same feature version
QC không fail
```

Nếu không, thay đổi có thể đến từ setup chứ không phải chức năng cơ.

## 3.2. Percent change

\[
\%\Delta=100\frac{x_{current}-x_{baseline}}{|x_{baseline}|}
\]

Ví dụ:

```text
baseline = 60 s
current  = 72 s
change   = 20%
```

Nếu baseline gần 0, không tính. Không dùng phép chia tạo số vô hạn.

## 3.3. Symmetry ratio

\[
Symmetry=100\frac{x_{affected}}{x_{reference}}
\]

Ví dụ:

```text
affected = 80
reference = 100
symmetry = 80%
```

Giới hạn:

- phụ thuộc normalization;
- phụ thuộc vị trí điện cực;
- không tự động đồng nghĩa với chức năng tốt/xấu;
- chỉ dùng khi hai bên cùng protocol và feature definition.

## 3.4. Coefficient of Variation — CoV

\[
CoV=100\frac{\sigma}{|\mu|}
\]

Dùng ký hiệu `CoV` để tránh nhầm với conduction velocity `CV`.

- CoV thấp: các repetition ít biến thiên hơn.
- Mean gần 0: CoV không ổn định, trả `not_available`.
- Window overlap hoặc số repetition ít có thể làm metric dễ bị hiểu quá mức.

## 3.5. Co-contraction Index candidate

\[
CCI=200\frac{\min(A,B)}{A+B}
\]

Với `A=20`, `B=30`:

\[
CCI=200\times\frac{20}{50}=80\%
\]

Có nhiều CCI definitions. Vì vậy output phải có:

```text
formulaVersion = cci-min-ratio-v0.1
validationStatus = not_validated
```

## 3.6. Cosine similarity

\[
cos(\theta)=\frac{a\cdot b}{\|a\|\|b\|}
\]

Nó đo hướng tương đồng của hai vector đặc trưng. Không đồng nghĩa:

```text
agreement
clinical equivalence
recovery
causality
```

Hai vector có cosine cao nhưng magnitude rất khác nhau.

## 3.7. Correlation khác agreement

Correlation cao cho thấy hai biến cùng tăng/giảm; không chứng minh chúng bằng nhau. Khi sau này đối chiếu thang lâm sàng, cần cân nhắc agreement, calibration và repeated-measures design, không chỉ Pearson correlation.

## 3.8. Missing data semantics

```text
not_available
= metric không tính được do thiếu dữ liệu cần thiết
```

```text
blocked
= dữ liệu tồn tại nhưng safety/compatibility gate không cho phép kết luận
```

Không dùng giá trị 0 để đại diện missing. `0` có thể là số đo thật.

---

# 4. Lịch thực hiện tuần tự

## Buổi sáng — Metric definitions và compatibility contract

### Bước 0 — Checkpoint — 08:00–08:15

```bash
git switch -c day23-uc2-quantitative
bash scripts/dev/run_day22_checks.sh
git status --short
```

### Bước 1 — Đọc proposal UC2 và UI hiện có — 08:15–08:45

Tách ba lớp:

```text
source-supported requirement
engineering inference
future clinical validation need
```

Ví dụ:

- Proposal hỗ trợ mục tiêu định lượng gesture/repeatability/similarity/CCI.
- Công thức cụ thể của “điểm phục hồi tổng hợp” chưa được proposal xác định.
- Không tự bổ sung composite score nếu chưa có validation plan.

### Bước 2 — Viết metric dictionary — 08:45–09:20

Mỗi metric có:

```text
metric ID
label tiếng Việt
formula
unit
input requirement
not-computable conditions
formula version
validation status
limitations
```

Output:

```text
docs/06-ai-signal-processing/day23-uc2-metric-definitions.md
```

### Bước 3 — Tính tay known answers — 09:20–09:50

Tự tính:

```text
percent change: 60 → 72 = 20%
symmetry: 80/100 = 80%
CoV: [10,10,10] = 0%
CCI: 20,30 = 80%
cosine([1,2,3],[1,2,3]) = 1
```

### Bước 4 — Implement pure metric functions — 09:50–10:35

File:

```text
packages/semg-core/semg_core/quantitative_metrics.py
```

Guardrails:

- finite inputs;
- no negative amplitude where invalid;
- baseline/reference near zero;
- minimum repetitions;
- vector length/norm.

Không import API hoặc UI.

### Bước 5 — Thiết kế SessionDescriptor — 10:35–11:00

Descriptor không chứa raw data; chỉ metadata/provenance cần cho compatibility.

```text
sessionId
subjectRef
affected/reference side
target muscles
protocol/version
gesture vocabulary version
unit/sampling rate
channel map version
preprocessing/feature version
QC status
```

### Bước 6 — Viết compatibility rules — 11:00–11:35

File:

```text
services/api-server/src/services/longitudinal_service.py
```

V0.1 dùng exact match cho version/config. Sau này nếu cho phép compatibility range, cần ADR rõ.

### Bước 7 — Viết JSON/Pydantic contracts — 11:35–12:00

Files:

```text
longitudinal-compatibility.v0.1.schema.json
uc2-quantitative-assessment.v0.1.schema.json
uc2_schema.py
```

Semantic invariants:

```text
blocked → conclusionAllowed=false
compatible → conclusionAllowed=true
not_available/blocked metric → value=null
```

---

## Buổi chiều — Service, API và UI

### Bước 8 — Xây deterministic scenarios — 13:00–13:25

```text
golden_uc2_longitudinal
uc2_protocol_incompatible
uc2_missing_baseline
uc2_qc_fail_session
uc2_bilateral_unavailable
```

Không dùng random để tạo metric cốt lõi.

### Bước 9 — Build assessment service — 13:25–14:05

Service:

1. tạo descriptors;
2. chạy compatibility;
3. nếu blocked, không tính longitudinal metrics;
4. nếu compatible, tính metric nào có input;
5. metric thiếu trả `not_available`;
6. gắn formula/source/limitations;
7. safety + review state.

### Bước 10 — API endpoints — 14:05–14:30

```text
POST /v1/uc2/assessments
GET  /v1/uc2/assessments/{assessment_id}
```

Đây là prototype endpoint. Khi tích hợp production, input phải là session IDs đã lưu, không phải scenario ID.

### Bước 11 — TypeScript contract/client — 14:30–15:00

Files:

```text
uc2-assessment.schema.ts
uc2-assessment-client.ts
```

Không duplicate metric definitions trong component.

### Bước 12 — KPI row — 15:00–15:30

KPI có:

- value hoặc `not_available`;
- unit;
- status;
- formula version;
- validation status.

Không chỉ hiện số lớn mà thiếu bối cảnh.

### Bước 13 — Compatibility table — 15:30–16:00

Hiển thị từng trường:

```text
match
mismatch
not_available
reason code
```

Nếu blocked, CTA đúng là:

```text
Xem session không tương thích
Chọn lại session
```

Không phải “vẫn tiếp tục”.

### Bước 14 — Panels metric — 16:00–16:35

```text
RepeatabilityPanel
SymmetryPanel
FatigueEndurancePanel
```

Panel phải giải thích limitation ngắn.

### Bước 15 — Accessible chart — 16:35–17:05

Mọi chart có:

- figcaption;
- aria-label;
- table dữ liệu;
- unit;
- source session labels.

Không dựa riêng vào màu teal/coral.

### Bước 16 — Assessment/Longitudinal pages — 17:05–17:30

Routes:

```text
/uc2/assessment/:sessionId
/uc2/longitudinal/:subjectRef
```

Dùng route fragment additive, không overwrite UC2 cũ.

---

## Cuối ngày — QA, safety và integration review

### Bước 17 — Metric tests — 17:30–17:50

Test known-answer và not-computable.

### Bước 18 — Compatibility/API tests — 17:50–18:15

- golden compatible;
- protocol mismatch blocked;
- QC fail blocked;
- missing baseline not_available;
- bilateral missing symmetry not_available.

### Bước 19 — Schema/TS strict — 18:15–18:35

```bash
tsc -p qa-validation/configs/day23_tsconfig.json
pytest -q qa-validation/automated-tests/test_day23_schemas.py
```

### Bước 20 — Clinical wording review — 18:35–18:50

Cấm:

```text
Bệnh nhân đã phục hồi 20%
Đủ điều kiện tăng tải
Chức năng tay bình thường 80%
```

Dùng:

```text
Trong protocol hiện tại, thời gian tới khi xuất hiện fatigue evidence tăng 20% so với baseline.
Kết quả cần được xem cùng đánh giá lâm sàng.
```

### Bước 21 — Checker — 19:15–19:35

```bash
bash scripts/dev/run_day23_checks.sh
```

### Bước 22 — Commit — 19:35–20:00

```bash
git add \
  packages/semg-core \
  packages/common-schemas \
  services/api-server \
  apps/web-portal \
  docs \
  qa-validation \
  scripts

git diff --staged --check
git commit -m "day23: implement uc2 quantitative metrics and longitudinal compatibility"
git tag day23-uc2-quantitative-v0.1
```

---

# 5. Scenario behavior

| Scenario | Compatibility | Metric behavior | UI |
|---|---|---|---|
| Golden | compatible | experimental/computed | Trend + table |
| Protocol mismatch | blocked | longitudinal summary blocked | reason table |
| Missing baseline | không đủ | percent change not_available | yêu cầu baseline |
| QC fail | blocked | không kết luận | remeasure/exclude |
| Bilateral unavailable | compatible cho metric khác | symmetry not_available | không giả reference |

---

# 6. Tích hợp với UC2 đã tồn tại

## 6.1. Bảo tồn module tốt

Giữ:

- endurance trend;
- symmetry;
- MDF/MNF;
- raw signal explorer;
- data table;
- accordion explanation.

Thay hard-coded data bằng adapter:

```typescript
const assessment = await client.get(assessmentId);
const symmetry = assessment.metrics.find(m => m.metricId === "symmetry_ratio");
```

## 6.2. P(mỏi) wording

Chỉ gọi probability khi model output đã calibration và contract ghi rõ. Nếu chưa:

```text
model support score
engineering confidence
technical evidence trend
```

## 6.3. Longitudinal selection

Trước khi vẽ trend:

```typescript
if (!assessment.compatibility.conclusionAllowed) {
  return <SessionCompatibilityTable result={assessment.compatibility} />;
}
```

Không tính trước rồi che chart bằng warning.

---

# 7. Definition of Done

- [ ] Pure metric functions có known-answer tests.
- [ ] Baseline/reference zero an toàn.
- [ ] CoV và CCI có formula version.
- [ ] Compatibility kiểm tra đầy đủ metadata/version/QC.
- [ ] Mismatch/QC fail block conclusion.
- [ ] Missing metric trả null + not_available.
- [ ] Metric có source sessions và limitations.
- [ ] UI có KPI status và compatibility table.
- [ ] Chart có table alternative.
- [ ] Human review state visible.
- [ ] Không clinical probability/conclusion tự động.
- [ ] Checker pass.

---

# 8. Bài tự kiểm tra

1. Tính percent change 60 → 72.
2. Vì sao baseline gần 0 không được chia?
3. Tính symmetry 80/100.
4. CoV khác CV/MFCV thế nào?
5. Tính CCI với 20 và 30.
6. Cosine similarity đo điều gì và không đo điều gì?
7. Correlation khác agreement thế nào?
8. Vì sao protocol mismatch phải block trend?
9. `not_available` khác 0 thế nào?
10. Vì sao UC2 metric chưa chứng minh phục hồi lâm sàng?

Đạt ít nhất 8/10.

---

# 9. Handoff sang Day 24

Sau Day 23, workflow đã có:

```text
Create Session
→ Import/Mapping/Calibration/QC
→ Analysis Runtime
→ UC1/UC2 Results
```

Day 24 hợp lý nhất:

```text
Human Review
→ Technical sign-off
→ Clinical sign-off
→ Feedback adjudication
→ Report preview
→ Draft/approved report states
```
