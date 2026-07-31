# DAY 32 — CLASSICAL BASELINE MODELING TRÊN 14-FEATURE CONTRACT

**Dự án:** MyoLab-AI — sEMG Clinical Intelligence  
**Ngày:** Day 32  
**Chế độ:** Single Operator · Public Dataset Engineering Baseline  
**Đầu vào:** Day 31 Feature Engineering Gate  
**Trạng thái đầu vào:** `GO_FOR_DAY32_SEPARATE_BASELINE_SMOKE`  
**Đầu ra mục tiêu:** baseline cổ điển riêng cho Mendeley và GRABMyo; không chọn model cuối  
**Ngôn ngữ:** Tiếng Việt

---

## 0. Kết luận điều hành

Day 32 là ngày đầu tiên được phép **chuẩn bị và chạy model fitting có kiểm soát**, nhưng chỉ sau khi một authorization riêng của Day 32 được phát hành dựa trên feature tables thật.

Câu hỏi Day 32 phải trả lời:

> Với cùng feature contract, cùng grouped validation và cùng metric contract, các họ mô hình linear generative, linear discriminative, max-margin và nonlinear tree khác nhau như thế nào trên từng dataset?

Day 32 không trả lời:

> Model tối ưu cuối cùng là gì?

Luồng đúng:

```text
Đóng hồ sơ Day 31
→ xác minh feature tables thật
→ khóa hashes và authorization Day 32
→ pivot matrix riêng theo dataset/view/feature arm
→ tạo grouped development folds
→ chạy 6 core models
→ kiểm tra core gate
→ chỉ sau đó mới chạy optional models
→ báo cáo theo dataset, arm, subject và class
```

Luồng bị cấm:

```text
Mendeley + GRABMyo
→ pooled matrix
→ random window split
→ global scaler
→ AutoML / huge search
→ chọn model theo sealed test
```

---

# 1. Phạm vi model

## 1.1. Core bắt buộc

| Model | ID | Vai trò |
|---|---|---|
| Dummy Majority | `dummy_majority` | Floor theo lớp đa số |
| Dummy Stratified | `dummy_stratified` | Random floor theo phân bố lớp |
| LDA Shrinkage | `lda_shrinkage` | Generative linear baseline chính |
| Logistic Regression | `logistic_regression` | Probabilistic linear baseline |
| Linear SVM | `linear_svm` | Max-margin linear baseline |
| Random Forest | `random_forest` | Nonlinear tree baseline |

Tất cả sáu model phải chạy trên cùng fold manifest. Không được loại model vì kết quả ban đầu không tốt.

## 1.2. Optional sau core gate

| Model | ID | Điều kiện |
|---|---|---|
| KNN | `knn` | Feature đã scale; compute budget đạt |
| QDA | `qda_regularized` | Rank/covariance gate đạt |
| RBF SVM | `rbf_svm` | Core hoàn tất; số mẫu phù hợp compute budget |
| Gradient Boosting | `gradient_boosting` | Core hoàn tất; không chạy search lớn |

## 1.3. Không dùng trong Day 32

```text
CNN
LSTM
Transformer
XGBoost/LightGBM search lớn
AutoML
Online learning
Domain adaptation
Fatigue classifier
Pooled cross-dataset model
```

---

# 2. Input thực tế và blocker phải xử lý đầu ngày

Theo báo cáo Day 31:

- 60/60 test Day 31 đạt;
- 52/52 regression Day 30 đạt;
- feature contract 14 đặc trưng đã khóa;
- evidence hiện là `portable_synthetic_validation`;
- chưa materialize feature matrix thật;
- `training_allowed=false`;
- `model_fitting_allowed=false`;
- `scaler_fitting_allowed=false`;
- `feature_matrix_pivot_allowed=false`;
- `day32_authorization_present=false`;
- evidence Day 31 còn untracked và commit chưa push.

Vì vậy, Day 32 **không bắt đầu bằng model.fit()**. Bắt đầu bằng đóng hồ sơ và authorization.

