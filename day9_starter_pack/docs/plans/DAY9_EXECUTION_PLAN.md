# DAY 9 — Nền tảng miền tần số v0.1: DFT, FFT, PSD, Hann, Welch và kiểm chứng Golden

**Dự án:** sEMG/MFCV Fatigue Clinical Intelligence Layer  
**Chế độ nhân sự:** một người thực hiện tuần tự toàn bộ vai trò  
**Điều kiện bắt đầu:** Day 1–8 đã hoàn thành; `scripts/dev/run_day8_checks.sh` đang PASS  
**Mức sản phẩm:** MVP-0, offline-first, synthetic/generic-CSV technical verification  
**Trọng tâm hôm nay:** tạo nền tảng ước lượng phổ công suất một phía, có đơn vị, provenance, kiểm thử toán học và golden E2E  
**Không phải mục tiêu hôm nay:** MDF, MNF, slope, fatigue onset, FRS, rule engine, ML, dashboard, chẩn đoán hoặc khuyến nghị lâm sàng

> Day 9 không chỉ là “gọi FFT”. Mục tiêu là chứng minh toàn bộ contract từ một cửa sổ sEMG hợp lệ đến Power Spectral Density có trục tần số, đơn vị, normalization, taper, dải phân tích và kiểm tra năng lượng đúng. Nếu tầng này sai, MDF/MNF ở Day 10 có thể trả về con số hợp lệ về kiểu dữ liệu nhưng sai về ý nghĩa.

---

# 0. Kết quả cuối ngày phải đạt

Cuối Day 9, pipeline phải chạy được đến đây:

```text
Motion Lab / Noraxon-like export / Synthetic CSV
        ↓
Data Ingestion Adapter
        ↓
NormalizedSignal
        ↓
Signal Quality Gate v0.1
        ↓
Preprocessing v0.1
        ↓
Windowing v0.1
        └── frequency_domain profile
            window = 1000 ms
            overlap = 50%
            119 windows trên active phase 60 s
                ↓
Spectral Estimation v0.1
        ├── kiểm tra window hợp lệ
        ├── detrend constant
        ├── Hann taper
        ├── one-sided Welch PSD
        ├── nperseg = toàn outer window
        ├── Welch internal overlap = 0
        ├── nfft = outer window length
        ├── không zero-padding
        ├── cắt dải 20–400 Hz
        ├── PSD unit = uV²/Hz
        ├── tích phân power = uV²
        ├── Parseval QA
        ├── peak frequency chỉ dùng QA
        ├── shared frequency axis
        └── deterministic result hash
                ↓
Spectral JSON + Spectral CSV + Analytical Evidence
```

## 0.1. Golden output bắt buộc

Với fixture hiện tại:

```text
Fs = 1000 Hz
active phase = 60 s
frequency-domain window = 1000 ms
hop = 500 ms
channel count = 1
outer window length = 1000 samples
nperseg = 1000
nfft = 1000
analysis band = 20–400 Hz, inclusive
```

phải thu được:

```text
status                 = completed
downstream_allowed     = true
total_row_count        = 119
computed_row_count     = 119
not_computed_row_count = 0
usable_window_ratio    = 1.0
frequency_bin_count    = 381
frequency_axis_start   = 20.0 Hz
frequency_axis_end     = 400.0 Hz
bin_spacing            = 1.0 Hz
mdf_mnf_computed       = false
```

Lý do có 381 bins:

```text
20, 21, 22, ..., 400 Hz
400 - 20 + 1 = 381 bins
```

## 0.2. Câu Done chính thức

> `spectral_estimation_v0.1` đã tạo one-sided Hann/Welch PSD deterministic trên mọi cửa sổ `frequency_domain` hợp lệ, giữ đúng đơn vị, shared frequency axis, power/Parseval QA và provenance; invalid hoặc low-power window không bị impute; upstream QC fail chặn toàn bộ spectral stage; analytical, E2E, schema, deterministic-hash và registry checks đều PASS; MDF/MNF và mọi diễn giải fatigue vẫn chưa được bật.

## 0.3. Day 9 không chứng minh điều gì

Day 9 không chứng minh:

- PSD tự nó phát hiện được mỏi cơ;
- peak frequency là fatigue biomarker cuối cùng;
- MDF hoặc MNF đã đúng, vì chưa triển khai;
- dải 20–400 Hz tối ưu cho mọi thiết bị, cơ hoặc protocol;
- Hann là taper tối ưu cho mọi dữ liệu thật;
- Welch một segment giảm được phương sai như Welch nhiều segment;
- spectral trend synthetic là hiện tượng sinh lý thật;
- hệ thống đã được clinical validation;
- pipeline đã sẵn sàng realtime;
- có thể sao chép accuracy/F1 từ paper sang dữ liệu local.

---

# 1. Vì sao Day 9 chỉ xây nền spectral, chưa tính MDF/MNF?

MDF và MNF đều được tính từ phân bố công suất theo tần số. Trước khi viết hai công thức này, phải khóa các câu hỏi upstream:

```text
Trục tần số được tạo thế nào?
PSD có đơn vị gì?
Taper nào được dùng?
Có detrend không?
One-sided PSD đã nhân hệ số đúng chưa?
Dải 20–400 Hz được cắt trước hay sau ước lượng?
Tích phân PSD có khớp power miền thời gian không?
Window invalid được xử lý thế nào?
Zero-padding có được phép không?
```

Nếu gộp PSD, MDF và MNF trong một ngày, khi test sai sẽ khó biết lỗi thuộc:

```text
FFT/PSD normalization
hay
frequency-axis geometry
hay
Hann/windowing
hay
MDF/MNF formula
```

Tách Day 9 giúp isolate lỗi và tạo một contract sạch cho Day 10.

## 1.1. Điểm cần đặc biệt cảnh giác khi đọc paper

Dự án sử dụng định nghĩa chuẩn:

```text
MNF = weighted mean frequency
MDF = frequency chia tổng spectral power thành hai nửa
```

Trong một số tài liệu, phần tiêu đề hoặc ký hiệu có thể bị đảo giữa “Median Frequency” và “Mean Frequency”. Bạn phải đọc công thức, không chỉ đọc nhãn. Day 9 chỉ nhận diện vấn đề này trong reading notes; Day 10 mới triển khai công thức chuẩn.

---

# 2. Chế độ làm việc một người

Bạn đổi vai trò tuần tự, không thực hiện đồng thời nhiều vai trò:

| Thứ tự | Vai trò tạm thời | Trách nhiệm Day 9 |
|---:|---|---|
| 1 | Program Manager | Xác nhận Day 8, khóa scope, tạo branch/checkpoint |
| 2 | DSP Learner | Học DFT/FFT/PSD/Hann/Welch/Parseval |
| 3 | Signal Architect | Chốt estimator contract, unit và failure behavior |
| 4 | DSP Engineer | Viết pure spectral core |
| 5 | Software Engineer | Viết config, models, service, schemas và CLI |
| 6 | QA Engineer | Viết nghiệm biết trước, negative tests, E2E và hash tests |
| 7 | Safety Reviewer | Xác nhận không MDF/MNF/fatigue output/overclaim |
| 8 | Program Manager | Evidence, registry, notes, commit và handoff Day 10 |

