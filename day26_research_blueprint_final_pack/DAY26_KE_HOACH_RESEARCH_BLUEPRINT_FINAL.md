# DAY 26 — Khóa Experiment Blueprint cho Core AI sEMG Clinical Intelligence

> **Phiên bản:** v2.0 — research-grounded, post-Day25 addendum  
> **Mô hình thực hiện:** một người, làm tuần tự; hoàn thành bước trước mới sang bước sau  
> **Điều kiện bắt đầu:** Day 25 đã hoàn thành, checker PASS, các quyết định Noraxon-output uncertainty đã được cô lập sau adapter và đã commit  
> **Trạng thái bắt buộc trong toàn bộ Day 26:** `trainingAllowed=false`, `execution_state=NOT_RUN`  
> **Kết quả hợp lệ cuối ngày:** Experiment Blueprint đầy đủ, test set tiếp tục sealed, không có model binary và không có metric giả

---

## 0. Mục tiêu và ranh giới

Day 26 chuyển các kết quả deep research thành một **hợp đồng thí nghiệm có thể kiểm thử bằng code**. Ngày này không tìm “model tốt nhất” và không chạy training. Nó khóa trước:

```text
Task contracts
→ preprocessing/windowing candidates
→ feature groups
→ classical model ladder
→ grouped/nested validation
→ personalization arms
→ fatigue-context/abstention experiments
→ metrics/calibration/coverage
→ experiment tracking/model registry/reproducibility
→ red-team audit
→ readiness gate
```

### Không được thực hiện

```text
Không gọi .fit() trên dữ liệu thật/public dataset.
Không tuning hyperparameter.
Không mở outer/sealed test.
Không báo accuracy/F1/Brier/ECE đã chạy.
Không chọn model winner.
Không gọi raw SVM/KNN score là probability.
Không biến Task B thành hard fatigue diagnosis mặc định.
Không kích hoạt MFCV khi site eligibility chưa xác minh.
Không dùng public healthy data để claim Vinmec/stroke performance.
Không mở lại dataset inventory và audit Noraxon tổng quát của Day 25.
```

### Trạng thái cuối ngày đúng

```yaml
blueprint_valid: true
day27_dataset_execution_allowed: true
day29_training_preparation_allowed: true
day29_training_execution_allowed: false
test_set_sealed: true
all_result_fields: NOT_RUN
motionlab_site_adapter_status: BLOCKED_EXTERNAL
clinical_claims_allowed: false
```

---

## 1. Nguồn đầu vào bắt buộc

Day 26 sử dụng 13 artifact nghiên cứu/contract đã cung cấp:

1. Research Protocol & Governance Framework.
2. Feature Engineering Review.
3. Classical Model Candidate Review.
4. Validation and Leakage Review.
5. Personalization & Adaptation Strategy.
6. Fatigue-induced Distribution Shift Blueprint.
7. Metrics, Calibration & Abstention.
8. Reproducibility, Model Governance & Deployment Constraints.
9. `evaluation_regimes.research.yaml`.
10. Experiment Tracking Specification.
11. Gesture Model Evaluation Plan.
12. Model Registry Specification.
13. Reproducible Training Policy.

### Cách dùng nguồn

| Nhóm nguồn | Quyết định lấy làm SSOT |
|---|---|
| Protocol | Scope locks, 8 workstreams, evidence taxonomy, stop rules |
| Feature review | Sparse 4–16 channel features, window grid, normalization/selection hygiene |
| Model review | Minimum baseline set, optional comparators, inner-CV search spaces |
| Validation review | Hierarchy, group keys, split-first/window-later, test seal |
| Personalization | P0–P4, P1 few-shot là MVP default research path, P4 No-Go |
| Fatigue review | Task B là context/supportability; Architecture 3 ưu tiên; E-fatigue-0…4 |
| Metrics review | Subject-macro repetition-level Macro F1, participant bootstrap, calibration/coverage |
| Governance specs | Hybrid manifest+MLflow, registry states, environment/seed/serialization controls |

Mọi kết luận mới phải mang một trong các trạng thái:

```text
OFFICIAL_VERIFIED
PEER_REVIEWED_VERIFIED
REPOSITORY_VERIFIED
SITE_VERIFIED
PROJECT_LOCKED
INFERRED
NOT_VERIFIED
CONFLICTING
```

---

## 2. Kết quả bàn giao bắt buộc

```text
docs/research/day26/
├── 00-research-protocol.md
├── 00-search-strategy.md
├── 00-evidence-schema.csv
├── 00-paper-appraisal-template.csv
├── 00-decision-ledger.md
├── 01-preprocessing-and-windowing-policy.md
├── 02-feature-engineering-review.md
├── 03-classical-model-candidate-review.md
├── 04-validation-and-leakage-review.md
├── 05-personalization-and-adaptation-strategy.md
├── 06-fatigue-distribution-shift-blueprint.md
├── 07-task-c-target-and-metric-framework.md
├── 08-metrics-calibration-abstention.md
├── 09-reproducibility-and-governance.md
├── 10-master-experiment-blueprint.md
├── 11-open-questions-and-dependencies.md
├── 12-red-team-audit-findings.md
├── 13-day26-readiness-gate.md
├── day26-source-traceability.csv
└── day26-final-manifest.json

ai-core/configs/
├── task_contracts.research.yaml
├── feature_groups.research.yaml
├── model_ladder.research.yaml
├── evaluation_regimes.research.yaml
├── personalization_strategies.research.yaml
├── fatigue_experiments.research.yaml
├── experiment_matrix.draft.yaml
├── training_authorization.research.yaml
├── model_registry_states.research.yaml
└── abstention_reason_registry.v0.1.yaml

scripts/dev/
scripts/ml/
qa-validation/
packages/common-schemas/json/
```

---

# PHẦN A — KIẾN THỨC PHẢI HỌC TRƯỚC KHI SỬA CONFIG

## 3. Data hierarchy và leakage

Hierarchy chuẩn:

```text
subject
└── day
    └── session
        └── trial/repetition
            └── segment
                └── window
                    └── sample
```

Quy tắc:

```text
split-first
→ segment-second
→ window-third
```

Không được:

```text
tạo toàn bộ overlapping windows
→ random split windows
```

Vì các windows cùng repetition/session có tương quan rất cao và có thể làm model nhớ subject/session thay vì học gesture.

### Bạn cần hiểu kỹ

- `window` là unit xử lý, không phải unit generalization.
- `repetition` là prediction unit chính cho Task A.
- `subject` là inference/bootstrap unit chính.
- outer fold chỉ đánh giá; inner fold mới chọn scaler, feature, model, calibration và threshold.

---

## 4. Feature engineering

### Sparse-channel baseline

```text
F0 — Amplitude sanity:
RMS, MAV

F1 — Sparse classical core:
RMS, MAV, STD, WL, ZC, SSC, AR(4)

F2 — Frequency extension:
F1 + MDF, MNF, spectral entropy, relative band power

F3 — Fatigue-context extension:
F2 + RMS/MDF/MNF trends + elapsed-time context + QC/context fields

F4 — Conditional inter-channel:
activation ratios, correlations, antagonist-pair metrics
```

Không trộn vào baseline sparse khi chưa đủ geometry:

```text
2D spatial maps
motor-unit decomposition
propagation vectors
MFCV-dependent features
HD-sEMG grid moments
```

### Window grid

| Window | Vai trò |
|---:|---|
| 150 ms | Task A low-latency candidate |
| 200 ms | Task A primary candidate |
| 250 ms | Task A primary candidate |
| 500 ms | Task B/C spectral-context candidate |
| 1000 ms | Task B/C stress-test, không phải realtime default |

Increment/overlap là biến thí nghiệm riêng, không được chọn sau khi xem outer test.

### Toán cần nắm

RMS:

\[
RMS=\sqrt{\frac{1}{N}\sum_{n=1}^{N}x[n]^2}
\]

MAV:

\[
MAV=\frac{1}{N}\sum_{n=1}^{N}|x[n]|
\]

MNF:

\[
MNF=\frac{\sum_f fP(f)}{\sum_fP(f)}
\]