---

# 3. Dataset views và feature arms

## 3.1. Mendeley primary

```yaml
dataset_id: mendeley-4channel-hand-gesture-v2
dataset_view_id: mendeley_core4_primary_v1
channels: [CH1, CH2, CH3]
classes:
  - rest
  - hand_close
  - wrist_flexion
  - wrist_extension
```

Feature dimensions:

| Arm | Kích thước |
|---|---:|
| F-TD8 | 24 |
| F-SP6 | 18 |
| F-ALL14 | 42 |
| F-NO-MOMENTS12 | 36 |

CH4 chỉ là sensitivity experiment riêng, không thuộc primary result.

## 3.2. GRABMyo primary

```yaml
dataset_id: grabmyo-v1.1.0
dataset_view_id: grabmyo_project_subset_native28_v1
channels: F1-F16 + W1-W12
classes:
  - rest
  - hand_open
  - hand_close
  - wrist_flexion
  - wrist_extension
```

Feature dimensions:

| Arm | Kích thước |
|---|---:|
| F-TD8 | 224 |
| F-SP6 | 168 |
| F-ALL14 | 392 |
| F-NO-MOMENTS12 | 336 |

U1–U4 tiếp tục bị loại khỏi primary view.

## 3.3. Core feature arms Day 32

### Gate A — bắt buộc

```text
F-TD8
F-ALL14
```

Hai arm này bắt buộc cho cả sáu core models.

### Gate B — diagnostic

```text
F-SP6
```

Chạy sau Gate A để đánh giá spectral-only. Không dùng F-SP6 làm headline duy nhất.

### Sensitivity sau core

```text
F-NO-MOMENTS12
W250 variants
Mendeley CH4 sensitivity
4-class cross-source intersection
```

Cross-source intersection vẫn phải train hai model riêng; không pooled.

---

# 4. Validation contract

## 4.1. Sealed test tiếp tục đóng

Day 32 chỉ dùng development partitions được phép:

```text
train
validation
development_outer_fold
```

Không đọc:

```text
test
sealed_test
outer_test
```

## 4.2. Primary regime — cross-subject grouped development CV

### GRABMyo

```yaml
outer_cv:
  preferred_splits: 5
  group: subject_id
  splitter: StratifiedGroupKFold
  shuffle: true
  random_state: 3201

inner_cv:
  preferred_splits: 3
  group: subject_id
```

### Mendeley

Do smoke coverage hiện nhỏ hơn:

```yaml
outer_cv:
  preferred_splits: 3
  maximum_after_full_coverage: 5
  group: subject_id

inner_cv:
  preferred_splits: 2
  maximum_after_full_coverage: 3
```

Script phải chọn số fold lớn nhất có thể mà:

- không có subject overlap;
- mỗi fold có class coverage phù hợp;
- không phá atomic repetition/session;
- tối thiểu hai group trong train.

## 4.3. Secondary GRABMyo cross-day regime

Chỉ chạy sau cross-subject core gate:

```text
train day(s) → evaluate held-out day
```

Không được gọi cross-day drift là fatigue.

## 4.4. Split-before-windowing vẫn là luật gốc

Day 32 không tạo lại window. Nó dùng `window_id`, `subject_id`, `session_id`, `repetition_id` và `split_version` từ Day 30–31.

---

# 5. Matrix materialization và null policy

## 5.1. Long table → matrix

Long feature rows được pivot theo:

```text
row key:
dataset_id × dataset_view_id × window_id

columns:
channel_id × feature_id
```

Metadata không được đưa vào `X`:

```text
dataset_id
subject_id
session_id
day_id
record_id
repetition_id
window_id
source_file_sha256
```

Các trường này chỉ dùng cho grouping, provenance và reporting.

## 5.2. Expected dimensions

Fail closed nếu dimension khác contract:

```yaml
mendeley_core4_primary_v1:
  F-TD8: 24
  F-SP6: 18
  F-ALL14: 42

grabmyo_project_subset_native28_v1:
  F-TD8: 224
  F-SP6: 168
  F-ALL14: 392
```

