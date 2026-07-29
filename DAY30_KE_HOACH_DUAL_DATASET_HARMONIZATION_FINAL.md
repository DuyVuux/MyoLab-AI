# DAY 30 — HARMONIZATION CÓ KIỂM SOÁT GIỮA MENDELEY 4-CHANNEL VÀ GRABMYO

**Dự án:** MyoLab-AI — sEMG Clinical Intelligence
**Ngày:** Day 30
**Chế độ:** Single Operator · Research Engineering · Không huấn luyện
**Trạng thái đầu vào do người thực hiện báo cáo:** `GO_FOR_DAY30_HARMONIZATION`
**Đầu ra mục tiêu:** khóa hợp đồng dữ liệu, data view và điều kiện chuyển Day 31
**Ngôn ngữ tài liệu:** Tiếng Việt
**Phạm vi:** Task A — Gesture Recognition engineering baseline; không suy diễn fatigue, Motion Lab hay hiệu năng lâm sàng

---

## 0. Kết luận điều hành

Day 30 **không phải ngày gộp hai dataset thành một bảng lớn rồi train**. Đây là ngày giải quyết các khác biệt có thể tạo ra kết quả sai hoặc leakage trước khi mô hình được phép nhìn thấy dữ liệu.

Luồng đúng:

```text
Mendeley EDA PASS ─┐
                   ├─> audit khác biệt
GRABMyo EDA PASS ──┘
                   ↓
          khóa ontology và data views
                   ↓
      khóa preprocessing/windowing contract
                   ↓
    tạo index/provenance, không copy raw signal
                   ↓
  cho phép Day 31 chạy baseline riêng từng dataset
```

Luồng bị cấm:

```text
Mendeley + GRABMyo
→ resample tùy ý
→ cắt random window
→ z-score toàn bộ dữ liệu
→ gộp 31/32 kênh thành một tensor
→ random train/test split
→ báo accuracy
```

### 0.1. Các quyết định được khóa trong Day 30

| Câu hỏi | Quyết định Day 30 |
|---|---|
| Chênh lệch biên độ khoảng 40 lần | Không sửa bằng global z-score. Loại DC theo record bằng phép biến đổi deterministic; feature scaling chỉ fit trong inner-train fold |
| Sampling 2048 Hz và 2000 Hz | Primary giữ native rate. Window định nghĩa bằng mili giây; PSD dùng đúng `fs` của từng record |
| Có bắt buộc resample không? | Không. Chỉ có comparator GRABMyo 2048 → 2000 Hz bằng polyphase `125/128` |
| Downsample về 1024 Hz? | Không dùng trong primary Day 30/31 vì không cần thiết và làm mất nội dung tần số |
| GRABMyo dùng kênh nào? | Primary giữ 28 kênh F1–F16 và W1–W12; U1–U4 bị loại khỏi view phân tích nhưng vẫn giữ provenance |
| Mendeley CH4 | `QUARANTINED_EXCLUDED_PRIMARY`; không gọi là reference/hỏng khi chưa có bằng chứng; tạo sensitivity view riêng |
| Map CH1–CH4 sang F/W? | Không được phép khi không có bằng chứng giải phẫu/montage tương đương |
| Gesture chung | Tính bằng code từ hai label dictionary đã version; không hard-code từ trí nhớ |
| `hand_open` | Mendeley không hỗ trợ; không tạo nhãn giả |
| Window primary | 200 ms, hop 100 ms; sensitivity 150/75 và 250/125 ms |
| Window 500/1000 ms | Dành cho spectral/context hoặc Task B/C; không phải primary Task A |
| Output canonical | Index/feature tables ưu tiên Parquet; CSV fallback; raw window không materialize mặc định |
| Training Day 30 | Cấm |
| Pooled training Day 31 | Cấm |
| Sealed test | Giữ hai test seal độc lập, không đọc tín hiệu |

---

## 1. Đọc báo cáo pre-Day 30: những gì đã có và chưa có

### 1.1. Những gì đã đạt

Theo báo cáo đầu vào:

- GRABMyo có 51/51 bản ghi EDA PASS;
- Mendeley có 9/9 bản ghi EDA PASS;
- không có NaN/Inf;
- test chưa mở;
- không model nào được train;
- GRABMyo đã bao phủ ba session và 17 gesture trong phần EDA đã chạy;
- U1–U4 đã được nhận diện là noise floor;
- Mendeley CH4 có độ lệch chuẩn thấp hơn rất nhiều so với CH1–CH3;
- cả hai nguồn dùng đơn vị mV;
- EDA đã đủ để bắt đầu thiết kế harmonization.

### 1.2. Điểm cần giữ trung thực

Báo cáo cũng cho thấy coverage chưa phải toàn bộ quần thể:

```text
GRABMyo: 29 unique / 43 total subjects
Mendeley: 9 sampled / 25 total subjects
```

Vì vậy Day 30 được chia thành hai lớp trạng thái:

```yaml
harmonization_contract:
  allowed: true

representative_data_validation:
  allowed: true

full_dataset_model_ready_materialization:
  allowed: conditional

full_benchmark_training:
  allowed: false
```

Day 30 có thể đạt `GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE`, nhưng **full baseline** phải chờ full metadata/split index hoặc một sampling protocol được khóa và ghi rõ giới hạn.

---

## 2. Mục tiêu, ngoài phạm vi và Definition of Done

## 2.1. Mục tiêu

1. Chuẩn hóa cách mô tả hai dataset mà không xóa khác biệt nguồn.
2. Khóa ontology chung và các class không hỗ trợ.
3. Khóa chiến lược sampling rate, DC, scaling, channel và window.
4. Tạo dataset-view registry có provenance.
5. Tạo index cửa sổ mà không đọc sealed test.
6. Tạo contract định dạng đầu ra cho Day 31.
7. Chỉ rõ experiment nào đủ điều kiện và experiment nào bị chặn.
8. Tạo automated tests chống leakage và chống pooled training sớm.

## 2.2. Ngoài phạm vi

- không train/tune model;
- không chọn model tốt nhất;
- không mở outer/sealed test;
- không tính clinical KPI;
- không gọi cross-day drift là fatigue;
- không dùng MFCV;
- không map kênh theo giải phẫu nếu chưa có placement metadata;
- không tạo pooled model;
- không sửa raw file nguồn;
- không commit raw signal vào repository.

## 2.3. Definition of Done

```text
[ ] Preflight cả hai readiness decision PASS
[ ] Hai sealed test độc lập và chưa mở
[ ] Common ontology sinh từ label dictionary, không viết tay
[ ] Mendeley hand_open được khai báo ABSENT
[ ] Unknown/protected labels không lọt vào supervised core view
[ ] GRABMyo U1–U4 bị loại khỏi analysis view nhưng còn provenance
[ ] Mendeley CH4 được quarantine, có sensitivity view riêng
[ ] Không có direct CH↔F/W anatomical mapping
[ ] Native-rate policy được khóa
[ ] Resample 2048→2000 chỉ là comparator 125/128
[ ] Primary window 200 ms, hop 100 ms
[ ] Window không vượt trial/repetition boundary
[ ] Split xảy ra trước windowing
[ ] Global full-dataset scaling bị cấm
[ ] Dataset-view registry sinh thành công
[ ] Output storage contract được khóa
[ ] Pooled training vẫn false
[ ] Day 31 handoff có điều kiện rõ ràng
[ ] Tất cả test Day 30 PASS
```

---

# 3. Kế hoạch thực thi theo từng bước

## Bước 0 — Tạo branch và snapshot đầu vào

### Input

- nhánh `main` đã merge `pre-day30/dual-dataset-real-eda`;
- Zone 1: `MyoLab-AI/`;
- Zone 2: `myolab-ai-data/`;
- các evidence Day 28/29 và pre-Day 30.

### Action

```bash
cd /home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI

git status --short
git switch -c day30/dual-dataset-harmonization

mkdir -p qa-validation/evidence/day30
git rev-parse HEAD > qa-validation/evidence/day30/input-git-commit.txt
git diff --binary > qa-validation/evidence/day30/input-working-tree.patch
```

Nếu working tree sạch, patch có thể rỗng nhưng vẫn được giữ làm bằng chứng.

### Output

