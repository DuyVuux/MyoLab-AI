# KẾ HOẠCH THỰC THI DAY 10 — MDF/MNF v0.1

**Dự án:** sEMG/MFCV Fatigue Clinical Intelligence Layer  
**Mô hình nhân sự:** một người thực hiện tuần tự nhiều vai trò  
**Phạm vi:** MVP-0 ngoại tuyến, dữ liệu synthetic/golden  
**Điều kiện bắt đầu:** Day 9 đã hoàn thành và `scripts/dev/run_day9_checks.sh` trả exit code `0`  
**Điều kiện chuyển Day 11:** toàn bộ `scripts/dev/run_day10_checks.sh` pass, đã commit và tự giải thích được toán MDF/MNF  
**Ngôn ngữ tài liệu:** tiếng Việt; tên API, field, identifier và thuật ngữ chuẩn có thể giữ tiếng Anh

---

## 1. Mục tiêu Day 10

Day 10 biến PSD đã được kiểm chứng ở Day 9 thành hai đặc trưng miền tần số có định nghĩa chuẩn, kiểm thử được và có provenance đầy đủ:

```text
SpectralEstimationResult v0.1
        ↓
Frequency Feature Extractor v0.1
        ├── xác nhận spectral result hợp lệ
        ├── xác nhận shared axis 20–400 Hz
        ├── propagate not_computed rows
        ├── recompute band power
        ├── MDF = spectral power median
        ├── MNF = spectral power weighted mean
        ├── kiểm tra MDF/MNF nằm trong analysis band
        ├── result hash + provenance
        └── JSON/CSV evidence
```

Kết quả cuối ngày phải trả lời được:

1. MDF và MNF khác nhau như thế nào?
2. Vì sao không được nhầm MDF là mean và MNF là median?
3. MDF được xác định thế nào trên PSD rời rạc?
4. Vì sao MDF/MNF không đổi khi nhân toàn PSD với một hằng số dương?
5. Vì sao một giá trị MDF/MNF đơn lẻ chưa đủ để kết luận mỏi cơ?
6. Vì sao module Day 10 phải phụ thuộc chính xác `spectral_estimation_v0.1`?

---

## 2. Phạm vi và những việc cố ý chưa làm

### 2.1. Trong phạm vi

- định nghĩa canonical MDF và MNF;
- pure DSP functions trong `packages/semg-core`;
- config có version `frequency_features_v0.1.yaml`;
- typed result rows và session result;
- known-answer tests;
- full pipeline CLI đến MDF/MNF;
- JSON Schema, deterministic hash, registry và evidence;
- learning notes bằng tiếng Việt.

### 2.2. Ngoài phạm vi

Không làm trong Day 10:

```text
MDF/MNF slope
RMS/MAV slope
fatigue onset
fatigue evidence
fatigue status
FRS
probability
KNN/SVM/LDA/Random Forest
clinical recommendation
MFCV/CV calculation
```

Nếu xuất hiện một trong các output trên, coi là **scope violation**.

---

## 3. Input và output tổng thể

### Input

```text
Day 9 SpectralEstimationResult v0.1
├── shared frequency axis: 20–400 Hz
├── 381 bins trên golden fixture
├── PSD per computed window: uV²/Hz
├── band power: uV²
├── 119 frequency-domain windows
└── provenance/hash
```

### Output

```text
frequency_features_v0.1
├── 119 frequency feature rows trên golden fixture
├── MDF: Hz
├── MNF: Hz
├── band power recomputed: uV²
├── reason codes cho not_computed
├── deterministic result hash
└── không chứa PSD vector hoặc raw samples
```

### Artifact bắt buộc

```text
packages/semg-core/semg_core/spectral_features.py
packages/semg-core/tests/test_spectral_features.py

services/feature-extraction-service/
├── configs/frequency_features_v0.1.yaml
├── src/frequency_feature_config.py
├── src/frequency_feature_result_models.py
├── src/frequency_feature_extractor.py
└── tests/
    ├── test_frequency_feature_config.py
    └── test_frequency_feature_extractor.py

packages/common-schemas/json/
├── frequency-feature-row.schema.json
├── frequency-feature-extraction-result.schema.json
└── frequency-feature-verification.schema.json

scripts/data/
├── verify_mdf_mnf.py
└── run_frequency_features.py

scripts/dev/
├── validate_day10_outputs.py
├── register_frequency_features_v0_1.py
├── check_day10_artifacts.py
└── run_day10_checks.sh
```

---