## 2.1. WIP limit

```text
WIP limit = 1 module hoặc 1 nhóm test tại một thời điểm
```

Thứ tự bắt buộc:

```text
học và tính tay
→ chốt config/spec
→ pure core
→ pure core tests
→ service function một window
→ result models
→ orchestration toàn session
→ schemas
→ CLI/E2E
→ analytical evidence
→ registry/docs
```

Không viết MDF/MNF “tiện tay” trong `spectral.py`.

## 2.2. Nội dung vẫn cần external review

Dù bạn tự hoàn thành phần kỹ thuật, các nội dung sau phải ghi:

```text
EXTERNAL_REVIEW_REQUIRED
```

- dải tần phù hợp với Noraxon export thực tế;
- hardware/software filter đã được Noraxon áp dụng trước export;
- lựa chọn một hay nhiều Welch segment trên dữ liệu local;
- normalization cần dùng khi so sánh giữa buổi;
- ý nghĩa lâm sàng của spectral shift theo từng cơ/task;
- ngưỡng MDF/MNF slope hoặc fatigue onset;
- wording báo cáo cho bác sĩ/KTV.

---

# 3. Scope bắt buộc và scope bị cấm mở rộng

## 3.1. Scope bắt buộc

- Tạo `spectral_estimation_v0.1.yaml` có version.
- Input từ `windowing_v0.1`, profile `frequency_domain`, purpose `psd_mdf_mnf`.
- Pure functions cho:
  - one-sided frequency axis;
  - bin spacing;
  - Rayleigh resolution;
  - PSD integration;
  - band selection;
  - periodogram;
  - Welch PSD.
- Hann taper chỉ trong spectral layer.
- `detrend=constant` được khai báo rõ.
- `scaling=density` để PSD có unit `uV²/Hz`.
- Outer window 1000 mẫu làm một Welch segment.
- Welch internal overlap bằng 0.
- Không zero-padding ở v0.1.
- Analysis band 20–400 Hz, không silently clip nếu vượt Nyquist.
- Một spectral row cho mỗi channel-window.
- Invalid window phải xuất `not_computed` row.
- Low-power window phải xuất `not_computed` row.
- Shared frequency axis lưu một lần ở result level.
- Không lưu raw samples trong spectral JSON.
- Deterministic spectral row ID và result hash.
- Analytical verifier với tín hiệu có nghiệm biết trước.
- Golden E2E 119 rows × 381 bins.
- Upstream QC fail phải block spectral stage.
- Registry có config/code/schema hashes.
- Tất cả Markdown mới bằng tiếng Việt.

## 3.2. Không làm trong Day 9

- Không MDF/MNF.
- Không spectral slope.
- Không spectral entropy.
- Không fatigue onset.
- Không FRS.
- Không rule engine.
- Không model ML.
- Không MFCV/CV.
- Không dashboard/report.
- Không realtime stream.
- Không zero-padding để quảng bá “độ phân giải cao hơn”.
- Không chỉnh `preprocess_v0.1` hoặc `windowing_v0.1` để làm test pass.
- Không thay đổi golden signal nếu không có decision record.
- Không dùng peak frequency như fatigue label.

Mọi ý tưởng ngoài scope được đưa vào `docs/01-product/backlog/day9-backlog.md` hoặc backlog Day 10+.

---

# 4. Cây artifact cuối ngày

Theo skeleton hiện tại, note cá nhân nằm tại `docs/note/`:

```text
semg-fatigue-platform/
├── docs/
│   ├── plans/
│   │   └── DAY9_EXECUTION_PLAN.md
│   ├── 00-executive/
│   │   └── day9-decision-log-append.md
│   ├── 01-product/backlog/
│   │   └── day9-backlog.md
│   ├── 03-architecture/adr/
│   │   └── ADR-0011-hann-welch-spectral-foundation-before-mdf-mnf.md
│   ├── 05-data/
│   │   └── spectral-estimation-result-contract.md
│   ├── 06-ai-signal-processing/
│   │   ├── frequency-domain-math-primer.md
│   │   └── spectral-estimation-spec.md
│   ├── 08-validation-qa/
│   │   └── day9-spectral-estimation-test-plan.md
│   └── note/day09/
│       ├── 01-learning-objectives.md
│       ├── 02-reading-notes.md
│       ├── 03-math-notes.md
│       ├── 04-signal-processing-notes.md
│       ├── 05-clinical-notes.md
│       ├── 06-questions.md
│       ├── 07-decisions.md
│       ├── 08-daily-summary.md
│       └── 09-todo-day10.md
├── packages/
│   ├── semg-core/
│   │   ├── semg_core/spectral.py
│   │   └── tests/test_spectral.py
│   └── common-schemas/json/
│       ├── spectral-window-row.schema.json
│       ├── spectral-estimation-result.schema.json
│       └── spectral-verification.schema.json
├── services/feature-extraction-service/
│   ├── configs/spectral_estimation_v0.1.yaml
│   ├── src/
│   │   ├── spectral_config.py
│   │   ├── frequency_domain.py
│   │   ├── spectral_result_models.py
│   │   ├── spectral_estimator.py
│   │   └── spectral_extractor.py
│   └── tests/
│       ├── test_spectral_config.py
│       ├── test_frequency_domain.py
│       └── test_spectral_estimator.py
├── scripts/
│   ├── data/
│   │   ├── verify_spectral_estimation.py
│   │   └── run_spectral_estimation.py
│   └── dev/
│       ├── register_spectral_estimator_v0_1.py
│       ├── check_day9_artifacts.py
│       └── run_day9_checks.sh
├── qa-validation/
│   ├── automated-tests/
│   │   └── test_spectral_estimation_analytical.py
│   ├── requirements/
│   │   └── day9-acceptance-criteria.md
│   └── evidence/
│       ├── day9-spectral-verification.json
│       ├── day9-spectral-verification.md
│       ├── day9-spectral-estimation.json
│       ├── day9-spectral-estimation-rerun.json
│       ├── day9-spectral-estimation.csv
│       └── day9-spectral-blocked.json
├── ai-core/validation-reports/
│   └── analytical_validation_spectral_estimation_v0.1.md
├── mlops/registry/
│   └── feature_extractors.yaml
└── DAY9_STARTER_PACK_README.md
```

---

# 5. Các quyết định kỹ thuật Day 9 phải khóa trước khi code

| Quyết định | Giá trị v0.1 | Lý do |
|---|---|---|
| Input profile | `frequency_domain` | Dùng window 1000 ms đã tạo ở Day 7 |
| Outer window | 1000 ms | Cân bằng ổn định phổ và temporal resolution cho MVP-0 |
| Estimator | Welch API | Giữ đường nâng cấp sang nhiều segment |
| Segments mỗi outer window | 1 | Dễ kiểm chứng; giữ 1 Hz resolution trên fixture |
| Taper | Hann | Giảm far spectral leakage |
| Detrend | constant | Loại residual mean trong mỗi spectral window |
| Scaling | density | PSD unit rõ `uV²/Hz` |
| One-sided | true | Input là tín hiệu thực |
| Internal overlap | 0 | Tránh nhầm outer overlap với Welch overlap |
| NFFT | bằng window length | Không zero-padding trong v0.1 |
| Analysis band | 20–400 Hz | Engineering default, chưa clinical validated |
| Output axis | shared một lần | Tránh lặp 381 giá trị trong metadata từng row |
| Peak frequency | QA-only | Không thay MDF/MNF |
| Parseval warning | warning-only | Dùng review estimator, không diễn giải lâm sàng |
| Invalid window | `not_computed` | Không impute/silently drop |
| Low power | `not_computed` | Không tạo feature từ phổ gần zero |