```text
qa-validation/evidence/day30/
├── input-git-commit.txt
└── input-working-tree.patch
```

### Stop condition

- dừng nếu đang ở nhánh khác có thay đổi chưa commit mà chưa xác định nguồn;
- dừng nếu Zone 2 trỏ sai `SEMG_DATA_ROOT`.

---

## Bước 1 — Chạy regression Day 28–29 và dual gate

### Input

```text
scripts/dev/run_day28_checks.sh
scripts/dev/run_day29_checks.sh
scripts/data/pre_day30_dual_gate.py
```

### Action

```bash
bash scripts/dev/run_day28_checks.sh
bash scripts/dev/run_day29_checks.sh

python scripts/data/pre_day30_dual_gate.py \
  --config data-platform/configs/pre_day30_remote_eda.research.yaml
```

### Output

```text
qa-validation/evidence/day30/day30-input-regression.log
qa-validation/evidence/day30/day30-input-gate.json
```

### Stop condition

Dừng Day 30 nếu:

```yaml
mendeley_readiness: not GO
grabmyo_readiness: not GO
test_set_opened: true
training_allowed: true
fatigue_inference_allowed: true
```

---

## Bước 2 — Khóa profile nguồn dữ liệu

### Input

- EDA summaries;
- readiness decisions;
- label dictionaries;
- channel dictionaries;
- sampling/unit metadata.

### Action

Sinh hai `DatasetProfile`:

```yaml
dataset_id: mendeley-4channel-hand-gesture-v2
sampling_rate_hz: 2000
signal_unit: mV
channel_policy_id: mendeley-ch123-primary-v1
session_structure: single_session
```

```yaml
dataset_id: grabmyo-v1.1.0
sampling_rate_hz: 2048
signal_unit: mV
channel_policy_id: grabmyo-fw28-primary-v1
session_structure: three_session_cross_day
```

Không thêm field mà nguồn không hỗ trợ.

### Output

```text
data-platform/configs/day30/dataset-profiles.yaml
qa-validation/evidence/day30/dataset-profile-validation.json
```

### Stop condition

Dừng nếu cùng một dataset có nhiều giá trị `sampling_rate_hz`, `unit` hoặc channel count nhưng không có reason code.

---

## Bước 3 — Giải quyết DC offset và chênh lệch biên độ

## 3.1. Phân biệt ba khái niệm

### DC removal

Với tín hiệu kênh \(x_c[n]\):

\[
x'_c[n] = x_c[n] - \bar{x}_c
\]

Phép này loại thành phần trung bình nhưng không làm độ lệch chuẩn về 1.

### Raw-signal normalization

Ví dụ per-trial z-score:

\[
z_c[n] = \frac{x_c[n]-\mu_c}{\sigma_c}
\]

Day 30 **không chọn cách này cho primary**, vì:

- có thể xóa thông tin biên độ;
- dùng toàn trial là không causal;
- dễ che domain gap;
- nếu áp dụng trước split/global sẽ tạo leakage.

### Feature scaling

Với feature \(f_j\), scaler chỉ fit trên inner-train:

\[
\tilde f_j = \frac{f_j-\mu_{j,\text{train}}}{\sigma_{j,\text{train}}}
\]

Đây là lựa chọn hợp lệ trong model pipeline.

## 3.2. Quyết định

```yaml
dc_policy:
  primary_offline_research: per_record_channel_mean_subtraction
  deployment_comparator: causal_high_pass_from_existing_preprocessing_spec
  new_bandpass_defined_by_day30: false

raw_signal_zscore:
  primary_allowed: false

feature_scaling:
  mandatory_comparator: none
  optional:
    - training_fold_per_feature_zscore
    - training_fold_robust_scaler
  global_full_dataset: prohibited
```

Day 30 không ghi đè filter spec đã xây ở những ngày DSP trước.

### Output

```text
ai-core/configs/day30_normalization_policy.research.yaml
docs/05-data/day30/02-normalization-and-dc-policy.md
```

### Stop condition

Dừng nếu code fit mean/std trên toàn dataset hoặc trên outer test.

---

## Bước 4 — Khóa sampling-rate policy

## 4.1. Primary: native-rate

