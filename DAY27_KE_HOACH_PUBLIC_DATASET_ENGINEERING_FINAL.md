# DAY 27 — Chọn, thu nhận và khóa Engineering Data Gate cho public dataset đầu tiên

> **Phiên bản:** v1.0 — research-grounded, kế thừa Day 25 + Day 26  
> **Mô hình thực hiện:** một người, làm tuần tự, không bỏ qua gate  
> **Điều kiện bắt đầu:** Day 25 và Day 26 đã hoàn thành, checker PASS, test set Day 26 chưa mở  
> **Trạng thái bắt buộc trong Day 27:** `trainingAllowed=false`, không huấn luyện, không tuning, không báo metric model  
> **Kết quả hợp lệ cuối ngày:** một public dataset cụ thể được xác minh nguồn–license–hash–schema–label–split ở mức engineering, hoặc kết thúc minh bạch bằng trạng thái `BLOCKED_SOURCE_OR_SCHEMA` thay vì đoán.

---

## 0. Day 27 thực sự giải quyết việc gì?

Day 26 đã khóa **Experiment Blueprint** nhưng vẫn chưa có một dataset cụ thể đủ điều kiện đi vào pipeline. Day 27 biến một dataset từ trạng thái “được research đánh giá là phù hợp” thành một **engineering dataset asset có provenance và gate rõ ràng**:

```text
Day 25: dataset landscape + license/access research + domain-gap register
Day 26: task/model/feature/validation/personalization/metric blueprint
Day 27: exact source → immutable archive → inventory → adapter profile
        → strict label map → canonical smoke conversion
        → subject-safe split + sealed test → Engineering Data Gate
```

Day 27 **không** giải quyết Motion Lab/Noraxon site output. Dependency đó tiếp tục được cô lập sau adapter và không chặn public-data engineering.

### Không được thực hiện

```text
Không tải file từ URL không xác minh.
Không dùng một trang tổng hợp/Google Drive mirror làm canonical source nếu chưa đối chiếu.
Không coi tải được là được phép dùng.
Không sửa file raw bằng Excel.
Không đổi tên/ghi đè archive gốc mà không lưu hash.
Không hard-code sampling rate, unit, channel order hoặc label khi data dictionary chưa chứng minh.
Không map unknown/ambiguous/artifact thành rest.
Không random split windows.
Không mở sealed test.
Không gọi public dataset là dữ liệu Noraxon hoặc dữ liệu Vinmec.
Không chạy model.fit(), hyperparameter tuning hay calibration.
Không commit raw signal/archive vào Git.
```

---

# 1. Quyết định dataset của Day 27

## 1.1. Primary candidate

```yaml
dataset_id: MENDELEY_4CH_GESTURE
role: first_sparse_task_a_adapter
selection_status: PRESELECTED_PENDING_CANONICAL_VERIFICATION
```

Lý do chọn làm dataset đầu tiên:

- 4 kênh, gần hơn với hướng sparse-channel 4–16 kênh của MVP so với HD-sEMG;
- label vocabulary được Day 25 đánh giá gần UC1 Gesture Recognition;
- phù hợp để khóa adapter, label mapper và canonical contract nhỏ trước;
- Day 26 yêu cầu classical baseline và leakage-safe evaluation; dataset này phù hợp để chuẩn bị E-A00 đến E-A05 nếu các trường thực tế được xác minh;
- đây chỉ là **engineering first dataset**, không phải dataset duy nhất của dự án.

## 1.2. Fallback candidate

```yaml
dataset_id: GRABMYO_V1_1
role: cross_day_robustness_and_secondary_task_a_dataset
selection_status: FALLBACK_PENDING_CANONICAL_VERIFICATION
```

Chuyển sang GRABMyo khi một trong các điều kiện sau xảy ra trước mốc kiểm tra Step 3:

- không xác định được canonical record/DOI/version của Mendeley 4-channel;
- license page hoặc license snapshot không thể xác minh;
- archive không có subject/repetition hierarchy đủ để split an toàn;
- format thực tế không thể đọc bằng công cụ có sẵn trong phạm vi một ngày;
- label vocabulary không thể mapping mà không suy diễn.

Không chuyển fallback chỉ vì Mendeley “khó hơn dự kiến” sau khi đã tải; phải ghi nguyên nhân vào decision ledger.

---

# 2. Trạng thái và cờ quyền hạn

Day 27 phải tách ba khái niệm:

```yaml
public_dataset_engineering_ready: false
public_baseline_training_eligible: false
training_execution_allowed: false
motionlab_training_allowed: false
clinical_training_allowed: false
```

Sau khi Engineering Data Gate PASS, chỉ được nâng:

```yaml
public_dataset_engineering_ready: true
public_baseline_training_eligible: true
training_execution_allowed: false
```

`training_execution_allowed` chỉ được xem xét ở Day 29 sau khi có environment lock thực, experiment manifest, test seal, leakage preflight và authorization record.

---

# 3. Kết quả bàn giao bắt buộc

```text
docs/05-data/day27/
├── 00-day27-scope-and-gates.md
├── 01-dataset-selection-decision.md
├── 02-canonical-source-verification-sop.md
├── 03-controlled-acquisition-and-hashing.md
├── 04-archive-inventory-and-safe-extraction.md
├── 05-adapter-and-mapping-profile.md
├── 06-label-ontology-mapping.md
├── 07-group-split-and-test-seal.md
├── 08-engineering-data-gate.md
├── 09-domain-gap-and-transfer-boundary.md
├── 10-day28-handoff.md
├── 11-external-dependencies.md
├── dataset-selection-scorecard.csv
├── dataset-experiment-eligibility-matrix.csv
└── day27-source-traceability.csv

ai-core/configs/
├── day27_dataset_selection.research.yaml
├── day27_training_authorization.research.yaml
├── mendeley_4ch_mapping_profile.template.json
└── mendeley_4ch_label_map.template.json

ai-core/data/day27/
├── contracts.py
├── hashing.py
├── source_record.py
├── safe_archive.py
├── label_mapping.py
├── group_split.py
├── profile_driven_csv_adapter.py
└── engineering_gate.py

data-platform/manifests/
├── day27-selected-public-source-record.template.json
├── day27-retrieval-receipt.template.json
├── day27-selected-dataset-manifest.template.json
└── day27-license-snapshot.template.json

scripts/data/
├── day27_verify_source_record.py
├── day27_acquire_public_dataset.py
├── day27_inventory_archive.py
├── day27_build_metadata_index.py
├── day27_build_group_split.py
├── day27_convert_csv_smoke.py
└── day27_run_engineering_gate.py

packages/common-schemas/json/
qa-validation/automated-tests/
qa-validation/requirements/
qa-validation/evidence/
scripts/dev/
```

Raw archive, raw signal và converted signal **không nằm trong ZIP và không commit vào repo**.

---

# PHẦN A — KIẾN THỨC PHẢI HỌC TRƯỚC KHI THAO TÁC DATA

## 4. Data provenance: “file này từ đâu và đã bị thay đổi chưa?”

Bạn cần hiểu bốn khái niệm:

1. **Canonical source:** trang/record chính thức gắn DOI hoặc repository ID.
2. **Version:** dataset có thể được cập nhật; cùng tên không có nghĩa cùng bytes.
3. **SHA-256:** dấu vân tay của file. Chỉ cần đổi một byte thì hash thay đổi.
4. **Retrieval receipt:** bằng chứng bạn tải file nào, lúc nào, từ URL nào và hash là gì.

SHA-256 không chứng minh file đúng về khoa học, nhưng chứng minh artifact đang xử lý không bị thay đổi ngoài ý muốn.

## 5. Sampling và đơn vị

Một mảng số chỉ trở thành tín hiệu có thể phân tích khi biết:

```text
sampling_rate_hz
signal_unit
channel_order
raw_or_processed
```

Quan hệ giữa số mẫu, thời gian và sampling rate:

\[
T = \frac{N}{F_s}
\]

Trong đó:

- \(N\): số mẫu;
- \(F_s\): sampling rate, đơn vị Hz;
- \(T\): thời lượng, đơn vị giây.

Ví dụ, 2.000 mẫu có thể là 1 giây nếu \(F_s=2000\) Hz nhưng là 2 giây nếu \(F_s=1000\) Hz. Không biết \(F_s\) thì không khóa được window theo mili-giây và không ánh xạ FFT bin sang Hz.

## 6. Label mapping không phải đổi tên tự do

Một source label như `grip`, `close`, `fist` chưa chắc tương đương `hand_close`. Mapping chỉ hợp lệ khi data dictionary/protocol/cue mô tả cùng semantics.

Các target label của Task A:

```text
rest
hand_open
hand_close
wrist_flexion
wrist_extension
```

Các trạng thái không được ép vào năm lớp trên:

```text
unknown
ambiguous
artifact
not_attempted
transition
```

## 7. Data hierarchy và leakage

Hierarchy kế thừa Day 26:

```text
subject
└── day
    └── session
        └── trial/repetition
            └── segment
                └── window
```

Quy tắc bất biến:

```text
split subject/session/repetition trước
→ sau đó mới segment/window
```

Nếu cùng một repetition tạo ra hàng chục overlapping windows và các windows bị chia ngẫu nhiên vào train/test, test không còn độc lập.

## 8. Domain gap

Public dataset được dùng để chứng minh:

- adapter/canonical pipeline hoạt động;
- label/split/feature contract có thể thực thi;
- baseline engineering có thể chạy sau gate.

Nó không chứng minh:

- model chạy đúng trên Noraxon Motion Lab;
- channel/muscle mapping tại Vinmec tương thích;
- hiệu năng trên bệnh nhân;
- MFCV khả dụng tại site.

---

# PHẦN B — KẾ HOẠCH THỰC THI 8 GIỜ

## Step 0 — Kiểm tra Day 25 và Day 26

**Thời lượng:** 20 phút  
**Input:** repo sau khi hoàn thành Day 26.  
**Action:**

```bash
bash scripts/dev/run_day25_research_checks.sh
bash scripts/dev/run_day26_research_checks.sh
```

Nếu tên script cũ khác, dùng script compatibility tương ứng. Sau đó:

```bash
git status --short
git log -5 --oneline
```

**Output:**

```yaml
day25_checks: PASS
day26_checks: PASS
test_set_opened: false
working_tree_state: recorded
```

**Dừng khi:** Day26 blueprint không valid, test seal đã mở hoặc working tree có thay đổi chưa hiểu nguồn gốc.

---

## Step 1 — Đọc và khóa scope Day 27

**Thời lượng:** 40 phút  
**Input:** Day25 free-first stack, Day26 task/experiment/validation contracts.  
**Action:** đọc kỹ:

```text
docs/05-data/day25-research/free-first-research-stack.md
docs/05-data/day25-research/task-a-gesture-data-spec.md
docs/research/day26/10-master-experiment-blueprint.md
docs/research/day26/04-validation-and-leakage-review.md
docs/research/day26/13-day26-readiness-gate.md
```

**Output:** ghi vào `docs/note/day27/08-decisions.md`:

- dataset primary/fallback;
- Task A là scope chính;
- Task B/C chưa dùng dataset này làm corpus chính;
- training vẫn bị khóa;
- MFCV disabled;
- cross-session/cross-day chỉ được bật nếu metadata thật hỗ trợ.

**Dừng khi:** chưa giải thích được khác nhau giữa `engineering-ready`, `training-eligible` và `training-authorized`.

---

## Step 2 — Freeze quyết định primary/fallback

**Thời lượng:** 20 phút  
**Input:** `dataset-selection-scorecard.csv`.  
**Action:** kiểm tra rationale và ghi decision record.

**Output:**

```yaml
primary_candidate: MENDELEY_4CH_GESTURE
fallback_candidate: GRABMYO_V1_1
decision_status: PRESELECTED_PENDING_CANONICAL_VERIFICATION
```

Không được đổi quyết định bằng cảm giác sau khi nhìn file; mọi thay đổi phải có trigger đã định trước.

---

## Step 3 — Xác minh canonical source và license

**Thời lượng:** 45 phút  
**Input:** canonical record page, DOI/repository ID, license page/file.  
**Action:** điền `day27-selected-public-source-record.template.json` và `day27-license-snapshot.template.json`.

Tối thiểu phải có:

```text
canonical_title
canonical_record_url
DOI/repository_id
version_or_record_revision
publisher/repository
retrieval_date
license_id
license_url
license_snapshot_path
license_snapshot_sha256
access_class
permitted research/internal/commercial/redistribution uses
citation text
```

Chạy:

```bash
python scripts/data/day27_verify_source_record.py \
  --record /secure/work/day27/source-record.json
```

**Output:** `source-record-verification.json` với `status=VERIFIED` hoặc danh sách lỗi cụ thể.

**Dừng khi:** URL/DOI/license còn placeholder, license chỉ xuất hiện trong bài blog, hoặc canonical title không khớp archive.

---

## Step 4 — Controlled acquisition và immutable hash

**Thời lượng:** 35 phút, không tính thời gian mạng  
**Input:** source record đã VERIFIED.  
**Action:** luôn dry-run trước:

```bash
python scripts/data/day27_acquire_public_dataset.py \
  --record /secure/work/day27/source-record.json \
  --destination /data/datasets/external/MENDELEY_4CH_GESTURE/raw \
  --dry-run
```

Sau khi kiểm tra URL, license, dung lượng dự kiến và đích lưu:

```bash
python scripts/data/day27_acquire_public_dataset.py \
  --record /secure/work/day27/source-record.json \
  --destination /data/datasets/external/MENDELEY_4CH_GESTURE/raw \
  --execute \
  --accept-license
```

**Output:**

```text
archive gốc không chỉnh sửa
retrieval-receipt.json
archive SHA-256
HTTP/source metadata khả dụng
```

**Dừng khi:** redirect sang domain không mong đợi, file vượt giới hạn dung lượng, hash thay đổi giữa hai lần tải không có version change, hoặc download yêu cầu điều khoản chưa được review.

---

## Step 5 — Inventory archive, không mở file mù quáng

**Thời lượng:** 55 phút  
**Input:** immutable archive.  
**Action:**

```bash
python scripts/data/day27_inventory_archive.py \
  --archive /data/datasets/external/MENDELEY_4CH_GESTURE/raw/<archive> \
  --output /data/datasets/external/MENDELEY_4CH_GESTURE/evidence/archive-inventory.json
```

Kiểm tra:

```text
file tree
extensions
compressed/uncompressed sizes
unsafe path traversal
subject/session/repetition structure
label files/data dictionary
signal file format
sampling-rate evidence
unit evidence
channel count/order
```

**Output:** `archive-inventory.json` và `data-dictionary-notes.md`.

**Dừng khi:** archive có unsafe path, encrypted/opaque binary không có reader, không xác định được subject IDs hoặc không có label provenance.

---

## Step 6 — Khóa adapter profile và canonical contract

**Thời lượng:** 60 phút  
**Input:** inventory và data dictionary.  
**Action:** điền `mendeley_4ch_mapping_profile.template.json`.

Các field bắt buộc:

```text
source_format
file_glob
encoding/delimiter nếu tabular
sampling_rate_hz
raw_or_processed
source_unit
channel source fields
canonical channel order
path/metadata regex cho subject/session/repetition
label source
```

Nếu format là wide CSV, chạy smoke conversion:

```bash
python scripts/data/day27_convert_csv_smoke.py \
  --input <một-file-signal-thật> \
  --profile /secure/work/day27/mapping-profile.json \
  --output-dir /data/datasets/external/MENDELEY_4CH_GESTURE/smoke
```

**Output:** canonical `.npz` + metadata sidecar cho một file smoke-test ở controlled storage.

**Dừng khi:** phải đoán sampling rate/unit/channel order hoặc phải sửa DSP core để đọc source. Nếu format không phải CSV, ghi `FORMAT_ADAPTER_REQUIRED` và tạo adapter-specific ticket; không ép file qua CSV.

---

## Step 7 — Strict label mapping

**Thời lượng:** 35 phút  
**Input:** source label dictionary/cue protocol.  
**Action:** điền `mendeley_4ch_label_map.template.json`.

Mỗi source label phải có:

```text
source_label
canonical_label hoặc null
mapping_status
mapping_evidence
exclusion_reason nếu không map
```

Chạy validation bằng metadata-index builder hoặc unit tests.

**Output:** label map versioned, không có unknown bị ép thành rest.

**Dừng khi:** `grip` được map sang `hand_close` chỉ vì tên nghe giống nhau; phải có protocol evidence.

---

## Step 8 — Build metadata index và canonical smoke set

**Thời lượng:** 50 phút  
**Input:** extracted/controlled files, mapping profile, label map.  
**Action:**

```bash
python scripts/data/day27_build_metadata_index.py \
  --root /data/datasets/external/MENDELEY_4CH_GESTURE/extracted \
  --profile /secure/work/day27/mapping-profile.json \
  --label-map /secure/work/day27/label-map.json \
  --output /data/datasets/external/MENDELEY_4CH_GESTURE/metadata/index.csv
```

Audit:

- subjects thực tế;
- sessions/days;
- repetitions/trials;
- class support theo subject;
- file hash;
- sampling rate/channel count consistency;
- excluded/unmapped labels.

**Output:** immutable metadata index hash và canonical smoke conversion report.

