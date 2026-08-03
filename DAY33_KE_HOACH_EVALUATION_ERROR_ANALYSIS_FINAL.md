# DAY 33 — EVALUATION VÀ ERROR ANALYSIS Ở CẤP REPETITION/SUBJECT

**Dự án:** MyoLab-AI  
**Ngày:** Day 33  
**Đầu vào:** prediction artifacts và fold manifests từ Day 32  
**Đơn vị đánh giá:** repetition và subject  
**Sealed test:** tiếp tục đóng  
**Dataset:** Mendeley và GRABMyo đánh giá riêng  
**Mục tiêu:** hiểu model sai ở đâu, với ai, ở gesture nào và có ổn định hay không

---

## 0. Kết luận điều hành

Day 33 không thêm model và không đổi hyperparameter. Nhiệm vụ là chuyển dự đoán ở cấp window thành bằng chứng đánh giá ở cấp repetition và subject, sau đó tạo failure registry có provenance.

Evidence Day 32 hiện tại ghi:

```yaml
scope: SYNTHETIC_TOOLING_SMOKE
real_data_rows_read: 0
real_fitting_executed: false
sealed_test_rows_read: 0
pooled_training_executed: false
```

Vì vậy Day 33 có hai chế độ:

### Mode A — Tooling validation

- dùng synthetic prediction fixture;
- kiểm aggregation, metrics, bootstrap, failure taxonomy;
- không tạo benchmark Mendeley/GRABMyo;
- trạng thái: `TOOLING_READY_REAL_EVALUATION_BLOCKED`.

### Mode B — Real development evaluation

Chỉ chạy khi có prediction rows thật từ development outer folds, kèm:

```text
run manifest
fold manifest
matrix manifest/hash
model config/hash
feature arm
dataset view
Day 32 authorization
```

Không mở sealed test.

---

## 1. Câu hỏi Day 33 phải trả lời

1. Repetition nào sai?
2. Subject nào có hiệu năng thấp?
3. Confusion pair nào lặp lại?
4. Window trong cùng repetition có đồng thuận không?
5. Có high-confidence error không?
6. GRABMyo có day/session degradation không?
7. F-TD8 và F-ALL14 khác nhau ở failure profile nào?
8. LDA, Logistic, Linear SVM và Random Forest khác nhau ở class/subject nào?
9. Model trung bình cao hơn có worst-subject tệ hơn không?
10. Optional model có tạo giá trị hay chỉ tăng complexity?

---

## 2. Nguyên tắc bất biến

```text
[1] Không dùng window-level accuracy làm headline.
[2] Không mở sealed test.
[3] Không pooled Mendeley + GRABMyo.
[4] Không xếp hạng trực tiếp Mendeley 4 lớp với GRABMyo 5 lớp.
[5] Không gọi cross-day degradation là fatigue.
[6] Không dùng synthetic F1 làm kết quả nghiên cứu.
[7] Không xóa failure cases để làm metric đẹp hơn.
[8] Không thay model/hyperparameter trong Day 33.
[9] Không biến SVM decision score thành probability.
[10] Không chọn model triển khai cuối từ một metric trung bình.
```

---

## 3. Prediction contract

Mỗi row tương ứng một window:

```text
dataset_id
dataset_view_id
run_id
model_id
feature_arm
outer_fold
subject_id
day_id
session_id
repetition_id
record_id
window_id
y_true
y_pred
split_name
score_type
class_order_json
class_scores_json
qc_flags_json
source_matrix_sha256
fold_manifest_sha256
model_config_sha256
```

### `score_type`

```text
probability
decision_function
label_only
```

**Probability:** vector hữu hạn, không âm, tổng xấp xỉ 1.  
**Decision function:** chỉ dùng argmax/margin; không gọi là probability.  
**Label only:** deterministic majority vote; không tạo confidence giả.

### Partition hợp lệ

```text
validation
development_outer_validation
```

Bị chặn:

```text
test
sealed_test
outer_test
```

---

## 4. Aggregation window → repetition

### Path 1 — Mean probability

\[
\bar p_{r,c}=\frac{1}{W_r}\sum_{w=1}^{W_r}p_{w,c}
\]

\[
\hat y_r=\arg\max_c\bar p_{r,c}
\]

- confidence = probability lớn nhất;
- margin = top-1 trừ top-2.

### Path 2 — Mean decision score

\[
\bar s_{r,c}=\frac{1}{W_r}\sum_{w=1}^{W_r}s_{w,c}
\]

Không diễn giải là xác suất.

### Path 3 — Majority vote

\[
\hat y_r=\operatorname{mode}(\hat y_{r,1},...,\hat y_{r,W})
\]

Tie giải deterministic theo `class_order`.

### Window disagreement

\[
D_r=1-\frac{\max_c n_{r,c}}{W_r}
\]

```yaml
warning: 0.30
high: 0.45
```

Đây là engineering review trigger, không phải clinical threshold.

---

## 5. Metric contract

### Primary

```text
subject_macro_repetition_macro_f1
```

