# Đặc tả trích xuất đặc trưng sEMG — Day 8 RMS/MAV v0.1

**Artifact:** `docs/06-ai-signal-processing/feature-extraction-spec.md`  
**Config:** `features_semg_v0.1`  
**Phase:** MVP-0 offline  
**Trạng thái xác nhận lâm sàng:** `not_validated`

## 1. Mục đích

Day 8 triển khai feature extractor đầu tiên của pipeline, tạo hai đặc trưng biên độ theo từng cửa sổ hợp lệ:

```text
RMS — Root Mean Square
MAV — Mean Absolute Value
```

Luồng dependency:

```text
CSV / Noraxon-like export / synthetic fixture
        ↓
Ingestion
        ↓
Signal Quality Gate
        ↓
Preprocessing v0.1
        ↓
Windowing v0.1 — time_domain profile 500 ms
        ↓
RMS/MAV Feature Extractor v0.1
        ↓
Feature rows có provenance
```

Module không tạo fatigue status, FRS, threshold lâm sàng, ML prediction hoặc khuyến nghị điều trị.

---

## 2. Phạm vi

### 2.1. Trong phạm vi

- Đọc `WindowingRunResult` đã `downstream_allowed=true`.
- Chỉ dùng profile `time_domain` có purpose `rms_mav`.
- Chỉ tính trên window có `status=valid`.
- Tính RMS và MAV trên `uV`, band-passed, unrectified, untapered samples.
- Giữ một row cho mỗi channel-window.
- Với invalid window, tạo row `not_computed` và không impute.
- Gắn geometry, context, version và hash upstream.
- Xuất JSON/CSV không chứa raw samples.
- Tạo deterministic result hash.

### 2.2. Ngoài phạm vi

- PSD, Welch, MDF, MNF.
- Slope/trend, percentage change, fatigue onset.
- MVC hoặc baseline normalization.
- Tổng hợp nhiều channel.
- So sánh hai bên hoặc longitudinal.
- MFCV/CV.
- Rule engine, FRS, classifier, confidence lâm sàng.
- Near-real-time/realtime production.

---

## 3. Input contract

### 3.1. Required upstream state

| Field | Required value |
|---|---|
| `windowing_result.downstream_allowed` | `true` |
| `windowing_config_id` | `windowing_v0.1` |
| `preprocess_config_id` | `preprocess_v0.1` |
| `profile_id` | `time_domain` |
| `profile.purpose` | `rms_mav` |
| canonical amplitude unit | `uV` |
| sample view | unrectified, untapered |
| window validity | `valid` trước khi tính |

### 3.2. Window geometry mặc định

```text
window duration = 500 ms
overlap = 50%
hop = 250 ms
active phase = 60 s
Fs = 1000 Hz
```

Golden expected:

```text
window size = 500 samples
hop = 250 samples
window count = 239 per channel
```

### 3.3. Defense-in-depth

Ngay cả khi Day 7 đánh dấu window valid, pure feature core vẫn từ chối:

- mảng rỗng;
- mảng không phải một chiều;
- `NaN`;
- `+Inf/-Inf`;
- output không hữu hạn.

---

## 4. Công thức

### 4.1. RMS

\[
RMS=\sqrt{\frac{1}{N}\sum_{n=0}^{N-1}x[n]^2}
\]

### 4.2. MAV

\[
MAV=\frac{1}{N}\sum_{n=0}^{N-1}|x[n]|
\]

### 4.3. Bất biến kiểm thử

```text
RMS >= MAV >= 0
RMS(-x) = RMS(x)
MAV(-x) = MAV(x)
RMS(c x) = |c| RMS(x)
MAV(c x) = |c| MAV(x)
```

### 4.4. Numerical stability

Implementation dùng scale normalization:

```python
scale = max(abs(x))
normalized = x / scale
rms = scale * sqrt(mean(normalized**2))
mav = scale * mean(abs(normalized))
```