## 5.3. NaN policy

Không impute `0`.

Primary Day 32:

1. window có critical QC flag → loại với reason code;
2. window có nonfinite feature → loại;
3. xuất exclusion report theo dataset/subject/class/feature;
4. block nếu exclusion mất toàn bộ class hoặc subject;
5. provisional warning nếu invalid-window ratio > 1%;
6. provisional block nếu > 5%, trừ khi có adjudication kỹ thuật.

Các ngưỡng 1%/5% là engineering defaults, không phải clinical thresholds.

## 5.4. Scaling

| Model | Scaling |
|---|---|
| Dummy | Không |
| LDA Shrinkage | `StandardScaler` trong pipeline |
| Logistic Regression | `StandardScaler` trong pipeline |
| Linear SVM | `StandardScaler` trong pipeline |
| Random Forest | Không |
| KNN | `StandardScaler` |
| QDA | `StandardScaler` |
| RBF SVM | `StandardScaler` |
| Gradient Boosting | Không |

Scaler chỉ fit trong inner-training fold. Mỗi dataset/view/arm có scaler độc lập.

---

# 6. Model contract

## 6.1. Core fixed smoke configurations

```yaml
dummy_majority:
  strategy: most_frequent

dummy_stratified:
  strategy: stratified
  random_state: 3201

lda_shrinkage:
  solver: lsqr
  shrinkage: auto

logistic_regression:
  solver: lbfgs
  class_weight: balanced
  max_iter: 2000
  C: 1.0

linear_svm:
  class_weight: balanced
  C: 1.0
  dual: auto

random_forest:
  n_estimators: 300
  class_weight: balanced_subsample
  max_features: sqrt
  random_state: 3201
  n_jobs: 1
```

Smoke config xác minh pipeline. Nó không phải hyperparameter winner.

## 6.2. Tiny controlled grids

Chỉ sau fixed smoke:

```yaml
logistic_regression:
  C: [0.1, 1.0, 10.0]

linear_svm:
  C: [0.1, 1.0, 10.0]

random_forest:
  max_depth: [null, 12]
  min_samples_leaf: [1, 5]
```

LDA shrinkage dùng `auto`; không search covariance method lớn trong Day 32.

## 6.3. Optional models

```yaml
knn:
  n_neighbors: [3, 5, 7, 11]
  weights: [uniform, distance]
  metric: euclidean

qda_regularized:
  reg_param: [0.01, 0.1, 0.3]

rbf_svm:
  C: [1.0, 10.0]
  gamma: [scale, 0.01]

gradient_boosting:
  n_estimators: [100, 200]
  learning_rate: [0.05, 0.1]
  max_depth: [2]
```

## 6.4. QDA gate

QDA dễ bất ổn khi \(p\) lớn hơn số mẫu/class. Chỉ chạy nếu:

```text
all folds have every class
no class has fewer than 2 samples
regularized QDA completes without non-finite output
covariance/rank diagnostics are recorded
```

QDA failure được ghi `NOT_ELIGIBLE_NUMERICAL`, không crash toàn pipeline.

## 6.5. Optional compute gate

RBF SVM và KNN có thể tốn thời gian/bộ nhớ trên GRABMyo. Chỉ chạy sau khi:

- core model run hoàn tất;
- feature matrix hash đã khóa;
- estimated fit size dưới budget;
- không dùng random window subsampling không có provenance.

---

# 7. Metric contract

## 7.1. Đơn vị đánh giá

Window prediction không phải headline.

```text
window predictions
→ aggregate theo repetition
→ tính metric theo subject
→ macro-average đều các subject
```

## 7.2. Metric chính

```text
subject_macro_repetition_macro_f1
```

Ý nghĩa: mỗi subject có trọng số ngang nhau, tránh subject có nhiều window thống trị kết quả.

## 7.3. Metric phụ

