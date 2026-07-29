# Báo cáo Day30 phục vụ Day31 — Feature Engineering 14 đặc trưng

## 1. Kết luận điều hành

Day30 đã hoàn thành lớp **harmonization, governance và leakage control** cho hai bộ dữ liệu Mendeley và GRABMyo. Day30 chưa tính 14 feature hay huấn luyện mô hình; đầu ra của nó là hợp đồng dữ liệu đủ chặt để Day31 triển khai feature engineering có thể tái lập.

Trạng thái bàn giao:

- Baseline commit: `1387879`
- Verification hardening: `66d1b12`, `4e81e4a`, `7b77d74`, `b099382`
- Window-ID digest: `bedc850968521b706109dca95f7680f8901bfcb9c69d4a11151999aa90231aa3`
- Tag: `day30-dual-dataset-harmonization-v1.0`
- Quyết định: `GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE`
- Chỉ được chạy baseline riêng từng dataset.
- Chưa được pooled training Mendeley + GRABMyo.
- Full baseline vẫn bị chặn do chưa xác minh full subject index, dependency lock, split hashes và training authorization đầy đủ.
- Stress test Day30:
  - 5.000 synthetic records
  - 92.255 windows
  - 6/6 partition/path attacks bị chặn
  - 9/9 stored-row mutation/duplicate attacks bị chặn
  - Không có false positive khi hai dataset dùng cùng `subject_id`
  - 9,463 giây trên runner bàn giao
  - Peak traced memory 109,821 MiB
  - Không có test signal bị truy cập
  - Không có training ngoài ý muốn
- Regression:
  - Day30: 52/52 test đạt
  - Core line coverage: 86,97% (Python stdlib trace; performance stress đo riêng)
  - Day28: 5/5
  - Day29: 14/14

Nguồn chính: [Day30 handoff](</data/projects/semg-fatigue/MyoLab-AI/docs/05-data/day30/08-experiment-eligibility-and-day31-handoff.md:1>), [readiness evidence](</data/projects/semg-fatigue/MyoLab-AI/qa-validation/evidence/day30/day30-readiness-decision.json:1>), [stress-test evidence](</data/projects/semg-fatigue/MyoLab-AI/qa-validation/evidence/day30/day30-stress-test.json:1>), [coverage evidence](</data/projects/semg-fatigue/MyoLab-AI/qa-validation/evidence/day30/day30-line-coverage.json:1>).

---

## 2. Đơn vị tính feature của Day31

Mỗi feature phải được tính độc lập trên:

```text
dataset_id × split × record_id × window_id × channel_id
```

Quy trình bắt buộc:

```text
Raw record
 → kiểm tra provenance/QC
 → split theo subject/session/repetition
 → DC removal
 → windowing trong atomic unit
 → tính 14 features trên từng channel
 → fit scaler chỉ bằng inner-train
 → pivot thành model matrix theo từng dataset view
```

Điểm quan trọng nhất: **split trước, window sau**. Các cửa sổ chồng lấn không được phép nằm ở hai partition khác nhau.

---

## 3. Dataset views và số chiều feature

### Mendeley primary

- Channel: `CH1–CH3`
- `CH4` bị quarantine, không dùng trong primary baseline.
- Nhãn: `rest`, `hand_close`, `wrist_flexion`, `wrist_extension`.
- Số chiều khi pivot: `3 × 14 = 42 features/window`.

### Mendeley CH4 sensitivity

- Channel: `CH1–CH4`
- Chỉ dùng làm sensitivity analysis.
- Số chiều: `4 × 14 = 56`.

Không được mô tả CH4 là “broken”, “reference” hay “invalid” khi chưa có bằng chứng provenance tương ứng.

### GRABMyo primary

- Channel: `F1–F16`, `W1–W12`
- Tổng cộng 28 channel.
- `U1–U4` không tham gia primary view nhưng vẫn giữ provenance.
- Nhãn: bốn lớp giao với Mendeley cộng `hand_open`.
- Số chiều: `28 × 14 = 392`.

### Cross-source comparator

Phần giao ontology chỉ gồm:

```text
rest
hand_close
wrist_flexion
wrist_extension
```

Không được tạo giả `hand_open` cho Mendeley.