---

# 6. Kiến thức cần học kỹ trước khi triển khai

## 6.1. Tín hiệu rời rạc và sinusoid

Một sinusoid rời rạc:

\[
x[n] = A\sin\left(2\pi f\frac{n}{F_s}+\phi\right)
\]

Trong đó:

- `A`: biên độ;
- `f`: tần số Hz;
- `Fs`: sampling rate;
- `φ`: pha.

Với `Fs=1000 Hz`, tone `80 Hz` có:

```text
80 chu kỳ mỗi giây
12,5 samples mỗi chu kỳ
```

Tuy nhiên, không bắt buộc số sample mỗi chu kỳ phải nguyên để FFT hoạt động. Vấn đề chính là tone có rơi đúng frequency bin của cửa sổ hữu hạn hay không.

## 6.2. Số phức và công thức Euler

\[
e^{j\theta}=\cos(\theta)+j\sin(\theta)
\]

DFT đo mức tín hiệu khớp với các basis phức. Bạn phải hiểu:

```text
abs(X[k])   → magnitude
angle(X[k]) → phase
abs(X[k])²  → đại lượng liên quan power
```

Không cần tự giải số phức bằng tay cho mọi window, nhưng cần hiểu vì sao FFT trả số phức.

## 6.3. DFT

\[
X[k]=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N}
\]

Tần số của bin `k`:

\[
f_k=\frac{kF_s}{N_{FFT}}
\]

Bài tập bắt buộc: tự tính DFT của vector 4 phần tử đơn giản hoặc chạy code DFT trực tiếp rồi so với FFT.

```python
import numpy as np


def dft_truc_tiep(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    index = np.arange(n)
    matrix = np.exp(-2j * np.pi * np.outer(index, index) / n)
    return matrix @ x


x = np.array([0.0, 1.0, -1.0, 0.0])
print(dft_truc_tiep(x))
print(np.fft.fft(x))
```

Kết luận cần ghi:

```text
DFT = phép biến đổi được định nghĩa bằng toán
FFT = thuật toán tính DFT nhanh
```

## 6.4. Nyquist và trục một phía

\[
f_{Nyquist}=\frac{F_s}{2}
\]

Với `Fs=1000 Hz`:

```text
Nyquist = 500 Hz
```

Với tín hiệu thực và `NFFT=1000`:

```text
one-sided bins = NFFT/2 + 1 = 501
axis = 0, 1, 2, ..., 500 Hz
```

Code:

```python
axis = np.fft.rfftfreq(1000, d=1 / 1000)
assert axis.size == 501
assert axis[0] == 0
assert axis[-1] == 500
```

## 6.5. Bin spacing và Rayleigh resolution

Khoảng cách bin:

\[
\Delta f_{bin}=\frac{F_s}{N_{FFT}}
\]

Độ phân giải Rayleigh xấp xỉ:

\[
\Delta f_{Rayleigh}\approx\frac{F_s}{N_{segment}}
\]

Nếu:

```text
Fs = 1000
Nsegment = 500
NFFT = 1000
```

thì:

```text
bin spacing = 1 Hz
Rayleigh resolution ≈ 2 Hz
```

Zero-padding có thể làm lưới tần số dày hơn nhưng không thêm quan sát thời gian, nên không tự động cải thiện khả năng phân biệt hai tone gần nhau.

Day 9 dùng:

```text
Nsegment = NFFT = 1000
bin spacing = Rayleigh resolution = 1 Hz
```

## 6.6. Spectral leakage

Một đoạn hữu hạn tương đương nhân tín hiệu dài với một cửa sổ thời gian. Nhân trong miền thời gian tạo convolution trong miền tần số, làm năng lượng lan sang các bin lân cận.

Leakage dễ thấy khi dùng tone `80,5 Hz` với cửa sổ 1 giây và bin spacing 1 Hz:

```text
80,5 Hz không nằm đúng bin 80 hoặc 81 Hz
```

## 6.7. Hann taper

\[
w[n]=0.5\left(1-\cos\frac{2\pi n}{N-1}\right)
\]

Tín hiệu spectral:

\[
x_w[n]=x[n]w[n]
\]

Hann:

- giảm sidelobe/leakage xa peak;
- làm main lobe rộng hơn;
- thay đổi amplitude trực tiếp;
- phải được estimator normalization đúng;
- không được dùng cho RMS/MAV.

Quy tắc:

```text
Windowing layer       → chỉ tạo geometry/slice
Time-domain features  → untapered signal
Spectral layer        → Hann taper
```

## 6.8. Power spectrum và PSD

Power spectrum thường bắt đầu từ:

\[
|X[k]|^2
\]

PSD mô tả power trên mỗi Hz:

```text
input unit  = uV
PSD unit    = uV²/Hz
```

Tích phân PSD:

\[
P=\int S_{xx}(f)\,df
\]

Đơn vị:

```text
uV²/Hz × Hz = uV²
```

Với trục đều:

```python
power_uV2 = float(np.sum(psd_uV2_per_hz) * df_hz)
```

## 6.9. Công suất sine có nghiệm biết trước

Với:

\[
x(t)=A\sin(2\pi ft)
\]

mean-square power:

\[
P=\frac{A^2}{2}
\]

Ví dụ `A=10 uV`:

```text
expected power = 10² / 2 = 50 uV²
```

Đây là test nền tảng của Day 9.

## 6.10. Periodogram

Periodogram dùng một segment để ước lượng PSD. Khi dùng Hann, thường gọi là modified periodogram.

Ưu điểm:

- dễ kiểm chứng;
- giữ resolution của toàn segment.

Hạn chế:

- variance cao;
- nhạy với từng window.

## 6.11. Welch

Welch thông thường:

```text
chia tín hiệu thành nhiều segment
→ taper từng segment
→ tính periodogram từng segment
→ average các periodogram
```

Điều cần phân biệt:

```text
Outer window overlap
= overlap giữa các window 1 giây của Day 7

Welch internal overlap
= overlap giữa các segment bên trong một outer window
```

Day 9 v0.1:

```text
outer window = 1000 samples
nperseg = 1000
internal overlap = 0
segment count = 1
```

Vì vậy Welch v0.1 tương đương modified periodogram. Ta vẫn dùng Welch API để giữ contract nâng cấp cho v0.2.

## 6.12. Detrend constant

`detrend=constant` trừ mean trong mỗi spectral segment trước ước lượng PSD.

Nó:

- giảm residual DC;
- không thay thế band-pass filter;
- không sửa motion artifact;
- phải được version hóa vì nó thay đổi PSD.

## 6.13. One-sided PSD