# 4. Phần phải học kỹ trước khi code

## 4.1. PSD là đầu vào, MDF/MNF là feature

Day 9 tạo hàm mật độ công suất rời rạc:

```text
f[k]     : Hz
PSD[k]   : uV²/Hz
Δf       : Hz
PSD[k]Δf : uV², công suất gần đúng trong bin
```

Day 10 không quay lại raw signal và không tự chạy FFT khác. Nguồn sự thật duy nhất là `SpectralEstimationResult v0.1`.

## 4.2. Mean Frequency — MNF

Với trục đều:

\[
MNF = \frac{\sum_k f_k P_k}{\sum_k P_k}
\]

Viết đầy đủ theo công suất bin:

\[
MNF = \frac{\sum_k f_k P_k\Delta f}{\sum_k P_k\Delta f}
\]

Do `Δf` giống nhau ở mọi bin, nó triệt tiêu.

### Bài tính tay bắt buộc

| f (Hz) | Trọng số |
|---:|---:|
| 50 | 1 |
| 100 | 2 |
| 150 | 1 |

\[
MNF = \frac{50+200+150}{4}=100\;Hz
\]

Bạn phải tự viết phép tính này vào:

```text
docs/note/day10/03-math-notes.md
```

## 4.3. Median Frequency — MDF

MDF là tần số chia tổng công suất thành hai phần bằng nhau:

\[
\int_{f_{low}}^{MDF}PSD(f)df
=\frac{1}{2}\int_{f_{low}}^{f_{high}}PSD(f)df
\]

Trên dữ liệu rời rạc:

```text
bin_power[k] = PSD[k] × Δf
cdf[k]       = cumulative sum of bin_power
MDF target   = 0.5 × total_power
```

Day 10 dùng quy ước:

```text
cdf_bin_edge_linear_v0.1
```

Tức là tìm bin chứa 50% và nội suy vị trí bên trong bin. Quy ước này phải được version hóa vì cách chọn “bin đầu tiên vượt 50%” hoặc nội suy giữa tâm bin có thể cho kết quả hơi khác.

## 4.4. Peak frequency không phải MDF hoặc MNF

```text
Peak frequency = vị trí PSD lớn nhất
MNF            = trọng tâm của toàn bộ phổ
MDF            = phân vị 50% của công suất
```

Không dùng `argmax(PSD)` để thay MDF/MNF.

## 4.5. Scale invariance

Nếu:

\[
P'_k=cP_k,\quad c>0
\]

thì:

\[
MDF(P')=MDF(P),\quad MNF(P')=MNF(P)
\]

Nhưng band power tăng `c` lần. Đây là invariant bắt buộc trong unit tests.

## 4.6. Ảnh hưởng của dải tần

MDF/MNF trên 20–400 Hz không nhất thiết bằng MDF/MNF trên 10–500 Hz. Vì vậy result phải lưu:

```text
spectral_estimator_id
analysis_band
frequency_feature_config_id
```

Không được so sánh các session có contract khác nhau mà không có calibration/validation.

## 4.7. Ý nghĩa sinh lý cần hiểu đúng

Trong các co cơ đẳng trường gây mỏi, sự dịch phổ về tần số thấp thường được theo dõi qua MDF/MNF giảm. Tuy nhiên:

- mức MVC khác nhau có thể tạo phổ khác nhau;
- after-fatigue/recovery có thể có xu hướng khác;
- electrode placement, crosstalk và filter ảnh hưởng phổ;
- một window không đại diện toàn bộ tiến trình.

Kết luận Day 10 chỉ là:

> “MDF/MNF đã được tính đúng theo contract kỹ thuật trên từng cửa sổ.”

Không được kết luận:

> “Cơ đã mỏi.”

---

# 5. Lịch thực thi tuần tự

## Buổi sáng — Học, khóa định nghĩa và pure DSP core

### Bước 0 — Tạo checkpoint Day 9

**Thời gian:** 08:00–08:10  
**Input:** repository sau Day 9  
**Hoạt động:**

```bash
git status --short
git log -1 --oneline
git switch -c day10-mdf-mnf-v0.1
```

**Output:** branch riêng cho Day 10.  
**Done:** working tree sạch hoặc mọi thay đổi chưa commit đã được giải thích.

---

### Bước 1 — Chạy regression Day 9

**Thời gian:** 08:10–08:35

```bash
bash scripts/dev/run_day9_checks.sh \
  2>&1 | tee qa-validation/evidence/day10-day9-regression.log
```