MDF là tần số chia tổng power thành hai phần bằng nhau. Hiểu rằng MDF/MNF phụ thuộc duration, force, task và cách ước lượng PSD; chúng không phải fatigue biomarker độc lập tuyệt đối.

---

## 5. Classical model ladder

### Minimum baseline set

```text
Dummy majority
Dummy stratified
LDA
Logistic Regression
Linear SVM
Random Forest
```

### Optional comparator set

```text
QDA
KNN
RBF SVM
Gradient Boosting
```

Không chọn KNN chỉ vì một paper báo F1 cao. Không chọn deep learning trước khi classical ladder được chạy đúng grouped/nested protocol.

### Những điểm phải hiểu

- Logistic Regression: boundary tuyến tính, cần scaling, dễ giải thích.
- LDA: shared covariance, mạnh với dữ liệu nhỏ-vừa, personalization nhanh.
- Linear SVM: raw margin không phải probability.
- Random Forest: nonlinear comparator; probability thường cần calibration.
- KNN: fit rẻ nhưng inference/memory tăng theo tập train và rất nhạy scaling.
- QDA: per-class covariance dễ bất ổn khi số mẫu mỗi lớp nhỏ.

---

## 6. Metrics, calibration và abstention

Primary metric được khóa:

```text
subject_macro_repetition_macro_f1
```

Quy trình:

```text
window scores
→ repetition prediction
→ Macro F1 từng subject
→ trung bình không trọng số giữa subjects
```

Balanced Accuracy là secondary bắt buộc để audit macro recall.

Participant bootstrap:

```text
resample subjects with replacement
→ giữ nguyên toàn bộ sessions/repetitions của subject
→ tính lại metric
```

Không bootstrap windows như iid samples.

### Probability semantics

Chỉ gọi output là `calibrated_class_probability` khi:

- calibrator fit trên dữ liệu tách khỏi classifier-fit data hoặc cross-fitted;
- method được chọn trong grouped inner validation;
- outer test không tham gia chọn method;
- Brier + reliability diagnostics được báo;
- phạm vi population/device/protocol được ghi rõ.

### Selective prediction

Luôn báo cùng nhau:

```text
coverage
+ selective accuracy/risk
+ abstention reasons
+ class-conditional coverage
+ unsafe prediction rate
```

Không báo “accuracy sau loại mẫu khó” mà bỏ coverage.

---

## 7. Reproducibility và governance

Day 26 khóa:

```text
File manifest có SHA-256 = governance SSOT
MLflow local = search/UI convenience
CPU single-thread = reference reproducibility profile
root seed → named child seeds
outer test sealed
model registry có human review
```

Registry states:

```text
draft
→ research
→ candidate
→ validated-for-engineering
→ pilot-candidate
```

Kèm `rejected`, `archived`. Không có trạng thái `clinical-validated` trong phạm vi hiện tại.

---

# PHẦN B — KẾ HOẠCH THỰC HIỆN TUẦN TỰ

## Step 0 — 08:00–08:20 — Preflight Day 25 và tạo branch

### Input

- Day 25 commit/tag.
- Day 25 readiness JSON.
- External-dependency register.

### Thực hiện

```bash
git status --short
git checkout -b day26/model-experiment-blueprint
bash scripts/dev/run_day25_research_checks.sh
```

### Output

```yaml
day25_regression: PASS
working_tree_before_day26: CLEAN
trainingAllowed: false
```

### Fail khi

- Day 25 regression fail.
- Noraxon site status bị đổi từ `NOT_VERIFIED` thành verified mà không có evidence.
- `motionlab_training_allowed=true`.

---

## Step 1 — 08:20–08:50 — Đăng ký và hash toàn bộ nguồn Day 26

### Input

13 file nghiên cứu/contract.

### Thực hiện

```bash
python scripts/ml/generate_hash_ledger.py \
  --root docs/research/day26 \
  --output qa-validation/evidence/day26-source-hash-ledger.json
```

### Output

- `day26-source-traceability.csv`.
- `day26-source-hash-ledger.json`.
- Mỗi claim/decision biết nguồn nào hỗ trợ.

