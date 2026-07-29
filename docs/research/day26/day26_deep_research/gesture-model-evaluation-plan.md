# Gesture Model Evaluation Plan — Day 26 Blueprint

**Artifact:** `docs/08-validation-qa/gesture-model-evaluation-plan.md`  
**schema_version:** `1.0`  
**status:** `PROVISIONAL_LOCKED_FOR_DAY26_BLUEPRINT`  
**trainingAllowed:** `false`  
**Owner đề xuất:** Biostatistics / Validation Lead  
**Review bắt buộc:** DSP Lead, ML Lead, Clinical AI Safety Lead, Human Reviewer

> Tài liệu này là **evaluation contract**, không phải báo cáo model performance. Mọi trường kết quả trong Day 26 phải là `NOT_RUN`.

---

## 1. Mục tiêu

Khóa trước khi training:

- primary và secondary classification metrics;
- unit aggregation `window → repetition → subject`;
- participant-level confidence interval;
- operational latency/memory/throughput metrics;
- probability-calibration policy;
- selective prediction, coverage và abstention policy;
- unsafe prediction rate;
- fold ownership của mọi learned decision;
- report schema và acceptance criteria.

Không thuộc scope:

- training/tuning;
- mở test set;
- chọn model winner;
- đặt clinical threshold;
- tuyên bố clinical performance;
- dùng Task C như classifier nếu target chưa được khóa.

---

## 2. Input và output

### 2.1. Input bắt buộc

| Input | Required state |
|---|---|
| Day 26 Research Protocol | `PROVISIONAL_LOCKED_FOR_DAY26` |
| Validation and Leakage Review | Group hierarchy và nested policy đã khóa |
| Feature Engineering Review | Window/normalization/selection policy đã khóa |
| Classical Model Candidate Review | Candidate model IDs đã khóa |
| Personalization Strategy | Target calibration/test separation đã khóa |
| Day 25 subject/session split manifest | Có group IDs và hash; test unopened |
| Class ontology | Versioned; ít nhất Task A supported classes |
| Abstention reason registry | Versioned; primary precedence rõ |

### 2.2. Output bắt buộc

| Output | Path/contract |
|---|---|
| Research rationale | `docs/research/day26/08-metrics-calibration-abstention.md` |
| Evaluation plan | Tài liệu hiện tại |
| Machine-readable config | `ai-core/configs/evaluation_regimes.research.yaml` |
| Future prediction ledger | `qa-validation/evidence/<run_id>/prediction-ledger.parquet` |
| Future metric summary | `qa-validation/evidence/<run_id>/evaluation-summary.json` |
| Future failure cases | `qa-validation/evidence/<run_id>/failure-cases.csv` |
| Future reliability figures | `qa-validation/evidence/<run_id>/calibration/` |
| Future risk–coverage data | `qa-validation/evidence/<run_id>/selective/risk-coverage.csv` |

Day 26 chỉ tạo contract/config; các future outputs phải ghi `NOT_RUN`.

---

## 3. Quyết định khóa

```yaml
primary_metric: subject_macro_repetition_macro_f1
primary_prediction_unit: repetition
primary_inference_unit: subject
confidence_interval: participant_cluster_bootstrap_95
balanced_accuracy_role: mandatory_secondary_macro_recall_audit
probability_gate_required: true
threshold_selection_fold: grouped_inner_validation_only
outer_test_selection_allowed: false
random_window_split_allowed: false
human_review_required: true
trainingAllowed: false
```

---

## 4. Data hierarchy và immutable IDs

```text
subject_id
  └── day_id
       └── session_id
            └── trial_id
                 └── repetition_id
                      └── segment_id
                           └── window_id
```

Minimum immutable keys in prediction ledger:

```text
source_id
subject_id
session_id
day_id
trial_id
repetition_id
window_id
outer_fold_id
inner_fold_or_oof_id
true_label
predicted_label_or_abstain
```

Rules:

1. Split raw registry at subject/session/trial level before windowing.
2. Sibling windows from one repetition cannot cross partitions.
3. Subject/session IDs are governance/grouping fields, never predictors.
4. Every prediction row points to model, feature, preprocess, calibrator and threshold versions.

