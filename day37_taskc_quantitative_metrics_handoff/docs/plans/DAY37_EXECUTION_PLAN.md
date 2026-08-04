# DAY 37 — TASK C QUANTITATIVE METRICS CONTRACTS

**Dự án:** MyoLab-AI  
**Ngày:** Day 37  
**Workstream:** Task C — Quantitative Assessment  
**Phạm vi:** Repeatability, Similarity và Co-contraction  
**Đơn vị chính:** repetition và session  
**Điều kiện vào ngày:** Day 36 Context Engine đã hoàn tất real handoff  
**Sealed test:** tiếp tục đóng  
**Notebook:** chỉ minh họa synthetic scenarios; implementation chính nằm trong package

---

## 0. Kết luận điều hành

Day 37 không huấn luyện thêm model và không tạo fatigue diagnosis. Mục tiêu là khóa ba hợp đồng định lượng:

```text
Q1 — Repeatability
Q2 — Similarity
Q3 — Co-contraction
```

Các output có thể được Day 36 Context Engine sử dụng như **evidence lane**, nhưng không được tự động biến thành:

```text
fatigued = true
abnormal = true
treatment recommendation
```

### Giới hạn dữ liệu hiện tại

- Mendeley và GRABMyo có thể hỗ trợ repeatability/similarity nếu repetition metadata đầy đủ.
- Co-contraction chỉ hợp lệ khi có:
  - muscle identity;
  - side;
  - agonist–antagonist pair;
  - synchronized channels;
  - envelope preprocessing;
  - normalization/reference contract.
- Không được suy luận agonist–antagonist từ tên kênh `CH1–CH4`, `F1–F16`, `W1–W12`.
- Vì vậy co-contraction real run trên hai public dataset mặc định là:

```text
NOT_ELIGIBLE_ANATOMICAL_MAPPING_UNVERIFIED
```

cho đến khi provenance chứng minh mapping hợp lệ.

---

# 1. Câu hỏi Day 37 phải trả lời

## Repeatability

1. Cùng subject, cùng protocol và cùng class có cho kết quả ổn định giữa repetitions không?
2. Within-session và between-session khác nhau thế nào?
3. Metric nào ổn định: RMS, MAV, MDF, MNF, feature vector hay Task A confidence?
4. Subject nào có repeatability thấp?
5. Repeatability thấp có liên quan QC, session/day hoặc electrode reapplication không?

## Similarity

1. Hai repetitions giống nhau về hướng feature vector hay cả magnitude?
2. Similarity theo class có cao hơn cross-class không?
3. Subject-specific template có ổn định không?
4. Một repetition khác template do signal quality hay genuine variation?
5. Similarity metric nào phù hợp với scale/gain sensitivity?

## Co-contraction

1. Hai muscle channels có thực sự là agonist–antagonist pair không?
2. Activation envelope có cùng time base và normalization không?
3. Overlap về magnitude và duration là bao nhiêu?
4. Metric có đủ điều kiện để so sánh giữa sessions/subjects không?
5. Output có được dùng làm quantitative context mà không tạo diagnosis không?

---

# 2. Nguyên tắc bất biến

```text
[1] Không random-window statistics.
[2] Không coi overlapping windows là independent repetitions.
[3] Không pooled Mendeley + GRABMyo.
[4] Không mở sealed test.
[5] Không direct cross-subject amplitude comparison nếu chưa normalize hợp lệ.
[6] Không gọi repeatability cao là clinical normality.
[7] Không gọi similarity thấp là pathology.
[8] Không tính co-contraction nếu muscle-pair mapping chưa xác minh.
[9] Không dùng Task C metrics làm hard fatigue label.
[10] Quality fail phải block hoặc abstain.
[11] Context Engine chỉ được dùng Task C output kèm provenance/supportability.
[12] MFCV ineligible không block basic Task C metrics nếu Task C prerequisites vẫn đạt.
```

---

# 3. Input contract

## 3.1. Repetition-level feature input

Mỗi repetition row:

```text
dataset_id
dataset_view_id
subject_id
session_id
day_id
protocol_id
protocol_version
task_label
repetition_id
feature_arm
feature_vector
feature_columns
quality_status
source_feature_sha256
split_version
preprocessing_policy_id
```

`feature_vector` phải có fixed column order đã khóa.

## 3.2. Envelope input cho co-contraction

Mỗi synchronized sample hoặc envelope frame:

```text
subject_id
session_id
protocol_id/version
repetition_id
time_seconds
muscle_id
side
functional_role
pair_id
envelope_value
envelope_unit
normalization_method
sampling_rate_hz
quality_status
source_signal_sha256
```

`functional_role`:

```text
agonist
antagonist
```

Không được tự gán role từ channel index.

---

# 4. Q1 — Repeatability contract

## 4.1. Phân biệt thuật ngữ

```text
Within-session repeatability:
cùng subject, cùng session, cùng protocol, repeated trials

Between-session reproducibility:
cùng subject, khác session/day, cùng compatible protocol

Agreement:
mức gần nhau về giá trị tuyệt đối

Consistency:
mức giữ thứ hạng/pattern dù có systematic shift
```

Day 37 ưu tiên **agreement** cho quantitative assessment.

## 4.2. Đơn vị tính

```text
subject × protocol × task_label × metric_id
```

Không trộn classes hoặc protocol versions.

## 4.3. Primary repeatability metrics

### A. Absolute difference

Với hai repetitions:

\[
AD=|x_1-x_2|
\]

### B. Symmetric relative difference

\[
SRD=\frac{2|x_1-x_2|}{|x_1|+|x_2|+\epsilon}
\]

Không dùng khi denominator quá nhỏ mà không flag.

### C. Within-subject coefficient of variation

Chỉ cho positive ratio-scale metrics:

\[
CV_w=100\frac{SD(x_1,\ldots,x_R)}{Mean(x_1,\ldots,x_R)}
\]

Eligibility:

```text
R >= 3
mean > epsilon
metric declared ratio_scale_positive = true
```

Không dùng CV cho signed mean, skewness hoặc values gần 0.

### D. Median absolute deviation ratio

Robust sensitivity:

\[
rMAD=\frac{1.4826\cdot MAD(x)}{|Median(x)|+\epsilon}
\]

### E. ICC absolute agreement

Primary reliability statistic khi cohort đủ:

```text
ICC(A,1)
```

Requirements:

- ít nhất 3 subjects;
- mỗi subject có cùng số repeated measurements hoặc documented missingness handling;
- cùng protocol/task/metric;
- report CI;
- không tính ICC từ windows.

Nếu implementation chưa có validated ICC routine, Day 37 chỉ tạo contract và block claim.

### F. Bland–Altman

Với pairwise repeated measurement:

```text
bias
SD of differences
95% limits of agreement
```

Between-session comparison phải báo Bland–Altman thay vì chỉ correlation.

## 4.4. Feature-vector repeatability

Feature vector \(x_r\) được đánh giá bằng:

- cosine similarity;
- Pearson correlation;
- normalized Euclidean distance;
- optional concordance correlation.

Không lấy trung bình 14 features khác đơn vị trước khi scale theo contract.

## 4.5. Repeatability output

```text
repeatability_id
subject_id
session_scope
protocol_id/version
task_label
metric_id
repetition_count
absolute_difference
symmetric_relative_difference
within_subject_cv_percent
robust_mad_ratio
icc_type
icc_value
icc_ci_low
icc_ci_high
bland_altman_bias
loa_low
loa_high
supportability
reason_codes
provenance
```

---

# 5. Q2 — Similarity contract

## 5.1. Similarity không phải một khái niệm duy nhất

### Shape/direction similarity

```text
cosine similarity
Pearson correlation
```

Ít nhạy magnitude hơn.

### Absolute agreement similarity

```text
normalized Euclidean distance
Lin concordance correlation
```

Nhạy cả shift và scale.

### Template similarity

```text
subject-specific class centroid
population class centroid
session-specific template
```

Template source phải khai báo rõ.

