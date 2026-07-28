# Day 26 — Metrics, Probability Calibration và Selective Prediction/Abstention

**Artifact:** `docs/research/day26/08-metrics-calibration-abstention.md`  
**schema_version:** `1.0`  
**status:** `PROVISIONAL_LOCKED_FOR_DAY26_BLUEPRINT`  
**trainingAllowed:** `false`  
**Ngày tìm kiếm:** `2026-07-27`  
**Phạm vi:** Task A — Gesture Recognition; Task B — Fatigue Context / Confidence Adjustment / Abstention. Task C chỉ dùng các nguyên tắc thống kê chung; không bị ép thành bài toán classification nếu target chưa được khóa.

---

## 1. Tóm tắt quyết định

Day 26 khóa framework đánh giá **trước khi nhìn thấy model results**. Điều này ngăn việc đổi metric theo model đang thắng và ngăn outer-test trở thành một validation set kéo dài.

Các quyết định chính:

| Câu hỏi | Quyết định Day 26 | Trạng thái bằng chứng |
|---|---|---|
| Primary classification metric | **Subject-macro repetition-level Macro F1**: tính dự đoán ở mức repetition, tính Macro F1 riêng theo subject, sau đó lấy trung bình không trọng số giữa subjects | `PROJECT_LOCKED + OFFICIAL_VERIFIED + INFERRED_AGGREGATION` |
| Vai trò Balanced Accuracy | Secondary metric bắt buộc; phản ánh **macro recall**, đặc biệt hữu ích để phát hiện model bỏ sót lớp thiểu số | `OFFICIAL_VERIFIED` |
| Unit đánh giá chính | `repetition`; `subject` là unit tổng hợp và inference; `window` chỉ là unit xử lý/diagnostic | `PROJECT_LOCKED + INFERRED` |
| Confidence score khi nào được gọi là probability | Chỉ sau fold-contained calibration, method freeze trước outer test, và evaluation phù hợp bằng proper scoring rule + reliability diagnostics | `OFFICIAL_VERIFIED + PEER_REVIEWED_VERIFIED` |
| Báo coverage và accuracy | Luôn báo như một cặp: **coverage + selective accuracy/selective risk**, kèm số attempted/eligible/covered và risk–coverage curve | `PEER_REVIEWED_VERIFIED` |
| Threshold chọn ở đâu | Chỉ từ **group-aware inner validation/cross-fitted inner predictions**; outer test chỉ evaluate một lần | `PROJECT_LOCKED + OFFICIAL_VERIFIED` |
| Unsafe prediction rate | Tỷ lệ phát prediction trên các unit mà specification yêu cầu phải abstain, mẫu số là toàn bộ `mandatory_abstain` units | `ENGINEERING_DEFINITION_INFERRED` |
| Absolute clinical threshold | **Không khóa** ở Day 26 | `NOT_VERIFIED` |
| Engineering failure gate | Khóa gate tương đối với dummy baselines, class-collapse gate, estimability gate và reporting-completeness gate | `ENGINEERING_HYPOTHESIS` |

**Primary metric chính thức:**

```text
subject_macro_repetition_macro_f1
```

Cụ thể:

1. Window hợp lệ được gom về repetition theo rule đã khóa.
2. Từ dự đoán repetition, tính Macro F1 cho từng subject.
3. Lấy trung bình không trọng số giữa các subject.
4. Báo đồng thời phân bố subject-level, 95% participant bootstrap CI và pooled repetition-level Macro F1.

Cách này tránh để một subject có nhiều session/windows hơn chi phối kết quả.

---

## 2. Scope locks và internal-source reconciliation

### 2.1. Những điều không mở lại

- `trainingAllowed=false`.
- Không train, tune, reproduce benchmark hay mở sealed test set.
- Không dùng random-window split làm benchmark chính.
- Không fit scaler, learned normalization, feature selection, calibrator hoặc threshold ngoài training/inner-validation fold.
- Không gộp Task A, B và C thành một model/metric chung.
- Task B ưu tiên fatigue context, confidence adjustment và abstention.
- Không gọi raw score là probability.
- Human review và abstention là bắt buộc.

### 2.2. Internal sources được dùng làm SSOT

| Evidence ID | Internal artifact | Nội dung được kế thừa |
|---|---|---|
| `INT-D26-PROTOCOL` | Day 26 Research Protocol và Governance Framework | Scope locks, evidence taxonomy, stop rules, fold-contained fitting, human review |
| `INT-D26-VALIDATION` | Day 26 Validation and Leakage Review | Group hierarchy, split-first/window-later, nested grouped evaluation, window→repetition→subject aggregation, participant bootstrap |
| `INT-D26-FEATURES` | Day 26 Feature Engineering Review | Windowing/normalization/feature-selection hygiene |
| `INT-D26-MODELS` | Classical Model Candidate Review | Classical baseline ladder; raw SVM/KNN/tree scores không mặc định là calibrated probability |
| `INT-D26-PERSONALIZATION` | Personalization and Adaptation Strategy | Target calibration subset tách khỏi locked test; calibration burden và fallback |
| `INT-D26-PLAN` | Day 26 single-operator plan | Primary `macro_f1`; secondary balanced accuracy, per-class metrics, coverage, abstention, p50/p95 latency |

Không phát hiện mâu thuẫn cốt lõi giữa năm review Day 26 đã truy hồi và metric hierarchy trong Day 26 execution plan. Điểm còn thiếu là **absolute numerical acceptance threshold**; báo cáo này cố ý không tự bịa ngưỡng lâm sàng.

---

## 3. Phương pháp tìm kiếm và screening log

Đây là **systematic scoping workstream theo tinh thần PRISMA-ScR**, dùng seed search + backward/forward citation chaining. Con số “records screened” là số top surfaced records đã thực sự rà ở seed stage; không phải tổng hit count của database nếu giao diện không cung cấp con số đáng tin cậy.

| Database/site | Exact query | Search date | Records screened | Inclusion reason | Exclusion reason | Duplicate status | Full text | Final decision |
|---|---|---:|---:|---|---|---|---|---|
| Internal SSOT | `Day 26 metric hierarchy macro F1 balanced accuracy coverage calibration abstention` | 2026-07-27 | 6 artifacts | Khóa project decisions và terminology | Không dùng làm external scientific evidence | Deduped | Yes | INCLUDE AS SSOT |
| BMJ / EQUATOR | `TRIPOD+AI updated guidance prediction model artificial intelligence`; `PROBAST+AI risk of bias applicability` | 2026-07-27 | 8 surfaced records | Reporting/appraisal backbone | Commentary, duplicate mirrors | Deduped | Yes/abstract | INCLUDE |
| BMJ | `evaluation of clinical prediction models part 1 part 2 calibration discrimination 2024` | 2026-07-27 | 6 surfaced records | Development/evaluation separation; discrimination vs calibration | Secondary summaries | Deduped | Yes/abstract | INCLUDE |
| scikit-learn official docs | `f1_score macro`; `balanced_accuracy_score`; `confusion_matrix`; `brier_score_loss multiclass` | 2026-07-27 | 8 pages | Canonical implementation semantics và formulas | Old/non-official mirrors | Deduped | Yes | INCLUDE |
| scikit-learn official docs | `probability calibration CalibratedClassifierCV sigmoid isotonic temperature` | 2026-07-27 | 6 pages | Calibration method, sample-size caveat, disjoint data requirement | Blogs | Deduped | Yes | INCLUDE |
| Google Scholar / original papers | `Platt probabilistic outputs support vector machines 1999`; `Transforming classifier scores into accurate multiclass probability estimates` | 2026-07-27 | 6 records | Original calibration methods | Secondary tutorials | Deduped | Yes/archival | INCLUDE |
| PMLR / NeurIPS | `On Calibration of Modern Neural Networks`; `Beyond temperature scaling Dirichlet calibration` | 2026-07-27 | 5 records | Multiclass calibration candidates | Paper không cung cấp methodological value cho tabular classical models | Deduped | Yes | INCLUDE / CONDITIONAL |
| JMLR | `selective classification risk coverage reject option` | 2026-07-27 | 5 records | Coverage, selective risk, risk–coverage curve | Generic uncertainty papers không có reject framework | Deduped | Yes | INCLUDE |
| IEEE / PubMed | `Evaluating Classifier Confidence for Surface EMG Pattern Recognition` | 2026-07-27 | 3 records | Direct EMG evidence rằng accuracy và confidence quality là hai mục tiêu khác nhau | Secondary reposts | Deduped | Yes/abstract | INCLUDE |
| PubMed / Springer | `cluster bootstrap hierarchical repeated measurements`; `bootstrap confidence intervals medical statisticians` | 2026-07-27 | 7 records | Participant/cluster resampling và CI construction | Window-level iid bootstrap | Deduped | Yes/abstract | INCLUDE |
| IEEE / PubMed | `balanced accuracy imbalanced multiclass Brodersen`; `multiclass Matthews correlation coefficient Gorodkin`; `multiclass AUC Hand Till` | 2026-07-27 | 8 records | Optional/secondary metric appraisal | Accuracy-only comparison articles | Deduped | Yes/abstract | INCLUDE |