Mendeley và GRABMyo không có ánh xạ giải phẫu channel tương đương, nên không được nối trực tiếp 42 và 392 chiều. Comparator xuyên dataset phải dùng channel summaries như:

- Median
- IQR
- Q90
- Maximum
- Active-channel fraction

Nếu áp dụng năm summary cho cả 14 feature, representation chung có tối đa `14 × 5 = 70` chiều.

Nguồn: [ontology và dataset views](</data/projects/semg-fatigue/MyoLab-AI/docs/05-data/day30/05-label-ontology-and-dataset-views.md:1>), [channel policy](</data/projects/semg-fatigue/MyoLab-AI/docs/05-data/day30/04-channel-strategy-and-ch4-quarantine.md:1>).

---

## 4. Windowing và sampling rate

### Primary window

- Window: 200 ms
- Hop: 100 ms
- Overlap: 50%
- Chuyển thời gian sang số mẫu bằng `round-half-up`.

Số mẫu gần đúng:

| Dataset | Sampling rate | 200 ms | 100 ms hop |
|---|---:|---:|---:|
| Mendeley | 2000 Hz | 400 | 200 |
| GRABMyo | 2048 Hz | 410 | 205 |

### Sensitivity windows

- 150/75 ms
- 250/125 ms

Các cửa sổ 500/250 ms và 1000/500 ms chỉ là context lane, không thay thế primary Task A.

### Sampling policy

Primary phải dùng native rate:

- Mendeley: 2000 Hz
- GRABMyo: 2048 Hz

Mọi feature phổ phải nhận `sampling_rate_hz` từ record metadata. Tuyệt đối không hard-code một `fs` chung.

Comparator resampling duy nhất được cho phép:

```text
GRABMyo 2048 Hz → 2000 Hz
polyphase ratio = 125/128
```

Độ phân giải phổ của primary window gần như tương đương:

- Mendeley: `2000 / 400 = 5 Hz`
- GRABMyo: `2048 / 410 ≈ 4,995 Hz`

Vì vậy, MDF và MNF có thể biểu diễn trực tiếp bằng Hz mà chưa cần resampling.

Nguồn: [sampling policy](</data/projects/semg-fatigue/MyoLab-AI/docs/05-data/day30/03-sampling-rate-and-resampling-policy.md:1>), [windowing policy](</data/projects/semg-fatigue/MyoLab-AI/docs/05-data/day30/06-windowing-and-segmentation-policy.md:1>).

---

## 5. Hợp đồng đề xuất cho 14 features

Ký hiệu:

- \(x_i\): mẫu sau DC removal
- \(N\): số mẫu hợp lệ
- \(\bar{x}\): trung bình trong window
- \(P_k\): PSD một phía
- \(f_k\): tần số tương ứng với bin \(k\)

| Feature | Hợp đồng tính toán đề xuất cho Day31 |
|---|---|
| RMS | \(\sqrt{\frac{1}{N}\sum x_i^2}\) |
| MAV | \(\frac{1}{N}\sum |x_i|\) |
| Skewness | Adjusted Fisher–Pearson skewness, tương đương `scipy.stats.skew(x, bias=False)` |
| Kurtosis | Cần khóa rõ Fisher excess hay Pearson; đề xuất Fisher excess, `fisher=True, bias=False` |
| Max | \(\max(x_i)\), giữ dấu |
| Min | \(\min(x_i)\), giữ dấu |
| STD | Cần khóa `ddof`; tài liệu Day26 dùng sample STD, tức `ddof=1` |
| Mean | \(\frac{1}{N}\sum x_i\) |
| Spectral_Min | \(\min(P_k)\) trên tập bin phổ hợp lệ |
| Spectral_Max | \(\max(P_k)\) |
| Spectral_STD | STD của \(P_k\), phải dùng cùng quy ước `ddof` đã khóa |
| MDF | Bin đầu tiên làm cumulative PSD đạt ít nhất 50% tổng power |
| MNF | \(\frac{\sum f_kP_k}{\sum P_k}\) |
| Spectral Entropy | \(-\sum p_k\log(p_k)\), với \(p_k=P_k/\sum P_k\) |