**Dừng khi:** subject/session/repetition bị suy từ row number, label map không hoàn chỉnh, cùng file xuất hiện nhiều partition candidate hoặc channel count không nhất quán không có reason code.

---

## Step 9 — Subject-safe split và sealed test

**Thời lượng:** 45 phút  
**Input:** metadata index đã audit.  
**Action:**

```bash
python scripts/data/day27_build_group_split.py \
  --metadata-index /data/datasets/external/MENDELEY_4CH_GESTURE/metadata/index.csv \
  --dataset-id MENDELEY_4CH_GESTURE \
  --output /data/datasets/external/MENDELEY_4CH_GESTURE/manifests/group-split.v1.json
```

Default:

```yaml
group_unit: subject
seed: 2701
ratios:
  train: 0.67
  validation: 0.17
  test: 0.16
test_set_sealed: true
```

**Output:** split manifest không overlap; test IDs được seal và không dùng trong EDA/model selection.

**Dừng khi:** dưới 6 subjects, class collapse do split, cùng subject xuất hiện nhiều partition hoặc split được tạo sau khi windowing.

---

## Step 10 — Map dataset vào Day 26 experiment matrix

**Thời lượng:** 25 phút  
**Input:** Day26 experiment matrix và metadata capabilities thực tế.  
**Action:** cập nhật `dataset-experiment-eligibility-matrix.csv`.

Quy tắc:

- E-A00…E-A05: chỉ `ELIGIBLE_AFTER_GATE` nếu label/class support đủ;
- E-A06 cross-session: chỉ eligible nếu có nhiều session thật;
- E-A07 cross-day: chỉ eligible nếu có day IDs thật;
- E-A08 electrode reapply: không eligible nếu dataset không có reapply event;
- E-P00…P03: phụ thuộc repetition count và calibration/test separation;
- E-F00…F04: không dùng Mendeley 4-channel làm Task B corpus nếu không có fatigue context;
- E-Cxx: không dùng làm Task C primary corpus.

**Output:** không có experiment nào tự động được coi là runnable chỉ vì dataset đã tải.

---

## Step 11 — Chạy Engineering Data Gate

**Thời lượng:** 25 phút  
**Input:** source verification, retrieval receipt, archive inventory, profile, label map, metadata index, split, eligibility matrix, smoke report.  
**Action:**

```bash
python scripts/data/day27_run_engineering_gate.py \
  --gate-input /secure/work/day27/gate-input.json \
  --output /data/datasets/external/MENDELEY_4CH_GESTURE/evidence/engineering-data-gate.v1.json
```

**PASS hợp lệ:**

```yaml
status: GO_FOR_DAY28_EDA
public_dataset_engineering_ready: true
public_baseline_training_eligible: true
training_execution_allowed: false
test_set_sealed: true
motionlab_transfer_verified: false
clinical_use_allowed: false
```

**FAIL hợp lệ:** trả reason codes rõ ràng, không sửa dữ liệu để “cho qua”.

---

## Step 12 — Regression, documentation, commit và handoff

**Thời lượng:** 25 phút  
**Input:** toàn bộ artifact Day27.  
**Action:**

```bash
bash scripts/dev/run_day27_checks.sh
```

Sau đó:

```bash
git add \
  ai-core/configs \
  ai-core/data/day27 \
  data-platform/manifests \
  docs/05-data/day27 \
  docs/note/day27 \
  docs/plans/DAY27_EXECUTION_PLAN.md \
  packages/common-schemas/json \
  qa-validation \
  scripts/data \
  scripts/dev

git diff --staged --check
git diff --staged --stat

git commit -m "day27: add controlled public dataset engineering gate"
git tag day27-public-dataset-engineering-v1.0
```

Chỉ commit code, schema, manifest/hash/evidence không chứa raw samples. Không commit `/data/datasets/...`.

---

# PHẦN C — CODE/ARCHITECTURE CẦN HIỂU

## 9. Canonical adapter không phụ thuộc model

```text
public source file
→ source-specific/profile-driven adapter
→ canonical signal + metadata
→ QC/preprocessing/windowing/features
```

Model không được đọc trực tiếp file Mendeley. Điều này giúp sau này thêm GRABMyo hoặc Noraxon site adapter mà không sửa model code.

## 10. Unit conversion

Canonical amplitude của project là \(\mu V\). Quy đổi:

```text
1 V  = 1,000,000 µV
1 mV = 1,000 µV
1 µV = 1 µV
```

Adapter phải reject unit không biết; không suy unit từ magnitude.