### 3.1. Screening rules

| Tình huống | Rule |
|---|---|
| Metric paper không nêu evaluation unit | Dùng cho formula/definition, không dùng để suy transfer sang sEMG |
| EMG paper dùng random windows hoặc không report split | Không dùng performance value; chỉ dùng methodological insight nếu rõ |
| Calibration fit trên classifier-training observations hoặc test | `CRITICAL_FLAW` |
| Threshold chọn trên outer/sealed test | `CRITICAL_FLAW` |
| Hàng nghìn windows từ cùng subject | Không xem là hàng nghìn independent samples |
| Paper chỉ báo accuracy | Không đủ cho Task B/selective prediction decision |
| Reliability diagram/ECE không report binning | Diagnostic không tái lập; hạ evidence strength |

---

## 4. Part A — Classification metrics

### 4.1. Evaluation units và aggregation contract

```text
raw samples
  → windows
  → repetition/trial prediction
  → subject-level metrics
  → population summary + participant bootstrap CI
```

| Level | Vai trò | Có được dùng làm headline metric không? |
|---|---|---|
| Sample | DSP input | Không |
| Window | Feature/model inference; debugging; transition analysis | Không |
| Repetition/trial | **Operational prediction unit chính của Task A** | Có |
| Session/day | Drift/robustness stratum | Có, như stress-test summary |
| Subject | **Statistical aggregation/resampling unit chính** | Có |

#### Repetition aggregation

Ưu tiên theo thứ tự:

1. Nếu có score vector đã được phép mang probability semantics: trung bình xác suất trên các windows đủ điều kiện, sau đó `argmax`.
2. Nếu chỉ có raw multiclass scores: dùng rule được predeclare theo model, ví dụ mean decision score sau orientation/scale contract; tên output vẫn là `aggregated_decision_score`.
3. Majority vote chỉ là comparator, vì bỏ mất score magnitude và có thể tạo tie.
4. Repetition phải abstain khi usable-window ratio dưới gate hoặc các window bị mandatory-abstain theo QC/protocol.

Không được thay rule aggregation sau khi xem outer-test results.

### 4.2. Macro F1 — primary metric

Với mỗi class \(k\):

\[
P_k = \frac{TP_k}{TP_k + FP_k}, \qquad
R_k = \frac{TP_k}{TP_k + FN_k}
\]

\[
F1_k = \frac{2P_kR_k}{P_k + R_k}
      = \frac{2TP_k}{2TP_k + FP_k + FN_k}
\]

\[
MacroF1 = \frac{1}{K}\sum_{k=1}^{K}F1_k
\]

**Lý do chọn primary:**

- Mỗi class có trọng số bằng nhau, phù hợp ontology gesture đa lớp khi support có thể lệch.
- Phạt cả false positive và false negative, trong khi Balanced Accuracy chỉ nhìn recall.
- Dễ gắn với per-class failure analysis.
- Đã được khóa trong Day 26 execution plan trước khi có model results.

**Canonical project metric:**

\[
Primary = \frac{1}{S}\sum_{s=1}^{S} MacroF1_s
\]

trong đó \(MacroF1_s\) được tính từ các repetition của subject \(s\). Đây là **subject-macro repetition-level Macro F1**.

**Zero-division rule:**

- Fixed class ontology luôn được truyền vào metric function.
- Nếu class có ground-truth support bằng 0 trong một fold/subject, metric class đó là `NOT_ESTIMABLE`, không được âm thầm loại rồi gọi là đầy đủ.
- Nếu class có support nhưng không có prediction đúng hoặc không được predicted, precision/recall/F1 dùng `zero_division=0`, đồng thời phát `CLASS_COLLAPSE_FLAG`.
- Headline subject-level Macro F1 chỉ tính cho subject có đủ minimum class support theo regime; các subject không đủ support phải được liệt kê riêng, không biến mất khỏi báo cáo.

### 4.3. Balanced Accuracy — secondary bắt buộc

\[
BalancedAccuracy = \frac{1}{K}\sum_{k=1}^{K} Recall_k
\]

Balanced Accuracy là **macro recall**. Nó trả lời: “trung bình, mỗi class được thu hồi bao nhiêu?” Nó có vai trò:

- kiểm tra model có bỏ quên class thiểu số không;
- bổ sung cho Macro F1 khi precision và recall tạo trade-off;
- làm secondary selection diagnostic trong inner validation;
- không thay thế Macro F1 vì không phạt trực tiếp false positives của từng class.

Project dùng `adjusted=false` làm báo cáo chính; adjusted balanced accuracy có thể báo thêm để so với chance nhưng không thay thế metric gốc.

### 4.4. Per-class Recall và Precision

- **Recall:** xác suất thực nghiệm một gesture thật được nhận đúng.
- **Precision:** trong các lần model phát gesture đó, tỷ lệ đúng.
- Bắt buộc báo support, số subject có class, và CI khi estimable.
- Không được chỉ báo macro average rồi che mất class `rest`, gesture hiếm hoặc class dễ nhầm.

### 4.5. Confusion matrix

Bắt buộc xuất ba biến thể:

1. Count matrix ở repetition level.
2. Row-normalized matrix (`normalize=true`) để đọc per-class recall/error destination.
3. **Abstention-aware matrix** với thêm cột `ABSTAIN`.

Đối với selective system, matrix chỉ trên covered predictions là chưa đủ; phải có matrix với `ABSTAIN` để thấy false rejection và class-conditional coverage.

### 4.6. Participant-level và repetition-level performance

| Metric view | Công thức/aggregation | Mục đích |
|---|---|---|
| Subject-macro | Mean của metric tính riêng theo subject | Headline, ngăn subject có nhiều data lấn át |
| Pooled repetition | Tính metric trên toàn bộ repetition OOF | Secondary, mô tả tổng operational volume |
| Per-subject distribution | Median, IQR, SD, p10, min, max | Thấy long tail và failure subjects |
| Per-session within subject | Metric theo session/day | Drift và repeatability |
| Window-level | Diagnostic only | Debug transitions/QC, không claim generalization |

### 4.7. Optional MCC

Multiclass Matthews Correlation Coefficient (MCC) có thể giữ như single-number consistency metric từ toàn confusion matrix. Ưu điểm là xem xét toàn bộ cells và tương đối hữu ích khi class imbalance; nhược điểm là khó diễn giải cho clinical/operator stakeholders và không thay thế per-class reporting.

**Decision:** `OPTIONAL_SECONDARY`, không dùng làm primary hoặc threshold-selection objective duy nhất.

### 4.8. Optional macro AUROC

Chỉ tính khi:

- model cung cấp continuous score cho tất cả classes;
- score orientation và class order đã khóa;
- tất cả classes có đủ positive/negative support;
- dùng convention được predeclare, ưu tiên Hand–Till one-vs-one macro AUC hoặc ghi rõ OVR.

Macro AUROC là ranking metric; nó có thể cao trong khi calibration, operating threshold hoặc selective coverage kém. Do đó:

**Decision:** `EXPLORATORY_ONLY`, không dùng làm primary, không dùng một mình để chọn model cho Task B.

### 4.9. Engineering failure gates — không phải clinical thresholds

