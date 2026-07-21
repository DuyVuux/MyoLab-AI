# Đặc tả Spectral Estimation v0.1

## 1. Mục đích

Chuyển mỗi cửa sổ hợp lệ của profile `frequency_domain` thành PSD một phía có đơn vị `uV^2/Hz`, phục vụ MDF/MNF ở Day 10. Module này không đưa kết luận mỏi cơ.

## 2. Input contract

```text
WindowingRunResult.downstream_allowed = true
windowing_config_id = windowing_v0.1
preprocess_config_id = preprocess_v0.1
profile_id = frequency_domain
profile purpose = psd_mdf_mnf
window status = valid
sample unit = uV
samples finite, unrectified, chưa taper upstream
```

## 3. Estimator v0.1

```yaml
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
analysis_band_hz: [20, 400]
```

Với fixture `Fs=1000 Hz`, outer window `N=1000`:

```text
Nyquist = 500 Hz
frequency bin spacing = Fs/N = 1 Hz
one-sided full bins = N/2 + 1 = 501
analysis band 20...400 Hz inclusive = 381 bins
```

## 4. Trình tự tính

```text
valid outer window
→ detrend constant trong scipy.signal.welch
→ Hann taper
→ one-sided PSD density
→ chọn bins 20–400 Hz
→ tích phân band power
→ tính full power và Parseval ratio cho QA
→ peak frequency cho QA
→ SpectralWindowRow
```

## 5. Đơn vị

```text
Input: uV
PSD density: uV^2/Hz
Tích phân PSD theo Hz: uV^2
Peak frequency: Hz
Parseval ratio: không đơn vị
```

## 6. Quy tắc validity

| Điều kiện | Hành vi |
|---|---|
| Window invalid từ upstream | `not_computed`, giữ reason code |
| NaN/Inf | `not_computed` |
| Band power quá thấp | `not_computed`, `SPECTRAL_POWER_TOO_LOW` |
| Parseval ratio ngoài dải cảnh báo | Vẫn computed; thêm QA flag |
| Không còn computed row | Toàn result `blocked` |
| Frequency axis khác giữa các row | Row lỗi; ghi reason code |

## 7. Output contract

Result gồm:

- shared frequency axis;
- estimator metadata;
- một row cho mỗi channel-window;
- PSD trong analysis band;
- band/full power;
- time-domain variance;
- Parseval ratio;
- peak frequency với nhãn `qa_only_not_fatigue_feature`;
- provenance và hash;
- limitations.

Không chứa raw samples, PHI, MDF, MNF, slope, fatigue status hoặc FRS.

## 8. Giới hạn

Welch v0.1 chỉ dùng một segment, nên chưa có averaging nhiều segment. Đây là quyết định MVP-0 để kiểm chứng nền tảng và giữ độ phân giải 1 Hz trên fixture. Phiên bản nhiều segment phải là config/version mới và được đánh giá về bias–variance trên dữ liệu thật.
