# DAY 28 — EDA và Data Quality Audit cho Mendeley 4-Channel Hand-Gesture Dataset v2

> **Phiên bản:** v1.0 — kế thừa trực tiếp Day 25–27  
> **Mô hình thực hiện:** một người, làm tuần tự, mỗi bước có Input/Action/Output/Stop condition  
> **Dataset chính:** `mendeley-4channel-hand-gesture-v2`  
> **Task chính:** Task A — Gesture Recognition, sparse 4-channel engineering baseline  
> **Trạng thái bắt buộc:** `trainingAllowed=false`, `test_set_opened=false`, không tuning, không model fitting  
> **Phạm vi dữ liệu EDA:** chỉ `train + validation`; sealed test không được đọc để chọn preprocessing, feature, threshold hoặc narrative  
> **Kết quả cuối ngày hợp lệ:** `GO_FOR_DAY29_TRAINING_PREFLIGHT` hoặc `BLOCKED_WITH_EVIDENCE`; tuyệt đối không tạo metric giả khi dữ liệu thật chưa có.

---

## 0. Kết luận quan trọng trước khi bắt đầu

Tôi đã đối chiếu 11 artifact bạn gửi. Phần **governance và chuẩn hóa cấu trúc Day 27 đã hoàn thành tốt**, bao gồm:

- canonical source và DOI đã được xác minh;
- license CC BY 4.0 đã được ghi rõ;
- `grip → hand_close` đã có bằng chứng;
- 10 source gestures đã được khóa;
- bốn nhãn lõi được map vào ontology;
- sáu nhãn ngoài scope được bảo vệ bằng `unknown`;
- public dataset vẫn bị cấm dùng cho clinical claim và Motion Lab transfer claim.

Tuy nhiên, bộ artifact hiện tại cũng đang ghi rõ:

```yaml
archive_status: PENDING_DOWNLOAD
real_dataset_present: false
mapping_profile_verification_status: NOT_VERIFIED
data_hierarchy_status: PENDING_EXTRACTION
field_dictionary_status: PENDING_INSPECTION
file_inventory_status: PENDING_EXTRACTION
engineering_gate: PENDING_EXTERNAL_DATA
```

Vì vậy, **Day 28 phải có hai mode**, không được giả rằng EDA thật đã được chạy:

```text
MODE A — TOOLING / EXTERNAL-DATA BLOCKED
Day 27 governance complete, archive chưa có
→ kiểm tra tooling, đóng gói script, tạo report NOT_RUN
→ không sinh thống kê tín hiệu giả

MODE B — REAL EDA
Archive + inventory + field dictionary + mapping profile + metadata index
+ subject-safe split + sealed test + Engineering Gate PASS
→ chạy EDA thật trên train/validation
```

Đây không phải làm lại Day 27. Đây là cách **materialize phần external-data dependency** và chỉ chạy EDA khi gate thật sự mở.

---

# 1. Mục tiêu Day 28

Day 28 trả lời bảy câu hỏi:

1. Archive thực tế có khớp với paper và source record không?
2. Có đúng 40 subjects, 10 gestures, 5 repetitions và 4 channels không?
3. Tần số lấy mẫu, đơn vị, raw/processed và channel order có được chứng minh không?
4. Bốn lớp lõi có đủ support theo subject/repetition không?
5. Sáu gesture ngoài scope được loại khỏi **derived training view** nhưng vẫn giữ provenance thế nào?
6. Tín hiệu có NaN/Inf, flatline, clipping candidate, offset, độ dài bất thường hoặc nhiễu phổ đáng chú ý không?
7. Dataset đủ điều kiện cho experiment nào của Day 26 và không đủ điều kiện cho experiment nào?

Luồng chuẩn:

```text
Day27 manifests
→ preflight reconciliation
→ partition visibility guard
→ structural EDA
→ label/hierarchy audit
→ signal descriptive statistics
→ quality flag audit
→ domain-gap update
→ experiment eligibility update
→ Day28 readiness decision
```

---

# 2. Các quyết định không được mở lại