Chênh lệch 2048 và 2000 Hz chỉ được xử lý bằng cách dùng thời lượng cửa sổ theo mili giây:

| Window | Mendeley 2000 Hz | GRABMyo 2048 Hz |
|---:|---:|---:|
| 150 ms | 300 mẫu | 307 mẫu |
| 200 ms | 400 mẫu | 410 mẫu |
| 250 ms | 500 mẫu | 512 mẫu |
| 500 ms | 1000 mẫu | 1024 mẫu |
| 1000 ms | 2000 mẫu | 2048 mẫu |

PSD/MDF/MNF nhận `sampling_rate_hz` thật của mỗi record, do đó không cần ép số mẫu bằng nhau cho classical feature model.

## 4.2. Comparator: GRABMyo 2048 → 2000 Hz

Tỷ lệ chính xác:

\[
\frac{2000}{2048}=\frac{125}{128}
\]

Dùng polyphase:

```python
from scipy.signal import resample_poly

y = resample_poly(x, up=125, down=128, axis=0)
```

Không resample Mendeley trong comparator này.

## 4.3. Không chọn 1024 Hz

1024 Hz chỉ có thể là later compute/latency arm. Nó không cần thiết để giải quyết chênh lệch 2.4% và có thể thay đổi nội dung phổ.

### Output

```text
ai-core/configs/day30_sampling_policy.research.yaml
qa-validation/evidence/day30/sampling-policy-validation.json
```

### Stop condition

- dừng nếu resampling không lưu `source_fs`, `target_fs`, `up`, `down`;
- dừng nếu PSD dùng một `fs` hard-code chung.

---

## Bước 5 — Khóa channel policy và xử lý CH4

## 5.1. GRABMyo

```yaml
primary_channels:
  - F1-F16
  - W1-W12
excluded_from_analysis:
  - U1-U4
exclusion_reason: CONFIRMED_NOISE_FLOOR
raw_provenance_retained: true
```

## 5.2. Mendeley

CH1–CH3 là primary view.

CH4:

```yaml
status: QUARANTINED_EXCLUDED_PRIMARY
reason:
  - standard_deviation_about_80x_lower_than_primary_channels
  - channel_role_not_verified
claims_not_allowed:
  - broken_channel
  - reference_channel
  - valid_semg_channel
sensitivity_view_allowed: true
```

Cần chạy thêm train/validation-only audit:

- variance ratio theo subject/trial;
- hoạt động so với rest;
- PSD shape;
- correlation;
- clipping/flatline;
- mức phân biệt gesture bằng thống kê mô tả, không train classifier;
- tính nhất quán giữa 9 file đã cache và phần còn lại khi được tải.

## 5.3. Không map vật lý trực tiếp

```text
Mendeley CH1 ≠ GRABMyo F1
Mendeley CH2 ≠ GRABMyo W1
```

Không có bằng chứng electrode placement tương đương.

## 5.4. Các strategy được phép

| ID | Strategy | Vai trò |
|---|---|---|
| C0 | Dataset-native channels | Primary Day 31 |
| C1 | Mendeley CH1–CH3, GRABMyo native 28 | Hai model riêng |
| C2 | Channel-summary representation | Cross-dataset comparator |
| C3 | Fixed four-channel GRABMyo subset | Blocked nếu chưa có placement/stability evidence |
| C4 | Common-muscle anatomical mapping | Blocked |

Channel-summary v1 tính trên từng base feature:

```text
median
IQR
q90
max
active_channel_fraction
```

Nó tạo vector có số chiều cố định nhưng làm mất thông tin không gian, vì vậy không phải primary.

### Output

```text
ai-core/configs/day30_channel_policy.research.yaml
qa-validation/evidence/day30/channel-decision.json
```

### Stop condition

Dừng nếu:

- U1–U4 lọt vào primary GRABMyo view;
- CH4 lọt vào primary Mendeley view;
- code đoán mapping giải phẫu từ tên cột.

---

## Bước 6 — Xây common ontology và dataset views

### Input

```text
Mendeley label-dictionary.yaml
GRABMyo label-dictionary.yaml
```

### Action