**Blocker rule:** nếu fail, dừng Day 10. Không sửa Day 10 để che lỗi Day 9.

**Output:** regression log.  
**Done:** exit code `0`.

---

### Bước 2 — Đọc lại spectral result contract

**Thời gian:** 08:35–08:55  
**File đọc:**

```text
docs/06-ai-signal-processing/spectral-estimation-spec.md
docs/05-data/spectral-estimation-result-contract.md
services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml
services/feature-extraction-service/src/spectral_result_models.py
```

**Câu hỏi phải trả lời:**

1. PSD vector nằm ở đâu?
2. Frequency axis được lưu một lần hay lặp ở mỗi row?
3. `band_power_uV2` và `full_power_uV2` khác nhau thế nào?
4. `not_computed` row cần được xử lý ra sao?

**Output:** `docs/note/day10/02-reading-notes.md`.

---

### Bước 3 — Đối chiếu công thức trong paper

**Thời gian:** 08:55–09:20  
**Hoạt động:** đọc phần spectral parameters của paper nền tảng; không chỉ nhìn nhãn MDF/MNF mà phải đối chiếu công thức.

**Bẫy cần ghi nhận:** một số tài liệu hoặc bản trích xuất văn bản có thể đảo nhãn mean/median. Canonical definition của dự án phải dựa trên công thức.

**Output:** bảng:

| Thuật ngữ | Định nghĩa canonical | Đơn vị |
|---|---|---|
| MDF | 50% spectral power quantile | Hz |
| MNF | power-weighted mean | Hz |

---

### Bước 4 — Tự giải ba bài toán known-answer

**Thời gian:** 09:20–09:50

1. Uniform PSD trên 20–400 Hz.
2. Single-bin power tại 80 Hz.
3. Trọng số 1:2:1 tại 50/100/150 Hz.

**Expected:**

```text
Uniform: MDF = MNF = 210 Hz
Single bin: MDF = MNF = 80 Hz
Weighted: MNF = 100 Hz
```

**Output:** phép tính tay trong math notes.  
**Done:** giải thích được vì sao MDF của hai đỉnh bằng nhau có thể không duy nhất về mặt lý thuyết và vì sao implementation cần quy ước xác định.

---

### Bước 5 — Khóa quyết định MDF/MNF

**Thời gian:** 09:50–10:10  
**Cập nhật:**

```text
docs/03-architecture/adr/ADR-0012-canonical-mdf-mnf-definitions.md
docs/00-executive/day10-decision-log-append.md
```

**Quyết định:**

- MNF: weighted centroid;
- MDF: CDF 50% + bin-edge interpolation;
- input: PSD 20–400 Hz từ Day 9;
- không peak substitution;
- không inference.

---

### Bước 6 — Review config trước code

**Thời gian:** 10:10–10:30  
**File:**

```text
services/feature-extraction-service/configs/frequency_features_v0.1.yaml
```

**Kiểm tra:**

```text
required_spectral_config_id = spectral_estimation_v0.1
clinical_validation_status = not_validated
MDF/MNF enabled
slope/evidence/rule/FRS/ML disabled
include_psd_vector = false
```

**Done:** config phản ánh đúng scope.

---

### Bước 7 — Implement pure core MDF/MNF

**Thời gian:** 10:30–11:15  
**File:**

```text
packages/semg-core/semg_core/spectral_features.py
```

**Hàm bắt buộc:**

```python
mean_frequency_hz(...)
median_frequency_hz(...)
extract_frequency_features(...)
```

**Guardrails:**

- vector 1D;
- frequency và PSD cùng kích thước;
- axis tăng nghiêm ngặt và đều;
- PSD hữu hạn, không âm;
- total power > threshold;
- output nằm trong band.

**Output:** pure functions không phụ thuộc service/API.

---

### Bước 8 — Viết known-answer unit tests

**Thời gian:** 11:15–12:00  
**File:**

```text
packages/semg-core/tests/test_spectral_features.py
```

**Tests:**

- uniform;
- single-bin;
- weighted centroid;
- scale invariance;
- zero power;
- negative PSD;
- non-uniform axis.

**Lệnh:**

```bash
pytest -q packages/semg-core/tests/test_spectral_features.py
```

**Done:** tất cả pass.

---

## Buổi chiều — Service, contract, CLI và E2E

### Bước 9 — Implement config loader

**Thời gian:** 13:00–13:25  
**File:**

```text
services/feature-extraction-service/src/frequency_feature_config.py
```

**Negative config tests:**