```text
Không đổi dataset primary chỉ vì EDA cho thấy dữ liệu khó.
Không đổi label ontology sau khi nhìn phân bố.
Không map unknown thành rest.
Không xóa raw rows/files của sáu gesture ngoài scope.
Không dùng test partition cho EDA.
Không fit scaler hoặc learned normalization trên toàn bộ dataset.
Không chọn filter/window/model bằng EDA trên test.
Không gọi mô tả trên public data là Noraxon compatibility.
Không suy performance khỏe mạnh sang bệnh nhân.
Không bật MFCV.
Không train model trong Day 28.
```

Điểm cần sửa cách hiểu:

> `unknown` không có nghĩa là xóa dữ liệu gốc. Sáu gesture ngoài scope phải được giữ trong raw registry và audit table. Chúng chỉ bị loại khỏi **derived four-class Task A view** bằng reason code `OUT_OF_SCOPE_LABEL`. Một phần của chúng có thể dùng sau này để nghiên cứu unknown-gesture abstention, nhưng không được dùng như fatigue labels.

Dataset này cung cấp bốn lớp lõi:

```text
rest
hand_close
wrist_flexion
wrist_extension
```

`hand_open` phải được ghi:

```yaml
status: UNSUPPORTED_BY_THIS_DATASET
```

Không được tạo class rỗng rồi báo như dataset năm lớp.

---

# 3. Cấu trúc repo áp dụng

Metadata được đặt dưới `data-platform`; raw archive và extracted signal nằm ngoài Git:

```text
semg-fatigue-platform/
├── data-platform/
│   └── datasets/
│       └── external/
│           └── mendeley-4channel-hand-gesture-v2/
│               ├── archive.sha256
│               ├── canonical-mapping-draft.yaml
│               ├── data-hierarchy.yaml
│               ├── data-quality-inventory.json
│               ├── dataset-source-record.yaml
│               ├── domain-gap-matrix.csv
│               ├── field-dictionary.csv
│               ├── file-inventory.csv
│               ├── label-dictionary.yaml
│               ├── license-record.yaml
│               ├── readiness-decision.yaml
│               └── day28-manifest-index.yaml
├── ai-core/
│   ├── configs/
│   │   ├── day28_eda.research.yaml
│   │   └── day28_quality_rules.provisional.yaml
│   └── data/day28/
├── docs/05-data/day28/
├── docs/learning/day28/
├── packages/common-schemas/json/
├── qa-validation/
└── scripts/
```

Controlled data storage, không commit Git:

```text
/data/datasets/external/mendeley-4channel-hand-gesture-v2/
├── source/
├── extracted/
├── metadata/
├── manifests/
├── derived/
│   └── taskA-core-4class/
└── evidence/day28/
```

---

# 4. Output bắt buộc của Day 28

Khi chạy real EDA, cần sinh:

```text
/data/datasets/external/mendeley-4channel-hand-gesture-v2/evidence/day28/
├── day28-preflight.json
├── observed-vs-documented-metadata.csv
├── partition-visibility-report.json
├── class-distribution.csv
├── subject-class-support.csv
├── repetition-audit.csv
├── excluded-label-audit.csv
├── file-level-statistics.csv
├── channel-level-statistics.csv
├── signal-quality-flags.csv
├── dataset-quality-summary.json
├── domain-gap-matrix.updated.csv
├── experiment-eligibility.updated.csv
├── eda-and-data-quality-report.md
├── dataset-card.md
└── day28-readiness-decision.yaml
```

Khi dữ liệu vẫn chưa có, chỉ được sinh:

```text
day28-preflight.json
eda-and-data-quality-report.md  # status NOT_RUN_BLOCKED_EXTERNAL_DATA
day28-readiness-decision.yaml  # BLOCKED_WITH_EVIDENCE
```

Không tạo bảng số liệu giả với số 0 để làm file “trông hoàn chỉnh”.

---

# PHẦN A — KIẾN THỨC PHẢI HỌC

## 5. Thống kê mô tả cơ bản

Với tín hiệu một kênh trong một file:

### Mean

\[
\bar{x}=\frac{1}{N}\sum_{i=1}^{N}x_i
\]

