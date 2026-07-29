# DAY 29 — EDA đa ngày và Data Quality Gate cho GRABMyo

> **Phiên bản:** v1.0 — kế thừa trực tiếp Day 25–28  
> **Mô hình thực hiện:** một người, làm tuần tự, mỗi bước có Input / Action / Output / Stop condition  
> **Dataset chính:** `grabmyo-v1.1.0` hoặc bản dataset GRABMyo mà Day 27-equivalent của bạn đã khóa  
> **Task chính:** Task A — Gesture Recognition; bổ sung đánh giá cross-day/cross-session  
> **Trạng thái bắt buộc:** `trainingAllowed=false`, `testSetOpened=false`, không fitting, không tuning, không mở sealed test  
> **Phạm vi EDA:** chỉ `train + validation`; test chỉ được kiểm tra tính tồn tại/hashes qua manifest, không được đọc signal  
> **Kết quả cuối ngày:** `GO_FOR_DAY30_HARMONIZATION` hoặc `BLOCKED_WITH_EVIDENCE`

---

## 0. Tóm tắt điều hành

Day 29 không lặp lại Day 28 một cách máy móc. Mendeley 4-channel chủ yếu giúp kiểm tra pipeline sparse-channel và ontology bốn lớp; GRABMyo có giá trị khác biệt ở cấu trúc nhiều người, nhiều ngày và nhiều kênh hơn. Vì vậy Day 29 tập trung vào ba câu hỏi mà Day 28 chưa trả lời được:

1. Dữ liệu có nhất quán giữa các ngày hay không?
2. Channel/montage và phân bố biên độ có thay đổi theo ngày đến mức nào?
3. GRABMyo đủ điều kiện cho experiment `cross-subject`, `cross-day`, personalization và unknown-gesture audit nào của Day 26?

Luồng chính:

```text
Day27-equivalent GRABMyo manifests
→ preflight và provenance reconciliation
→ khóa partition visibility
→ audit hierarchy subject/day/session/repetition
→ structural EDA
→ signal-quality audit
→ cross-day drift audit
→ feature eligibility
→ experiment eligibility
→ readiness decision cho Day 30
```

Day 29 **không** được diễn giải thay đổi giữa ngày là mỏi cơ. Day-to-day shift có thể đến từ tháo–đeo điện cực, da, mồ hôi, posture, force level, sensor orientation, channel mapping hoặc protocol execution.

---

# 1. Mục tiêu Day 29

Day 29 phải trả lời chín câu hỏi:

1. Archive, file inventory, license và source record có còn nhất quán với Day 27-equivalent không?
2. Cấu trúc thực tế có đủ `subject → day → session → repetition` hay chỉ một phần?
3. Có record bị thiếu ngày, thiếu gesture, thiếu repetition hoặc channel không?
4. Label ontology đã được map có căn cứ và không biến `unknown` thành `rest` chưa?
5. Tần số lấy mẫu, unit, raw/processed state và channel order có nhất quán giữa file/ngày không?
6. Có NaN/Inf, flatline, clipping candidate, DC offset, độ dài bất thường hoặc channel dropout không?
7. Các feature group F0/F1/F2/F4 của Day 26 có đủ điều kiện không?
8. Cross-day drift có được mô tả theo subject/gesture/channel mà không quy kết nguyên nhân không?
9. Dataset có đủ điều kiện chuyển sang Day 30 harmonization với Mendeley không?

---

# 2. Các quyết định không được mở lại

```text
Không thay đổi source/license vì EDA khó.
Không dùng random-window split.
Không sinh window trước khi khóa subject/day/session/repetition partition.
Không đọc signal thuộc test partition.
Không map unknown/unsupported gesture thành rest.
Không gọi ngày khác là fatigue state.
Không gọi raw classifier score là probability.
Không bật MFCV chỉ vì dataset có nhiều channel.
Không gộp GRABMyo và Mendeley trong Day 29.
Không train model trong Day 29.
Không tạo metric model hoặc benchmark giả.
Không suy public healthy performance sang Motion Lab/Vinmec/bệnh nhân.
```

---

# 3. Input bắt buộc

## 3.1. Input governance từ Day 27-equivalent

Dataset root dự kiến:

```text
data-platform/datasets/external/grabmyo-v1.1.0/
├── dataset-source-record.yaml
├── license-record.yaml
├── archive.sha256
├── file-inventory.csv
├── data-hierarchy.yaml
├── field-dictionary.csv
├── label-dictionary.yaml
├── canonical-mapping-draft.yaml
├── domain-gap-matrix.csv
├── data-quality-inventory.json
└── readiness-decision.yaml
```