Day26 xem RMS là mandatory baseline; MAV và STD là comparator; MDF/MNF là conditional; spectral entropy là engineering hypothesis. Do đó, việc sử dụng toàn bộ 14 feature cần được xem là một **experiment arm có kiểm soát**, không phải bộ feature mặc nhiên thắng. Nguồn: [Day26 feature review](</data/projects/semg-fatigue/MyoLab-AI/docs/research/day26/02-feature-engineering-review.md:37>) và [feature classification](</data/projects/semg-fatigue/MyoLab-AI/docs/research/day26/02-feature-engineering-review.md:537>).

---

## 6. Những quy ước phải khóa trước khi viết extractor

Danh sách 14 feature hiện vẫn thiếu một số chi tiết có thể làm hai implementation cho kết quả khác nhau.

### Kurtosis

Phải chọn chính thức:

- Fisher/excess kurtosis: phân phối chuẩn bằng 0; hoặc
- Pearson kurtosis: phân phối chuẩn bằng 3.

Đề xuất cho Day31:

```python
scipy.stats.kurtosis(x, fisher=True, bias=False)
```

Tên feature nên phản ánh rõ:

```text
kurtosis_fisher_unbiased
```

### Standard deviation

Tài liệu Day26 dùng:

\[
\sqrt{\frac{1}{N-1}\sum(x_i-\bar{x})^2}
\]

Do đó nên khóa:

```text
ddof = 1
```

Nếu cần tương thích một implementation legacy dùng `ddof=0`, phải tạo feature version khác, không âm thầm thay đổi.

### PSD

Công thức `|FFT(x)|² / nfft` chưa đủ để tái lập. Day31 cần khóa:

- `rfft` một phía;
- `nfft`;
- window function: rectangular hay Hann;
- có nhân đôi các interior one-sided bins hay không;
- có loại DC/Nyquist không;
- dải tần hợp lệ;
- normalization unit.

Đề xuất cho bản tương thích trực tiếp với định nghĩa người dùng:

```text
estimator     = one-sided periodogram
fft           = rfft
nfft          = N
window        = rectangular
normalization = |FFT(x)|² / nfft
```

Cần đặt tên nó là `periodogram_power` hoặc `legacy_psd_proxy` nếu không áp dụng normalization theo Hz. Không nên gọi là power spectral density vật lý nếu chưa chia theo sampling rate/window energy đúng chuẩn.

### Spectral entropy

Phải khóa:

- log tự nhiên hay log base 2;
- entropy thô hay normalized entropy;
- cách xử lý bin có xác suất 0.

Đề xuất:

```text
log_base      = 2
zero bins     = bỏ khỏi phép p·log(p)
output        = entropy_bits
```

Nếu muốn so sánh giữa cấu hình có số bin khác nhau, bổ sung phiên bản:

\[
H_\text{normalized} = \frac{H}{\log_2 K}
\]

Không thay entropy thô bằng normalized entropy dưới cùng một feature name.

### Zero-power và constant windows

Nếu tổng PSD bằng 0, MDF, MNF và entropy không xác định. Hợp đồng nên:

- trả `NaN`;
- gắn QC flag như `zero_power_window`;
- không tự động trả 0;
- không loại window mà không ghi audit record.

---

## 7. Ảnh hưởng của normalization

Day30 khóa primary normalization là:

```text
per-record, per-channel mean subtraction
```

Không có:

- raw per-trial z-score;
- global z-score;
- global robust scaler;
- learned normalization fit trên toàn dataset.

Hệ quả với 14 features:

- `Mean` trở thành độ lệch cục bộ của window quanh mean toàn record, không nhất thiết bằng 0.
- RMS và STD sẽ gần nhau nếu window mean nhỏ.
- RMS, MAV, Max, Min, STD, Spectral_Max và Spectral_STD phụ thuộc mạnh vào gain/amplitude.
- Skewness, Kurtosis và normalized spectral entropy ít nhạy với scale hơn, nhưng vẫn nhạy với artifact và windowing.

Feature scaler chỉ được fit:

```text
grouped inner-training fold only
```

Mỗi dataset/view phải có scaler riêng. Không được fit scaler chung Mendeley + GRABMyo vì hai nguồn có scale/gain khác nhau đáng kể.