- repetition-level macro-F1;
- balanced accuracy;
- per-class precision;
- per-class recall;
- per-class F1;
- confusion matrix;
- worst-subject macro-F1;
- worst-class recall;
- fold mean/std;
- invalid-window ratio;
- fit time;
- prediction latency;
- model failure count.

## 7.4. Aggregation prediction

Ưu tiên:

1. mean class probability nếu `predict_proba`;
2. mean decision score nếu `decision_function`;
3. majority vote nếu chỉ có label.

Tie phải được xử lý deterministic theo class order đã version.

## 7.5. Uncertainty

- participant-cluster bootstrap 95%;
- paired bootstrap model differences dùng cùng subjects/folds;
- smoke baseline không dùng p-value để tuyên bố winner;
- không so sánh trực tiếp Mendeley 4-class macro-F1 với GRABMyo 5-class macro-F1 như cùng một task.

---

# 8. Thứ tự thực thi Day 32

## Bước 0 — Đóng hồ sơ Day 31

### Input

- commit `bd67d1a`;
- Day 31 evidence untracked;
- remote repository.

### Action

```bash
git status --short

git add \
  ai-core/configs/day31_* \
  ai-core/pipelines/day31_* \
  packages/semg-core/src/semg_core/features \
  data-platform/contracts/day31 \
  docs/05-data/day31 \
  docs/note/day31 \
  qa-validation/evidence/day31 \
  qa-validation/automated-tests \
  scripts

git diff --staged --check
git commit -m "day31: finalize 14-feature engineering evidence"
git tag day31-feature-engineering-v1.0
git push
git push --tags
```

### Output

```text
qa-validation/evidence/day32/day31-housekeeping.json
```

### Stop condition

Dừng nếu evidence không khớp commit hoặc working tree chứa raw data.

---

## Bước 1 — Regression Day 30–31

```bash
bash scripts/dev/run_day30_checks.sh
bash scripts/dev/run_day31_checks.sh
```

Output:

```text
qa-validation/evidence/day32/day32-input-regression.log
```

Dừng nếu regression fail.

---

## Bước 2 — Materialize feature tables thật

### Input

- train/validation window index;
- raw references trong Zone 2;
- Day 31 extractor;
- Day 31 feature contract;
- dataset views.

### Action

Chạy riêng:

```bash
python ai-core/pipelines/day31_extract_features.py \
  --dataset-view mendeley_core4_primary_v1 \
  --partitions train validation

python ai-core/pipelines/day31_extract_features.py \
  --dataset-view grabmyo_project_subset_native28_v1 \
  --partitions train validation
```

### Output

```text
ZONE 2/features/day31/
├── mendeley_core4_primary_v1/
└── grabmyo_project_subset_native28_v1/
```

Không materialize test.

---

## Bước 3 — Feature-table integrity gate

Kiểm:

- schema;
- feature version;
- 14 feature IDs;
- expected channels;
- duplicate rows;
- `window × channel × feature` completeness;
- nonfinite count;
- hashes;
- split version;
- class distribution;
- subject/group coverage.

Output:

```text
qa-validation/evidence/day32/
├── mendeley-feature-table-audit.json
├── grabmyo-feature-table-audit.json
└── day32-feature-input-gate.json
```

---

## Bước 4 — Pivot matrices riêng

```bash
python ai-core/pipelines/day32_materialize_matrix.py \
  --dataset-view mendeley_core4_primary_v1 \
  --feature-arm F-TD8

python ai-core/pipelines/day32_materialize_matrix.py \
  --dataset-view mendeley_core4_primary_v1 \
  --feature-arm F-ALL14

python ai-core/pipelines/day32_materialize_matrix.py \
  --dataset-view grabmyo_project_subset_native28_v1 \
  --feature-arm F-TD8

python ai-core/pipelines/day32_materialize_matrix.py \
  --dataset-view grabmyo_project_subset_native28_v1 \
  --feature-arm F-ALL14
```

Mỗi matrix cần:

```text
X.npz
y.npy
groups.npy
metadata.parquet
columns.json
matrix-manifest.json
```

Model artifacts và matrices thật nằm Zone 2, không commit.

---

## Bước 5 — Tạo fold manifest trước model

Fold manifest được tạo một lần cho mỗi dataset/view và tái sử dụng cho mọi model/arm.

Kiểm:

```text
train subjects ∩ validation subjects = ∅
repetition không chia đôi
class order giống nhau
fold hash ổn định
```

Output:

```text
qa-validation/evidence/day32/folds/
├── mendeley-subject-cv.v1.json
└── grabmyo-subject-cv.v1.json
```

---

## Bước 6 — Phát hành Day 32 authorization

Authorization chỉ được sinh khi:

```yaml
day31_commit_closed: true
day30_day31_regression_passed: true
real_feature_tables_present: true
feature_table_hashes_verified: true
matrix_dimensions_verified: true
fold_manifests_verified: true
test_set_opened: false
pooled_training_allowed: false
```

Authorization phải khóa:

- commit hash;
- feature-table hashes;
- matrix hashes;
- fold hashes;
- dataset view;
- feature arms;
- model allowlist;
- prohibited model list;
- expiry hoặc run scope.

---

## Bước 7 — Chạy core fixed smoke

Thứ tự:

```text
Dummy Majority
Dummy Stratified
LDA Shrinkage
Logistic Regression
Linear SVM
Random Forest
```

Cho mỗi dataset:

```text
F-TD8
F-ALL14
```

Không chạy optional trước khi tất cả core cells hoàn thành hoặc có failure record hợp lệ.

---

## Bước 8 — Core gate

Core gate PASS không yêu cầu model phải đạt một F1 cụ thể.

Nó yêu cầu:

- hai Dummy floors tồn tại;
- sáu core model có status;
- không leakage;
- mọi fold dùng cùng fold manifest;
- scaler nằm trong pipeline;
- repetition/subject metrics sinh được;
- failures có reason code;
- test signal rows read = 0;
- pooled rows = 0.

Trạng thái:

```text
CORE_GATE_PASS
CORE_GATE_PASS_WITH_MODEL_FAILURES
CORE_GATE_BLOCKED
```

`PASS_WITH_MODEL_FAILURES` cho phép optional chỉ khi failure là model-specific và đã giải thích.

---

## Bước 9 — Tiny grid trong inner CV

Chỉ chạy cho:

```text
Logistic Regression
Linear SVM
Random Forest
```

Không search lớn.

Selection metric trong inner CV:

```text
repetition_macro_f1
```

Outer development fold chỉ đánh giá, không tham gia tuning.

---

## Bước 10 — Diagnostic và optional

Thứ tự đề xuất:

1. F-SP6 với core models;
2. KNN;
3. QDA sau numerical gate;
4. RBF SVM sau compute gate;
5. Gradient Boosting;
6. F-NO-MOMENTS12;
7. W250 sensitivity;
8. Mendeley CH4 sensitivity;
9. separate 4-class intersection analysis.

---

## Bước 11 — Báo cáo

Không ghi:

```text
Random Forest là model tốt nhất để triển khai tại Vinmec.
```

Nên ghi:

```text
Trong development grouped CV trên public healthy dataset X,
model family A cho median subject-level macro-F1 cao hơn family B
trên feature arm Y, nhưng chưa được đánh giá trên sealed test,
Noraxon site data hoặc population lâm sàng.
```

---

# 9. Output repository

```text
MyoLab-AI/
├── ai-core/
│   ├── configs/
│   │   ├── day32_baseline_protocol.research.yaml
│   │   ├── day32_core_models.research.yaml
│   │   ├── day32_optional_models.research.yaml
│   │   ├── day32_validation_protocol.research.yaml
│   │   ├── day32_metrics_contract.research.yaml
│   │   ├── day32_compute_budget.research.yaml
│   │   └── day32_execution_authorization.template.yaml
│   ├── modeling/day32/
│   └── pipelines/
├── data-platform/contracts/day32/
├── docs/
│   ├── 06-ai-signal-processing/day32/
│   ├── note/day32/
│   └── plans/DAY32_EXECUTION_PLAN.md
├── packages/common-schemas/json/
├── qa-validation/
└── scripts/
```