Tên folder có thể khác nếu bạn đã khóa ID khác. Không đổi tên mù quáng; cập nhật `dataset_root` trong config Day 29.

## 3.2. Input kỹ thuật cần có để chạy EDA thật

```text
metadata-index.csv
split-manifest.csv hoặc partition column trong metadata-index.csv
test-seal.yaml/json
canonical signal files hoặc adapter có thể đọc được
```

`metadata-index.csv` tối thiểu cần các cột:

```text
record_id
subject_id
day_id
session_id
repetition_id
source_label
canonical_label
partition
signal_path
sampling_rate_hz
signal_unit
channel_count
```

Các cột nên có:

```text
trial_id
gesture_id
channel_columns
source_file_sha256
adapter_id
adapter_version
mapping_profile_version
```

## 3.3. Input kế thừa Day 26

- Validation hierarchy và grouped split policy.
- Feature groups F0–F4.
- Experiment matrix.
- Evaluation metric contract.
- Reproducibility/training policy.
- Registry và clinical-claim guardrails.

---

# 4. Output bắt buộc

Khi dữ liệu thật sẵn sàng:

```text
/data/datasets/external/grabmyo-v1.1.0/evidence/day29/
├── day29-preflight.json
├── partition-visibility-report.json
├── observed-vs-documented-metadata.csv
├── subject-day-coverage.csv
├── subject-day-gesture-support.csv
├── repetition-audit.csv
├── label-audit.csv
├── file-level-statistics.csv
├── channel-level-statistics.csv
├── signal-quality-flags.csv
├── cross-day-feature-summary.csv
├── cross-day-drift-summary.csv
├── cross-day-drift-observations.md
├── feature-eligibility.yaml
├── experiment-eligibility.yaml
├── dataset-quality-summary.json
├── eda-and-data-quality-report.md
└── day29-readiness-decision.yaml
```

Nếu input thật chưa được mount hoặc gate chưa mở, chỉ được sinh:

```text
day29-preflight.json
eda-and-data-quality-report.NOT_RUN.md
day29-readiness-decision.yaml
```

Không dùng số 0 để giả lập EDA đã chạy.

---

# 5. Cấu trúc repository

```text
semg-fatigue-platform/
├── ai-core/
│   ├── configs/
│   │   ├── day29_grabmyo_eda.research.yaml
│   │   ├── day29_grabmyo_quality_rules.provisional.yaml
│   │   └── day29_cross_day_drift.research.yaml
│   └── data/day29/
│       ├── contracts.py
│       ├── manifest_io.py
│       ├── partition_guard.py
│       ├── signal_loader.py
│       ├── hierarchy_audit.py
│       ├── label_audit.py
│       ├── descriptive_stats.py
│       ├── signal_quality.py
│       ├── cross_day_drift.py
│       ├── feature_eligibility.py
│       └── readiness.py
├── data-platform/datasets/external/grabmyo-v1.1.0/
│   └── day29-manifest-index.yaml
├── docs/05-data/day29/
├── docs/note/day29/
├── docs/plans/DAY29_EXECUTION_PLAN.md
├── packages/common-schemas/json/
├── qa-validation/
└── scripts/
```

Raw/public signal vẫn nằm ngoài Git. Repo chỉ giữ manifest, schema, config, code, report và evidence nhỏ không chứa raw signal.

---

# PHẦN A — KIẾN THỨC CẦN HỌC KỸ

## 6. Hierarchical/repeated-measures data

Một subject tạo ra nhiều ngày, mỗi ngày nhiều repetition và mỗi repetition nhiều window. Các quan sát này không độc lập:

```text
subject
└── day
    └── session
        └── repetition
            └── window
```

Nếu chia random theo window, cùng một repetition có thể xuất hiện ở train và test. Model sẽ nhận ra “dấu vân tay” của subject/session thay vì học gesture.

### Khái niệm phải hiểu

- **Independent unit:** subject là đơn vị độc lập mạnh nhất.
- **Repeated measure:** nhiều record từ cùng subject.
- **Cluster:** nhóm observations cùng subject/day/session.
- **Within-subject shift:** khác biệt giữa các ngày của cùng người.
- **Between-subject variation:** khác biệt giữa người.