---

## 5. Step-by-step execution contract

## Step 0 — Verify blueprint-only mode

**Input**

- Git branch/worktree.
- Day 25 readiness and test seal.

**Action**

```bash
# Planning commands only; no fit/evaluate command is allowed.
git status --short
# Validate trainingAllowed=false in config.
```

**Output**

```yaml
blueprint_mode: true
trainingAllowed: false
test_opened: false
```

**Failure**

- `trainingAllowed=true`.
- Test manifest missing or `opened=true`.

---

## Step 1 — Freeze class ontology and class order

**Input**

- Task A class registry.
- Supported/unknown/transition definition.

**Action**

Lock:

```yaml
class_order:
  - rest
  - hand_open
  - hand_close
  - wrist_flexion
  - wrist_extension
```

Class list above is an example from project scope and must match the versioned ontology actually selected. No class may be silently dropped because one fold lacks support.

**Output**

- `class_ontology_version`.
- `class_order`.
- per-class minimum support policy.

**Failure**

- Class order inferred from alphabetic sorting at evaluation time.
- Unknown/transition mixed into a supported gesture without explicit ontology decision.

---

## Step 2 — Freeze repetition aggregation

**Input**

- Window predictions/scores.
- QC and usable-window flags.
- Score semantics.

**Action**

Preferred rule:

```text
eligible calibrated probability vectors
→ arithmetic mean by repetition
→ argmax
```

Fallback for non-probability scores:

```text
eligible raw decision score vectors
→ predeclared model-specific aggregation
→ predicted class
```

**Output**

```yaml
aggregation_method_id: probability_mean_or_locked_score_rule
minimum_usable_window_ratio: null
abstain_on_insufficient_windows: true
```

`minimum_usable_window_ratio` remains `NOT_VERIFIED` until protocol/QC workstream sets it.

**Failure**

- Majority vote/mean score chosen after seeing outer-test results.
- QC-failed windows included without explicit policy.

---

## Step 3 — Compute classification metrics at repetition level

**Input**

- Outer-test/OOF repetition predictions.
- Fixed class order.

**Action**

Compute:

```text
per_class_precision
per_class_recall
per_class_f1
macro_f1
balanced_accuracy
confusion_matrix_count
confusion_matrix_row_normalized
multiclass_mcc_optional
macro_auroc_optional
```

**Output**

- One metric bundle per subject.
- One pooled repetition bundle.
- One bundle per outer fold.

**Failure**

- Only accuracy is emitted.
- Missing class support is silently excluded.
- Headline metric computed at window level.

---

## Step 4 — Compute primary metric

For subject \(s\):

\[
MacroF1_s = \frac{1}{K}\sum_{k=1}^{K}F1_{s,k}
\]

Primary point estimate:

\[
SubjectMacroMacroF1 = \frac{1}{S}\sum_{s=1}^{S}MacroF1_s
\]

**Input**

- Per-subject repetition confusion matrices.

**Output**

```yaml
metric_id: subject_macro_repetition_macro_f1
value: NOT_RUN
n_subjects: NOT_RUN
n_repetitions: NOT_RUN
```

**Failure**

- Weight subject by number of windows.
- Report pooled Macro F1 as the only primary result.

---

## Step 5 — Compute participant-level confidence interval

**Input**

- Immutable OOF prediction ledger.
- Subject clusters.

**Action**

```text
for b in 1..2000:
  resample subjects with replacement
  retain all nested sessions/repetitions for selected subject
  recompute complete aggregation + primary metric
return percentile 2.5% and 97.5%
```

Optional for cross-session/day:

```text
subject bootstrap
  → session/day bootstrap within subject
```

**Output**

```yaml
ci_level: 0.95
method: participant_cluster_bootstrap
n_resamples: 2000
seed: 260826
lower: NOT_RUN
upper: NOT_RUN
```

**Failure**

- Bootstrap windows independently.
- Construct CI from outer-fold means as if folds were independent trials.

---

## Step 6 — Report fold, subject and session variance