1. Đọc label dictionary bằng code.
2. Chỉ giữ label có `analysis_eligibility=SUPPORTED` hoặc tương đương.
3. Loại `unknown`, protected non-target và ambiguous.
4. Tính intersection.
5. Ghi support theo từng source.

Mendeley core đã khóa:

```text
rest
hand_close
wrist_flexion
wrist_extension
```

`hand_open`:

```yaml
mendeley: ABSENT
synthetic_fill_allowed: false
unknown_to_hand_open_allowed: false
```

### Dataset views

```yaml
mendeley_core4_primary_v1:
  classes: [rest, hand_close, wrist_flexion, wrist_extension]
  channels: [CH1, CH2, CH3]

mendeley_core4_ch4_sensitivity_v1:
  classes: [rest, hand_close, wrist_flexion, wrist_extension]
  channels: [CH1, CH2, CH3, CH4]
  role: sensitivity_only

grabmyo_project_subset_native28_v1:
  classes: computed_from_verified_mapping
  channels: [F1-F16, W1-W12]

cross_source_intersection_summary_v1:
  classes: computed_intersection
  channel_representation: channel_summary_v1
  pooled_training_allowed: false
```

### Output

```text
data-platform/configs/day30/common-ontology.yaml
data-platform/configs/day30/dataset-view-registry.yaml
qa-validation/evidence/day30/ontology-build-report.json
```

### Stop condition

Dừng nếu:

- intersection rỗng;
- class có mapping ambiguous;
- raw label unknown bị dùng như supervised target;
- class order không được version.

---

## Bước 7 — Khóa segmentation và windowing

### Input

- Day 26 window grid;
- metadata hierarchy của từng source;
- split manifests.

### Quyết định

```yaml
primary:
  window_ms: 200
  hop_ms: 100

sensitivity:
  - window_ms: 150
    hop_ms: 75
  - window_ms: 250
    hop_ms: 125

context_only:
  - 500
  - 1000
```

### Quy tắc bắt buộc

```text
split subject/day/session/repetition
→ chọn partition
→ segment trong partition
→ window trong segment
```

Window không được:

- vượt repetition/trial;
- chứa mẫu từ hai gesture;
- chứa cả train và validation;
- được tạo trước subject split;
- dùng filename để suy label nếu mapping chưa verify.

### Output

```text
ai-core/configs/day30_windowing_policy.research.yaml
data-platform/contracts/day30/window-index-columns.csv
```

### Stop condition

- dừng nếu `partition=test`;
- dừng nếu start/end vượt record length;
- dừng nếu cùng `window_id` xuất hiện ở hai partition.

---

## Bước 8 — Khóa định dạng đầu ra

## 8.1. Không copy raw windows mặc định

Mỗi window chỉ lưu reference:

```text
dataset_id
record_id
subject_id
day_id
session_id
repetition_id
canonical_label
partition
signal_path
start_sample
end_sample_exclusive
sampling_rate_hz
channel_policy_id
preprocessing_policy_id
```

## 8.2. Canonical format

| Tài sản | Format ưu tiên | Fallback |
|---|---|---|
| Metadata index | Parquet | CSV |
| Window index | Parquet | CSV |
| Feature table | Partitioned Parquet | CSV.gz |
| Config/decision | YAML | JSON |
| Evidence | JSON/Markdown | — |
| Training matrix tạm | NPZ + column manifest | NPY |
| Raw signal | Giữ ở source format | Không copy |

Feature table dùng long schema để chịu được số kênh khác nhau:

```text
dataset_id
window_id
channel_id
feature_id
feature_value
feature_version
```

Day 31 có thể pivot theo từng data view.

### Output

```text
data-platform/contracts/day30/storage-contract.yaml
packages/common-schemas/json/day30-window-index.v1.schema.json
```

### Stop condition

Dừng nếu output mất:

- source hash;
- split version;
- label mapping version;
- preprocessing version;
- channel policy version.

---

## Bước 9 — Khóa experiment eligibility

### Mendeley