Không khóa một con số “clinical acceptable” ở Day 26. Thay vào đó, khóa các gate sau:

| Gate | Failure condition | Status |
|---|---|---|
| `G-METRIC-BASELINE` | Subject-macro Macro F1 không vượt best dummy baseline trong cùng split/regime | `ENGINEERING_HYPOTHESIS` |
| `G-METRIC-MARGIN` | Development target chưa đạt ít nhất `+0.10` absolute Macro F1 so với best dummy | `PROVISIONAL_ENGINEERING_TARGET`; không dùng như clinical claim |
| `G-CLASS-COLLAPSE` | Bất kỳ supported class nào có recall = 0 trong từ hai outer folds trở lên, hoặc class không estimable do split design lỗi | `FAIL` |
| `G-SUBJECT-TAIL` | Không báo được p10/min subject metric, hoặc headline tốt nhưng ≥20% subjects không vượt best dummy | `FAIL_REPORTING_OR_MODEL` |
| `G-COVERAGE` | Selective accuracy/Macro F1 được báo mà không có coverage và abstention breakdown | `FAIL_REPORTING` |
| `G-ESTIMABILITY` | Fold không chứa đủ classes do grouping/split design và không có remediation được predeclare | `FAIL_PROTOCOL` |
| `G-TEST-PEEK` | Metric/threshold/calibration method đổi sau khi xem outer test | `CRITICAL_FLAW` |

`+0.10` chỉ là development-margin hypothesis để tránh “nhỉnh hơn dummy không đáng kể”; nó phải được review lại trước Day 27 và không có ý nghĩa lâm sàng.

---

## 5. Part B — Statistical reporting

### 5.1. Subject-level aggregation

Headline estimate phải cho mỗi subject trọng số bằng nhau. Không dùng số windows làm weight mặc định.

```text
window predictions
→ repetition prediction
→ subject confusion/metric
→ unweighted mean across subjects
```

Báo thêm pooled repetition metrics để thể hiện operational volume, nhưng không để pooled metric thay thế subject-macro metric.

### 5.2. Confidence interval

**Default:** 95% participant-cluster bootstrap CI.

Algorithm:

1. Dùng duy nhất outer-fold out-of-fold predictions.
2. Lấy mẫu lại `subject_id` với replacement.
3. Khi subject được chọn, giữ nguyên toàn bộ sessions/repetitions/windows liên quan.
4. Tính lại toàn bộ aggregation và metric.
5. Lặp `B=2000` với fixed seed; `B=5000` là sensitivity option khi compute budget cho phép.
6. Báo percentile 2.5%–97.5% CI; BCa chỉ là sensitivity analysis khi số cluster đủ và implementation đã kiểm thử.

**Cấm:** bootstrap individual windows như iid observations.

Đối với cross-session/cross-day analysis, cho phép bootstrap hai tầng:

```text
sample subjects with replacement
  → within selected subject, sample sessions/days with replacement
```

Phải ghi rõ resampling hierarchy; không mặc định hai tầng nếu mỗi subject có quá ít session.

### 5.3. Khi số subject nhỏ

- CI phải gắn `SMALL_CLUSTER_COUNT_WARNING`.
- Không dùng CI hẹp giả tạo từ hàng nghìn windows.
- Báo toàn bộ per-subject values và leave-one-subject-out sensitivity.
- Không suy “population-level stability” khi số subject không đủ.
- Exact minimum number of subjects cho decision-grade claim là `NOT_VERIFIED` và phụ thuộc design/effect precision.

### 5.4. Fold summary

Mỗi outer fold phải báo:

- train/validation/test subject counts;
- class support;
- Macro F1, Balanced Accuracy, per-class metrics;
- coverage/abstention nếu bật;
- calibration metrics nếu semantics hợp lệ;
- failure reasons;
- selected pipeline/calibrator/threshold ID từ inner loop.

Summary across folds:

- mean ± SD;
- median [IQR];
- min/max;
- participant-bootstrap CI từ OOF predictions.

**Không dùng các folds như independent samples để tạo p-value/CI chính.** Fold statistics là stability diagnostics.

### 5.5. Variance across subjects và sessions

Bắt buộc:

| Component | Reporting |
|---|---|
| Between-subject | SD, IQR, p10, min của subject-level metric |
| Within-subject across sessions | Per-subject session SD/range; summary của các SD/range |
| Between-day | Day-level delta và distribution khi có multi-day data |
| Electrode reapply | Pre/post performance delta và calibration burden |
| Fatigue strata | Metric/calibration/coverage theo fatigue context, giữ group split gốc |

Mixed-effects variance decomposition có thể là later statistical extension; Day 26 chưa khóa model thống kê này.

### 5.6. Worst-subgroup reporting

Subgroup phải **predeclare**, không được data-mine sau outer test. Candidate strata:

- dataset/source;
- subject sex/age band khi có metadata và consent phù hợp;
- clinical vs healthy;
- severity stratum nếu Task C có reference standard;
- session/day;
- electrode reapply state;
- fatigue context;
- device/montage/protocol version.

Rules:

- Báo `n_subjects`, `n_repetitions`, support theo class.
- Nhóm dưới 5 subjects chỉ báo count/failure cases; metric gắn `NOT_ESTIMABLE_FOR_SUBGROUP_INFERENCE`.
- Luôn báo worst subgroup + overall; không chỉ chọn subgroup tốt nhất.
- Không coi observed subgroup gap là bias causally established nếu design không hỗ trợ.

### 5.7. Failure-case reporting

Mỗi outer evaluation sinh một failure table tối thiểu:

```text
subject_id_pseudonym
session_id
day_id
repetition_id
true_class
predicted_class_or_abstain
primary_abstention_reason
secondary_reason_codes
qc_status
protocol_support_status
calibration_status
fatigue_context
transition_flag
score_semantics
max_score
error_category
review_status
```

Error categories:

- supported-class confusion;
- unknown accepted as known;
- transition accepted as steady gesture;
- QC-fail accepted;
- calibration failure ignored;
- unsupported protocol accepted;
- false abstention;
- low-confidence error;
- high-score error;
- missing/invalid metric.

---

## 6. Part C — Operational metrics

### 6.1. Timing boundary contract

Latency dễ bị báo sai nếu không tách window wait khỏi compute. Day 26 khóa bốn timestamps:

```text
t_window_start       first sample used by decision window
t_window_close       last required sample becomes available
t_decision_ready     model + calibration + abstention output is complete
t_user_visible       UI/API consumer receives/renderable result
```

### 6.2. Metric definitions

| Metric | Definition | Notes |
|---|---|---|
| `p50_pipeline_compute_latency_ms` | p50 of `t_decision_ready - t_window_close` | Excludes window acquisition duration |
| `p95_pipeline_compute_latency_ms` | p95 of same | Main tail-latency metric |
| `p50_end_to_end_latency_ms` | p50 of `t_user_visible - t_window_close` | Includes service transport/serialization/render-ready path |
| `p95_end_to_end_latency_ms` | p95 of same | Report with hardware/software manifest |
| `signal_to_feedback_latency_ms` | `t_user_visible - t_window_start` | Includes window duration; separate from compute latency |
| `feature_extraction_time_ms` | End feature extraction − start feature extraction | Per window/repetition as applicable |
| `model_inference_time_ms` | Base estimator predict end − start | Excludes calibrator unless explicitly combined |
| `calibration_mapping_time_ms` | Calibrator transform end − start | Usually small but logged separately |
| `abstention_decision_time_ms` | Reject/supportability logic end − start | Includes unknown/QC/protocol checks after prerequisites |
| `memory_peak_rss_mb` | Maximum process resident set size during test | Warm/cold run distinguished |
| `memory_steady_state_rss_mb` | Median RSS after warm-up | Same workload and duration |
| `model_artifact_size_mb` | Serialized model+scaler+selector+calibrator+policy bytes | Versioned artifact bundle |
| `throughput_windows_per_s` | Processed windows / measured wall-clock seconds | Include concurrency setting |
| `real_time_factor` | Processing time / signal duration processed | `<1` means faster than real-time; no clinical claim |
| `dropped_window_ratio` | Expected scheduled windows not processed / expected scheduled windows | Abstained windows are **not** dropped |
| `calibration_duration_s` | Wall-clock from instruction start to calibration outcome | Break down setup, acquisition, confirmation, processing, retry |
| `calibration_failure_rate` | Failed calibration attempts / calibration attempts started | Reason-coded |
| `remeasurement_rate` | Sessions requiring repeat acquisition / sessions started | QC/protocol/calibration reasons separated |