**Input**

- Fold/subject/session metric bundles.

**Output**

```text
outer_fold_mean_sd
outer_fold_median_iqr
subject_mean_sd
subject_median_iqr
subject_p10_min_max
within_subject_session_sd
cross_day_delta
reapply_delta
```

**Failure**

- Overall mean only.
- No worst-subject or failure-case report.

---

## Step 7 — Measure operational metrics

**Input**

- Instrumented runtime timestamps.
- Runtime/hardware manifest.

**Timestamp contract**

```text
t_window_start
t_window_close
t_feature_start
t_feature_end
t_model_start
t_model_end
t_calibrator_end
t_abstention_end
t_decision_ready
t_user_visible
```

**Output**

```text
p50_pipeline_compute_latency_ms
p95_pipeline_compute_latency_ms
p50_end_to_end_latency_ms
p95_end_to_end_latency_ms
signal_to_feedback_latency_ms
feature_extraction_time_ms
model_inference_time_ms
calibration_mapping_time_ms
abstention_decision_time_ms
memory_peak_rss_mb
memory_steady_state_rss_mb
model_artifact_size_mb
throughput_windows_per_s
real_time_factor
dropped_window_ratio
calibration_duration_s
calibration_failure_rate
remeasurement_rate
```

**Failure**

- Timing model function only and calling it end-to-end latency.
- Counting abstention as dropped window.
- Reporting p95 without sample count or runtime manifest.

---

## Step 8 — Calibrate score semantics

**Input**

- Cross-fitted inner-validation raw scores.
- Candidate calibrators.
- Group-aware splits.

**Candidate methods**

```text
none
sigmoid_platt
isotonic
multiclass_temperature_provisional
vector_or_dirichlet_later
```

**Action**

1. Fit base model on inner model-fit groups.
2. Generate scores on disjoint inner calibration groups.
3. Fit calibrator only on those scores/labels.
4. Evaluate candidate calibrator on cross-fitted inner predictions.
5. Select/freeze method in inner loop.
6. Evaluate once on outer test.

**Output**

```yaml
score_semantics: raw_score|uncalibrated_confidence_score|calibrated_class_probability
calibrator_id: NOT_RUN
calibration_method: NOT_RUN
```

**Probability gate**

All must pass:

- values non-negative;
- row sum approximately 1;
- no model/calibration data overlap;
- group-aware inner selection;
- outer-test independent evaluation;
- Brier + classwise reliability report;
- scope and limitations declared.

**Failure**

- Raw SVM margin or KNN vote fraction labeled probability.
- Default non-grouped `CalibratedClassifierCV` used without explicit group splits.

---

## Step 9 — Compute calibration metrics

**Input**

- Repetition-level probability vectors only after probability-shape validation.

**Required**

```text
multiclass_brier_unscaled_0_to_2
classwise_brier
log_loss_optional
confidence_ece_equal_frequency_15
classwise_ece
reliability_diagram_top_label
reliability_diagram_per_class
```

**Output**

- Before/after calibration report.
- Bin counts and boundaries.
- Subject-level Brier distribution and CI.

**Failure**

- ECE without binning details.
- Reliability plot from training predictions.
- “Calibrated” conclusion based only on visual diagonal proximity.

---

## Step 10 — Freeze selective-prediction threshold in inner validation

**Input**

- Cross-fitted inner calibrated scores.
- Candidate threshold grid.
- Predeclared constraints.

**Objective**

```text
maximize coverage
subject to selective risk, unsafe accept and class/subject coverage constraints
```

**Output**

```yaml
threshold_policy_id: NOT_RUN
threshold_source: grouped_inner_validation
threshold_value: NOT_RUN
outer_test_used_for_selection: false
```

**Failure**

- Threshold selected by outer-test risk–coverage curve.
- Threshold changed after failure-case inspection on test.

---

## Step 11 — Compute selective metrics

**Input**

- Attempted, model-eligible, covered and abstained units.

**Required**