### Output học tập

Bạn phải tự giải thích được:

> Vì sao 100.000 windows không có nghĩa là 100.000 mẫu độc lập nếu chúng chỉ đến từ 43 người?

---

## 7. Robust statistics cho sEMG

### Median và MAD

\[
MAD = median\left(|x_i - median(x)|\right)
\]

Để đưa MAD về scale gần standard deviation của phân bố chuẩn:

\[
\sigma_{robust} \approx 1.4826 \times MAD
\]

Dùng median/MAD giúp hạn chế ảnh hưởng của spike, clipping và artifact.

### Robust day-to-day shift score

Với feature `f` của hai ngày A và B:

\[
Z_{robust} = \frac{median(f_B)-median(f_A)}{1.4826\times pooledMAD + \epsilon}
\]

Trong đó:

\[
pooledMAD = \frac{MAD_A + MAD_B}{2}
\]

Ý nghĩa:

- gần 0: median khá giống nhau;
- độ lớn tăng: shift tương đối lớn so với độ phân tán nội tại;
- không phải p-value;
- không chứng minh fatigue/electrode shift; chỉ là mô tả.

### RMS ratio

\[
R = \frac{median(RMS_B)}{median(RMS_A)+\epsilon}
\]

RMS ratio nhạy với unit, gain, contact, force và montage. Chỉ dùng khi unit/channel semantics tương thích.

---

## 8. Phân biệt drift với fatigue

Day-to-day drift có thể do:

```text
electrode reattachment
sensor orientation
skin impedance
sweat/contact
gain/unit mismatch
posture/arm position
force level
protocol execution
channel order
actual physiological fatigue/recovery
```

Không có independent fatigue label thì không được viết:

```text
MDF giảm giữa Day 1 và Day 3 → subject mỏi hơn
```

Cách viết đúng:

```text
MDF distribution ở Day 3 thấp hơn Day 1 trong các record đủ điều kiện.
Nguyên nhân chưa xác định; cần đối chiếu protocol, force, QC và electrode setup.
```

---

## 9. Channel montage và domain gap

GRABMyo có cấu hình channel khác Mendeley 4-channel và khác Noraxon site. Bạn cần phân biệt:

- **channel count:** có bao nhiêu chuỗi tín hiệu;
- **channel order:** thứ tự các kênh;
- **electrode montage:** bố trí vật lý;
- **muscle mapping:** kênh đại diện cơ nào;
- **derived bipolar channel:** hiệu giữa hai điện cực;
- **sensor ID:** định danh phần cứng;
- **channel semantics:** ý nghĩa của kênh.

Có cùng số channel không đồng nghĩa cùng input domain.

---

## 10. Sampling rate và frequency eligibility

Nyquist:

\[
f_{Nyquist}=\frac{f_s}{2}
\]

Để tính MDF/MNF đáng tin, cần biết:

- sampling rate thật;
- raw/processed state;
- filter đã áp dụng;
- window length;
- PSD method;
- channel unit;
- artifact policy.

Frequency feature được `ELIGIBLE` chỉ khi tất cả điều kiện trên có provenance.

---

# PHẦN B — KẾ HOẠCH THỰC THI TỪNG BƯỚC

## Bước 0 — Tạo branch và snapshot

**Input**

- Repository đã hoàn thành Day 28.
- GRABMyo Day 27-equivalent artifacts.

**Action**

```bash
git switch -c day29/grabmyo-eda-qc

git status --short
```

Tạo hash snapshot các manifest GRABMyo:

```bash
find data-platform/datasets/external/grabmyo-v1.1.0 \
  -maxdepth 1 -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > qa-validation/evidence/day29-input-manifest-hashes.sha256
```

**Output**

- Branch riêng.
- Hash ledger.
- Không raw signal trong Git.

**Stop condition**

- Có raw/public archive được stage vào Git.
- Working tree có thay đổi chưa hiểu nguồn gốc.

---

## Bước 1 — Chạy regression Day 28

**Input:** codebase sau Day 28.

**Action:**

```bash
bash scripts/dev/run_day28_checks.sh
```

**Output:** Day 28 regression `PASS`.

**Stop condition:** regression fail. Không tiếp tục bằng cách bỏ test.

---

## Bước 2 — Preflight GRABMyo

**Input**

- Dataset root.
- Config Day 29.
- Test seal.

**Action**