### 6.3. Measurement rules

- Use monotonic high-resolution clock.
- Report cold start and warmed steady-state separately.
- Run deterministic workload and list CPU/GPU/RAM/OS/runtime/library versions.
- Report sample count, session count and concurrency.
- p95 is undefined/unstable with too few observations; emit warning rather than a confident number.
- Do not hide queueing/backpressure by timing only the model function.
- Do not count deliberate abstention as dropped inference.
- Operational thresholds remain `NOT_VERIFIED` until target runtime/workflow is site-confirmed.

---

## 7. Part D — Probability calibration

### 7.1. Terminology gate

| Output | Allowed name |
|---|---|
| SVM margin, LDA discriminant, KNN vote fraction, RF raw class fraction, arbitrary normalized score | `raw_score` hoặc `uncalibrated_confidence_score` |
| `predict_proba` from a model before calibration evaluation | `model_probability_output` hoặc `uncalibrated_probability_like_score`; không gọi là deployment probability |
| Fold-contained calibrated and independently evaluated score meeting criteria below | `calibrated_class_probability` within declared scope |

Một score chỉ được gọi là **probability** trong project-facing output khi tất cả điều kiện sau đạt:

1. Mỗi vector không âm và tổng bằng 1 trong tolerance đã khóa.
2. Base model và calibrator không được fit trên cùng observations theo cách gây resubstitution bias.
3. Calibration method được chọn trong group-aware inner validation.
4. Method/hyperparameters được freeze trước outer test.
5. Được đánh giá trên untouched outer predictions bằng Brier score, classwise calibration/reliability diagnostics và support counts.
6. Không có calibration leakage hoặc test peeking.
7. Population, protocol, device/montage, personalization regime và time horizon được ghi rõ.
8. Reliability không bị suy rộng từ public healthy data sang stroke/Vinmec.

Nếu thiếu một điều kiện, output phải giữ tên `score`.

### 7.2. Candidate methods

| Method | Strength | Main limitation | Day 26 status |
|---|---|---|---|
| `none` | Comparator để thấy raw calibration | Không cấp probability semantics | Mandatory comparator |
| Platt/sigmoid scaling | Low-variance, phù hợp score SVM-like và calibration sample nhỏ hơn isotonic | Sigmoid-shape assumption; multiclass thường OvR + renormalization | Core candidate |
| Isotonic regression | Flexible monotonic mapping | Dễ overfit khi calibration set nhỏ; stepwise/ties | Conditional candidate |
| Temperature scaling | Một scalar, native multiclass khi có coherent logits/score vector; giữ argmax với positive T | Toolchain/version và score semantics phải pin; không sửa class-specific distortion | Provisional multiclass candidate |
| Vector scaling | Class-specific scale/bias | Nhiều parameters hơn; cần nhiều calibration data | Later research candidate |
| Dirichlet calibration | Multiclass mapping linh hoạt và interpretable parameters hơn một số black-box alternatives | Data/burden cao; chưa cần cho minimum baseline | Later research candidate |

**Toolchain note:** scikit-learn current documentation có temperature scaling, nhưng project runtime version chưa được site/repo pin trong source pack; implementation availability vì vậy là `NOT_VERIFIED` cho repo hiện tại.

### 7.3. Fold-contained calibration design

Canonical nested process:

```text
OUTER TRAIN SUBJECTS
  └── grouped inner splits
        ├── inner model-fit groups
        └── inner calibration/validation groups
             → cross-fitted raw scores
             → fit/evaluate candidate calibrators
             → choose calibrator + threshold policy

LOCK decisions
REFIT only on OUTER TRAIN under predeclared cross-fitting design
EVALUATE ONCE on OUTER TEST
```

Rules:

- Default `CalibratedClassifierCV` with integer `cv` is not sufficient if it ignores project group keys; pass an explicit group-aware iterable or implement manual cross-fitting.
- Every class phải có support trong model-fit và calibration partitions; nếu không, calibration fold invalid.
- Test set không dùng để chọn calibration method, bins, temperature, isotonic complexity, threshold hoặc target coverage.
- Personalized regime: target calibration subset tách trước ở session/day/repetition level; locked target test remains untouched.

### 7.4. Brier score

Project dùng multiclass unscaled Brier loss:

\[
BS = \frac{1}{N}\sum_{i=1}^{N}\sum_{k=1}^{K}
      (p_{ik} - y_{ik})^2
\]

Range: `[0, 2]` cho multiclass convention này; thấp hơn tốt hơn. Brier là proper scoring rule và là **primary calibration metric**.

Reporting units:

- repetition-level Brier là chính;
- subject-level mean Brier và participant bootstrap CI;
- classwise one-vs-rest Brier là secondary;
- window-level Brier chỉ diagnostic.

### 7.5. Expected Calibration Error (ECE)

Top-label ECE:

\[
ECE = \sum_{m=1}^{M}\frac{|B_m|}{N}
      |acc(B_m)-conf(B_m)|
\]

Day 26 convention:

- default `M=15` equal-frequency bins;
- report bin boundaries, counts, mean confidence and empirical accuracy;
- sensitivity at `M=10` and `M=20`;
- ECE là diagnostic, **không** thay Brier làm primary calibration metric;
- ECE có thể thay đổi theo binning và sample size.

### 7.6. Classwise ECE

Tính one-vs-rest calibration error cho từng class, rồi báo:

- từng class;
- unweighted classwise mean;
- class support;
- class-conditional coverage.

Classwise ECE quan trọng vì top-label ECE có thể che một class hiếm bị overconfident.

### 7.7. Reliability diagrams

Bắt buộc:

1. Top-label reliability diagram.
2. One-vs-rest reliability diagram cho mỗi supported class khi đủ support.
3. Histogram/count per bin.
4. Before-vs-after calibration comparison dùng **inner/OOF or outer untouched predictions**, không dùng training predictions.

Không tuyên bố calibrated chỉ vì đường nhìn “gần diagonal”; phải đi kèm Brier, ECE/classwise ECE, support và CI/sensitivity.

---

## 8. Part E — Selective prediction và abstention

### 8.1. Unit accounting

Ba mẫu số phải tách rõ:

```text
attempted_units
  ├── model_ineligible_units   # QC/protocol/calibration gate
  └── model_eligible_units
        ├── abstained_by_model
        └── covered_units      # prediction emitted
```

### 8.2. Coverage

\[
SystemCoverage = \frac{N_{covered}}{N_{attempted}}
\]

\[
ModelCoverage = \frac{N_{covered}}{N_{model\_eligible}}
\]

Phải báo cả hai. `SystemCoverage` phản ánh toàn workflow; `ModelCoverage` tách riêng behavior của confidence/unknown/transition gate sau khi prerequisites đã qua.

### 8.3. Selective accuracy và selective risk

\[
SelectiveAccuracy =
\frac{N_{correct\;and\;covered}}{N_{covered}}
\]

Với 0–1 loss:

\[
SelectiveRisk = 1 - SelectiveAccuracy
\]

Đối với multiclass imbalance, báo thêm `selective_macro_f1` và `selective_balanced_accuracy` trên covered units, nhưng luôn đi kèm class-conditional coverage.

### 8.4. Abstention rate

\[
AbstentionRate = \frac{N_{abstained}}{N_{attempted}}
\]

Báo theo:

- primary reason;
- all triggered reason codes;
- subject;
- class;
- session/day;
- fatigue stratum;
- QC/protocol/calibration category.

### 8.5. Risk–coverage curve

Sweep threshold trên **inner-validation cross-fitted scores** để tạo candidate operating points. Trên outer test, curve chỉ để evaluate locked policy; không chọn threshold từ curve outer-test.

Curve phải có:

- coverage x-axis;
- selective risk y-axis;
- marked locked operating point;
- class-conditional coverage at marked point;
- subject-level coverage distribution;
- unsafe prediction rate at marked point.