Điều này giảm nguy cơ overflow khi bình phương các giá trị hữu hạn rất lớn.

---

## 5. Semantics preprocessing

### 5.1. Không rectify trước feature

RMS và MAV đã loại ảnh hưởng của dấu bằng bình phương/trị tuyệt đối. Feature layer không áp dụng transform thêm.

```text
apply_rectification_before_rms = false
apply_rectification_before_mav = false
```

### 5.2. Không taper

Hann taper dành cho spectral estimation, không dùng cho RMS/MAV vì làm thay đổi biên độ.

```text
apply_taper = false
```

### 5.3. Không trừ mean lại theo window

Preprocessing v0.1 đã mean-center/band-pass. Nếu sau này cần per-window demean, phải tạo cấu hình/version mới và kiểm chứng ảnh hưởng.

```text
remove_window_mean_again = false
```

### 5.4. Không normalization

```text
normalization.mode = none
mvc_normalized = false
baseline_normalized = false
```

Hệ quả: không cho phép so sánh amplitude trực tiếp giữa subject/session/device/protocol khác nhau.

---

## 6. Thuật toán

### 6.1. Pseudocode

```text
function extract(windowing_result):
    if windowing blocked:
        return blocked(FEATURE_EXTRACTION_BLOCKED_BY_WINDOWING)

    validate windowing/preprocess versions
    select time_domain profile
    validate purpose == rms_mav

    rows = []
    for channel in deterministic channel order:
        for geometry, validity in deterministic window order:
            if validity != valid:
                emit not_computed row
                propagate reason codes
                continue

            samples = read_only_window_view(...)
            try:
                rms = RMS(samples)
                mav = MAV(samples)
                assert rms >= mav within tolerance
                emit computed row
            except computation error:
                emit not_computed row(FEATURE_COMPUTATION_FAILED)

    if computed_count == 0:
        return blocked(FEATURE_NO_COMPUTED_ROWS)

    result_hash = SHA256(canonical JSON over metadata + rows)
    return completed or completed_with_exclusions
```

### 6.2. Deterministic ordering

```text
channel_id ascending
then window_index ascending
```

Không dựa vào thứ tự ngẫu nhiên của dictionary hoặc filesystem.

---

## 7. Status model

### 7.1. Result status

| Status | Meaning | Downstream |
|---|---|---:|
| `completed` | mọi valid window được tính | allowed |
| `completed_with_exclusions` | có row không tính được/invalid | allowed, nhưng phải propagate warning |
| `blocked` | không có input/không còn computed row/version mismatch | blocked |

### 7.2. Row status

| Status | Feature values | Reason codes |
|---|---|---|
| `computed` | có RMS/MAV | rỗng |
| `not_computed` | `null` | ít nhất một code |

Không nội suy invalid row và không bỏ row im lặng, nhằm giữ traceability với window plan.

---

## 8. Reason codes

| Code | Level | Meaning |
|---|---:|---|
| `FEATURE_EXTRACTION_BLOCKED_BY_WINDOWING` | blocking | upstream không có valid plan |
| `FEATURE_WINDOWING_CONFIG_MISMATCH` | blocking | sai windowing version |
| `FEATURE_PREPROCESS_CONFIG_MISMATCH` | blocking | sai preprocessing version |
| `FEATURE_PROFILE_NOT_FOUND` | blocking | không có `time_domain` |
| `FEATURE_PROFILE_PURPOSE_MISMATCH` | blocking | profile không dành cho RMS/MAV |
| `FEATURE_NO_COMPUTED_ROWS` | blocking | không còn row tính được |
| `FEATURE_WINDOWS_EXCLUDED` | warning | một số row không tính |
| `FEATURE_COMPUTATION_FAILED` | warning/block tùy số lượng | defense-in-depth thất bại |
| inherited Day 7 reason | row-level | window invalid do mask/non-finite |

---

## 9. Output contract

### 9.1. Feature row

Mỗi row chứa:

- ID deterministic;
- session/channel/muscle/side/role;
- phase/profile;
- window geometry;
- status;
- RMS/MAV hoặc `null`;
- reason codes;
- feature/window/preprocess versions;
- source and window-plan hashes.

### 9.2. Không chứa

- raw signal samples;
- patient PHI;
- fatigue label;
- diagnosis;
- treatment recommendation;
- FRS;
- probability/confidence lâm sàng.

### 9.3. Hash

`result_hash_sha256` được tính từ canonical JSON gồm metadata và feature rows. Hash dùng cho:

- deterministic rerun;
- audit;
- regression;
- traceability.

Hash không chứng minh giá trị lâm sàng và không chứng minh nguồn dữ liệu là thiết bị thật.

---

## 10. Interface và repository mapping

| Trách nhiệm | File |
|---|---|
| Pure RMS/MAV math | `packages/semg-core/semg_core/features.py` |
| Service wrapper | `services/feature-extraction-service/src/time_domain.py` |
| Config validation | `services/feature-extraction-service/src/feature_config.py` |
| Result models | `services/feature-extraction-service/src/feature_result_models.py` |
| Orchestration | `services/feature-extraction-service/src/extractor.py` |
| Config | `services/feature-extraction-service/configs/features_semg_v0.1.yaml` |
| Row schema | `packages/common-schemas/json/feature-row.schema.json` |
| Result schema | `packages/common-schemas/json/time-domain-feature-result.schema.json` |
| E2E CLI | `scripts/data/run_time_domain_features.py` |
| Analytical verifier | `scripts/data/verify_time_domain_features.py` |

---

## 11. Verification requirements

### 11.1. Hand-calculated vectors

- `[-3, -1, 1, 3]`.
- `[-5, 5, -5, 5]`.
- zero vector.

### 11.2. Analytical signal

- sine có biên độ biết trước;
- test RMS `A/sqrt(2)`;
- test MAV với tolerance sampling rõ.

### 11.3. Properties

- sign invariance;
- scaling;
- RMS ≥ MAV;
- large finite values không overflow không cần thiết;
- non-finite rejected.

### 11.4. Pipeline

- golden có 239 computed rows;
- invalid mask tạo `not_computed` row đúng index;
- deterministic result hash;
- schema pass;
- không có raw sample;
- upstream block được propagate.

---

## 12. Safety and clinical boundary

RMS/MAV là evidence kỹ thuật có điều kiện, không phải ground truth fatigue.

Không được tạo câu:

```text
RMS tăng nên cơ đã mỏi.
Bệnh nhân cần dừng tập.
Bệnh nhân đủ/không đủ return-to-play.
```

Chỉ được tạo câu kỹ thuật:

```text
RMS/MAV được tính trên 239 cửa sổ hợp lệ của active_contraction.
Giá trị chưa được chuẩn hóa MVC và chỉ có ý nghĩa trong context của session/protocol hiện tại.
```

Mọi interpretation lâm sàng về sau phải có:

- QC pass/warning context;
- spectral/trend evidence;
- protocol metadata;
- local validation;
- human review.

---

## 13. Versioning

`features_semg_v0.1` được xem là thay đổi version nếu thay đổi bất kỳ mục nào:

- công thức;
- denominator;
- window profile;
- preprocessing semantics;
- unit;
- normalization;
- invalid-window policy;
- output row schema;
- aggregation behavior.

Không sửa file nhưng giữ nguyên version sau khi đã đăng ký evidence. Thay đổi phải tạo `features_semg_v0.2` hoặc phiên bản phù hợp.

---

## 14. Exit criteria

- Pure core test pass.
- Config guardrail test pass.
- Service test pass.
- Analytical verification pass.
- Golden 239/239 computed rows.
- Invalid-window test tạo null row đúng.
- JSON Schema pass.
- Deterministic hash pass.
- Registry ghi `clinical_validation_status=not_validated`.
- Không có fatigue/ML/report logic trong extractor.