Tín hiệu thực có phổ đối xứng ở tần số âm/dương. One-sided PSD giữ từ 0 đến Nyquist và điều chỉnh power của các bin nội bộ.

Không tự nhân đôi lại PSD nếu thư viện đã dùng:

```python
return_onesided=True
```

## 6.14. Parseval và Hann-weighted power

Parseval nói năng lượng/công suất được bảo toàn giữa hai miền khi convention normalization nhất quán.

Với Hann density normalization, reference phù hợp là công suất đã chuẩn hóa theo năng lượng taper:

\[
P_w=
\frac{\sum_n(x_d[n]w[n])^2}
{\sum_n w[n]^2}
\]

trong đó `x_d` là tín hiệu sau detrend.

Day 9 tính:

\[
R_{Parseval}=\frac{P_{PSD}}{P_w}
\]

Expected gần 1.

Lưu ý:

```text
raw variance
không luôn bằng
Hann-weighted power
```

Cả hai được lưu riêng để QA, tránh diễn giải sai.

## 6.15. Quy luật scale

Nếu:

\[
y[n]=c\,x[n]
\]

thì:

\[
PSD_y(f)=c^2PSD_x(f)
\]

Nhân biên độ 2 lần phải làm PSD và integrated power tăng 4 lần. Đây là test bắt buộc cho unit/normalization.

## 6.16. Dải phân tích 20–400 Hz

Estimator tạo full one-sided PSD 0–500 Hz, sau đó mới cắt 20–400 Hz.

Không silently cắt high bound xuống Nyquist. Nếu dữ liệu có `Fs<800 Hz`, dải 20–400 không hợp lệ và phải block hoặc dùng config version khác.

## 6.17. Chỉ nhận diện công thức MDF/MNF, chưa code

Định nghĩa chuẩn để chuẩn bị Day 10:

\[
MNF=\frac{\sum_k f_kP_k}{\sum_kP_k}
\]

MDF là tần số mà cumulative power đạt 50% tổng power trong dải phân tích.

Day 9 phải giữ:

```text
mdf_mnf_computed = false
```

---

# 7. Lịch Day 9 theo từng bước

Lịch gợi ý dành cho một người mới. Có thể kéo dài thời gian học, nhưng không được bỏ test để chạy theo đồng hồ.

| Bước | Khung giờ | Nội dung | Artifact/checkpoint |
|---:|---:|---|---|
| 0 | 08:00–08:10 | Xác nhận Day 8 hoàn thành | Working tree/commit |
| 1 | 08:10–08:20 | Tạo branch và checkpoint | Branch Day 9 |
| 2 | 08:20–08:40 | Chạy regression Day 8 | Regression log |
| 3 | 08:40–09:00 | Đọc handoff và khóa scope | Scope note |
| 4 | 09:00–09:35 | Học DFT/FFT/số phức | Math notes |
| 5 | 09:35–10:00 | Học axis/Nyquist/bin/resolution | Bài tính tay |
| 6 | 10:00–10:25 | Học leakage/Hann | DSP notes |
| 7 | 10:25–10:50 | Học PSD/unit/Parseval | Power notes |
| 8 | 10:50–11:10 | Đọc ba paper và phản biện | Reading notes |
| 9 | 11:10–11:30 | Chốt spectral config | YAML contract |
| 10 | 11:30–11:50 | Viết spec + ADR trước code | Architecture docs |
| 11 | 11:50–12:10 | Thiết kế pure core API | Function contracts |
| 12 | 13:00–13:30 | Implement axis/band/power helpers | `spectral.py` phần 1 |
| 13 | 13:30–14:00 | Implement periodogram/Welch | `spectral.py` phần 2 |
| 14 | 14:00–14:25 | Viết pure core tests | Core tests PASS |
| 15 | 14:25–14:45 | Implement config validator | Config tests |
| 16 | 14:45–15:10 | Implement one-window spectral function | `frequency_domain.py` |
| 17 | 15:10–15:35 | Implement result models | Typed contract |
| 18 | 15:35–16:05 | Implement session estimator | 119-row orchestration |
| 19 | 16:05–16:25 | Viết JSON Schemas | Contract validation |
| 20 | 16:25–16:50 | Viết analytical verifier | Synthetic evidence |
| 21 | 16:50–17:15 | Viết CLI E2E | JSON/CSV output |
| 22 | 17:15–17:35 | Chạy targeted tests | Test checkpoint |
| 23 | 17:35–17:55 | Chạy analytical verification | 8 checks PASS |
| 24 | 17:55–18:15 | Chạy golden E2E lần 1 | 119 rows/381 bins |
| 25 | 18:15–18:25 | Rerun deterministic | Same hash |
| 26 | 18:25–18:40 | Chạy QC-fail blocked E2E | 0 rows |
| 27 | 19:15–19:30 | Validate schemas/privacy/safety | Safety review |
| 28 | 19:30–19:45 | Register estimator | Registry entry |
| 29 | 19:45–20:00 | Hoàn thiện docs/notes | 9 note files |
| 30 | 20:00–20:15 | Tự kiểm tra kiến thức | Self-assessment |
| 31 | 20:15–20:30 | Chạy one-command checker | All checks PASS |
| 32 | 20:30–20:40 | Review diff và commit | Git checkpoint |
| 33 | 20:40–20:45 | Viết handoff Day 10 | MDF/MNF readiness |

---

# 8. Hướng dẫn thực thi tuần tự

## Bước 0 — Xác nhận điểm bắt đầu

### Mục tiêu

Đảm bảo Day 8 đã hoàn thành và không có thay đổi chưa kiểm soát.

### Input

```text
Repository sau Day 8
Commit hoặc tag Day 8
scripts/dev/run_day8_checks.sh
```

### Thao tác

```bash
git status --short
git log -1 --oneline
```

Nếu working tree có thay đổi:

```bash
git diff
git diff --staged
```

### Output

- Biết chính xác commit bắt đầu Day 9.
- Không có file raw clinical hoặc secret trong Git.
- Không có thay đổi Day 8 chưa hiểu.

### Done criteria

```text
Day 8 commit xác định
+ trạng thái repo được ghi lại
+ không tiếp tục trên working tree mơ hồ
```

---

## Bước 1 — Tạo branch và checkpoint

```bash
git switch -c day9-spectral-estimation-v0.1

git status --porcelain=v1 > /tmp/day9-start-status.txt
git diff > /tmp/day9-start-working-tree.patch
```

### Output

```text
Branch: day9-spectral-estimation-v0.1
Snapshot trước Day 9
```

---

## Bước 2 — Chạy regression Day 8

```bash
mkdir -p qa-validation/evidence

bash scripts/dev/run_day8_checks.sh \
  2>&1 | tee qa-validation/evidence/day9-day8-regression.log
```

### Done criteria

- Exit code `0`.
- RMS/MAV vẫn 239 computed rows.
- Windowing vẫn có 119 frequency-domain windows.
- Không chỉnh Day 8 code để “chuẩn bị” cho Day 9.

### Khi fail

Dừng Day 9. Sửa upstream hoặc quay lại commit Day 8 ổn định trước.

---

## Bước 3 — Đọc handoff và khóa scope

Đọc:

```text
docs/note/day08/09-todo-day09.md
docs/06-ai-signal-processing/feature-extraction-spec.md
docs/06-ai-signal-processing/segmentation-windowing-spec.md
services/feature-extraction-service/configs/windowing_v0.1.yaml
```

Ghi vào:

```text
docs/note/day09/01-learning-objectives.md
docs/note/day09/07-decisions.md
```

Câu hỏi phải trả lời:

1. Profile nào được dùng?
2. Mỗi window có bao nhiêu mẫu?
3. Hann được áp dụng ở layer nào?
4. Day 9 có được tính MDF/MNF không?
5. Invalid window đi đâu?

---

## Bước 4 — Học DFT/FFT và chạy DFT trực tiếp

### Input

```text
frequency-domain-math-primer.md
Python + NumPy
```

### Thao tác

Chạy DFT trực tiếp và FFT trên vector nhỏ. Ghi maximum complex error.

### Output

```text
docs/note/day09/03-math-notes.md
```

### Done criteria

Bạn tự giải thích được:

```text
FFT không phải một loại phổ khác DFT.
FFT chỉ là thuật toán tính DFT hiệu quả hơn.
```

---

## Bước 5 — Tính tay geometry miền tần số

Tự tính:

```text
Fs = 1000 Hz
N = 1000
NFFT = 1000
Nyquist = 500 Hz
one-sided bins = 501
bin spacing = 1 Hz
Rayleigh resolution = 1 Hz
analysis bins 20–400 = 381
```

Thêm bài phản ví dụ:

```text
Nsegment = 500
NFFT = 1000
bin spacing = 1 Hz
Rayleigh resolution = 2 Hz
```

### Output

Bảng tính tay trong `03-math-notes.md`.

---

## Bước 6 — Học leakage và Hann

Tạo hai periodogram của tone `80,5 Hz`:

```python
from scipy.signal import periodogram

for taper in ("boxcar", "hann"):
    frequencies, spectrum = periodogram(
        signal,
        fs=1000,
        window=taper,
        detrend=False,
        return_onesided=True,
        scaling="spectrum",
    )
```

So sánh power ngoài vùng ±4 Hz quanh tone.

### Output

Ghi:

- Hann giảm far leakage thế nào;
- main lobe rộng hơn thế nào;
- vì sao không dùng Hann cho RMS/MAV.

---

## Bước 7 — Học PSD, unit và Parseval

Bài tập bắt buộc:

1. PSD bằng `2 uV²/Hz` trên dải 10 Hz có power bao nhiêu?
2. Sine amplitude 10 uV có mean-square power bao nhiêu?
3. Tín hiệu nhân 2 thì PSD thay đổi thế nào?
4. Vì sao raw variance và Hann-weighted power có thể khác?

Đáp án số:

```text
1. 2 × 10 = 20 uV²
2. 10² / 2 = 50 uV²
3. PSD/power ×4
```

---

## Bước 8 — Đọc paper và ghi phản biện

### Paper 1 — After-Fatigue

Đọc kỹ phần:

- sampling 2048 Hz;
- lọc 20–400 Hz;
- định nghĩa MDF/MNF;
- 1000 ms và 500 ms segments;
- các hình PSD onset/middle/end.

### Paper 2 — ML Springer

Đọc:

- feature domain;
- công thức power spectrum/entropy;
- công thức gắn nhãn MNF/MDF;
- hạn chế sample size và generalizability.

Ghi rõ nếu nhãn tiêu đề và công thức bị đảo.

### Paper 3 — Prolonged driving

Đọc:

- Fs=1000 Hz;
- window 250 samples, increment 125 samples;
- cách tính MNF/MDF;
- vì sao cấu hình paper không được sao chép vào protocol 60 giây của dự án.

### Output

```text
docs/note/day09/02-reading-notes.md
```

### Done criteria

Mỗi paper có:

```text
method used
what is reusable
what is dataset-specific
what requires external review
```

---

## Bước 9 — Chốt `spectral_estimation_v0.1.yaml`

### Input

- `windowing_v0.1.yaml`;
- `preprocess_v0.1.yaml`;
- protocol 60 giây;
- math notes.

### Output

```text
services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml
```

Các field bắt buộc:

```yaml
estimator:
  method: welch
  return_onesided: true
  taper: hann
  detrend: constant
  scaling: density
  average: mean
  nperseg_policy: full_outer_window
  noverlap_samples: 0
  nfft_policy: equal_outer_window_length
  zero_padding_enabled: false

analysis_band:
  low_hz: 20.0
  high_hz: 400.0
  include_endpoints: true
```

### Done criteria

- `clinical_validation_status: not_validated`.
- MDF/MNF disabled.
- `include_raw_samples: false`.
- `do_not_interpret_fatigue: true`.

---

## Bước 10 — Viết spec, contract và ADR trước code

Tạo/cập nhật:

```text
docs/06-ai-signal-processing/spectral-estimation-spec.md
docs/05-data/spectral-estimation-result-contract.md
docs/03-architecture/adr/ADR-0011-hann-welch-spectral-foundation-before-mdf-mnf.md
```

### Done criteria

Spec phải trả lời:

- input/output;
- estimator parameters;
- units;
- failure behavior;
- shared axis;
- reason codes;
- deterministic hash;
- privacy;
- clinical boundary.

---

## Bước 11 — Thiết kế pure core API

Các function tối thiểu:

```python
one_sided_frequency_axis(...)
frequency_bin_spacing_hz(...)
rayleigh_resolution_hz(...)
integrate_uniform_psd(...)
select_frequency_band(...)
estimate_periodogram_psd(...)
estimate_welch_psd(...)
```

Pure core:

- không biết session/patient;
- không đọc YAML;
- không ghi file;
- không tạo fatigue interpretation;
- chỉ nhận vector, sampling rate và tham số DSP.

---

## Bước 12 — Implement axis, band và power helpers

### Code cốt lõi

```python
def one_sided_frequency_axis(
    *, sampling_rate_hz: float, nfft_samples: int
) -> np.ndarray:
    return np.fft.rfftfreq(
        nfft_samples,
        d=1.0 / sampling_rate_hz,
    )


def integrate_uniform_psd(
    frequencies_hz: np.ndarray,
    psd_density: np.ndarray,
) -> float:
    df = float(np.median(np.diff(frequencies_hz)))
    return float(np.sum(psd_density) * df)
```

### Validation bắt buộc

- vector một chiều;
- finite;
- axis tăng nghiêm ngặt;
- axis cách đều;
- PSD không âm;
- high band không vượt Nyquist;
- band có ít nhất 2 bins.

---

## Bước 13 — Implement periodogram và Welch PSD

### Code cốt lõi

```python
from scipy.signal import welch

frequencies, psd = welch(
    samples,
    fs=sampling_rate_hz,
    window="hann",
    nperseg=len(samples),
    noverlap=0,
    nfft=len(samples),
    detrend="constant",
    return_onesided=True,
    scaling="density",
    average="mean",
)
```

### Output object phải có

```text
frequencies_hz
psd_uV2_per_hz
nperseg/noverlap/nfft
bin spacing
Rayleigh resolution
full integrated power
time-domain variance
Hann-weighted power
Parseval ratio
```

### Done criteria