```text
system_coverage
model_coverage
selective_accuracy
selective_risk
selective_macro_f1
selective_balanced_accuracy
abstention_rate
class_conditional_coverage
subject_level_coverage
risk_coverage_curve
```

**Output format**

```yaml
attempted_units: NOT_RUN
model_eligible_units: NOT_RUN
covered_units: NOT_RUN
system_coverage: NOT_RUN
model_coverage: NOT_RUN
selective_accuracy: NOT_RUN
selective_risk: NOT_RUN
selective_macro_f1: NOT_RUN
subject_coverage_p10: NOT_RUN
```

**Failure**

- Accuracy reported without coverage.
- Covered-set metrics without abstention-aware confusion matrix.

---

## Step 12 — Compute unsafe prediction rate

**Input**

- Adjudicated/deterministic `mandatory_abstain` reference.
- Emitted prediction/abstention decision.

**Definitions**

```text
unsafe_prediction_event =
  prediction_emitted == true
  AND mandatory_abstain == true
```

\[
UPR = \frac{unsafe\ prediction\ events}{mandatory\ abstain\ units}
\]

Also report:

```text
unsafe_prediction_rate_overall
mandatory_abstain_prevalence
```

**Output**

```yaml
unsafe_prediction_events: NOT_RUN
mandatory_abstain_units: NOT_RUN
unsafe_prediction_rate: NOT_RUN
unsafe_prediction_rate_overall: NOT_RUN
mandatory_abstain_prevalence: NOT_RUN
```

**Failure**

- Denominator is all windows only, diluting rare hazardous cases.
- `mandatory_abstain` inferred from the model’s own low score rather than an independent/adjudicated reference.

---

## Step 13 — Produce failure-case and subgroup reports

**Input**

- Prediction ledger.
- Predeclared subgroup registry.

**Output**

- Worst class.
- Worst subject.
- Worst eligible predeclared subgroup.
- High-score errors.
- Unsafe accepts.
- False abstentions.
- Calibration failures.
- QC/protocol bypass incidents.

**Failure**

- Subgroups selected after test results solely to produce a favorable narrative.
- Groups with tiny `n` presented as stable estimates.

---

## 6. Metric dictionary

| Metric ID | Unit | Direction | Required | Notes |
|---|---|---:|---:|---|
| `subject_macro_repetition_macro_f1` | subject/repetition | Higher | Primary | Equal subject weight |
| `pooled_repetition_macro_f1` | repetition | Higher | Secondary | Operational pooled view |
| `balanced_accuracy` | repetition/subject | Higher | Yes | Macro recall |
| `per_class_recall` | class | Higher | Yes | With support |
| `per_class_precision` | class | Higher | Yes | With support |
| `confusion_matrix_count` | repetition | N/A | Yes | Fixed class order |
| `confusion_matrix_row_normalized` | repetition | N/A | Yes | Error destination |
| `multiclass_mcc` | repetition | Higher | Optional | Global consistency |
| `macro_auroc_hand_till` | repetition score | Higher | Exploratory | Before abstention; ranking only |
| `multiclass_brier_unscaled` | repetition probability | Lower | Calibration primary | Range 0–2 |
| `confidence_ece` | repetition probability | Lower | Diagnostic | 15 equal-frequency bins |
| `classwise_ece` | class probability | Lower | Diagnostic | Report support |
| `system_coverage` | attempted unit | Higher conditional | Yes | Covered / attempted |
| `model_coverage` | eligible unit | Higher conditional | Yes | Covered / eligible |
| `selective_accuracy` | covered unit | Higher | Yes | Must pair with coverage |
| `selective_risk` | covered unit | Lower | Yes | 1 − selective accuracy |
| `unsafe_prediction_rate` | mandatory-abstain unit | Lower | Yes for Task B safety eval | Conditional false accept |
| `p95_end_to_end_latency_ms` | decision | Lower | Yes | After window close to user-visible |
| `dropped_window_ratio` | scheduled window | Lower | Yes | Excludes abstention |
| `calibration_duration_s` | calibration attempt | Lower | Yes for personalization | User-facing wall-clock |
| `calibration_failure_rate` | calibration attempt | Lower | Yes for personalization | Reason-coded |
| `remeasurement_rate` | session | Lower | Yes | QC/protocol/calibration reasons |