Mean lớn bất thường có thể gợi ý DC offset, nhưng không tự động kết luận cảm biến lỗi.

### Standard deviation

\[
s=\sqrt{\frac{1}{N-1}\sum_{i=1}^{N}(x_i-\bar{x})^2}
\]

STD mô tả độ phân tán quanh mean. Với tín hiệu gần zero-mean, STD và RMS có thể khá gần nhau nhưng không hoàn toàn giống.

### RMS

\[
RMS=\sqrt{\frac{1}{N}\sum_{i=1}^{N}x_i^2}
\]

RMS nhạy với amplitude scale, gain, unit, electrode contact và lực co. Không được so sánh RMS giữa nguồn nếu unit/protocol không tương thích.

### MAV

\[
MAV=\frac{1}{N}\sum_{i=1}^{N}|x_i|
\]

MAV cũng mô tả amplitude và thường rẻ tính toán.

### Median và MAD

\[
MAD = median(|x_i-median(x)|)
\]

Median/MAD bền vững hơn mean/STD trước spike. Day 28 dùng chúng để mô tả outlier, không dùng để tự động sửa raw signal.

## 6. Missingness và tỷ lệ lỗi

\[
nonfinite\_ratio=\frac{\#(NaN, +Inf, -Inf)}{N}
\]

- Một giá trị non-finite trong raw signal đã là vấn đề cần audit.
- Không được `fillna(0)` âm thầm.
- Nếu có quy tắc điền thiếu, quy tắc phải versioned và nằm sau quality decision.

## 7. Flatline và clipping candidate

### Flatline candidate

Một phép đo mô tả đơn giản:

\[
flatline\_ratio=\frac{\#(x_i=x_{i-1})}{N-1}
\]

Nó chỉ là heuristic. Tín hiệu số hóa có thể lặp mẫu tự nhiên; vì vậy Day 28 gắn cờ để review, không gọi đó là sensor failure tuyệt đối.

### Clipping candidate

Nếu rất nhiều samples bằng chính xác min hoặc max của file, có thể có saturation/clipping. Nhưng chưa biết ADC range thì chỉ được gọi `CLIPPING_CANDIDATE`.

## 8. Robust outlier

Robust z-score thường dùng:

\[
z_i^{robust}=0.6745\frac{x_i-median(x)}{MAD}
\]

Day 28 không xóa samples có robust z-score cao. Chỉ đếm và đánh dấu file/channel cần xem waveform.

## 9. Sampling và phổ

Nyquist:

\[
f_{Nyquist}=\frac{F_s}{2}
\]

Frequency resolution cơ bản:

\[
\Delta f=\frac{F_s}{N}
\]

Nếu sampling rate chưa được xác minh, mọi chỉ số Hz như MDF/MNF/powerline ratio phải bị khóa. Không được đoán sampling rate từ số rows.

## 10. Phân bố lớp và support

Một dataset có tổng số file cân bằng chưa chắc cân bằng theo subject. Cần kiểm:

```text
count by canonical label
count by source label
count by subject × canonical label
count by repetition × label
```

Cross-subject experiment chỉ hợp lệ khi lớp được hỗ trợ ở đủ nhiều subjects, không chỉ có nhiều windows.

## 11. Leakage ở Day 28

EDA cũng có thể gây leakage. Ví dụ sai:

```text
xem toàn bộ train + validation + test
→ chọn threshold loại outlier
→ báo test sau đó
```

Đúng:

```text
train: phát triển rule/threshold
validation: audit rule đã khóa
sealed test: không mở trong Day 28
```

---

# PHẦN B — KẾ HOẠCH THỰC THI

## Step 0 — Chạy regression Day 25–27

**Thời lượng:** 20 phút  
**Input:** repository sau Day 27.  
**Action:** chạy các checker tồn tại:

```bash
bash scripts/dev/run_day25_research_checks.sh
bash scripts/dev/run_day26_research_checks.sh
bash scripts/dev/run_day27_checks.sh

git status --short
```

**Output:**

```yaml
day25: PASS
day26: PASS
day27_tooling: PASS
working_tree: RECORDED
```

**Stop condition:** test seal đã mở, Day26 blueprint không valid hoặc repo có raw data bị stage.

---

## Step 1 — Reconcile 11 manifest Day 27

**Thời lượng:** 35 phút  
**Input:** thư mục manifest permanent.  
**Action:**

```bash
python scripts/data/day28_preflight.py \
  --manifest-dir data-platform/datasets/external/mendeley-4channel-hand-gesture-v2 \
  --output qa-validation/evidence/day28-preflight.json
```

Tool kiểm:

- source và license verified;
- archive có hash thật hay còn `PENDING_DOWNLOAD`;
- inventory có data rows;
- field dictionary có header thật;
- mapping profile còn placeholder không;
- hierarchy đã quan sát hay chưa;
- test seal có còn đóng;
- label mapping có đúng bốn lớp lõi không;
- `hand_open` có bị tạo giả không;
- sáu non-target labels có được giữ provenance không.

**Output:** một trong hai:

```yaml
mode: TOOLING_ONLY_BLOCKED_EXTERNAL_DATA
```

hoặc:

```yaml
mode: READY_FOR_REAL_EDA
```

**Stop condition:** safety flag bị đổi thành `clinical_use_allowed=true`, `motion_lab_transfer_verified=true` hoặc `training_execution_allowed=true`.

---

## Step 2 — Materialize external data dependency, không đoán schema

**Thời lượng:** 45–90 phút, chỉ khi archive đã có thể tải hợp lệ.  
**Input:** controlled archive, source DOI/URL, hash.  
**Action:** hoàn tất các artifact còn pending:

```text
archive.sha256
file-inventory.csv
data-hierarchy.yaml
field-dictionary.csv
canonical-mapping-draft.yaml
metadata-index.csv
group-split.v1.json
test-seal.v1.json
readiness-decision.yaml
```

Quy tắc:

- `dataset-source-record.yaml` mô tả **expected from paper**;
- inventory mô tả **observed from files**;
- nếu expected ≠ observed, ghi conflict; không tự sửa record để che conflict;
- profile chỉ chuyển `verification_status: VERIFIED` khi source columns, Fs, unit, channel order và path regex có evidence;
- group split phải có `subject_id` làm outer group;
- raw 10 labels vẫn được giữ trong metadata index;
- derived 4-class view chỉ là một cột/view bổ sung.

**Output:** `Engineering Gate = GO_FOR_DAY28_EDA` hoặc reason-coded `BLOCKED`.

**Stop condition:** không xác định được Fs/unit/channel fields, không có subject IDs, archive hash mismatch hoặc label/file structure không khớp evidence.

---

## Step 3 — Khóa partition visibility

**Thời lượng:** 25 phút  
**Input:** metadata index và split manifest.  
**Action:** tool phải lọc trước khi đọc signal:

```python
allowed_partitions = {"train", "validation"}
assert "test" not in loaded_partitions
```

CLI:

```bash
python scripts/data/day28_run_eda.py \
  --manifest-dir data-platform/datasets/external/mendeley-4channel-hand-gesture-v2 \
  --data-root /data/datasets/external/mendeley-4channel-hand-gesture-v2/extracted \
  --metadata-index /data/datasets/external/mendeley-4channel-hand-gesture-v2/metadata/index.csv \
  --output-dir /data/datasets/external/mendeley-4channel-hand-gesture-v2/evidence/day28 \
  --partitions train validation
```

**Output:** `partition-visibility-report.json` với test rows = 0.

**Stop condition:** metadata index không có `partition`, bất kỳ test row nào được load, hoặc same subject xuất hiện nhiều partition.

---

## Step 4 — Structural EDA

**Thời lượng:** 55 phút  
**Input:** train/validation metadata index, file inventory.  
**Action:** tính và đối chiếu:

```text
observed files
observed subjects
observed source labels
observed canonical labels
repetitions per subject/label
rows/samples per file
channels per file
duration per file
file format and encoding consistency
exact duplicate hashes
```

Expected từ source record:

```yaml
participants: 40
gestures: 10
repetitions_per_participant: 5
channels: 4
```

Nhưng expected không được thay thế observed.

**Output:**

```text
observed-vs-documented-metadata.csv
class-distribution.csv
subject-class-support.csv
repetition-audit.csv
```

**Stop condition:** subject count < 10, channel count không phải 4 mà không có giải thích, duplicate files giữa partitions hoặc core class bị thiếu toàn bộ.

---

## Step 5 — Label và ontology audit

**Thời lượng:** 50 phút  
**Input:** label dictionary + metadata index.  
**Action:** tạo ba tầng label:

```text
source_label          # giữ nguyên 10 gesture
canonical_label       # 4 target + unknown
analysis_eligibility  # CORE_TASK_A | UNKNOWN_GESTURE_AUDIT | EXCLUDED
```

Quy tắc:

```yaml
Rest: CORE_TASK_A/rest
Grip: CORE_TASK_A/hand_close
Flexion: CORE_TASK_A/wrist_flexion
Extension: CORE_TASK_A/wrist_extension
6 remaining gestures: UNKNOWN_GESTURE_AUDIT/unknown
hand_open: UNSUPPORTED_BY_THIS_DATASET
```

**Output:**

```text
excluded-label-audit.csv
label-coverage-summary.json
```

**Stop condition:** unknown bị xóa khỏi raw registry, unknown bị map thành rest, hoặc pipeline tạo class `hand_open` không có source evidence.

---

## Step 6 — File-level và channel-level signal statistics

**Thời lượng:** 75 phút  
**Input:** source files, verified mapping profile.  
**Action:** không filter, không normalize learned; chỉ mô tả:

```text
sample_count
duration_s
nonfinite_ratio
mean/median/std/MAD
RMS/MAV
p01/p99
robust_range
flatline_ratio
clipping_candidate_ratio
DC-offset ratio
50-Hz/60-Hz powerline candidate ratio nếu Fs verified
low-frequency ratio nếu raw signal và Fs verified
```

**Output:**

```text
file-level-statistics.csv
channel-level-statistics.csv
signal-quality-flags.csv
```

Mọi flag phải có:

```text
rule_id
severity
observed_value
provisional_threshold
reason
human_review_required
```

**Stop condition:** script tự sửa raw signal, tự loại channel hoặc gọi heuristic là clinical threshold.

---

## Step 7 — Distribution and consistency audit

**Thời lượng:** 45 phút  
**Input:** channel statistics và label hierarchy.  
**Action:** so sánh descriptive distribution theo:

```text
channel
subject
canonical label
source label
partition
```

Kiểm:

- subject có amplitude scale khác cực lớn;
- một channel thường xuyên zero/flatline;
- duration khác nhau bất thường giữa repetitions;
- core labels có sample count quá lệch;
- unknown gesture có signal distribution rất giống core class, hữu ích cho future abstention audit;
- validation distribution khác train nhưng không dùng validation để fit lại rule trong cùng vòng.

**Output:** `dataset-quality-summary.json` và chart PNG theo từng biểu đồ riêng.

**Stop condition:** dùng test để giải thích distribution hoặc thay threshold liên tục sau khi nhìn validation.

---

## Step 8 — Update domain-gap và Day 26 experiment eligibility

**Thời lượng:** 45 phút  
**Input:** EDA/QC summary + Day26 experiment matrix.  
**Action:** khóa eligibility:

### Có thể đủ điều kiện sau quality gate

```text
E-A00 dummy majority — 4-class core
E-A01 dummy stratified — 4-class core
E-A02 LDA F1 — nếu feature prerequisites pass
E-A03 Logistic F1
E-A04 Linear SVM F1
E-A05 RF F2 — chỉ khi Fs/raw signal đủ cho frequency features
E-P00 normalization-only — nếu personalization protocol tách được
E-P01 2 reps calibration — nếu còn test reps độc lập
E-P02 3 reps calibration — nếu còn test reps độc lập
E-F03 unknown-gesture abstention arm — partial eligibility only
```

### Không đủ điều kiện trên dataset này

```text
E-A06 cross-session — trừ khi archive chứng minh multi-session
E-A07 cross-day — trừ khi archive chứng minh multi-day
E-A08 electrode reapply — không có reapply event
E-P03 5 reps calibration — nếu dataset chỉ có 5 reps thì không còn locked test reps
E-F00/E-F01/E-F02/E-F04 fatigue lanes — không có fatigue context
E-C00…E-C03 — không phải primary Task C corpus theo contracts hiện tại
```

Điểm quan trọng: sáu unknown gestures chỉ hỗ trợ `unknown_gesture` arm của E-F03; chúng không biến Mendeley thành fatigue dataset.

**Output:** `experiment-eligibility.updated.csv` và `domain-gap-matrix.updated.csv`.

---

## Step 9 — Viết dataset card và EDA report

**Thời lượng:** 50 phút  
**Input:** toàn bộ evidence Day28.  
**Action:** report phải có:

1. nguồn, version, DOI, license;
2. expected vs observed;
3. hierarchy và split;
4. label mapping và excluded labels;
5. signal statistics;
6. quality flags;
7. experiment eligibility;
8. domain gap;
9. limitations;
10. no clinical/Noraxon transfer claim.

**Output:**

```text
eda-and-data-quality-report.md
dataset-card.md
```

Không dùng câu:

```text
Dữ liệu sạch hoàn toàn.
Dataset phù hợp Noraxon.
Model sẽ chạy tốt trên Vinmec.
```

Dùng câu:

```text
Dataset đủ/không đủ điều kiện cho engineering baseline trong phạm vi đã khai báo.
Compatibility với Noraxon Motion Lab chưa được xác minh.
```

---

## Step 10 — Day 28 readiness gate

**Thời lượng:** 25 phút  
**Input:** preflight, label audit, signal quality, split integrity.  
**PASS hợp lệ:**

```yaml
status: GO_FOR_DAY29_TRAINING_PREFLIGHT
public_dataset_engineering_ready: true
public_baseline_training_eligible: true
training_execution_allowed: false
test_set_sealed: true
supported_class_count: 4
hand_open_supported: false
motion_lab_transfer_verified: false
clinical_use_allowed: false
```

**BLOCK hợp lệ:**

```yaml
status: BLOCKED_WITH_EVIDENCE
training_execution_allowed: false
blockers:
  - <reason code>
```

Day 28 không tự cấp quyền training. Day 29 vẫn cần authorization record, environment lock thật, experiment manifest và leakage preflight.

---

## Step 11 — Regression, commit và tag

**Thời lượng:** 30 phút  
**Action:**

```bash
bash scripts/dev/run_day28_checks.sh
```

Commit additive, tránh overwrite file bạn đã hoàn thiện:

```bash
git add \
  ai-core/configs/day28_*.yaml \
  ai-core/data/day28 \
  data-platform/datasets/external/mendeley-4channel-hand-gesture-v2/day28-manifest-index.yaml \
  docs/05-data/day28 \
  docs/learning/day28 \
  docs/plans/DAY28_EXECUTION_PLAN.md \
  packages/common-schemas/json/day28-*.schema.json \
  qa-validation \
  scripts/data/day28_*.py \
  scripts/dev/run_day28_checks.sh

git diff --staged --check
git diff --staged --stat

git commit -m "day28: add train-validation EDA and data quality audit gate"
git tag day28-eda-data-quality-v1.0
```

Không stage:

```text
/data/datasets/**
*.zip raw dataset
raw signal CSV/MAT/C3D
plots chứa identifier không kiểm soát
```

---

# PHẦN C — ACCEPTANCE CRITERIA

## 12. Definition of Done

### Tooling mode

```text
[ ] Day25–27 regression PASS.
[ ] 11 manifest được đọc và hash.
[ ] Preflight phát hiện đúng PENDING_EXTERNAL_DATA.
[ ] Không sinh fake EDA statistics.
[ ] NOT_RUN report được sinh.
[ ] training_execution_allowed=false.
```

### Real EDA mode

```text
[ ] Archive hash hợp lệ.
[ ] File inventory không còn placeholder.
[ ] Field dictionary dựa trên actual headers.
[ ] Mapping profile VERIFIED, không còn <REQUIRED>.
[ ] Data hierarchy OBSERVED.
[ ] Metadata index có subject/repetition/source label.
[ ] Group split không overlap.
[ ] Test partition không được load.
[ ] Expected vs observed được đối chiếu.
[ ] Raw 10 labels được giữ provenance.
[ ] Derived core view có đúng 4 labels.
[ ] hand_open được ghi UNSUPPORTED, không tạo giả.
[ ] Six non-target labels có exclusion audit.
[ ] File/channel statistics được tạo.
[ ] NaN/Inf/flatline/clipping/DC/powerline candidates được audit.
[ ] Quality flags reason-coded và provisional.
[ ] Domain-gap matrix được cập nhật.
[ ] Day26 experiment eligibility được cập nhật.
[ ] Dataset card + EDA report tồn tại.
[ ] Day28 readiness decision rõ ràng.
[ ] training_execution_allowed=false.
[ ] Không raw data/model artifact trong Git/ZIP.
```

---

# PHẦN D — NHỮNG ĐIỂM CẦN HỌC KỸ

## 13. Bắt buộc hiểu trước Day 29

1. Mean, median, variance, standard deviation.
2. RMS và MAV khác nhau thế nào.
3. MAD và robust outlier vì sao bền hơn STD.
4. Sampling rate, Nyquist và duration.
5. PSD/FFT chỉ có nghĩa theo Hz khi Fs đúng.
6. Class balance toàn dataset khác class support theo subject.
7. Unknown label khác rest.
8. Raw registry khác derived training view.
9. Train/validation/test có vai trò khác nhau.
10. EDA cũng có thể gây leakage.

## 14. Câu hỏi tự kiểm tra

1. Vì sao không xóa sáu gesture ngoài scope khỏi raw registry?
2. Vì sao dataset thiếu `hand_open` phải là four-class dataset thay vì five-class dataset có class count bằng 0?
3. Tại sao `grip → hand_close` có thể xác nhận nhưng `abduction → hand_open` không được tự suy ra?
4. Vì sao E-P03 không khả thi nếu mỗi subject chỉ có 5 repetitions và cả 5 dùng để calibration?
5. Tại sao unknown gestures có thể hữu ích cho abstention nhưng không có giá trị làm fatigue labels?
6. Vì sao một file có RMS cao chưa chắc bị lỗi?
7. Vì sao powerline ratio không được tính khi sampling rate chưa biết?
8. Vì sao threshold QC trong Day28 chỉ là provisional engineering rule?
9. Vì sao test set không được dùng trong EDA?
10. `GO_FOR_DAY29_TRAINING_PREFLIGHT` khác `training_execution_allowed=true` thế nào?

---

# PHẦN E — HANDOFF DAY 29

Day 29 chỉ được xem xét training baseline khi:

```yaml
day28_status: GO_FOR_DAY29_TRAINING_PREFLIGHT
public_baseline_training_eligible: true
training_execution_allowed: false
test_set_sealed: true
resolved_environment_lock_present: true
experiment_manifest_valid: true
license_gate_passed: true
leakage_preflight_passed: true
human_review_plan_present: true
```

Day 29 phải bắt đầu bằng authorization, không bắt đầu bằng `model.fit()`.

Dataset scope cho Day 29 nếu gate PASS:

```yaml
task: TaskA
class_count: 4
classes:
  - rest
  - hand_close
  - wrist_flexion
  - wrist_extension
unsupported_class:
  - hand_open
unknown_gesture_corpus:
  preserved: true
  training_as_core_class: false
clinical_use_allowed: false
motion_lab_transfer_verified: false
```

---

# 15. Câu chốt quản trị

> Day 28 không nhằm tạo thật nhiều biểu đồ. Day 28 nhằm chứng minh dataset có cấu trúc, nhãn, chất lượng và split đủ tin cậy cho một experiment engineering cụ thể; đồng thời biết chính xác phần nào chưa thể dùng. Khi archive vẫn chưa có, kết quả đúng là `BLOCKED_WITH_EVIDENCE`, không phải một báo cáo EDA giả.