- Output read-only hoặc immutable ở pure-core boundary.
- Không có MDF/MNF function trong code path Day 9.

---

## Bước 14 — Viết pure core tests

Test bắt buộc:

1. Trục 0–500 có 501 bins.
2. Rayleigh dùng segment length, không dùng NFFT.
3. Tone 80 Hz có peak gần 80 Hz.
4. Tích phân PSD khớp power.
5. Signal ×2 → power ×4.
6. PSD không âm.
7. Band 20–400 có 381 bins.
8. Vector rỗng/ngắn/NaN bị reject.
9. Welch geometry không hợp lệ bị reject.
10. Dải vượt Nyquist bị reject.
11. Rerun deterministic.

Chạy:

```bash
pytest -q packages/semg-core/tests/test_spectral.py
```

Không chuyển sang service trước khi PASS.

---

## Bước 15 — Implement config validator

File:

```text
services/feature-extraction-service/src/spectral_config.py
```

Validator phải khóa semantic, không chỉ parse YAML:

- config ID đúng;
- clinical status đúng;
- input profile đúng;
- Hann/density/one-sided đúng;
- no zero-padding;
- MDF/MNF disabled;
- safety flags true.

Chạy:

```bash
pytest -q \
  services/feature-extraction-service/tests/test_spectral_config.py
```

---

## Bước 16 — Implement spectral function cho một window

File:

```text
services/feature-extraction-service/src/frequency_domain.py
```

Flow:

```text
samples finite
→ Welch full axis
→ select 20–400 Hz
→ integrate band power
→ low-power guard
→ peak frequency QA
→ Parseval QA flag
→ SpectralWindowValues
```

Pseudo-code:

```python
estimate = estimate_welch_psd(...)
band_f, band_psd = select_frequency_band(...)
band_power = integrate_uniform_psd(band_f, band_psd)

if band_power <= minimum_power:
    raise SpectralPowerTooLow
```

Peak frequency phải có metadata:

```text
purpose = qa_only_not_fatigue_feature
```

---

## Bước 17 — Implement result models

File:

```text
services/feature-extraction-service/src/spectral_result_models.py
```

Model cấp row:

- identity/context;
- window geometry;
- status;
- spectral values hoặc null;
- reason codes;
- provenance.

Model cấp result:

- status;
- downstream allowed;
- config;
- shared frequency axis;
- estimator metadata;
- summary;
- all rows;
- result hash;
- limitations.

### Invariant

```text
computed row      → spectral != null, reason_codes empty
not_computed row  → spectral = null, reason_codes non-empty
blocked result    → rows empty, frequency_axis null
```

---

## Bước 18 — Implement estimator toàn session

File:

```text
services/feature-extraction-service/src/spectral_estimator.py
```

Flow:

```text
WindowingResult blocked?
→ block spectral

Wrong windowing/preprocess/profile/purpose?
→ block spectral

Loop channel × frequency windows
→ invalid window: not_computed
→ valid window: compute PSD
→ low power: not_computed
→ axis mismatch: not_computed/review

No computed rows?
→ block downstream

Otherwise
→ shared axis
→ result hash
→ completed/completed_with_exclusions
```

### Không được

- silently skip invalid window;
- replace invalid samples bằng zero;
- lưu raw samples trong JSON;
- tính fatigue status.

---

## Bước 19 — Viết JSON Schemas

Tạo:

```text
spectral-window-row.schema.json
spectral-estimation-result.schema.json
spectral-verification.schema.json
```

Dùng JSON Schema Draft 2020-12.

Schema phải kiểm tra:

- enum status;
- unit chính xác;
- SHA-256 pattern;
- computed/not-computed structure;
- frequency-axis metadata;
- PSD array type;
- `mdf_mnf_computed=false`.

---

## Bước 20 — Viết analytical verifier

File:

```text
scripts/data/verify_spectral_estimation.py
```

Tối thiểu 8 checks:

1. DFT trực tiếp = FFT.
2. Frequency-axis geometry.
3. Single-tone peak + power.
4. Multi-tone dominant frequency + total power.
5. Welch full-window = modified periodogram.
6. Hann giảm far leakage.
7. PSD integral = Hann-weighted power.
8. Amplitude ×2 → PSD/power ×4.

Output:

```text
qa-validation/evidence/day9-spectral-verification.json
qa-validation/evidence/day9-spectral-verification.md
ai-core/validation-reports/analytical_validation_spectral_estimation_v0.1.md
```

---

## Bước 21 — Viết CLI E2E

File:

```text
scripts/data/run_spectral_estimation.py
```

CLI phải chạy:

```text
manifest
→ ingestion
→ QC
→ preprocessing
→ windowing
→ spectral estimator
→ JSON/CSV
```

Ví dụ:

```bash
python scripts/data/run_spectral_estimation.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day9-spectral-estimation.json \
  --csv-out qa-validation/evidence/day9-spectral-estimation.csv
```

---

## Bước 22 — Chạy targeted tests

```bash
pytest -q \
  packages/semg-core/tests/test_spectral.py \
  services/feature-extraction-service/tests/test_spectral_config.py \
  services/feature-extraction-service/tests/test_frequency_domain.py \
  services/feature-extraction-service/tests/test_spectral_estimator.py \
  qa-validation/automated-tests/test_spectral_estimation_analytical.py
```

### Done criteria

Tất cả PASS; không xfail safety-critical test.

---

## Bước 23 — Chạy analytical verification

```bash
python scripts/data/verify_spectral_estimation.py \
  --json-output qa-validation/evidence/day9-spectral-verification.json \
  --evidence-md qa-validation/evidence/day9-spectral-verification.md \
  --validation-md \
    ai-core/validation-reports/analytical_validation_spectral_estimation_v0.1.md
```

Expected:

```text
verification_status = passed
check count >= 8
clinical_validation_status = not_validated
```

---

## Bước 24 — Chạy golden E2E lần 1

```bash
python scripts/data/run_spectral_estimation.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day9-spectral-estimation.json \
  --csv-out qa-validation/evidence/day9-spectral-estimation.csv \
  --expect-status completed \
  --expect-total-row-count 119 \
  --expect-computed-row-count 119 \
  --expect-not-computed-row-count 0 \
  --expect-frequency-bin-count 381
```

Kiểm tra thủ công:

- first row start/end đúng;
- PSD length 381;
- unit đúng;
- band power ≤ full power;
- peak nằm trong 20–400 Hz;
- no raw samples;
- no MDF/MNF.

---

## Bước 25 — Chạy deterministic rerun

```bash
python scripts/data/run_spectral_estimation.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day9-spectral-estimation-rerun.json \
  --quiet
```

So hash:

```python
assert first["result_hash_sha256"] == second["result_hash_sha256"]
```

Cùng environment phải có exact hash. Khác environment có thể cần numerical tolerance; không giả định bitwise identical giữa mọi SciPy/platform.

---

## Bước 26 — Chạy upstream-blocked E2E

Sinh fixture flatline nếu cần:

```bash
python qa-validation/test-data/synthetic/generate_qc_fixtures.py \
  --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --output-dir qa-validation/test-data/synthetic \
  --overwrite
```

Chạy:

```bash
python scripts/data/run_spectral_estimation.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json \
  --json-out qa-validation/evidence/day9-spectral-blocked.json \
  --expect-status blocked \
  --expect-total-row-count 0 \
  --expect-computed-row-count 0 \
  --expect-not-computed-row-count 0 \
  --expect-reason SPECTRAL_ESTIMATION_BLOCKED_BY_WINDOWING
```

Expected:

```text
QC fail
→ preprocessing blocked
→ windowing blocked
→ spectral blocked
→ rows = []
```

---

## Bước 27 — Validate schemas, privacy và safety

Kiểm tra:

```text
result schema PASS
row schema PASS
verification schema PASS
PSD arrays khớp shared axis
không raw samples
không patient identifiers
không fatigue status
không FRS
mdf_mnf_computed=false
```

Lệnh chính nằm trong `scripts/dev/run_day9_checks.sh`.

---

## Bước 28 — Đăng ký estimator

```bash
python scripts/dev/register_spectral_estimator_v0_1.py
```

Registry entry phải có:

```yaml
config_id: spectral_estimation_v0.1
implemented_features:
  - welch_psd
clinical_validation_status: not_validated
```

Không ghi MDF/MNF vào `implemented_features`.

---

## Bước 29 — Hoàn thiện documentation và daily notes

Hoàn thiện 9 file:

```text
docs/note/day09/01-learning-objectives.md
docs/note/day09/02-reading-notes.md
docs/note/day09/03-math-notes.md
docs/note/day09/04-signal-processing-notes.md
docs/note/day09/05-clinical-notes.md
docs/note/day09/06-questions.md
docs/note/day09/07-decisions.md
docs/note/day09/08-daily-summary.md
docs/note/day09/09-todo-day10.md
```

Daily summary phải ghi:

- số tests pass;
- 8 analytical checks;
- golden row/bin count;
- result hash trên máy bạn;
- limitations;
- câu hỏi cần Motion Lab/clinical review.

---

## Bước 30 — Tự kiểm tra kiến thức

Không nhìn tài liệu, trả lời:

1. DFT và FFT khác nhau thế nào?
2. Với `Fs=2000`, `NFFT=1000`, bin spacing là bao nhiêu?
3. Với `Fs=1000`, `N=1000`, có bao nhiêu one-sided bins?
4. Vì sao zero-padding không tăng resolution vật lý?
5. PSD có đơn vị gì nếu input là uV?
6. Sine amplitude 20 uV có mean-square power bao nhiêu?
7. Hann giảm gì và đánh đổi gì?
8. Outer overlap khác Welch internal overlap thế nào?
9. Vì sao Parseval reference dùng Hann-weighted power?
10. Vì sao peak frequency không được dùng như fatigue label?
11. MNF là weighted mean hay half-power frequency?
12. MDF là weighted mean hay half-power frequency?

Đáp án số:

```text
Câu 2: 2000 / 1000 = 2 Hz
Câu 3: 1000/2 + 1 = 501 bins
Câu 6: 20²/2 = 200 uV²
Câu 11: weighted mean
Câu 12: half-power frequency
```

Nên đúng ít nhất 10/12 trước Day 10.

---

## Bước 31 — Chạy one-command checker

Cài dependency nếu thiếu:

```bash
python -m pip install \
  "numpy>=1.26,<3" \
  "scipy>=1.11,<2" \
  pyyaml \
  jsonschema \
  pytest
```

Chạy nhanh:

```bash
bash scripts/dev/run_day9_checks.sh
```

Chạy kèm toàn bộ Day 8 regression:

```bash
DAY9_FULL_REGRESSION=1 \
bash scripts/dev/run_day9_checks.sh
```

### Checker thực hiện

```text
1. Optional Day 8 regression
2. Core/config/service/analytical tests
3. DFT/FFT/PSD/Hann/Parseval/scale verification
4. Golden spectral E2E
5. Deterministic rerun
6. Upstream-blocked E2E
7. JSON Schema/shared-axis/hash checks
8. Spectral invariants/privacy checks
9. Registry update
10. Artifact/safety checker
11. Done
```

---

## Bước 32 — Review diff và commit

```bash
git status --short
git diff --check
git diff --stat
```

Không commit raw clinical data hoặc binary artifact ngoài policy:

```bash
git status --short \
  | grep -E '\.(mat|c3d|edf|bdf|npz)$' \
  || true
```

Stage:

```bash
git add \
  docs \
  packages/semg-core \
  packages/common-schemas \
  services/feature-extraction-service \
  scripts \
  qa-validation \
  ai-core/validation-reports \
  mlops/registry
```

Review:

```bash
git diff --staged --check
git diff --staged --stat
```

Commit:

```bash
git commit -m \
  "day9: implement deterministic Welch PSD spectral foundation v0.1"
```

Tag tùy chọn:

```bash
git tag day9-spectral-estimation-v0.1
```

---

## Bước 33 — Handoff Day 10

Day 10 sẽ dùng:

```text
SpectralEstimationResult
+ shared frequency axis
+ analysis-band PSD rows
+ power guard
+ valid/not-computed status
```

để triển khai:

```text
MDF v0.1
MNF v0.1
```

Day 10 phải có:

- PSD discrete tính tay;
- MNF weighted-mean tests;
- MDF cumulative-half-power tests;
- interpolation policy cho MDF;
- zero/low-power behavior;
- unit = Hz;
- schema/provenance;
- không slope/fatigue rule/FRS/ML.

---

# 9. Ma trận kiểm thử bắt buộc

| ID | Tình huống | Expected |
|---|---|---|
| D9-T01 | DFT trực tiếp vs FFT | Max error ≤ tolerance |
| D9-T02 | Fs=1000, NFFT=1000 | 501 one-sided bins |
| D9-T03 | Tone 80 Hz | Peak gần 80 Hz |
| D9-T04 | Sine A=10 uV | Power gần 50 uV² |
| D9-T05 | Multi-tone | Dominant peak/power đúng |
| D9-T06 | Welch one segment vs periodogram | PSD arrays tương đương |
| D9-T07 | Off-bin 80,5 Hz | Hann giảm far leakage |
| D9-T08 | Deterministic noise | Parseval ratio trong range |
| D9-T09 | Signal ×2 | PSD/power ×4 |
| D9-T10 | Analysis band 20–400 | 381 bins |
| D9-T11 | Zero/near-zero power | `not_computed` |
| D9-T12 | Invalid window | `not_computed`, không impute |
| D9-T13 | QC fail | result `blocked`, 0 rows |
| D9-T14 | Golden session | 119 computed rows |
| D9-T15 | Rerun | same result hash |
| D9-T16 | Schema | all schemas PASS |
| D9-T17 | Privacy | no raw samples/PHI |
| D9-T18 | Safety | no MDF/MNF/fatigue/FRS |

---

# 10. Reason codes chính