---

## 7. Abstention reason registry

```yaml
primary_reason_precedence:
  - QC_FAIL
  - UNSUPPORTED_PROTOCOL_OR_ANATOMY
  - CALIBRATION_FAILURE_OR_EXPIRED
  - UNKNOWN_GESTURE
  - TRANSITION
  - FATIGUE_DRIFT_OUTSIDE_SUPPORT
  - LOW_MODEL_CONFIDENCE
  - QC_WARNING_POLICY
```

Required fields:

```text
primary_reason
secondary_reason_codes[]
trigger_source
trigger_version
mandatory_or_optional
human_review_required
remeasurement_suggested
```

No output may recommend treatment or automatically stop exercise.

---

## 8. Report schema

```yaml
schema_version: "1.0"
status: "NOT_RUN"
run_id: ""
regime_id: ""
task_id: "TaskA"
trainingAllowed: false
provenance:
  dataset_manifest_hash: ""
  split_manifest_hash: ""
  test_seal_hash: ""
  class_ontology_version: ""
  preprocess_version: ""
  feature_version: ""
  model_version: ""
  calibrator_version: ""
  threshold_policy_version: ""
counts:
  subjects: null
  sessions: null
  repetitions: null
  windows: null
classification:
  primary_metric_id: "subject_macro_repetition_macro_f1"
  primary_value: null
  ci95: {lower: null, upper: null, method: "participant_cluster_bootstrap"}
  balanced_accuracy: null
  per_class: {}
calibration:
  score_semantics: "raw_score"
  brier_multiclass_unscaled: null
  ece: null
  classwise_ece: {}
selective_prediction:
  attempted_units: null
  model_eligible_units: null
  covered_units: null
  system_coverage: null
  model_coverage: null
  selective_accuracy: null
  selective_risk: null
  unsafe_prediction_rate: null
operational:
  p50_pipeline_compute_latency_ms: null
  p95_pipeline_compute_latency_ms: null
  p50_end_to_end_latency_ms: null
  p95_end_to_end_latency_ms: null
  memory_peak_rss_mb: null
  throughput_windows_per_s: null
  dropped_window_ratio: null
human_review:
  required: true
  status: "not_reviewed"
limitations: []
not_verified: []
```

---

## 9. Engineering failure gates

Các gate này là **engineering hypothesis**, không phải clinical acceptance thresholds.

| Gate ID | Pass condition | Failure handling |
|---|---|---|
| `EVAL-G01` | Primary metric vượt best dummy baseline | Reject candidate or investigate pipeline |
| `EVAL-G02` | Development target ≥ best dummy + 0.10 Macro F1 | Mark `BELOW_ENGINEERING_TARGET` if not met |
| `EVAL-G03` | Không supported class nào recall=0 trong ≥2 outer folds | `CLASS_COLLAPSE_FAIL` |
| `EVAL-G04` | Primary CI được tính ở participant level | `INFERENCE_INVALID` |
| `EVAL-G05` | Coverage + selective performance + reason breakdown đồng thời có | `REPORT_INCOMPLETE` |
| `EVAL-G06` | Probability gate pass trước dùng từ probability | `SEMANTIC_SAFETY_FAIL` |
| `EVAL-G07` | Calibrator/threshold source là grouped inner validation | `LEAKAGE_CRITICAL` |
| `EVAL-G08` | Test seal unopened during development | `TEST_CONTAMINATION_INCIDENT` |
| `EVAL-G09` | Worst-subject/class/failure cases được báo | `REPORT_INCOMPLETE` |
| `EVAL-G10` | Human review status present | `GOVERNANCE_FAIL` |

---

## 10. Negative tests bắt buộc