### 8.6. Class-conditional và subject-level coverage

\[
Coverage_k =
\frac{N_{covered,\;true\;class=k}}
     {N_{eligible,\;true\;class=k}}
\]

\[
Coverage_s =
\frac{N_{covered,\;subject=s}}
     {N_{eligible,\;subject=s}}
\]

Báo mean, median, IQR, p10 và minimum `Coverage_s`. Một global coverage tốt không được che việc một class hoặc subject gần như luôn bị abstain.

### 8.7. Threshold selection

Threshold chỉ được chọn trong grouped inner validation. Canonical objective:

```text
maximize model_coverage
subject to:
  selective_risk <= r_max
  unsafe_prediction_rate <= u_max
  class_conditional_coverage[k] >= c_min[k]
  subject_coverage_p10 >= c_subject_p10_min
```

Tại Day 26:

- `r_max`, `u_max`, `c_min` và `c_subject_p10_min` = `NOT_VERIFIED`.
- Không tự đặt clinical threshold.
- Candidate values chỉ được ghi `ENGINEERING_HYPOTHESIS` và phải được chọn hoàn toàn từ development data.
- Global threshold là default MVP candidate.
- Class-specific thresholds chỉ được phép khi class support đủ, predeclare, và không làm tăng overfitting/operational complexity vô kiểm soát.

### 8.8. Abstention taxonomy và precedence

Một unit có thể kích hoạt nhiều reason codes, nhưng cần một `primary_reason` deterministic.

| Precedence | Primary reason | Condition |
|---:|---|---|
| 1 | `QC_FAIL` | Critical signal-quality gate fail |
| 2 | `UNSUPPORTED_PROTOCOL_OR_ANATOMY` | Protocol, muscle, device/montage hoặc ontology không supported |
| 3 | `CALIBRATION_FAILURE_OR_EXPIRED` | Calibration missing, failed, expired hoặc invalid after electrode replacement |
| 4 | `UNKNOWN_GESTURE` | Evidence corpus/adjudication xác định out-of-ontology motion |
| 5 | `TRANSITION` | Window/repetition thuộc transition không được phép decode như steady gesture |
| 6 | `FATIGUE_DRIFT_OUTSIDE_SUPPORT` | Fatigue context làm input ra ngoài support envelope theo policy đã khóa |
| 7 | `LOW_MODEL_CONFIDENCE` | Không reason mạnh hơn và calibrated/eligible confidence dưới threshold |
| 8 | `QC_WARNING_POLICY` | Warning được cấu hình bắt buộc abstain trong regime cụ thể |

`QC_FAIL`, unsupported protocol và calibration failure là **system/prerequisite abstention**; low confidence là **model selective abstention**. Hai loại không được gộp khi báo coverage.

### 8.9. Unsafe prediction rate

#### Ground-truth/event definition

`mandatory_abstain = true` khi adjudicated reference hoặc deterministic system contract xác nhận một trong các điều kiện:

- QC critical fail;
- unsupported protocol/anatomy/device/montage;
- calibration failed/expired/invalid;
- unknown gesture;
- non-decodable transition;
- fatigue drift ngoài support envelope đã predeclare;
- condition khác được hazard log xác định phải abstain.

`unsafe_prediction_event = true` khi hệ thống **phát một supported class prediction** trong khi `mandatory_abstain=true`.

#### Primary metric

\[
UnsafePredictionRate =
\frac{N_{unsafe\_prediction\_events}}
     {N_{mandatory\_abstain\_units}}
\]

Đây là conditional false-accept rate trên các trường hợp hệ thống đáng ra phải từ chối.

Báo thêm:

\[
UnsafePredictionRateOverall =
\frac{N_{unsafe\_prediction\_events}}
     {N_{attempted\_units}}
\]

và:

\[
MandatoryAbstainPrevalence =
\frac{N_{mandatory\_abstain\_units}}
     {N_{attempted\_units}}
\]

Lý do cần ba metric: overall rate có thể nhìn rất thấp nếu unsafe cases hiếm; conditional rate mới đo khả năng chặn đúng khi hazard xuất hiện.

**Không mặc định** mọi supported-class misclassification là `unsafe_prediction_event`. Những lỗi đó thuộc `selective_risk`, trừ khi task-specific hazard mapping predeclare một confusion cụ thể là safety-critical.

### 8.10. Cách báo coverage và accuracy cùng nhau

Mỗi kết quả selective phải dùng tối thiểu format:

```yaml
attempted_units: 1000
model_eligible_units: 900
covered_units: 720
system_coverage: 0.72
model_coverage: 0.80
selective_accuracy: 0.91
selective_risk: 0.09
selective_macro_f1: 0.89
class_conditional_coverage: {...}
subject_coverage_p10: 0.61
unsafe_prediction_rate: 0.03
abstention_reasons: {...}
```

Không được viết “accuracy 91%” mà bỏ `coverage=72%`.

---

## 9. Decision matrix

| Decision area | Option | Decision | Rationale | Evidence status |
|---|---|---|---|---|
| Primary metric | Accuracy | Reject | Bị class prevalence chi phối; che class failure | OFFICIAL_VERIFIED |
| Primary metric | Balanced Accuracy | Secondary | Chỉ macro recall; thiếu precision penalty | OFFICIAL_VERIFIED |
| Primary metric | Macro F1 | **Select** | Equal class weighting + precision/recall; pre-results project lock | PROJECT_LOCKED + OFFICIAL_VERIFIED |
| Headline unit | Window | Reject | Non-independent repeated windows | PROJECT_LOCKED + METHODOLOGICAL_EVIDENCE |
| Headline unit | Repetition→subject | **Select** | Operational unit + participant-level inference | INFERRED + PROJECT_LOCKED |
| Calibration primary metric | ECE | Reject as primary | Binning-sensitive, not proper scoring rule | PEER_REVIEWED_VERIFIED |
| Calibration primary metric | Brier | **Select** | Proper scoring rule, multiclass definition explicit | OFFICIAL_VERIFIED |
| Calibrator default candidate | Sigmoid/Platt | **Select candidate** | Lower variance, practical for SVM-like scores | OFFICIAL_VERIFIED |
| Isotonic | Conditional | Needs much larger calibration support | OFFICIAL_VERIFIED |
| Temperature | Provisional | Natural multiclass; toolchain/version dependency | OFFICIAL_VERIFIED + SITE/REPO_NOT_VERIFIED |
| Selective reporting | Accuracy only | Reject | Can improve merely by abstaining more | PEER_REVIEWED_VERIFIED |
| Selective reporting | Risk–coverage bundle | **Select** | Explicit trade-off and coverage accounting | PEER_REVIEWED_VERIFIED |
| Threshold source | Outer test | Reject / critical flaw | Test leakage | PROJECT_LOCKED |
| Threshold source | Grouped inner OOF | **Select** | Development-only selection | PROJECT_LOCKED + OFFICIAL_VERIFIED |

---

## 10. Provisional decisions

1. Primary metric: `subject_macro_repetition_macro_f1`.
2. Balanced Accuracy: mandatory secondary and class-recall audit.
3. Brier score: primary calibration metric; ECE/classwise ECE/reliability diagrams are diagnostics.
4. Participant bootstrap: default CI method; no window bootstrap.
5. Coverage and selective performance always reported together.
6. Threshold and calibration method selected only inside grouped inner validation.
7. Unsafe prediction rate uses mandatory-abstain cases as denominator.
8. `probability` semantics are earned, not inherited from an API method name.
9. Absolute clinical acceptance thresholds remain unverified.
10. Task C is not forced into this classification framework unless its target ontology is later locked.

---

## 11. Rejected alternatives