### Acceptance

- Không thiếu source nào.
- Hash không rỗng.
- Source copy không bị sửa trong ngày nếu không tạo revision mới.

---

## Step 2 — 08:50–09:30 — Khóa protocol, taxonomy bằng chứng và stop rules

### Input

`00-research-protocol.md`.

### Thực hiện

Hoàn thiện:

```text
00-search-strategy.md
00-evidence-schema.csv
00-paper-appraisal-template.csv
00-decision-ledger.md
```

### Output

- 8 workstream questions.
- Dependency graph.
- Source hierarchy.
- Critical flaw flags.
- Quy tắc paper incomparable.

### Acceptance

- `trainingAllowed=false` xuất hiện trong protocol/config.
- Random-window split bị cấm.
- Không paper score nào được dùng như expected project performance.

---

## Step 3 — 09:30–10:00 — Khóa Task A/B/C contracts

### Input

- Day 25 label/metric taxonomies.
- Day 26 protocol.

### Thực hiện

Tạo `task_contracts.research.yaml`:

```yaml
TaskA:
  target_type: multiclass_gesture
  prediction_unit: repetition
TaskB:
  target_type: context_supportability
  hard_fatigue_classifier_default: false
TaskC:
  target_type: metric_engine
  classifier_required: false
```

### Output

Ba lane không dùng chung target, metric hoặc claim.

### Acceptance

- Task B không chứa `fatigue_diagnosis=true`.
- Task C không bị ép thành classifier.
- MFCV là optional và `NOT_VERIFIED` cho site.

---

## Step 4 — 10:00–10:50 — Khóa preprocessing, windowing và feature groups

### Input

- Feature Engineering Review.
- DSP core Day 5–12.

### Thực hiện

1. Map feature hiện có vào F0–F4.
2. Ghi `implemented`, `planned`, `conditional`, `excluded`.
3. Khóa window grid 150/200/250/500/1000 ms.
4. Khóa normalization eligibility.
5. Khóa feature-selection rule: inner fold only.

### Output

```text
01-preprocessing-and-windowing-policy.md
feature_groups.research.yaml
```

### Acceptance

- Không có HD-only/MFCV feature trong sparse baseline.
- Scaler/selector không fit global.
- Window được sinh sau split.
- Feature order là compatibility field.

---

## Step 5 — 10:50–11:40 — Khóa model ladder và search-space contract

### Input

Classical Model Candidate Review.

### Thực hiện

Tạo `model_ladder.research.yaml` với:

- minimum baseline set;
- optional comparators;
- scaling requirements;
- score semantics;
- inner-CV search spaces;
- failure modes;
- personalization suitability.

### Output

- Model ladder machine-readable.
- Model-card templates.

### Acceptance

- Dummy baselines bắt buộc.
- LDA/LR/Linear SVM/RF nằm trong core set.
- `LinearSVM.raw_score_semantics=decision_score`.
- Không model nào có `winner=true`.

---

## Step 6 — 13:00–14:10 — Khóa validation regimes và leakage controls

### Input

- Validation Review.
- Day 25 subject/session hierarchy.
- `evaluation_regimes.research.yaml`.

### Thực hiện

Khóa:

```text
within-session sanity          → debug only
cross-subject zero-shot        → primary population benchmark
cross-session                  → deployment realism
cross-day                      → deployment realism
personalized new-subject       → separate personalization regime
electrode remove-and-replace   → mandatory stress test
fatigue-stratified             → Task B robustness audit
unsupported/unknown            → mandatory abstention regime
```

### Output

- Evaluation contract.
- Leakage-prevention plan.
- Test-seal template.

### Acceptance

- Outer group keys đúng theo regime.
- Atomic seal unit ít nhất là trial/repetition.
- Target calibration subset tách locked target test.
- Outer test không chọn feature/calibrator/threshold.

---

## Step 7 — 14:10–14:50 — Khóa personalization strategy

### Input

Personalization & Adaptation Strategy.

### Thực hiện

Khóa P0–P4:

```text
P0 normalization-only        → mandatory baseline/fallback
P1 few-shot calibration      → MVP default research path
P2 prototype adaptation      → later candidate
P3 domain adaptation         → research only
P4 incremental learning      → No-Go for MVP
```

P1 engineering grid:

```text
2 reps/gesture → minimum arm
3 reps/gesture → default arm
5 reps/gesture → saturation stress-test
```

### Output

`personalization_strategies.research.yaml`.

### Acceptance

- Calibration subset không nằm trong target test.
- Không online learning từ feedback chưa adjudicate.
- Báo calibration duration/failure/retention.

---

## Step 8 — 14:50–15:35 — Khóa fatigue-context architecture và experiments

### Input

Fatigue Distribution Shift Review.

### Thực hiện

Khóa kiến trúc:

```text
Gesture model độc lập
+ fatigue-context engine
→ abstention/recalibration recommendation
```

Khóa E-fatigue-0…4:

- E0: no fatigue adjustment baseline.
- E1: fatigue features inside gesture predictor — conditional comparator.
- E2: post-hoc confidence adjustment.
- E3: supportability/abstention engine — priority.
- E4: governed recalibration — research arm, không auto-learning.

### Output

`fatigue_experiments.research.yaml`.

### Acceptance

- Không dùng MDF/MNF vừa dựng label vừa làm predictor mà không có circularity flag.
- MFCV missing không block basic sEMG.
- Fatigue không được trình bày như diagnosis.

---

## Step 9 — 15:35–16:25 — Khóa metrics, calibration và selective prediction

### Input

- Metrics review.
- Gesture Model Evaluation Plan.

### Thực hiện

Khóa:

```text
Primary = subject_macro_repetition_macro_f1
CI = participant-cluster bootstrap 95%
Balanced Accuracy = mandatory secondary
Calibration = grouped inner cross-fitted only
Threshold = grouped inner validation only
Coverage + selective risk = luôn báo cùng
Unsafe prediction denominator = mandatory-abstain units
```

### Output

- Evaluation config.
- Abstention reason registry.
- Evaluation summary schema.
- Metric utility functions chưa chạy trên dữ liệu thật.

### Acceptance

- Tất cả result field là `NOT_RUN`/null.
- Raw score không có tên probability.
- `ABSTAIN` xuất hiện trong confusion-matrix contract.

---

## Step 10 — 16:25–17:05 — Tạo experiment matrix draft

### Input

Task, feature, model, validation, personalization và fatigue configs.

### Thực hiện

Tạo matrix tối thiểu:

```text
E-A00…E-A11  — Task A classical baseline/feature/window arms
E-P00…E-P04  — personalization arms
E-F00…E-F04  — fatigue-context arms
E-C00…E-C03  — Task C deterministic metric studies
```

Mỗi row phải có:

```text
experiment_id
hypothesis
feature_group
model_family
regime
personalization
fatigue_architecture
primary_metric
result_status=NOT_RUN
outer_test_opened=false
```

### Output

- `experiment_matrix.draft.yaml`.
- CSV/JSON render trong `qa-validation/evidence/`.

### Acceptance

- Không có metric value.
- Không có selected winner.
- Mỗi experiment trả lời một hypothesis rõ ràng.
- Task A/B/C không bị trộn target.

---

## Step 11 — 17:05–17:50 — Khóa reproducibility, tracking và registry

### Input

- Reproducibility/Governance Review.
- Tracking, Registry và Training Policy.

### Thực hiện

1. File manifest + hash là SSOT.
2. MLflow local chỉ là convenience mirror.
3. Khóa experiment ID, manifest schema, hash policy.
4. Khóa environment/seed/thread profile.
5. Khóa registry state machine và promotion gates.
6. Khóa serialization/security/license rules.

### Output

```text
experiment-manifest.template.yaml
model-registry-record.schema.json
training-authorization.schema.json
environment-lock.research.yaml
scripts/start_mlflow_local.sh
capture_environment.py
```

### Acceptance