| Experiment | Day 30 eligibility |
|---|---|
| E-A00–E-A04 | Conditional GO trên core4 primary |
| E-A05 | Conditional nếu F2/spectral contract pass |
| E-A06/E-A07 | Không đủ multi-session/day |
| E-P01/E-P02 | Chỉ khi repetition split cho calibration/test đủ |
| E-P03 | Không dùng nếu hết repetition test |
| E-F03 | Có thể dùng unknown gesture làm safety audit, chưa chạy |
| Task C | Không primary |

### GRABMyo

| Experiment | Day 30 eligibility |
|---|---|
| E-A00–E-A05 | Conditional GO trên native28 |
| E-A06 | Conditional theo session semantics |
| E-A07 | GO về contract cross-day |
| E-P01/E-P02 | Conditional nếu repetitions support |
| E-F03 | Conditional cho unsupported/unknown |
| Fatigue hard label | Không |
| MFCV | Không |

### Cross-source

```yaml
zero_shot_contract_definition: allowed
pooled_training: prohibited
pooled_hyperparameter_selection: prohibited
common_summary_view_training: later_only
```

### Output

```text
ai-core/configs/day30_experiment_eligibility.research.yaml
docs/05-data/day30/08-experiment-eligibility-and-day31-handoff.md
```

---

## Bước 10 — Chạy Day 30 tooling trên fixture rồi trên repo thật

### Fixture/smoke

```bash
bash scripts/dev/run_day30_checks.sh
```

### Repo thật

```bash
python scripts/data/day30_preflight.py \
  --config ai-core/configs/day30_harmonization.research.yaml \
  --report qa-validation/evidence/pre-day30/pre-day30-report.json \
  --output qa-validation/evidence/day30/day30-preflight.json

python scripts/data/day30_build_common_ontology.py \
  --mendeley-labels <Mendeley label-dictionary.yaml> \
  --grabmyo-labels <GRABMyo label-dictionary.yaml> \
  --output data-platform/configs/day30/common-ontology.yaml

python scripts/data/day30_run_harmonization.py \
  --config ai-core/configs/day30_harmonization.research.yaml
```

### Output

```text
qa-validation/evidence/day30/
├── day30-preflight.json
├── day30-common-ontology.json
├── day30-dataset-view-registry.json
├── day30-channel-decision.json
├── day30-sampling-policy-validation.json
├── day30-window-index-summary.json
├── day30-harmonization-report.md
└── day30-readiness-decision.yaml
```

---

## Bước 11 — Readiness và handoff Day 31

### Trạng thái có thể đạt

#### A. `GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE`

Khi:

- contract pass;
- representative EDA pass;
- ontology/view registry pass;
- test sealed;
- full coverage chưa hoàn tất.

Cho phép Day 31 chạy smoke baseline giới hạn, ghi rõ cohort.

#### B. `GO_FOR_DAY31_SEPARATE_BASELINE_FULL`

Khi thêm:

- GRABMyo full subject index hoặc sampling protocol khóa;
- Mendeley full subject index hoặc sampling protocol khóa;
- hashes/splits đầy đủ;
- environment dependency lock thật;
- authorization Day 31 được phê duyệt.

#### C. `BLOCKED_WITH_EVIDENCE`

Khi ontology/channel/split/provenance còn mâu thuẫn.

### Cờ bắt buộc

```yaml
training_allowed: false
pooled_training_allowed: false
test_set_opened: false
motionlab_transfer_verified: false
clinical_use_allowed: false
fatigue_inference_allowed: false
mfcv_eligible: false
```

---

# 4. Phần cần học kỹ

## 4.1. Cần hiểu kỹ nhất: tại sao z-score không phải “thuốc chữa” domain gap

Z-score làm hai phân bố có trung bình 0 và độ lệch chuẩn 1 trong không gian được fit. Nó không làm cho:

- electrode placement giống nhau;
- muscle coverage giống nhau;
- gain response giống nhau;
- gesture protocol giống nhau;
- subject population giống nhau;
- session drift biến mất.

Nếu fit scaler trên toàn dữ liệu, thông tin của validation/test đã đi vào train pipeline.

## 4.2. Tần số lấy mẫu và Nyquist

Nếu sampling rate là \(f_s\), tần số cao nhất biểu diễn được theo lý thuyết là:

\[
f_N = \frac{f_s}{2}
\]

