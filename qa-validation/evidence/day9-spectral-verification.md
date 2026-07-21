# Bằng chứng kiểm chứng spectral estimation v0.1

- Trạng thái: **passed**
- Loại bằng chứng: kiểm chứng toán học/DSP trên tín hiệu synthetic xác định
- Xác nhận lâm sàng: **chưa có**

## Kết quả

| Kiểm tra | Trạng thái | Ý nghĩa |
|---|---|---|
| `dft_fft_equivalence` | passed | FFT phải cho cùng kết quả số với DFT trực tiếp trong sai số dấu phẩy động. |
| `frequency_axis_geometry` | passed | Fs=1000 Hz, N=1000 cho trục một phía 0--500 Hz và khoảng cách bin 1 Hz. |
| `single_tone_peak_and_power` | passed | Sine biên độ 10 uV phải có công suất trung bình 50 uV^2 và peak tại 80 Hz. |
| `multitone_dominant_frequency_and_power` | passed | Thành phần 120 Hz có biên độ lớn nhất và tổng PSD phải khớp tổng công suất các sine trực giao. |
| `welch_full_window_periodogram_equivalence` | passed | Với một segment bằng toàn outer window và overlap 0, Welch v0.1 tương đương modified periodogram. |
| `hann_reduces_far_spectral_leakage` | passed | Hann giảm sidelobe/leakage xa peak cho tone không nằm đúng frequency bin, đổi lại main lobe rộng hơn. |
| `psd_integral_window_weighted_power_consistency` | passed | Tích phân PSD density phải khớp công suất miền thời gian đã chuẩn hóa theo năng lượng Hann; variance không trọng số được giữ riêng để QA. |
| `amplitude_scaling_squares_psd_and_power` | passed | Nhân tín hiệu với 2 phải làm PSD và công suất tích phân tăng 4 lần; đây là kiểm tra đơn vị và chuẩn hóa bắt buộc. |

## Chỉ số chi tiết

### `dft_fft_equivalence`

```json
{
  "sample_count": 8,
  "max_absolute_complex_error": 1.0129226104955297e-14,
  "threshold": 1e-10
}
```

### `frequency_axis_geometry`

```json
{
  "sampling_rate_hz": 1000.0,
  "sample_count": 1000,
  "one_sided_bin_count": 501,
  "nyquist_hz": 500.0,
  "bin_spacing_hz": 1.0,
  "rayleigh_resolution_hz": 1.0,
  "analysis_band_bin_count": 381
}
```

### `single_tone_peak_and_power`

```json
{
  "expected_peak_hz": 80.0,
  "observed_peak_hz": 80.0,
  "expected_variance_uV2": 50.0,
  "integrated_psd_power_uV2": 49.9999999999999,
  "relative_power_error": 1.9895196601282807e-15,
  "parseval_ratio": 0.999999999999998
}
```

### `multitone_dominant_frequency_and_power`

```json
{
  "expected_dominant_frequency_hz": 120.0,
  "observed_dominant_frequency_hz": 120.0,
  "expected_total_power_uV2": 42.0,
  "integrated_psd_power_uV2": 41.99999999999977,
  "relative_power_error": 5.4136589391245725e-15
}
```

### `welch_full_window_periodogram_equivalence`

```json
{
  "max_absolute_psd_difference": 0.0,
  "threshold": 1e-10,
  "nperseg_samples": 1000,
  "noverlap_samples": 0
}
```

### `hann_reduces_far_spectral_leakage`

```json
{
  "off_bin_frequency_hz": 80.5,
  "boxcar_far_leakage_ratio": 0.05031330756719596,
  "hann_far_leakage_ratio": 2.6716386387723605e-05,
  "improvement_factor": 1883.2377566718876,
  "pass_rule": "hann_ratio < 0.1 * boxcar_ratio"
}
```

### `psd_integral_window_weighted_power_consistency`

```json
{
  "time_domain_variance_uV2": 25.823452231019196,
  "window_weighted_power_uV2": 26.37407469718909,
  "integrated_psd_power_uV2": 26.37407469718905,
  "parseval_ratio": 0.9999999999999986,
  "accepted_range": [
    0.95,
    1.05
  ]
}
```

### `amplitude_scaling_squares_psd_and_power`

```json
{
  "amplitude_scale_factor": 2.0,
  "expected_power_scale_factor": 4.0,
  "observed_power_scale_factor": 4.0,
  "maximum_psd_scale_absolute_error": 0.0
}
```

## Giới hạn

- Tín hiệu kiểm thử là synthetic và có cấu trúc biết trước.
- Kiểm chứng peak/power không chứng minh MDF/MNF hay fatigue interpretation đúng trên dữ liệu thật.
- Welch v0.1 chỉ có một segment; chưa đánh giá trade-off nhiều segment trên dữ liệu Motion Lab.
- Dải 20-400 Hz và Hann cần được đánh giá lại sau audit Noraxon và local validation.