| Alternative | Lý do bác bỏ |
|---|---|
| Accuracy làm primary | Dễ bị class imbalance và subject volume chi phối |
| Window-level bootstrap/CI | Vi phạm independence; tạo CI quá hẹp |
| Pool toàn bộ repetitions rồi chỉ báo một score | Subject nhiều dữ liệu lấn át subject ít dữ liệu |
| ECE làm calibration metric duy nhất | Binning/sample-size sensitive; không proper |
| Gọi raw SVM margin/KNN vote/RF fraction là probability | Không đủ calibration semantics |
| Fit calibrator trên observations đã fit classifier | Resubstitution bias |
| Chọn threshold bằng outer test risk–coverage curve | Threshold leakage |
| Báo selective accuracy mà không báo coverage | Khuyến khích abstain cực đoan |
| Gộp QC fail với low-confidence abstention | Che failure ở acquisition/protocol layer |
| Dùng một global average để kết luận subgroup robustness | Che worst-subject/worst-class behavior |

---

## 12. NOT_VERIFIED items

| Item | Vì sao chưa khóa |
|---|---|
| Absolute minimum Macro F1 cho clinical use | Chưa có intended-use clinical study/site evidence |
| Maximum acceptable selective risk | Cần hazard analysis + clinical review |
| Maximum acceptable unsafe prediction rate | Cần clinical safety owner và target workflow |
| Minimum coverage | Phụ thuộc use case, operator burden và class mix |
| Minimum calibration sample count per class | Phụ thuộc model, method, ontology và grouped design |
| Temperature scaling availability in actual repo | Toolchain version chưa được pin |
| Exact latency budget | Runtime hardware và user-facing workflow chưa site-verified |
| Exact minimum subgroup sample size for inferential claims | Cần statistical analysis plan theo design thật |
| Fatigue drift reference/ground truth cho mandatory abstain | Task B label/protocol chưa site-verified |
| Unknown/transition corpus đầy đủ | Dataset/protocol-dependent |

---

## 13. Open questions và dependencies

| Open question | Dependency/owner |
|---|---|
| Exact supported class ontology và transition labeling rule | Task A protocol owner |
| Repetition aggregation rule cho từng model family | ML Lead + Biostat Lead |
| Calibration buffer có được phép ở deployment không | Clinical workflow + personalization workstream |
| QC warning nào bắt buộc abstain, warning nào cho phép analysis | Signal Quality Gate owner |
| Unknown gesture corpus gồm những motion nào | Safety Lead + clinical reviewer |
| Fatigue support envelope được định nghĩa bằng feature/context nào | Task B workstream |
| Runtime target và latency budget | Solution Architect/site IT |
| Clinical hazard mapping cho specific class confusions | Clinical AI Safety Lead |
| Số subject/session thực tế cho bootstrap và subgroup estimates | Data readiness owner |

### Dependencies cho workstream tiếp theo

- Experiment matrix phải dùng đúng metric IDs và aggregation unit trong YAML config.
- Model selection workstream không được dùng outer-test metric.
- Calibration/threshold implementation phải nhận explicit group-aware split iterable.
- UI/report phải hiển thị `score` thay vì `probability` cho tới khi probability gate pass.
- Abstention UI phải hiển thị primary reason + secondary reason codes.

---

## 14. Machine-readable handoff fragment

```yaml
schema_version: "1.0"
status: "PROVISIONAL_LOCKED_FOR_DAY26_BLUEPRINT"
rationale: >
  Metric hierarchy, calibration semantics and selective prediction policy are
  frozen before model results. No training or outer-test use is allowed on Day 26.
evidence_ids:
  - INT-D26-PROTOCOL
  - INT-D26-VALIDATION
  - INT-D26-MODELS
  - INT-D26-PERSONALIZATION
  - INT-D26-PLAN
  - MET-SKLEARN-F1
  - MET-SKLEARN-BALACC
  - CAL-SKLEARN
  - SEL-ELYANIV-2010
  - EMG-FURUI-2023
open_questions:
  - "Absolute operating risk and coverage constraints require site and clinical review."
  - "Actual runtime latency budget is not site-verified."
primary_metric:
  id: "subject_macro_repetition_macro_f1"
  base_metric: "macro_f1"
  prediction_unit: "repetition"
  aggregation_unit: "subject"
  confidence_interval: "participant_cluster_bootstrap_95"
secondary_metrics:
  - balanced_accuracy
  - per_class_recall
  - per_class_precision
  - per_class_f1
  - confusion_matrix_count
  - confusion_matrix_row_normalized
  - multiclass_mcc_optional
calibration:
  primary_metric: "multiclass_brier_unscaled_0_to_2"
  diagnostics: [ece_equal_frequency_15, classwise_ece, reliability_diagram]
  selection_fold: "grouped_inner_validation_only"
  outer_test_selection_allowed: false
selective_prediction:
  report_together:
    - system_coverage
    - model_coverage
    - selective_accuracy
    - selective_risk
    - class_conditional_coverage
    - subject_coverage_distribution
    - unsafe_prediction_rate
  threshold_selection_fold: "grouped_inner_validation_only"
trainingAllowed: false
```

---

## 15. Selected evidence matrix rows

Các row dưới đây dùng đúng schema chung. Trường không áp dụng hoặc không được report được ghi rõ, không tự điền.