- clinical status bị đổi thành validated;
- slope bật sớm;
- MDF method sai;
- output chứa PSD vector.

---

### Bước 10 — Implement typed result models

**Thời gian:** 13:25–13:55  
**File:**

```text
services/feature-extraction-service/src/frequency_feature_result_models.py
```

**Row states:**

```text
computed
not_computed
```

**Session states:**

```text
completed
completed_with_exclusions
blocked
```

**Bất biến:** computed phải có values; not_computed phải có reason codes.

---

### Bước 11 — Implement extractor

**Thời gian:** 13:55–14:40  
**File:**

```text
services/feature-extraction-service/src/frequency_feature_extractor.py
```

**Luồng:**

```text
validate spectral stage
→ validate axis
→ iterate every spectral row
→ propagate not_computed
→ calculate MDF/MNF
→ compare recomputed band power
→ emit rows
→ canonical SHA-256
```

**Safety:** không silently drop row.

---

### Bước 12 — Viết service tests

**Thời gian:** 14:40–15:10

```bash
pytest -q \
  services/feature-extraction-service/tests/test_frequency_feature_config.py \
  services/feature-extraction-service/tests/test_frequency_feature_extractor.py
```

**Done:** config mismatch và blocked upstream đều được test.

---

### Bước 13 — Viết JSON Schemas

**Thời gian:** 15:10–15:35

```text
frequency-feature-row.schema.json
frequency-feature-extraction-result.schema.json
frequency-feature-verification.schema.json
```

**Kiểm tra:** `result_hash_sha256` là 64 ký tự hex hoặc null khi blocked.

---

### Bước 14 — Implement analytical verifier

**Thời gian:** 15:35–16:00  
**File:**

```text
scripts/data/verify_mdf_mnf.py
```

**Output:**

```text
qa-validation/evidence/day10-mdf-mnf-verification.json
qa-validation/evidence/day10-mdf-mnf-verification.md
```

---

### Bước 15 — Implement full pipeline CLI

**Thời gian:** 16:00–16:40  
**File:**

```text
scripts/data/run_frequency_features.py
```

**Pipeline:**

```text
CSV → Import → QC → Preprocess → Window → PSD → MDF/MNF
```

**CSV export:** chỉ chứa feature values và provenance; không lặp PSD vector.

---

### Bước 16 — Chạy targeted tests

**Thời gian:** 16:40–16:55

```bash
pytest -q \
  packages/semg-core/tests/test_spectral_features.py \
  services/feature-extraction-service/tests/test_frequency_feature_config.py \
  services/feature-extraction-service/tests/test_frequency_feature_extractor.py
```

---

### Bước 17 — Chạy golden E2E lần 1

**Thời gian:** 16:55–17:15

```bash
python scripts/data/run_frequency_features.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day10-frequency-features.json \
  --csv-out qa-validation/evidence/day10-frequency-features.csv \
  --expect-status completed \
  --expect-total-row-count 119 \
  --expect-computed-row-count 119 \
  --expect-not-computed-row-count 0
```

**Done:** 119/119 computed.

---

### Bước 18 — Deterministic rerun

**Thời gian:** 17:15–17:25

```bash
python scripts/data/run_frequency_features.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day10-frequency-features-rerun.json \
  --expect-status completed \
  --expect-total-row-count 119 \
  --expect-computed-row-count 119 \
  --expect-not-computed-row-count 0 \
  --quiet
```

**Done:** hai result hash giống nhau.

---

### Bước 19 — Negative E2E: upstream fail

**Thời gian:** 17:25–17:40

```bash
python scripts/data/run_frequency_features.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json \
  --json-out qa-validation/evidence/day10-frequency-features-blocked.json \
  --expect-status blocked \
  --expect-total-row-count 0 \
  --expect-reason FREQ_FEATURE_BLOCKED_BY_SPECTRAL \
  --quiet
```

**Done:** block đúng, không có row giả.

---

## Cuối ngày — Governance, notes và gate

### Bước 20 — Validate schema/hash/invariants

**Thời gian:** 17:40–17:55

```bash
python scripts/dev/validate_day10_outputs.py
```

**Invariants:**

- MDF/MNF trong 20–400 Hz;
- không PSD vector trong frequency feature output;
- blocked result không có rows;
- deterministic hash.

---

### Bước 21 — Đăng ký extractor

**Thời gian:** 17:55–18:05

```bash
python scripts/dev/register_frequency_features_v0_1.py
```

**Output:** entry trong:

```text
mlops/registry/feature_extractors.yaml
```