Zone 2:

```text
myolab-ai-data/
├── features/day31/
├── matrices/day32/
├── models/day32/
└── predictions/day32/
```

---

# 10. Phần cần học kỹ

## 10.1. Generative và discriminative

LDA mô hình hóa \(p(x|y)\) và prior \(p(y)\). Logistic Regression mô hình hóa trực tiếp \(p(y|x)\). Linear SVM tối ưu margin, không mặc định tạo probability.

## 10.2. LDA

LDA giả định các class có covariance chung. Shrinkage giúp covariance ổn định khi số feature lớn hoặc tương quan cao.

## 10.3. Logistic Regression

Multiclass logistic dùng softmax. Regularization \(C\) nhỏ hơn nghĩa là regularization mạnh hơn.

## 10.4. SVM

Linear SVM tìm hyperplane có margin lớn. RBF SVM thêm kernel phi tuyến nhưng có rủi ro compute và overfit cao hơn.

## 10.5. Random Forest

Random Forest trung bình hóa nhiều cây được tạo từ bootstrap sample và feature subset. Nó không cần StandardScaler nhưng vẫn có thể học source/artifact shortcut.

## 10.6. KNN và curse of dimensionality

Trong 392 chiều, khoảng cách giữa các điểm có thể trở nên kém phân biệt. Vì vậy KNN là comparator, không phải mặc định mạnh.

## 10.7. QDA

QDA ước lượng covariance riêng mỗi class. Số tham số tăng nhanh theo số chiều, nên dễ singular với GRABMyo F-ALL14.

## 10.8. Macro-F1

Macro-F1 tính F1 riêng cho từng class rồi trung bình đều. Nó phù hợp hơn accuracy khi lớp mất cân bằng.

## 10.9. Nested grouped CV

Inner folds chọn hyperparameter. Outer development folds đánh giá lựa chọn đó. Subject grouping ngăn cùng người xuất hiện ở cả train và validation.

---

# 11. Acceptance criteria

```text
[ ] Day 31 evidence đã commit/tag/push
[ ] Day 30–31 regression PASS
[ ] Feature tables thật tồn tại
[ ] Feature hashes và matrix hashes đã khóa
[ ] Không test rows
[ ] Không pooled rows
[ ] Matrix dimensions đúng
[ ] Fold manifest không group overlap
[ ] Authorization Day 32 hợp lệ
[ ] Sáu core models có kết quả/status
[ ] Dummy floors tồn tại
[ ] Scaler fit trong pipeline
[ ] Metrics aggregate tới repetition/subject
[ ] Core gate được ghi
[ ] Optional chỉ chạy sau core gate
[ ] Không deep learning/AutoML/domain adaptation
[ ] Model registry state = research
[ ] Không claim Motion Lab/clinical performance
```

---

# 12. Handoff cuối Day 32

Các trạng thái hợp lệ:

```text
GO_FOR_DAY33_BASELINE_ERROR_ANALYSIS
GO_FOR_DAY33_WITH_MODEL_FAILURES
BLOCKED_WITH_EVIDENCE
```

Cờ cuối ngày:

```yaml
sealed_test_opened: false
pooled_training_executed: false
fatigue_classifier_trained: false
motionlab_transfer_verified: false
clinical_use_allowed: false
registry_state: research
```

Kết luận daily summary:

> Day 32 đã tạo classical engineering baselines riêng cho Mendeley và GRABMyo trên cùng feature, fold và metric contracts. Kết quả chỉ mô tả khác biệt giữa các model family trong development evaluation; chưa xác định model cuối, chưa mở sealed test và chưa có giá trị suy diễn cho Noraxon/Motion Lab hoặc bệnh nhân.