```bash
python scripts/data/day29_preflight.py \
  --config ai-core/configs/day29_grabmyo_eda.research.yaml \
  --output qa-validation/evidence/day29-preflight.json
```

Preflight kiểm tra:

```text
source record
license record
archive hash
file inventory
field dictionary
hierarchy
label dictionary
mapping profile
readiness decision
metadata index
partition declaration
test seal
signal files existence
```

**Output**

```yaml
mode: READY_FOR_REAL_EDA | TOOLING_ONLY_BLOCKED
training_allowed: false
test_signal_access_allowed: false
blockers: []
```

**Stop condition**

- License chưa pass.
- Test seal missing/opened.
- Metadata index không có group keys.
- Mapping profile chưa xác minh nhưng code cố chạy EDA.

---

## Bước 3 — Khóa partition visibility

**Input:** metadata index.

**Action**

```bash
python scripts/data/day29_audit_partition_visibility.py \
  --metadata-index /data/.../metadata-index.csv \
  --allowed-partitions train validation \
  --output /data/.../evidence/day29/partition-visibility-report.json
```

Guard phải:

- từ chối record `partition=test`;
- từ chối path nằm dưới thư mục test;
- ghi hash/index count nhưng không đọc signal test;
- từ chối missing partition.

**Output:** report với số record train/validation và số test record chỉ từ manifest.

**Stop condition:** script EDA nhận path test.

---

## Bước 4 — Audit hierarchy

**Input:** metadata index chỉ train/validation.

**Action:** kiểm tra uniqueness của:

```text
record_id
subject_id + day_id + session_id + repetition_id + canonical_label
source_file_sha256
```

Tạo các bảng:

```text
subject-day-coverage.csv
subject-day-gesture-support.csv
repetition-audit.csv
```

Kiểm tra:

- subject thiếu ngày;
- day không đồng nhất;
- duplicate repetition;
- gesture thiếu theo subject/day;
- session/repetition IDs rỗng;
- same file hash xuất hiện ở nhiều partition.

**Output:** hierarchy status `VERIFIED`, `PARTIAL` hoặc `CONFLICTING`.

**Stop condition:** overlap train/validation/test ở subject/session/repetition theo regime đã khóa.

---

## Bước 5 — Audit label ontology

**Input:** source labels và label dictionary.

**Action:** xuất:

```text
source_label
canonical_label
record_count
subject_count
day_count
analysis_eligibility
mapping_evidence
```

Rules:

```text
unknown != rest
unsupported labels giữ provenance
class order cố định từ ontology
không tự drop class vì một fold thiếu support
```

**Output:** `label-audit.csv` và label decision summary.

**Stop condition:** label không map nhưng bị xóa im lặng; unknown bị map thành rest.

---

## Bước 6 — Structural EDA

**Input:** train/validation canonical records.

**Action:** tính theo file/record:

```text
sample_count
duration_sec
channel_count
sampling_rate_hz
unit
mean
std
median
MAD
RMS
MAV
minimum
maximum
nonfinite_ratio
zero_ratio
flatline_ratio
clipping_candidate_ratio
```

**Output:** file-level và channel-level statistics.

**Stop condition:** unit/sampling/channel order khác mà vẫn gộp statistic không reason-code.

---

## Bước 7 — Signal Quality Audit

**Input:** statistics và provisional QC policy.

**Action:** phát hiện mô tả:

```text
NONFINITE_PRESENT
FLATLINE_CANDIDATE
CONSTANT_CHANNEL
CLIPPING_CANDIDATE
EXTREME_DC_OFFSET_CANDIDATE
SHORT_RECORD
SAMPLING_RATE_CONFLICT
UNIT_CONFLICT
CHANNEL_COUNT_CONFLICT
MISSING_CHANNEL
```

Các rule là engineering heuristic. Không đặt ngưỡng amplitude tuyệt đối nếu unit/protocol chưa đủ bằng chứng.

**Output:** `signal-quality-flags.csv`, summary và reason codes.

**Stop condition:** quality fail bị biến thành “không có gesture” hoặc “không mỏi”.

---

## Bước 8 — Cross-day drift audit

**Input:** record-level features theo subject/day/gesture/channel.

**Action:** với mỗi cặp ngày hợp lệ:

```text
median feature day A/day B
MAD day A/day B
RMS ratio
MAV ratio
robust median shift z
channel activation rank correlation (conditional)
record/gesture support
```

Không so sánh hai ngày nếu:

- canonical label không trùng;
- channel mapping không tương thích;
- unit khác;
- sampling/preprocessing khác mà chưa harmonize;
- subject không có đủ data cả hai ngày.

**Output:** `cross-day-feature-summary.csv`, `cross-day-drift-summary.csv`, narrative có limitations.

**Stop condition:** viết fatigue conclusion từ day shift.

---

## Bước 9 — Frequency-domain eligibility

**Input:** sampling/processing provenance.

**Action:** chỉ đánh dấu F2 đủ điều kiện khi:

```yaml
sampling_rate_verified: true
raw_or_near_raw_verified: true
frequency_band_known: true
prior_filtering_known: true
window_policy_locked: true
unit_and_channel_mapping_verified: true
```

Có thể chạy descriptive PSD/MDF/MNF trên train/validation nếu pass, nhưng không chọn filter/window dựa vào test.

**Output:** `feature-eligibility.yaml`.

**Stop condition:** frequency features chạy trên envelope/rectified/low-rate data mà không ghi rõ.

---

## Bước 10 — Experiment eligibility

### Có thể đủ điều kiện

```text
Task A in-domain cross-subject baseline
Task A cross-day evaluation
zero-shot cross-subject arm
P0 normalization-only baseline
P1 few-shot personalization — nếu calibration/test repetitions tách được
unknown-gesture abstention audit — nếu unsupported labels giữ nguyên
```

### Chỉ conditional

```text
F2 frequency extension
inter-channel ratios/correlation
channel subset experiments
personalization 2/3/5 repetitions
```

### Không đủ điều kiện chỉ từ GRABMyo

```text
clinical claims
Motion Lab transfer claims
stroke performance claims
MFCV site activation
hard fatigue diagnosis
Task C clinical longitudinal recovery score
```

**Output:** `experiment-eligibility.yaml`.

---

## Bước 11 — Readiness Gate

Gate `GO_FOR_DAY30_HARMONIZATION` khi:

```yaml
source_and_license_verified: true
archive_and_file_hashes_verified: true
metadata_index_verified: true
hierarchy_verified_or_documented_partial: true
label_mapping_frozen: true
partition_guard_passed: true
test_seal_present_and_unopened: true
critical_duplicate_or_group_overlap: false
unit_sampling_channel_provenance_sufficient: true
eda_completed_on_train_validation: true
cross_day_audit_completed: true
feature_eligibility_frozen: true
```

Nếu fail:

```yaml
status: BLOCKED_WITH_EVIDENCE
blockers:
  - <reason code>
next_action:
  - <specific repair>
```

Không đổi thành GO chỉ vì tooling tests pass.

---

## Bước 12 — Chạy test và đóng gói evidence

```bash
bash scripts/dev/run_day29_checks.sh
```

Expected:

```text
Day28 regression: PASS hoặc SKIPPED_NOT_PRESENT
Python compile: PASS
Schemas: PASS
Automated tests: PASS
Partition guard: PASS
No training/model artifact: PASS
No test signal access: PASS
Tooling smoke: PASS
```

---

# PHẦN C — CODE GỢI Ý CỐT LÕI

## 11. Partition guard

```python
from pathlib import Path

ALLOWED = {"train", "validation"}


def assert_eda_visible(partition: str, signal_path: str) -> None:
    normalized = partition.strip().lower()
    if normalized not in ALLOWED:
        raise PermissionError(
            f"Day29 EDA không được đọc partition={partition!r}"
        )

    path_parts = {part.lower() for part in Path(signal_path).parts}
    if "test" in path_parts or "sealed-test" in path_parts:
        raise PermissionError("Path có dấu hiệu thuộc sealed test")
```

## 12. Robust drift score

```python
import numpy as np


def mad(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    median = float(np.median(values))
    return float(np.median(np.abs(values - median)))


def robust_shift(day_a: np.ndarray, day_b: np.ndarray) -> float:
    a = np.asarray(day_a, dtype=float)
    b = np.asarray(day_b, dtype=float)
    pooled_mad = (mad(a) + mad(b)) / 2.0
    scale = 1.4826 * pooled_mad
    return float((np.median(b) - np.median(a)) / (scale + 1e-12))
```

## 13. Không suy fatigue

```python
DRIFT_INTERPRETATION = {
    "allowed": "distribution_shift_observed",
    "prohibited": [
        "fatigue_confirmed",
        "electrode_shift_confirmed",
        "physiological_decline_confirmed",
    ],
    "required_note": (
        "Nguyên nhân chưa xác định; cần đối chiếu protocol, force, "
        "QC, electrode setup và metadata độc lập."
    ),
}
```