| Reason code | Nghĩa | Hành vi |
|---|---|---|
| `SPECTRAL_ESTIMATION_BLOCKED_BY_WINDOWING` | Upstream không tạo window plan hợp lệ | Block result |
| `SPECTRAL_WINDOWING_CONFIG_MISMATCH` | Sai windowing version | Block result |
| `SPECTRAL_PREPROCESS_CONFIG_MISMATCH` | Sai preprocessing version | Block result |
| `SPECTRAL_PROFILE_NOT_FOUND` | Thiếu frequency profile | Block result |
| `SPECTRAL_PROFILE_PURPOSE_MISMATCH` | Profile purpose không đúng | Block result |
| `SPECTRAL_WINDOW_INVALID` | Window upstream invalid | Row `not_computed` |
| `SPECTRAL_POWER_TOO_LOW` | Band power quá thấp | Row `not_computed` |
| `SPECTRAL_COMPUTATION_FAILED` | Lỗi số học/contract | Row `not_computed` |
| `SPECTRAL_FREQUENCY_AXIS_MISMATCH` | Grid giữa rows không nhất quán | Exclude/review |
| `SPECTRAL_WINDOWS_EXCLUDED` | Có row không tính được | Result warning |
| `SPECTRAL_QA_WARNINGS_PRESENT` | Có Parseval hoặc QA flags | Result warning |
| `SPECTRAL_NO_COMPUTED_ROWS` | Không còn PSD row | Block downstream |

---

# 11. Review an toàn cuối ngày

Bạn phải xác nhận từng câu:

- [ ] QC fail không thể đi đến PSD.
- [ ] Invalid window không bị thay bằng zero.
- [ ] Low-power window không sinh MDF/MNF giả.
- [ ] Hann chỉ dùng trong spectral stage.
- [ ] PSD output không chứa raw samples.
- [ ] Peak frequency được gắn `qa_only_not_fatigue_feature`.
- [ ] `mdf_mnf_computed=false`.
- [ ] Không có fatigue label hoặc FRS.
- [ ] `clinical_validation_status=not_validated`.
- [ ] Synthetic verification được mô tả là software/DSP evidence.
- [ ] Dải 20–400 Hz được ghi là engineering default.
- [ ] External-review questions đã được lưu.

---

# 12. Definition of Done Day 9

## Code

- [ ] Có pure `semg_core/spectral.py`.
- [ ] Có one-sided axis/band/power helpers.
- [ ] Có periodogram và Welch wrappers.
- [ ] Có config validator.
- [ ] Có one-window spectral function.
- [ ] Có result models.
- [ ] Có session-level estimator.
- [ ] Invalid/low-power windows không bị impute.
- [ ] Shared axis nhất quán.

## Golden E2E

- [ ] 119 total rows.
- [ ] 119 computed rows.
- [ ] 0 not-computed rows.
- [ ] 381 frequency bins.
- [ ] Axis 20–400 Hz.
- [ ] Bin spacing 1 Hz.
- [ ] Deterministic result hash.

## Analytical verification

- [ ] DFT=FFT.
- [ ] Geometry đúng.
- [ ] Single-tone peak/power đúng.
- [ ] Multi-tone power đúng.
- [ ] Welch=periodogram trong v0.1.
- [ ] Hann leakage test PASS.
- [ ] Parseval/Hann-weighted power PASS.
- [ ] Amplitude scaling ×2 → power ×4.

## Contract

- [ ] 3 JSON schemas PASS.
- [ ] PSD unit `uV²/Hz`.
- [ ] Integrated power unit `uV²`.
- [ ] No raw samples.
- [ ] No MDF/MNF.
- [ ] No fatigue/FRS/ML output.

## Governance

- [ ] Registry entry có config/code/schema hashes.
- [ ] `not_validated` giữ nguyên.
- [ ] Tất cả Markdown mới bằng tiếng Việt.
- [ ] ADR/decision log/backlog được cập nhật.
- [ ] 9 daily-note files hoàn chỉnh.
- [ ] Day 10 handoff rõ.

---

# 13. Các lỗi người mới thường gặp

## Lỗi 1 — Gọi FFT rồi bình phương, nhưng không ghi normalization

Hậu quả: power phụ thuộc `N`, không có unit rõ, không so được giữa config.

## Lỗi 2 — Nhầm FFT với PSD

FFT trả hệ số phức; PSD là estimator có normalization và unit power/Hz.

## Lỗi 3 — Tự nhân đôi one-sided PSD lần nữa

Nếu SciPy đã `return_onesided=True`, nhân đôi thủ công làm power sai.

## Lỗi 4 — Dùng zero-padding rồi nói “resolution tăng”

Zero-padding chỉ làm lưới tần số dày hơn; resolution vật lý vẫn do segment duration quyết định.

## Lỗi 5 — Dùng Hann cho RMS/MAV

Taper làm thay đổi amplitude feature. Hann chỉ dùng cho spectral path.

## Lỗi 6 — Nhầm outer overlap với Welch overlap

Day 7 đã tạo outer windows overlap 50%; Day 9 v0.1 không chia tiếp thành multiple Welch segments.

## Lỗi 7 — So PSD integral với raw variance mà bỏ qua taper

Với density normalization và Hann, reference QA phù hợp là taper-energy-normalized power.

## Lỗi 8 — Dùng peak frequency thay MDF/MNF

Peak dễ dao động và không có cùng định nghĩa với weighted mean hoặc half-power frequency.

## Lỗi 9 — Silently clip 400 Hz về Nyquist

Điều này làm hai session dùng dải khác nhau mà metadata không rõ. Phải block/reconfigure.

## Lỗi 10 — Thấy PSD shift rồi kết luận mỏi

PSD còn phụ thuộc force, electrode placement, crosstalk, filter, protocol và nhiều yếu tố khác.

---

# 14. Tài liệu cần đọc trong Day 9

## Bắt buộc

1. `docs/06-ai-signal-processing/frequency-domain-math-primer.md`.
2. `docs/06-ai-signal-processing/spectral-estimation-spec.md`.
3. `docs/05-data/spectral-estimation-result-contract.md`.
4. `packages/semg-core/semg_core/spectral.py`.
5. `scripts/data/verify_spectral_estimation.py`.

## Paper tham chiếu

1. *After-Fatigue Condition: A Novel Analysis Based on Surface EMG Signals* — phần acquisition/filter, MDF/MNF formulas, PSD plots và time segmentation.
2. *Detection of Muscles Fatigue Through Surface EMG Signals Utilizing Machine Learning Algorithm* — feature-domain definitions và limitations.
3. *Classification of Muscle Fatigue during Prolonged Driving* — sliding-window MNF/MDF workflow và sự phụ thuộc protocol/window size.

## Nguyên tắc đọc

Không ghi “paper dùng như vậy nên dự án phải dùng như vậy”. Ghi theo ba cột:

```text
Reference fact
Project decision
Validation still required
```

---

# 15. Kết luận Day 9

Day 9 thành công khi bạn có thể giải thích toàn bộ đường đi:

```text
1000 samples uV
→ detrend constant
→ Hann taper
→ one-sided Welch density
→ 0–500 Hz axis
→ select 20–400 Hz
→ 381 PSD values uV²/Hz
→ integrate power uV²
→ Parseval QA
→ result with provenance
```

và đồng thời nói rõ:

```text
PSD artifact hợp lệ
≠ fatigue conclusion
≠ clinical validation
```

Day 10 chỉ được bắt đầu khi checker Day 9 PASS và bạn phân biệt đúng:

```text
MNF = weighted mean frequency
MDF = half-power/median frequency
```