Nguồn: [normalization policy](</data/projects/semg-fatigue/MyoLab-AI/docs/05-data/day30/02-normalization-and-dc-policy.md:1>).

---

## 8. Thiết kế experiment phù hợp cho Day31

Tôi đề xuất Day31 không chỉ chạy một vector 14 feature duy nhất mà chia thành các arm predeclared:

| Arm | Feature set | Mục đích |
|---|---|---|
| F-TD8 | RMS, MAV, Skewness, Kurtosis, Max, Min, STD, Mean | Baseline miền thời gian |
| F-SP6 | Spectral_Min, Spectral_Max, Spectral_STD, MDF, MNF, Entropy | Đánh giá riêng đóng góp phổ |
| F-ALL14 | Toàn bộ 14 feature | Full requested feature set |
| F-ABLATE-MOMENTS | Bỏ Skewness/Kurtosis | Kiểm tra độ nhạy với spike/outlier |
| F-ABLATE-SPECTRAL | Chỉ TD8 | Kiểm tra PSD ngắn 200 ms có thực sự hữu ích |

MDF/MNF và spectral entropy trên 200 ms có thể nhiễu. Day26 khuyến nghị ưu tiên từ 250–500 ms cho PSD ổn định hơn. Vì vậy nên:

- Giữ 200 ms là primary để đúng Task A.
- Chạy 250 ms sensitivity.
- Chỉ dùng 500 ms làm context/spectral stability study.
- Không chọn window bằng kết quả test.

---

## 9. Schema đầu ra đề xuất

Canonical storage nên là long format:

```text
dataset_id
dataset_view_id
split_name
subject_id
session_id
record_id
window_id
channel_id
feature_id
feature_value
feature_version
sampling_rate_hz
window_ms
hop_ms
preprocessing_policy_id
channel_policy_id
source_file_sha256
split_version
label_mapping_version
qc_flags
```

Sau đó mới pivot cho model:

```text
window_id × (channel_id, feature_id)
```

Không nên lưu raw windows mặc định. Feature table ưu tiên partitioned Parquet; fallback là CSV.gz long format.

Nguồn: [storage contract](</data/projects/semg-fatigue/MyoLab-AI/docs/05-data/day30/07-output-storage-contract.md:1>).

---

## 10. Các giới hạn khoa học phải mang sang Day31

- MDF/MNF có thể nhạy với fatigue nhưng cũng bị ảnh hưởng bởi force, contraction mode, electrode placement và task.
- Không được diễn giải MDF/MNF là biomarker fatigue độc lập.
- Không được vừa dùng MDF/MNF để tạo fatigue label, vừa dùng chính family feature đó làm predictor mà không có nhãn fatigue độc lập; đây là circularity leakage.
- Các feature amplitude không được so sánh trực tiếp về magnitude giữa hai dataset.
- Không được tuyên bố direct anatomical equivalence giữa Mendeley và GRABMyo.
- `Spectral_Min` thường rất gần 0 và nhạy với `nfft`; cần kiểm tra variance/near-constant rate trong train.
- RMS, MAV và STD có tương quan cao; Day31 phải báo correlation/redundancy thay vì mặc định coi chúng là ba nguồn thông tin độc lập.
- Skewness và Kurtosis nhạy mạnh với spike, clipping và motion artifact; cần stress test outlier trước bàn giao.

## Kết luận cho Day31

Day31 có thể bắt đầu feature engineering 14 đặc trưng ở chế độ **separate baseline smoke** với:

- Mendeley primary: 42 chiều;
- GRABMyo primary: 392 chiều;
- native sampling rates;
- window 200/100 ms;
- split-before-windowing;
- scaler fit inner-train only;
- full mathematical feature contract được version hóa;
- F-TD8 và F-ALL14 được đánh giá như hai arm riêng;
- spectral sensitivity 250–500 ms;
- không pooled training và không fatigue/clinical claim.

Điểm cần khóa ngay trong Day31 implementation là: **kurtosis convention, STD `ddof`, PSD estimator/`nfft`/band, entropy base và zero-power behavior**. Nếu không khóa năm mục này, bộ “14 features” sẽ không đạt yêu cầu tái lập chuẩn quốc tế.