## 14. Readiness decision

```python
REQUIRED_TRUE = {
    "source_and_license_verified",
    "metadata_index_verified",
    "partition_guard_passed",
    "test_seal_present_and_unopened",
    "eda_completed_on_train_validation",
    "cross_day_audit_completed",
}


def decide_readiness(checks: dict[str, bool]) -> str:
    missing = [key for key in REQUIRED_TRUE if checks.get(key) is not True]
    return "GO_FOR_DAY30_HARMONIZATION" if not missing else "BLOCKED_WITH_EVIDENCE"
```

---

# PHẦN D — LỘ TRÌNH HỌC CHO NGƯỜI MỚI

## 15. Phần phải học thật kỹ

### Mức bắt buộc

1. Subject/session/day/repetition/window khác nhau thế nào.
2. Vì sao split theo subject phải diễn ra trước windowing.
3. Mean, median, standard deviation, MAD, RMS và MAV.
4. Sampling rate, Nyquist và PSD.
5. Difference giữa signal quality, distribution shift và model performance.
6. Vì sao multi-day không đồng nghĩa fatigue dataset.
7. Vì sao channel count không đồng nghĩa cùng montage.
8. Provenance: mỗi con số EDA phải truy được về record/file/config.

### Mức nên hiểu trong Day 29

1. Robust z-like score không phải z-test/p-value.
2. Ratio dễ bị lỗi khi mẫu số gần 0.
3. Multiple comparisons khi audit nhiều subject×day×gesture×channel.
4. Clustered data và participant-level inference.
5. Within-subject vs between-subject variation.

### Chưa cần học sâu hôm nay

- Deep domain adaptation.
- Mixed-effects model đầy đủ.
- Bayesian hierarchical modeling.
- Online learning.
- MFCV estimation.

Các chủ đề này ghi vào backlog, không làm phình Day 29.

---

# 16. Lịch thực thi đề xuất

| Khối | Nội dung | Thời lượng |
|---|---|---:|
| A | Regression + snapshot + preflight | 45 phút |
| B | Hierarchy/label/partition audit | 90 phút |
| C | Structural + signal quality EDA | 120 phút |
| D | Cross-day drift audit | 120 phút |
| E | Feature/experiment eligibility | 60 phút |
| F | Report, tests, readiness gate | 75 phút |
| Learning | Đọc/ghi chú toán và DSP | 90 phút |
| Buffer | Sửa mapping/path/schema | 60 phút |

Tổng dự kiến: khoảng 10–11 giờ. Nếu dữ liệu lớn, tách chạy statistic theo batch và lưu checkpoint; không đọc toàn bộ vào RAM.

---

# 17. Definition of Done

```text
[ ] Day 28 regression PASS
[ ] Không có raw/public archive trong Git
[ ] Input manifest hashes được ghi
[ ] Source/license/readiness được reconcile
[ ] Metadata index có subject/day/session/repetition
[ ] Test signal không được đọc
[ ] Train/validation partition guard PASS
[ ] Hierarchy audit hoàn thành
[ ] Label audit hoàn thành, unknown != rest
[ ] Structural EDA hoàn thành
[ ] Signal-quality flags có reason code
[ ] Cross-day drift được mô tả, không suy fatigue
[ ] Feature eligibility được khóa
[ ] Experiment eligibility được khóa
[ ] Readiness = GO_FOR_DAY30_HARMONIZATION hoặc BLOCKED_WITH_EVIDENCE
[ ] Không training, tuning, model artifact, fake metric
[ ] Report tiếng Việt và evidence hashes được lưu
```

---

# 18. Handoff sang Day 30

Day 30 chỉ bắt đầu harmonization Mendeley + GRABMyo khi:

```yaml
mendeley_day28_gate: GO_OR_DOCUMENTED_READY
grabmyo_day29_gate: GO_FOR_DAY30_HARMONIZATION
both_test_sets_sealed: true
common_ontology_not_yet_assumed: true
pooled_training_allowed: false
```

Day 30 sẽ khóa:

```text
common ontology
source-specific data views
channel strategy
sampling/resampling policy
cross-dataset intersection
in-domain vs cross-domain experiment contracts
pooled-training blockers
```

Day 29 không được tự gộp hai dataset trước khi các quyết định này tồn tại.