## 11. Canonical smoke conversion

Smoke conversion chỉ cần chứng minh một source file có thể được chuyển nhất quán và có provenance:

```text
source hash
sampling rate
channel order
unit conversion
sample count
time vector
metadata IDs
adapter/profile version
```

Nó không phải EDA đầy đủ và không phải training corpus.

---

# PHẦN D — ACCEPTANCE CRITERIA

## 12. Definition of Done

Day 27 hoàn thành khi tất cả điều kiện sau đúng:

```text
[ ] Day25 và Day26 checker PASS.
[ ] Primary/fallback decision được ghi và có switch trigger.
[ ] Canonical source record không còn placeholder.
[ ] License snapshot/hash và permitted-use decision tồn tại.
[ ] Archive gốc có SHA-256 và retrieval receipt.
[ ] Archive inventory không có unsafe path.
[ ] Exact source format được xác định.
[ ] Sampling rate, unit và channel order có evidence hoặc gate FAIL rõ.
[ ] Mapping profile versioned và không hard-code vào DSP/model.
[ ] Label map strict; unknown/ambiguous/artifact không bị map thành rest.
[ ] Metadata index có subject/session/repetition provenance.
[ ] Group split không overlap và test được seal.
[ ] Dataset được map vào từng Day26 experiment ID theo eligibility.
[ ] Engineering Data Gate có status rõ.
[ ] training_execution_allowed=false.
[ ] Không có raw signal/archive/model binary trong Git/ZIP.
[ ] Day28 handoff được ghi.
```

## 13. Kết quả kết thúc được chấp nhận

### Kết quả tốt nhất

```yaml
status: GO_FOR_DAY28_EDA
```

### Kết quả vẫn hợp lệ về quy trình

```yaml
status: BLOCKED_SOURCE_OR_SCHEMA
```

với blocker, evidence cần bổ sung và fallback decision. Không hoàn thành Day27 bằng cách bịa sampling rate, format hoặc label.

---

# PHẦN E — NHỮNG PHẦN CẦN HỌC KỸ

## 14. Kiến thức toán và DSP

### Bắt buộc hiểu

- Sampling rate, thời lượng và sample index.
- Nyquist ở mức trực giác: tần số cao nhất có thể biểu diễn nhỏ hơn \(F_s/2\).
- Unit scaling và ảnh hưởng đến RMS/MAV/QC.
- Vector/matrix: `samples.shape = (n_samples, n_channels)`.
- Hash là hàm một chiều phục vụ integrity, không phải encryption.
- Tỷ lệ split và vì sao group split khác random row split.

### Cần đọc hiểu, chưa cần chứng minh sâu

- FFT bin-to-frequency mapping.
- PSD/Welch phụ thuộc window length.
- Class imbalance và class support theo subject.
- Domain shift giữa thiết bị, montage, protocol và population.

## 15. Câu hỏi tự kiểm tra

1. Vì sao cùng 2.000 samples nhưng thời lượng có thể khác?
2. Vì sao không được đoán `mV` hay `µV` từ biên độ?
3. Vì sao `grip` không tự động bằng `hand_close`?
4. Vì sao phải hash archive trước khi extract?
5. Vì sao split theo subject trước windowing?
6. Dataset single-session cho phép chạy experiment nào và không cho phép experiment nào?
7. `public_baseline_training_eligible=true` khác `training_execution_allowed=true` như thế nào?
8. Vì sao public dataset không chứng minh Noraxon Motion Lab compatibility?

---

# PHẦN F — HANDOFF DAY 28

Day 28 chỉ bắt đầu khi:

```yaml
engineering_data_gate: GO_FOR_DAY28_EDA
test_set_sealed: true
training_execution_allowed: false
```

Day 28 tập trung:

```text
EDA trên train/validation partitions
→ class/subject/session distribution
→ duration/sampling/channel/unit consistency
→ signal QC statistics
→ missing/nonfinite/clipping/flatline/noise review
→ label/repetition audit
→ canonical dataset card
→ adapter regression fixtures
```

Không dùng sealed test để chọn preprocessing, feature hoặc threshold.

---

# 16. Câu chốt quản trị

> Day 27 không nhằm “có data bằng mọi giá”. Day 27 nhằm biến một public dataset thành tài sản engineering có nguồn gốc, quyền sử dụng, schema, label và split có thể audit; chỉ sau đó mới cho phép Day 28 EDA và chuẩn bị Day 29 baseline training.