```yaml
selected_evidence_matrix_rows:
  - evidence_id: INT-D26-PROTOCOL
    workstream: metrics_calibration_abstention
    research_question: "What project constraints govern metric and threshold decisions?"
    claim: "Day 26 is blueprint-only; Tasks A/B/C remain separate; learned transforms, calibration and threshold selection must be fold-contained; human review and abstention are mandatory."
    decision_implication: "Constrains the entire evaluation plan and forbids test-driven metric or threshold selection."
    source_title: "Day 26 Research Protocol và Governance Framework cho sEMG Clinical Intelligence"
    source_type: INTERNAL_SSOT
    authors: "Project internal"
    year: 2026
    doi_or_official_url: NOT_APPLICABLE
    population: NOT_APPLICABLE
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Day 26 governance"
    device: "Noraxon-compatible project scope"
    channel_count: "4-16 sparse-channel scope; MFCV optional"
    electrode_geometry: NOT_VERIFIED
    n_sessions_or_days: NOT_APPLICABLE
    window_length: "Candidate grid defined elsewhere"
    overlap: "Split-first, window-later rule"
    feature_set: NOT_APPLICABLE
    model: "Classical baseline ladder"
    split_unit: "subject/session/trial group-aware"
    validation_regime: "grouped nested validation"
    metric: "discrimination, calibration, coverage, utility separated"
    main_finding: "No hidden optimization and no test-set use."
    limitations: "Internal source is SSOT for project decisions, not external scientific evidence."
    project_transferability: "Direct"
    evidence_status: PROJECT_LOCKED
    reviewer_note: "Use as scope authority only."

  - evidence_id: INT-D26-VALIDATION
    workstream: metrics_calibration_abstention
    research_question: "What are the correct aggregation and inference units?"
    claim: "Metrics should aggregate window to repetition to subject; participant-level bootstrap is preferred over window-level bootstrap."
    decision_implication: "Defines headline metric unit and CI resampling unit."
    source_title: "Day 26 Validation and Leakage Review for sEMG Clinical Intelligence"
    source_type: INTERNAL_SSOT
    authors: "Project internal"
    year: 2026
    doi_or_official_url: NOT_APPLICABLE
    population: "Project datasets, not yet selected for training"
    n_subjects: NOT_VERIFIED
    clinical_or_healthy: "Mixed potential sources"
    muscle_or_anatomical_region: "Forearm/upper-limb project scope"
    task_or_protocol: "Task A/B/C validation regimes"
    device: "Vendor-neutral grouped validation"
    channel_count: "4-16 primary scope"
    electrode_geometry: NOT_VERIFIED
    n_sessions_or_days: NOT_VERIFIED
    window_length: "150-1000 ms candidate grid"
    overlap: "May exist within partition; never across split seals"
    feature_set: "Classical handcrafted candidates"
    model: "Multiple"
    split_unit: "subject/session/day/trial before window"
    validation_regime: "cross-subject primary + realism stack"
    metric: "Macro F1, balanced accuracy, calibration, coverage"
    main_finding: "Repeated windows are not independent observations."
    limitations: "Aggregation policy is methodological and still requires dataset-specific support checks."
    project_transferability: "Direct"
    evidence_status: PROJECT_LOCKED_INFERRED
    reviewer_note: "Do not bootstrap windows."

  - evidence_id: MET-SKLEARN-F1
    workstream: classification_metrics
    research_question: "How is multiclass Macro F1 defined?"
    claim: "F1 is the harmonic mean of precision and recall; macro averaging computes each label metric and takes the unweighted mean."
    decision_implication: "Supports Macro F1 as class-balanced primary metric."
    source_title: "scikit-learn f1_score documentation"
    source_type: OFFICIAL_DOCUMENTATION
    authors: "scikit-learn developers"
    year: 2026
    doi_or_official_url: "https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html"
    population: "Generic classification"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Multiclass metric definition"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: NOT_APPLICABLE
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: NOT_APPLICABLE
    model: "Any classifier"
    split_unit: "Not prescribed by source"
    validation_regime: "Not prescribed by source"
    metric: "F1 and macro F1"
    main_finding: "Macro F1 gives each label equal weight."
    limitations: "Does not solve repeated-measures aggregation or clinical threshold selection."
    project_transferability: "High for definition only"
    evidence_status: OFFICIAL_VERIFIED
    reviewer_note: "Project adds subject-level aggregation."

  - evidence_id: MET-SKLEARN-BALACC
    workstream: classification_metrics
    research_question: "What does Balanced Accuracy measure in multiclass classification?"
    claim: "Balanced Accuracy is the average recall across classes."
    decision_implication: "Use as mandatory secondary class-recall audit."
    source_title: "scikit-learn balanced_accuracy_score documentation"
    source_type: OFFICIAL_DOCUMENTATION
    authors: "scikit-learn developers"
    year: 2026
    doi_or_official_url: "https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html"
    population: "Generic classification"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Multiclass imbalanced evaluation"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: NOT_APPLICABLE
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: NOT_APPLICABLE
    model: "Any classifier"
    split_unit: "Not prescribed"
    validation_regime: "Not prescribed"
    metric: "Balanced accuracy"
    main_finding: "Each class recall contributes equally."
    limitations: "Does not penalize per-class false positives as Macro F1 does."
    project_transferability: "High for definition"
    evidence_status: OFFICIAL_VERIFIED
    reviewer_note: "Secondary, not primary."

  - evidence_id: CAL-BRIER-SKLEARN
    workstream: probability_calibration
    research_question: "Which primary score should evaluate multiclass probabilistic predictions?"
    claim: "Multiclass Brier loss is the mean summed squared difference between one-hot outcomes and predicted probabilities and is a strictly proper scoring rule."
    decision_implication: "Select unscaled multiclass Brier as primary calibration metric."
    source_title: "scikit-learn brier_score_loss documentation; Brier 1950"
    source_type: OFFICIAL_DOCUMENTATION_AND_PRIMARY_METHOD
    authors: "scikit-learn developers; Glenn W. Brier"
    year: "1950; 2026 documentation"
    doi_or_official_url: "https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html"
    population: "Generic probabilistic forecasts"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Probability scoring"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: NOT_APPLICABLE
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: NOT_APPLICABLE
    model: "Any probabilistic classifier"
    split_unit: "Not prescribed"
    validation_regime: "Independent evaluation required by project"
    metric: "Multiclass Brier score"
    main_finding: "Lower is better; canonical multiclass range is 0-2 without half scaling."
    limitations: "Combines calibration and refinement; should be paired with reliability diagnostics."
    project_transferability: "High"
    evidence_status: OFFICIAL_VERIFIED
    reviewer_note: "Store scale convention explicitly."

  - evidence_id: CAL-SKLEARN
    workstream: probability_calibration
    research_question: "How should calibration be fit without leakage and which methods are available?"
    claim: "Classifier-fit data and calibration data must be disjoint; sigmoid and isotonic are standard candidates, temperature scaling is a multiclass option in current documentation; isotonic overfits with low calibration sample size."
    decision_implication: "Use grouped inner cross-fitting and keep isotonic conditional."
    source_title: "scikit-learn Probability calibration and CalibratedClassifierCV documentation"
    source_type: OFFICIAL_DOCUMENTATION
    authors: "scikit-learn developers"
    year: 2026
    doi_or_official_url: "https://scikit-learn.org/stable/modules/calibration.html"
    population: "Generic classification"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Post-hoc calibration"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: NOT_APPLICABLE
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: NOT_APPLICABLE
    model: "Any classifier exposing decision_function or predict_proba"
    split_unit: "CV splitter supplied by user"
    validation_regime: "Project requires group-aware nested design"
    metric: "Brier, log loss, reliability"
    main_finding: "Calibration requires unbiased/disjoint predictions."
    limitations: "Default stratified CV is not automatically group-aware; project must override."
    project_transferability: "High"
    evidence_status: OFFICIAL_VERIFIED
    reviewer_note: "Temperature implementation depends on pinned package version."

  - evidence_id: CAL-PLATT-1999
    workstream: probability_calibration
    research_question: "What is Platt/sigmoid calibration?"
    claim: "A sigmoid mapping can transform classifier decision scores into probability estimates and was motivated for SVM outputs."
    decision_implication: "Include sigmoid as core low-variance candidate."
    source_title: "Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods"
    source_type: PRIMARY_METHOD
    authors: "John C. Platt"
    year: 1999
    doi_or_official_url: "https://www.microsoft.com/en-us/research/publication/probabilistic-outputs-for-support-vector-machines-and-comparisons-to-regularized-likelihood-methods/"
    population: "Benchmark classification datasets"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Score calibration"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: NOT_APPLICABLE
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: "Dataset-dependent"
    model: "Support Vector Machine"
    split_unit: "Dataset-dependent"
    validation_regime: "Calibration requires held-out/cross-validated outputs"
    metric: "Probability estimates/log likelihood"
    main_finding: "SVM margins can be post-hoc mapped by a sigmoid."
    limitations: "Binary origin; project multiclass handling requires explicit strategy."
    project_transferability: "High for candidate method, not direct sEMG effect"
    evidence_status: PEER_REVIEWED_VERIFIED
    reviewer_note: "Do not fit on resubstitution scores."

  - evidence_id: CAL-GUO-2017
    workstream: probability_calibration
    research_question: "What is temperature scaling and what does ECE capture?"
    claim: "Temperature scaling is a simple post-hoc multiclass calibration method; calibration and accuracy can diverge."
    decision_implication: "Keep temperature as a provisional multiclass candidate and separate discrimination from calibration."
    source_title: "On Calibration of Modern Neural Networks"
    source_type: PEER_REVIEWED_PRIMARY_RESEARCH
    authors: "Chuan Guo; Geoff Pleiss; Yu Sun; Kilian Q. Weinberger"
    year: 2017
    doi_or_official_url: "https://proceedings.mlr.press/v70/guo17a.html"
    population: "Image classification benchmarks"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Neural network calibration"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: NOT_APPLICABLE
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: "Deep model logits"
    model: "Neural networks"
    split_unit: "Dataset samples"
    validation_regime: "Held-out validation calibration"
    metric: "ECE, negative log likelihood"
    main_finding: "Temperature scaling can improve calibration without changing accuracy."
    limitations: "Not direct evidence for classical sEMG models or clinical population."
    project_transferability: "Method idea only"
    evidence_status: PEER_REVIEWED_VERIFIED
    reviewer_note: "Classical-score compatibility and toolchain remain to verify."

  - evidence_id: SEL-ELYANIV-2010
    workstream: selective_prediction
    research_question: "Why must coverage and risk be reported together?"
    claim: "Selective classification trades classifier coverage for lower risk/higher accuracy; the risk-coverage trade-off is fundamental."
    decision_implication: "Require risk-coverage curves and paired coverage/performance reporting."
    source_title: "On the Foundations of Noise-free Selective Classification"
    source_type: PEER_REVIEWED_METHOD
    authors: "Ran El-Yaniv; Yair Wiener"
    year: 2010
    doi_or_official_url: "https://jmlr.org/papers/v11/el-yaniv10a.html"
    population: "Theoretical/generic classification"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Classification with reject option"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: NOT_APPLICABLE
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: NOT_APPLICABLE
    model: "Selective classifier"
    split_unit: "Not prescribed"
    validation_regime: "Independent evaluation"
    metric: "Coverage, selective risk, risk-coverage curve"
    main_finding: "Higher selective accuracy can be purchased by lower coverage."
    limitations: "Does not define medical hazard-specific unsafe prediction."
    project_transferability: "High for metric framework"
    evidence_status: PEER_REVIEWED_VERIFIED
    reviewer_note: "Project adds system-vs-model coverage and reason taxonomy."

  - evidence_id: EMG-FURUI-2023
    workstream: selective_prediction
    research_question: "Does confidence quality matter independently of accuracy in sEMG pattern recognition?"
    claim: "In EMG pattern recognition, classifier confidence quality is a distinct evaluation target relevant to motion rejection and online adaptation."
    decision_implication: "Supports Task B calibration/abstention metrics rather than accuracy-only evaluation."
    source_title: "Evaluating Classifier Confidence for Surface EMG Pattern Recognition"
    source_type: PEER_REVIEWED_CONFERENCE_PAPER
    authors: "Akira Furui"
    year: 2023
    doi_or_official_url: "https://doi.org/10.1109/EMBC40787.2023.10340977"
    population: "Four EMG datasets"
    n_subjects: "Dataset-dependent"
    clinical_or_healthy: "Benchmark EMG contexts"
    muscle_or_anatomical_region: "Multiple EMG contexts"
    task_or_protocol: "EMG pattern recognition confidence comparison"
    device: "Surface EMG"
    channel_count: "Dataset-dependent"
    electrode_geometry: "Dataset-dependent"
    n_sessions_or_days: "Dataset-dependent"
    window_length: "Dataset-dependent"
    overlap: "Dataset-dependent"
    feature_set: "Multiple"
    model: "Discriminative and generative classifiers"
    split_unit: "Dataset-dependent"
    validation_regime: "Comparative EMG study"
    metric: "Accuracy and confidence quality"
    main_finding: "High accuracy does not guarantee confidence aligned with correctness."
    limitations: "Does not define project-specific mandatory-abstain taxonomy or clinical thresholds."
    project_transferability: "High for Task B philosophy"
    evidence_status: PEER_REVIEWED_VERIFIED
    reviewer_note: "Use with calibration-aware grouped evaluation."

  - evidence_id: STAT-CLUSTERBOOT-2020
    workstream: statistical_reporting
    research_question: "How should uncertainty be estimated for clustered repeated measurements?"
    claim: "Cluster/hierarchical bootstrap resamples higher-level independent clusters and preserves nested observations rather than treating lower-level measurements as independent."
    decision_implication: "Use participant bootstrap; optionally subject-then-session bootstrap."
    source_title: "ClusterBootstrap: An R package for analysis of hierarchical data using generalized linear models with the cluster bootstrap"
    source_type: PEER_REVIEWED_METHOD
    authors: "Mathijs Deen; Mark de Rooij"
    year: 2020
    doi_or_official_url: "https://doi.org/10.3758/s13428-019-01252-y"
    population: "Hierarchical/repeated-measures datasets"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Clustered statistical inference"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: "Repeated measurements"
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: NOT_APPLICABLE
    model: "Generalized linear models/cluster bootstrap"
    split_unit: "Independent cluster"
    validation_regime: "Bootstrap resampling"
    metric: "Confidence intervals/inference"
    main_finding: "Cluster resampling respects nested dependence."
    limitations: "Not sEMG-specific; exact CI performance depends on cluster count/design."
    project_transferability: "High for resampling logic"
    evidence_status: PEER_REVIEWED_VERIFIED
    reviewer_note: "Subject is the primary independent cluster."

  - evidence_id: GUIDE-TRIPODAI-2024
    workstream: governance_reporting
    research_question: "What reporting discipline applies to AI prediction-model evaluation?"
    claim: "Prediction-model studies should transparently report development/evaluation methods, data, performance and limitations."
    decision_implication: "Supports prespecification, complete metric bundle and no hidden test optimization."
    source_title: "TRIPOD+AI statement"
    source_type: OFFICIAL_REPORTING_GUIDELINE
    authors: "TRIPOD+AI Group"
    year: 2024
    doi_or_official_url: "https://doi.org/10.1136/bmj-2023-078378"
    population: "Prediction-model studies"
    n_subjects: NOT_APPLICABLE
    clinical_or_healthy: NOT_APPLICABLE
    muscle_or_anatomical_region: NOT_APPLICABLE
    task_or_protocol: "Reporting guideline"
    device: NOT_APPLICABLE
    channel_count: NOT_APPLICABLE
    electrode_geometry: NOT_APPLICABLE
    n_sessions_or_days: NOT_APPLICABLE
    window_length: NOT_APPLICABLE
    overlap: NOT_APPLICABLE
    feature_set: NOT_APPLICABLE
    model: "Regression/AI prediction models"
    split_unit: "Study-dependent"
    validation_regime: "Development and evaluation reporting"
    metric: "Comprehensive performance reporting"
    main_finding: "Transparent prespecified reporting is required."
    limitations: "Does not select a specific sEMG metric or threshold."
    project_transferability: "High for governance"
    evidence_status: OFFICIAL_VERIFIED
    reviewer_note: "Used as methodology backbone, not a clinical endorsement."
```