| Test ID | Invalid input/behavior | Expected rejection |
|---|---|---|
| `NEG-MET-001` | `primary_metric=accuracy` | Config invalid |
| `NEG-MET-002` | `evaluation_unit=window` cho headline | Config invalid |
| `NEG-MET-003` | `bootstrap_unit=window` | Config invalid |
| `NEG-MET-004` | Macro F1 không có fixed class order | Config invalid |
| `NEG-CAL-001` | `score_semantics=probability` nhưng calibrator/evaluation absent | Semantic validation fail |
| `NEG-CAL-002` | Calibrator fit data overlaps classifier fit data | Leakage fail |
| `NEG-CAL-003` | Calibration method selected on outer test | Leakage fail |
| `NEG-SEL-001` | Selective accuracy present, coverage missing | Report validation fail |
| `NEG-SEL-002` | Threshold source = outer test | Leakage fail |
| `NEG-SEL-003` | UPR denominator = attempted units only | Metric definition fail |
| `NEG-OPS-001` | End-to-end latency measured only around `model.predict` | Instrumentation fail |
| `NEG-GOV-001` | Human review omitted | Governance fail |

---

## 11. Acceptance criteria / Definition of Done

- [ ] `trainingAllowed=false` ở mọi artifact.
- [ ] Primary metric là `subject_macro_repetition_macro_f1`.
- [ ] Balanced Accuracy được định nghĩa là macro recall và là secondary bắt buộc.
- [ ] Fixed class ontology/order được version hóa.
- [ ] Window→repetition→subject aggregation được khóa.
- [ ] Participant bootstrap CI, không window bootstrap.
- [ ] Fold summary, subject variance, session variance và failure cases có contract.
- [ ] p50/p95 latency có timestamp boundary rõ.
- [ ] Memory, throughput, dropped-window, calibration duration/failure, remeasurement có định nghĩa.
- [ ] Brier convention `[0,2]` cho multiclass được ghi rõ.
- [ ] ECE binning và classwise ECE được khóa.
- [ ] Probability semantic gate có đủ điều kiện.
- [ ] Threshold source là grouped inner validation.
- [ ] System coverage và model coverage tách riêng.
- [ ] Selective accuracy/risk luôn đi cùng coverage.
- [ ] Abstention reason precedence được version hóa.
- [ ] Unsafe prediction rate có `mandatory_abstain` denominator.
- [ ] Không có absolute clinical threshold giả.
- [ ] Human review bắt buộc.
- [ ] Test set remains sealed/unopened.
- [ ] YAML config parse thành công.

---

## 12. Kết luận bắt buộc

### 12.1. Primary metric là gì?

**Subject-macro repetition-level Macro F1** (`subject_macro_repetition_macro_f1`).

### 12.2. Balanced Accuracy đóng vai trò gì?

Secondary metric bắt buộc để audit macro recall và phát hiện model bỏ sót lớp; không thay Macro F1 vì không phạt precision error đầy đủ.

### 12.3. Confidence score khi nào được gọi là probability?

Chỉ sau group-aware fold-contained calibration, method freeze trước outer test, probability-shape validation, và independent evaluation bằng Brier + classwise/reliability diagnostics trong scope đã khai báo.

### 12.4. Coverage và accuracy phải báo cùng nhau thế nào?

Báo tối thiểu `system_coverage`, `model_coverage`, `selective_accuracy`, `selective_risk`, class-conditional coverage, subject-level coverage và risk–coverage curve. Không báo “accuracy X%” độc lập.

### 12.5. Threshold được chọn ở fold nào?

**Grouped inner-validation fold**, dùng cross-fitted development predictions. Outer/sealed test không tham gia chọn threshold.

### 12.6. Unsafe prediction rate được định nghĩa ra sao?

Số lần hệ thống phát supported prediction trong unit mà contract/reference yêu cầu phải abstain, chia cho tổng số mandatory-abstain units. Báo thêm overall rate và mandatory-abstain prevalence.

---

## 13. Go status

**GO_WITH_CONDITIONS** cho Day 26 Experiment Blueprint.

Điều kiện:

- Không thay metric hierarchy sau model results.
- Không mở test set.
- Không gọi score là probability trước probability gate.
- Clinical/operational thresholds vẫn `NOT_VERIFIED`.
- Human review phải ký duyệt mandatory-abstain reference trước safety evaluation.