---

### Bước 22 — Hoàn thiện tài liệu

**Thời gian:** 18:05–18:30

```text
docs/06-ai-signal-processing/mdf-mnf-math-primer.md
docs/06-ai-signal-processing/frequency-domain-feature-spec.md
docs/05-data/frequency-domain-feature-result-contract.md
docs/08-validation-qa/day10-mdf-mnf-test-plan.md
```

---

### Bước 23 — Điền toàn bộ notes

**Thời gian:** 19:15–19:45

Không để file note chỉ còn placeholder. Ghi:

- phép tính tay;
- điểm chưa hiểu;
- output hash trên máy;
- quyết định kỹ thuật;
- giới hạn lâm sàng.

---

### Bước 24 — Tự kiểm tra kiến thức

**Thời gian:** 19:45–20:00

Không nhìn tài liệu, trả lời:

1. MNF là gì?
2. MDF là gì?
3. Peak frequency khác gì?
4. Vì sao `Δf` triệt tiêu trong MNF trên trục đều?
5. Vì sao MDF cần quy ước nội suy?
6. Vì sao scale PSD không đổi MDF/MNF?
7. Vì sao analysis band phải nằm trong provenance?
8. Vì sao một MDF giảm đơn lẻ chưa đủ kết luận?

Đạt tối thiểu 7/8.

---

### Bước 25 — Chạy one-command checker

**Thời gian:** 20:00–20:10

```bash
bash scripts/dev/run_day10_checks.sh
```

Chạy full regression khi cần:

```bash
DAY10_FULL_REGRESSION=1 bash scripts/dev/run_day10_checks.sh
```

---

### Bước 26 — Commit và gate

**Thời gian:** 20:10–20:20

```bash
git add \
  docs \
  packages/semg-core \
  packages/common-schemas \
  services/feature-extraction-service \
  scripts \
  qa-validation \
  mlops/registry

git diff --staged --check
git diff --staged --stat

git commit -m "day10: implement verified MDF and MNF features v0.1"
git tag day10-frequency-features-v0.1
```

Không bắt đầu Day 11 nếu checker chưa pass.

---

# 6. Kết quả kỳ vọng trên golden fixture

```text
status                 = completed
total_row_count        = 119
computed_row_count     = 119
not_computed_row_count = 0
feature_names          = [mdf, mnf]
frequency unit         = Hz
clinical validation    = not_validated
```

Không hard-code giá trị MDF/MNF từng window vào acceptance criteria vì chúng phụ thuộc synthetic generator và implementation version. Chỉ khóa known-answer tests và deterministic output trong cùng environment.

---

# 7. Sai lầm thường gặp

1. Đảo MDF và MNF do chỉ đọc nhãn trong một tài liệu.
2. Dùng peak frequency thay MDF.
3. Tính MDF trên raw FFT magnitude thay vì PSD contract.
4. Quên giới hạn analysis band.
5. Dùng `np.mean(frequency)` làm MNF.
6. Cho zero-power row một giá trị 0 Hz thay vì `not_computed`.
7. Bỏ row lỗi khỏi output và làm sai window count.
8. Kết luận “fatigue” từ một feature window.
9. Không lưu spectral result hash.
10. So sánh session có config khác nhau.

---

# 8. Definition of Done Day 10

- [ ] Day 9 regression pass.
- [ ] Core MDF/MNF known-answer tests pass.
- [ ] Uniform PSD: MDF=MNF=210 Hz.
- [ ] Single-bin 80 Hz: MDF=MNF=80 Hz.
- [ ] Scale invariance pass.
- [ ] Golden E2E 119/119 rows.
- [ ] Upstream fail block đúng.
- [ ] JSON schemas pass.
- [ ] Deterministic hash pass.
- [ ] Registry updated.
- [ ] Output không chứa PSD/raw signal.
- [ ] Không slope/evidence/status/FRS/ML.
- [ ] `clinical_validation_status=not_validated`.
- [ ] Notes tiếng Việt đã điền đầy đủ.
- [ ] Commit/tag hoàn tất.

---

# 9. Handoff sang Day 11

Day 11 chỉ bắt đầu khi Day 10 pass. Input Day 11:

```text
TimeDomainFeatureExtractionResult v0.1
        RMS/MAV, 239 windows
+
FrequencyFeatureExtractionResult v0.1
        MDF/MNF, 119 windows
```

Day 11 sẽ fit mỗi feature **độc lập theo `center_time_s`**, không ép ghép một-một hai profile window khác nhau.