---

## 16. Go / No-Go handoff

**Decision:** `GO_WITH_CONDITIONS` cho việc đưa metric/calibration/abstention block vào Day 26 Experiment Blueprint.

Điều kiện:

1. Primary metric và unit aggregation không được thay sau khi xem model/outer-test results.
2. Absolute performance/risk/coverage thresholds vẫn để `NOT_VERIFIED` hoặc `ENGINEERING_HYPOTHESIS`.
3. Calibration implementation phải group-aware; default non-grouped CV bị cấm.
4. Coverage, selective risk và unsafe prediction rate phải được tính từ cùng immutable prediction ledger.
5. Test set vẫn sealed; `trainingAllowed=false`.
6. Human reviewer phải duyệt taxonomy `mandatory_abstain` trước khi dùng unsafe prediction rate cho bất kỳ safety claim nào.

---

## 17. References

1. Collins GS, et al. TRIPOD+AI statement. *BMJ*. 2024. DOI: `10.1136/bmj-2023-078378`.
2. Moons KGM, et al. PROBAST+AI. *BMJ*. 2025. DOI: `10.1136/bmj-2024-082505`.
3. Van Calster B, et al. Evaluation of clinical prediction models, BMJ series. 2024.
4. Brier GW. Verification of forecasts expressed in terms of probability. *Monthly Weather Review*. 1950.
5. Platt JC. Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods. 1999.
6. Zadrozny B, Elkan C. Transforming Classifier Scores into Accurate Multiclass Probability Estimates. KDD. 2002.
7. Guo C, Pleiss G, Sun Y, Weinberger KQ. On Calibration of Modern Neural Networks. ICML/PMLR. 2017.
8. Kull M, Perello-Nieto M, Kängsepp M, et al. Beyond temperature scaling: Obtaining well-calibrated multiclass probabilities with Dirichlet calibration. NeurIPS. 2019.
9. El-Yaniv R, Wiener Y. On the Foundations of Noise-free Selective Classification. *JMLR*. 2010;11:1605–1641.
10. Geifman Y, El-Yaniv R. Selective Classification for Deep Neural Networks. NeurIPS. 2017.
11. Furui A. Evaluating Classifier Confidence for Surface EMG Pattern Recognition. EMBC. 2023. DOI: `10.1109/EMBC40787.2023.10340977`.
12. Deen M, de Rooij M. ClusterBootstrap. *Behavior Research Methods*. 2020. DOI: `10.3758/s13428-019-01252-y`.
13. Carpenter J, Bithell J. Bootstrap confidence intervals: when, which, what? *Statistics in Medicine*. 2000;19:1141–1164.
14. Brodersen KH, et al. The Balanced Accuracy and Its Posterior Distribution. ICPR. 2010.
15. Gorodkin J. Comparing two K-category assignments by a K-category correlation coefficient. *Computational Biology and Chemistry*. 2004.
16. Hand DJ, Till RJ. A Simple Generalisation of the Area Under the ROC Curve for Multiple Class Classification Problems. *Machine Learning*. 2001.
17. scikit-learn official documentation: F1, Balanced Accuracy, Confusion Matrix, Brier Score and Probability Calibration; accessed 2026-07-27.