- MLflow bind `127.0.0.1`.
- Không raw PHI trong tags/artifacts.
- `pickle/joblib` external/untrusted bị cấm.
- `uv.lock` thật là hard gate trước Day 29; không tạo file giả.
- Single operator không tự approve pilot-candidate.

---

## Step 12 — 17:50–18:20 — Red-team audit

### Input

Toàn bộ artifacts Day 26.

### Kiểm tra bắt buộc

```text
Có fit/train command nào không?
Có fake metric/model binary không?
Có random-window split không?
Có global scaler/selector không?
Có outer-test threshold tuning không?
Có raw score gọi probability không?
Có Task B hard fatigue diagnosis không?
Có MFCV site claim không?
Có model state clinical-validated không?
Có public healthy → Vinmec claim không?
```

### Output

`12-red-team-audit-findings.md`.

### Acceptance

- Không có critical finding mở.
- Finding trung bình/thấp có owner và remediation.

---

## Step 13 — 18:20–18:45 — Chạy checker và sinh readiness gate

### Thực hiện

```bash
python -m pip install pytest pyyaml jsonschema
bash scripts/dev/run_day26_research_checks.sh
```

Expected:

```text
Blueprint schema: PASS
Training blocked: PASS
No fake results: PASS
Task separation: PASS
Grouped validation: PASS
Test seal: PASS
Model registry: PASS
Source hashes: PASS
Automated tests: PASS
```

### Output

```json
{
  "blueprint_valid": true,
  "training_execution_allowed": false,
  "test_set_sealed": true,
  "result_status": "NOT_RUN",
  "day27_allowed": true,
  "day29_training_blocked_until_gates_pass": true
}
```

---

## Step 14 — 18:45–19:00 — Review, commit và tag

```bash
git add \
  ai-core \
  configs \
  docs \
  environment \
  mlops \
  packages/common-schemas \
  qa-validation \
  scripts

git diff --staged --check
git diff --staged --stat

git commit -m "day26: freeze research-grounded experiment blueprint"
git tag day26-research-blueprint-v2.0
```

---

# PHẦN C — GATE SANG DAY 27 VÀ DAY 29

## 8. Day 27 được phép làm gì?

```text
Chọn exact public dataset đầu tiên
→ xác minh canonical source/license
→ tải archive vào controlled storage
→ tính hash
→ viết dataset adapter
→ canonical conversion
→ label mapping
→ subject/session split manifest
```

## 9. Khi nào Day 29 mới được training?

Chỉ khi đồng thời:

```text
public dataset Engineering Data Gate = GO
+ exact source/license/hash
+ adapter tests PASS
+ split manifest PASS
+ test seal unopened
+ real resolved uv.lock exists
+ environment lock hash recorded
+ training authorization reviewed
+ leakage preflight PASS
```

Motion Lab local training và clinical training vẫn blocked độc lập.

---

# 10. Definition of Done Day 26

```text
[ ] 13 research/contract sources được hash và truy vết
[ ] 8 workstreams có research question và stop rule
[ ] Task A/B/C tách target, metric và claim
[ ] Sparse feature groups + window grid được khóa
[ ] Minimum/optional classical model ladder được khóa
[ ] Grouped/nested validation regimes được khóa
[ ] Split-first/window-later được kiểm bằng test
[ ] P0–P4 personalization được khóa; P4 No-Go
[ ] E-fatigue-0…4 được khóa; Task B không phải hard diagnosis
[ ] Primary metric và participant bootstrap được khóa
[ ] Probability semantic gate được khóa
[ ] Coverage/selective-risk/unsafe-prediction contract được khóa
[ ] Experiment matrix có NOT_RUN, không fake metrics
[ ] Hybrid tracking và registry state machine được khóa
[ ] CPU/reference environment + seed policy được khóa
[ ] Real uv.lock là pre-Day29 hard gate
[ ] Test set vẫn sealed
[ ] No critical red-team finding
[ ] All tests PASS
```

## Kết luận

Day 26 thành công không tạo ra model. Nó tạo ra một **hệ thống thí nghiệm không cho phép team tự đánh lừa mình** bằng leakage, test peeking, probability giả, accuracy thiếu coverage hoặc public-data claim vượt phạm vi.