- 2000 Hz → Nyquist 1000 Hz;
- 2048 Hz → Nyquist 1024 Hz;
- 1024 Hz → Nyquist 512 Hz.

Downsample phải có anti-alias filter trước khi giảm tốc độ lấy mẫu.

## 4.3. Resample polyphase

2048 → 2000:

\[
y[m] = \text{Downsample}_{128}
       \left(
       h[n] * \text{Upsample}_{125}(x[n])
       \right)
\]

Không cần tự viết filter; dùng `scipy.signal.resample_poly`, nhưng phải log tỷ lệ.

## 4.4. Robust statistics

Với channel feature \(f_1,\ldots,f_C\):

\[
IQR = Q_{0.75} - Q_{0.25}
\]

Median và IQR ít bị một channel cực đoan chi phối hơn mean/std. Đây là lý do channel-summary comparator dùng median/IQR.

## 4.5. Data leakage

Leakage không chỉ là “test file bị mở”. Nó còn xảy ra khi:

- global mean/std dùng toàn dataset;
- chọn kênh dựa trên outer test;
- quyết định CH4 sau khi nhìn test performance;
- chọn common labels theo kết quả model;
- window chồng lấp từ cùng repetition bị chia sang train/test;
- resampling/filter thresholds được tune bằng test.

## 4.6. Domain shift và source shortcut

Nếu pooled model dễ nhận ra dataset từ amplitude/channel count, nó có thể học:

```text
dataset identity → label prevalence
```

thay vì:

```text
sEMG pattern → gesture
```

Đây là lý do Day 30 chưa cho pooled training.

---

# 5. Cấu trúc file cần tích hợp

```text
MyoLab-AI/
├── ai-core/
│   ├── configs/
│   │   ├── day30_harmonization.research.yaml
│   │   ├── day30_normalization_policy.research.yaml
│   │   ├── day30_sampling_policy.research.yaml
│   │   ├── day30_channel_policy.research.yaml
│   │   ├── day30_windowing_policy.research.yaml
│   │   ├── day30_dataset_views.research.yaml
│   │   ├── day30_experiment_eligibility.research.yaml
│   │   └── day30_training_authorization.research.yaml
│   └── data/day30/
├── data-platform/
│   ├── configs/day30/
│   └── contracts/day30/
├── docs/
│   ├── 05-data/day30/
│   ├── note/day30/
│   └── plans/DAY30_EXECUTION_PLAN.md
├── packages/common-schemas/json/
├── qa-validation/
│   ├── automated-tests/
│   ├── evidence/
│   ├── requirements/
│   ├── test-plans/
│   └── traceability/
└── scripts/
    ├── data/
    └── dev/
```

Raw data vẫn ở:

```text
/home/duyvd9/massive/projects/myolab-ai-data/
```

---

# 6. Lệnh commit cuối ngày

```bash
git add \
  ai-core \
  data-platform \
  docs \
  packages/common-schemas \
  qa-validation \
  scripts

git diff --staged --check
git diff --staged --stat

git commit -m "day30: lock dual-dataset harmonization contracts"
git tag day30-dual-dataset-harmonization-v1.0
```

Không commit:

```text
*.mat
*.dat
*.hea signal payload
raw CSV
raw NPY/NPZ
feature tables chứa dữ liệu thật nếu policy không cho phép
```

---

# 7. Đầu ra cuối ngày

```text
DAY30_KE_HOACH_DUAL_DATASET_HARMONIZATION_FINAL.md
day30-harmonization-manifest.json
day30-readiness-decision.yaml
common-ontology.yaml
dataset-view-registry.yaml
channel-policy.yaml
sampling-policy.yaml
normalization-policy.yaml
windowing-policy.yaml
storage-contract.yaml
experiment-eligibility.yaml
automated tests
hash ledger
check log
```

Kết luận cần ghi trong daily summary:

> Day 30 đã khóa cách Mendeley và GRABMyo cùng tồn tại trong một hệ thống nghiên cứu mà không giả định chúng cùng miền dữ liệu. Hai dataset vẫn có model/data view riêng; cross-source intersection mới chỉ là contract. Không model được huấn luyện, không sealed test bị đọc, không pooled training được cho phép.