## 5.2. Primary metrics

### Cosine similarity

\[
cos(x,y)=\frac{x^\top y}{\|x\|\|y\|}
\]

Block nếu norm gần 0.

### Pearson correlation

Tính sau khi center từng vector. Block nếu vector constant.

### Normalized Euclidean distance

Sau frozen scaler:

\[
d_n(x,y)=\frac{\|x-y\|_2}{\sqrt{p}}
\]

Không fit scaler trên evaluation repetitions.

### Template distance

\[
d(x_{eval},\mu_{calibration,class})
\]

Template phải được tạo chỉ từ allowed calibration repetitions.

## 5.3. Comparison lanes

```text
within-subject same-class
within-subject cross-class
cross-subject same-class
cross-session same-subject same-class
```

Headline Task C ưu tiên:

```text
within-subject same-class
cross-session same-subject same-class
```

Không dùng cross-subject magnitude similarity nếu normalization không đủ.

## 5.4. Similarity output

```text
similarity_id
subject_id
reference_repetition_id
query_repetition_id
reference_scope
task_label_reference
task_label_query
cosine_similarity
pearson_correlation
normalized_euclidean_distance
template_source
feature_arm
scaler_hash
supportability
reason_codes
provenance
```

## 5.5. Threshold policy

Day 37 không khóa universal normal/abnormal threshold.

Allowed:

```text
descriptive distribution
subject-specific percentile
training-subject-derived engineering threshold
```

Bị cấm:

```text
similarity < 0.7 = abnormal patient
```

---

# 6. Q3 — Co-contraction contract

## 6.1. Eligibility gate

Co-contraction chỉ chạy khi tất cả điều kiện đạt:

```text
verified agonist–antagonist mapping
same side
synchronized time base
same active phase
compatible envelope units
quality pass/warning
normalization method declared
minimum overlap duration
```

Fail states:

```text
NOT_ELIGIBLE_ANATOMICAL_MAPPING_UNVERIFIED
NOT_ELIGIBLE_UNSYNCHRONIZED
NOT_ELIGIBLE_UNIT_MISMATCH
NOT_ELIGIBLE_ACTIVE_PHASE_MISSING
QUALITY_BLOCKED
```

## 6.2. Envelope preprocessing

Canonical lane:

```text
raw sEMG
→ QC
→ bandpass/notch per preprocessing version
→ full-wave rectification
→ low-pass envelope
→ baseline correction
→ optional MVC/reference normalization
→ active-phase crop
```

Day 37 không định nghĩa lại filter coefficients; sử dụng preprocessing policy đã version.

## 6.3. Primary co-contraction metrics

Gọi hai envelope không âm là \(A(t)\) và \(B(t)\).

### A. Instantaneous ratio CCI

\[
CCI(t)=\frac{2\min(A(t),B(t))}{A(t)+B(t)+\epsilon}
\]

Aggregate:

```text
mean_cci
median_cci
q90_cci
```

Range gần `[0,1]` khi envelopes không âm.

### B. Overlap area ratio

\[
OAR=\frac{\int\min(A(t),B(t))dt}
{\int\max(A(t),B(t))dt+\epsilon}
\]

### C. Simultaneous activation duration

Với thresholds hợp lệ:

\[
SADF=\frac{\#\{t:A(t)>\theta_A \land B(t)>\theta_B\}}
{\#\{t \in active\ phase\}}
\]

Threshold source:

```text
baseline-noise-derived
protocol-reference-derived
MVC-percent-derived
```

Không dùng một magic threshold chung cho mọi subject.

### D. Coactivation load

\[
CAL=\int \min(A(t),B(t))dt
\]

Chỉ so sánh across sessions/subjects nếu normalization tương thích.

## 6.4. Interpretation boundary

Hợp lệ:

> Co-contraction index cao hơn trong repetition X theo contract Y.

Không hợp lệ:

> Subject có pathological co-contraction.

Không được dùng co-contraction đơn độc để xác nhận fatigue context.

## 6.5. Co-contraction output

```text
cocontraction_id
subject_id
session_id
protocol_id/version
repetition_id
pair_id
agonist_muscle_id
antagonist_muscle_id
side
normalization_method
mean_cci
median_cci
q90_cci
overlap_area_ratio
simultaneous_activation_duration_fraction
coactivation_load
active_duration_seconds
supportability
reason_codes
preprocessing_policy_id
source_signal_hashes
```

---

# 7. Supportability taxonomy

```text
SUPPORTED
SUPPORTED_WITH_WARNING
INSUFFICIENT_REPETITIONS
INCOMPATIBLE_PROTOCOL
INCOMPATIBLE_NORMALIZATION
ZERO_NORM_VECTOR
CONSTANT_VECTOR
MISSING_METADATA
NOT_ELIGIBLE_ANATOMICAL_MAPPING_UNVERIFIED
NOT_ELIGIBLE_UNSYNCHRONIZED
QUALITY_BLOCKED
```

`not eligible` không được ghi thành giá trị `0`.

---

# 8. Tích hợp với Day 36 Context Engine

Task C gửi event:

```text
metric_family
metric_id
value
reference_scope
supportability
reason_codes
provenance
```

Context Engine có thể dùng:

- repeatability degradation;
- cross-session similarity degradation;
- co-contraction trend;

như evidence lane `performance_consistency`.

Context Engine không được:

```text
Task C metric
→ hard fatigue diagnosis
```

Rules:

```text
unsupported Task C metric → ignored with reason
quality blocked → context QUALITY_BLOCKED
single Task C metric change → at most POSSIBLE context
multi-lane evidence required for SUPPORTED context
```

---

# 9. Quy trình thực thi Day 37

## Bước 0 — Day 36 handoff gate

### Input

- `day36-final-manifest.json`;
- context taxonomy;
- provenance contract;
- language guard evidence.

### Action

Verify:

```text
Day36 status = GO_FOR_DAY37...
confidence_may_increase = false
hard_fatigue_diagnosis_allowed = false
language_guard = pass
```

### Output

```text
day37-input-gate.json
```

### Stop condition

Dừng nếu Day 36 mới chỉ tooling-ready nhưng người chạy yêu cầu real Task C claims.

---

## Bước 1 — Dataset and protocol eligibility

### Input

Repetition feature tables và channel/muscle metadata.

### Action

Tạo eligibility matrix:

```text
dataset × metric_family × protocol
```

Expected:

```text
Mendeley:
repeatability = potentially eligible
similarity = potentially eligible
co-contraction = blocked until anatomical mapping verified

GRABMyo:
repeatability = potentially eligible
similarity = potentially eligible
co-contraction = blocked unless official muscle mapping supports pairs
```

### Output

```text
day37-metric-eligibility.json
```

---

## Bước 2 — Freeze Task C metric registry

### Input

Metric definitions và preprocessing versions.

### Action

Khóa:

- formula;
- unit;
- aggregation unit;
- eligibility;
- epsilon;
- missing-value behavior;
- version.

### Output

```text
taskc-metric-registry.yaml
```

---

## Bước 3 — Build repetition table

### Input

Day 31 features + Day 33 repetition metadata.

### Action

Pivot/aggregate đúng:

```text
subject × session × protocol × class × repetition
```

### Output

```text
taskc-repetition-features.parquet
taskc-repetition-feature-manifest.json
```

### Stop condition

Dừng khi repetition IDs thiếu hoặc pooled datasets.

---

## Bước 4 — Compute repeatability

### Input

Repeated repetitions cùng subject/protocol/class.

### Action

Tính:

- AD;
- SRD;
- CV khi eligible;
- robust MAD ratio;
- ICC/Bland–Altman nếu design đủ.

### Output

```text
repeatability-results.csv
repeatability-subject-summary.csv
repeatability-supportability.csv
```

---

## Bước 5 — Compute similarity

### Input

Repetition vectors và frozen scaler/template source.

### Action

Tính:

- cosine;
- Pearson;
- normalized Euclidean;
- template distance.

### Output

```text
similarity-results.csv
similarity-subject-summary.csv
similarity-distributions.json
```

---

## Bước 6 — Co-contraction eligibility gate

### Input

Muscle/channel mapping và synchronized envelopes.

### Action

Fail closed nếu mapping không verified.

### Output

```text
cocontraction-eligibility.json
```

Mendeley/GRABMyo không được tự động pass.

---

## Bước 7 — Compute co-contraction khi eligible

### Input

Synchronized agonist/antagonist envelopes.

### Action

Tính CCI, OAR, SADF và CAL.

### Output

```text
cocontraction-results.csv
cocontraction-pair-summary.csv
```

---

## Bước 8 — Quality and sensitivity audit

Kiểm tra:

- epsilon sensitivity;
- envelope smoothing version;
- normalization method;
- minimum repetition count;
- outlier sensitivity;
- session/day effects;
- missing metadata.

Output:

```text
taskc-sensitivity-report.json
```

---

## Bước 9 — Synthetic notebook scenarios

Notebook chỉ minh họa:

```text
high vs low repeatability
same-shape different-magnitude similarity
constant/zero vector blocks
low vs high co-contraction envelopes
unsynchronized/mapping-ineligible scenario
```

Không dùng notebook làm production implementation.

---

## Bước 10 — Context Engine integration test

Synthetic events:

```text
supported repeatability degradation
unsupported co-contraction
quality-blocked similarity
single metric change
multiple Task C evidence lanes
```

Output:

```text
day37-day36-integration-report.json
```

---

## Bước 11 — Final handoff

Valid statuses:

```text
GO_FOR_DAY38_TASK_C_VALIDATION
GO_FOR_DAY38_WITH_METRIC_LIMITATIONS
BLOCKED_WITH_EVIDENCE
```

---

# 10. Output repository

```text
MyoLab-AI/
├── ai-core/
│   ├── configs/day37_*.yaml
│   ├── quantitative/day37/
│   └── pipelines/day37_*.py
├── data-platform/contracts/day37/
├── docs/
│   ├── 09-quantitative/day37/
│   ├── note/day37/
│   └── plans/DAY37_EXECUTION_PLAN.md
├── notebooks/
│   └── Day37_TaskC_Quantitative_Metrics_Scenarios.ipynb
├── packages/common-schemas/json/
├── qa-validation/
└── scripts/
```

---

# 11. Outputs bắt buộc

```text
taskc-metric-registry.yaml
day37-metric-eligibility.json
repeatability-results.csv
similarity-results.csv
cocontraction-eligibility.json
cocontraction-results.csv hoặc explicit blocked evidence
taskc-sensitivity-report.json
day37-day36-integration-report.json
day37-final-manifest.json
Day37_TaskC_Quantitative_Metrics_Scenarios.ipynb
```

---

# 12. Acceptance criteria

```text
[ ] Day36 real handoff verified
[ ] repetition/session units frozen
[ ] no random-window statistics
[ ] repeatability agreement/consistency distinguished
[ ] CV only used on eligible positive ratio-scale metrics
[ ] ICC not computed from windows
[ ] Bland–Altman included for agreement studies
[ ] similarity scaler/template provenance stored
[ ] universal abnormal similarity threshold prohibited
[ ] co-contraction anatomical mapping verified
[ ] synchronized envelopes verified
[ ] normalization method stored
[ ] ineligible metric returns state, not zero
[ ] quality fail blocks
[ ] Task C does not create fatigue diagnosis
[ ] context integration preserves supportability
[ ] notebook is illustrative only
[ ] sealed test remains closed
```

---

# 13. Kết luận

Day 37 hoàn thành khi hệ thống có thể trả lời một cách tái lập:

```text
Repetition có ổn định không?
Hai repetitions giống nhau ở khía cạnh nào?
Hai muscle được xác minh có co-contract ở mức nào?
Metric có đủ điều kiện để diễn giải không?
```

mà không vượt quá bằng chứng để tạo diagnosis, normality claim hoặc treatment recommendation.