Quy trình:

```text
window predictions
→ repetition prediction
→ macro-F1 riêng từng subject
→ trung bình đều giữa subjects
```

### Repetition-level

- macro-F1;
- balanced accuracy;
- per-class precision/recall/F1;
- confusion matrix;
- số repetition;
- invalid/excluded repetition.

### Subject-level

Mỗi subject:

```text
repetition_count
class_coverage
macro_f1
balanced_accuracy
per_class_recall
error_count
high_disagreement_count
high_confidence_error_count
```

Summary:

- mean;
- median;
- std;
- p10;
- minimum;
- maximum;
- worst subject;
- bottom quartile subjects.

### Fold stability

- mean/std theo outer fold;
- minimum/maximum fold;
- subject/class coverage;
- model failure count.

---

## 6. Bootstrap và so sánh model

### Subject-cluster bootstrap

Không bootstrap window.

Mỗi iteration:

1. sample subject IDs với replacement;
2. giữ toàn bộ repetition của subject;
3. tính primary metric;
4. lưu metric.

```yaml
smoke_iterations: 500
full_iterations: 2000
random_state: 3301
confidence_interval: percentile_95
```

### Paired model comparison

Chỉ hợp lệ nếu hai run có:

- cùng dataset view;
- cùng feature arm;
- cùng fold manifest;
- cùng subject set;
- cùng repetition set.

Báo:

```text
mean delta
95% paired bootstrap CI
proportion(delta > 0)
```

Không gọi winner khi CI chứa 0.

---

## 7. Failure taxonomy

### Repetition-level

| Code | Ý nghĩa |
|---|---|
| `MISCLASSIFIED_REPETITION` | Repetition sai |
| `HIGH_CONFIDENCE_ERROR` | Sai với probability ≥ 0.80 |
| `LOW_MARGIN_ERROR` | Sai và top-2 margin thấp |
| `HIGH_WINDOW_DISAGREEMENT` | Window không đồng thuận |
| `SYSTEMATIC_CLASS_CONFUSION` | Thuộc confusion pair phổ biến |
| `QC_ASSOCIATED_ERROR` | Lỗi đi cùng QC flag |
| `INSUFFICIENT_WINDOWS` | Thiếu window |
| `MISSING_SCORE_VECTOR` | Thiếu score vector |
| `LABEL_INCONSISTENCY` | y_true không nhất quán |
| `DUPLICATE_WINDOW_PREDICTION` | Window lặp |

### Subject-level

| Code | Ý nghĩa |
|---|---|
| `SUBJECT_PERFORMANCE_COLLAPSE` | Macro-F1 rất thấp |
| `SUBJECT_CLASS_COLLAPSE` | Recall một class bằng 0 |
| `SUBJECT_HIGH_VARIANCE` | Bất ổn theo day/session |
| `SUBJECT_LOW_COVERAGE` | Thiếu class/repetition |
| `SESSION_SPECIFIC_DEGRADATION` | Một session giảm |
| `DAY_SPECIFIC_DEGRADATION` | Một day giảm |
| `MODEL_SPECIFIC_FAILURE` | Chỉ một model lỗi |
| `FEATURE_ARM_SPECIFIC_FAILURE` | Chỉ một arm lỗi |

`HIGH_CONFIDENCE_ERROR` chỉ áp dụng cho probability đã validate.

---

## 8. Failure case registry

```text
case_id
dataset_id
dataset_view_id
run_id
model_id
feature_arm
outer_fold
subject_id
day_id
session_id
repetition_id
y_true
y_pred
reason_codes
probability_confidence
decision_margin
window_disagreement
window_count
qc_flags
source_matrix_sha256
fold_manifest_sha256
review_status
review_note
```

Review status:

```text
UNREVIEWED
REVIEWED_EXPLAINED
REVIEWED_DATA_ISSUE
REVIEWED_MODEL_ISSUE
REVIEWED_PROTOCOL_ISSUE
REVIEWED_UNKNOWN
```

Không commit raw signal. Full registry ở Zone 2; repo chỉ giữ summary và hashes.

---

## 9. GRABMyo cross-day analysis

Báo theo:

```text
model × feature_arm × day/session
macro_f1
balanced_accuracy
per_class_recall
subject_count
repetition_count
```

Hợp lệ:

> Development performance giảm ở day/session X.

Không hợp lệ:

> Subject mỏi hơn ở ngày X.

---

## 10. Các bước thực thi

### Bước 0 — Đóng hồ sơ Day 32

**Input:** commit/tag Day 32 và evidence.  
**Output:** `day32-input-ledger.json`.

```bash
git status --short
git log -1 --oneline
git tag --points-at HEAD
```

Dừng nếu evidence không khớp commit.

### Bước 1 — Regression

```bash
bash scripts/dev/run_day31_checks.sh
bash scripts/dev/run_day32_checks.sh
```

Dừng nếu fail.

### Bước 2 — Prediction inventory

Tìm:

```text
ZONE 2/predictions/day32/
├── mendeley_core4_primary_v1/
└── grabmyo_project_subset_native28_v1/
```

Mỗi run phải có prediction table, run manifest, model config, fold manifest và matrix manifest.

Không có real predictions:

```text
TOOLING_READY_REAL_EVALUATION_BLOCKED
```

### Bước 3 — Prediction gate

Kiểm:

- một dataset/run;
- không test rows;
- unique window;
- y_true nhất quán theo repetition;
- class order đúng;
- score vector đúng;
- không nonfinite;
- hashes khớp.

### Bước 4 — Aggregate repetition

Output:

```text
repetition-predictions.parquet
aggregation-audit.json
duplicate-window-report.csv
label-consistency-report.csv
```

### Bước 5 — Repetition metrics

Output:

```text
repetition-metrics.json
per-class-metrics.csv
confusion-matrix.csv
```

### Bước 6 — Subject metrics

Output:

```text
subject-metrics.csv
subject-summary.json
worst-subjects.csv
subject-class-recall.csv
```

### Bước 7 — Bootstrap CI

Output:

```text
bootstrap-primary-metric.json
bootstrap-distribution.npz
```

NPZ ở Zone 2.

### Bước 8 — Failure extraction

Output:

```text
failure-cases.csv
failure-summary.json
top-confusion-pairs.csv
high-confidence-errors.csv
high-disagreement-errors.csv
qc-associated-errors.csv
```

### Bước 9 — Cross-day GRABMyo

Output:

```text
grabmyo-day-metrics.csv
grabmyo-subject-day-matrix.csv
grabmyo-day-degradation-cases.csv
```

### Bước 10 — Pairwise comparison

Predeclared:

```text
LDA vs Logistic
LDA vs Linear SVM
LDA vs Random Forest
Logistic vs Linear SVM
Logistic vs Random Forest
Linear SVM vs Random Forest
F-TD8 vs F-ALL14 trong cùng model
```

### Bước 11 — Render report

Report gồm:

1. scope;
2. provenance;
3. coverage;
4. repetition metrics;
5. subject metrics;
6. per-class/confusion;
7. bootstrap CI;
8. failure registry;
9. cross-day;
10. limitations;
11. handoff.

---

## 11. Cấu trúc tích hợp

```text
MyoLab-AI/
├── ai-core/
│   ├── configs/day33_*.yaml
│   ├── evaluation/day33/
│   └── pipelines/day33_*.py
├── data-platform/contracts/day33/
├── docs/
│   ├── 07-evaluation/day33/
│   ├── note/day33/
│   └── plans/DAY33_EXECUTION_PLAN.md
├── packages/common-schemas/json/
├── qa-validation/
└── scripts/
```

Zone 2:

```text
myolab-ai-data/
├── predictions/day32/
└── evaluation/day33/
    ├── repetition-predictions/
    ├── subject-metrics/
    ├── bootstrap/
    └── failure-registry/
```

---

## 12. Phần cần học kỹ

1. Confusion matrix: row=true, column=predicted.
2. Macro-F1 và balanced accuracy.
3. Dữ liệu phân cấp: window → repetition → subject.
4. Cluster bootstrap theo subject.
5. Confidence khác calibration.
6. Decision score khác probability.
7. Paired comparison.
8. Worst-subject analysis.
9. Error taxonomy và provenance.
10. Multiple-comparison discipline.

---

## 13. Acceptance criteria

```text
[ ] Day 32 evidence/commit khóa
[ ] Real/synthetic mode khai báo đúng
[ ] Không test rows
[ ] Không pooled rows
[ ] Prediction schema pass
[ ] Repetition aggregation deterministic
[ ] Probability validation trước confidence analysis
[ ] Repetition metrics đủ
[ ] Subject metrics đủ
[ ] Primary metric từ subject-level
[ ] Per-class/confusion đủ
[ ] Bootstrap theo subject
[ ] Failure registry có provenance
[ ] High-confidence error chỉ cho probability
[ ] Cross-day không fatigue inference
[ ] Pairwise comparison paired
[ ] Synthetic result không thành benchmark
[ ] Không đổi model/hyperparameter
```

---

## 14. Readiness cuối ngày

```text
TOOLING_READY_REAL_EVALUATION_BLOCKED
BLOCKED_WITH_EVIDENCE
GO_FOR_DAY34_ROBUSTNESS_CALIBRATION
GO_FOR_DAY34_WITH_KNOWN_FAILURES
```

Cờ bắt buộc:

```yaml
sealed_test_opened: false
pooled_evaluation_executed: false
fatigue_inference_allowed: false
clinical_use_allowed: false
motionlab_transfer_verified: false
registry_state: research
```

> Day 33 chuyển prediction cửa sổ thành metrics cấp repetition/subject, định lượng uncertainty bằng subject-cluster bootstrap và tạo failure registry. Kết quả vẫn là development evaluation riêng từng public dataset, chưa mở sealed test và chưa chứng minh chuyển giao sang Noraxon/Motion Lab.
