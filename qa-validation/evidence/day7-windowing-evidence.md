# Bằng chứng kiểm chứng segmentation và windowing v0.1

- Trạng thái: **PASS**
- Config: `windowing_v0.1`
- Sampling rate: `1000 Hz`
- Active phase: `60000` mẫu, tương ứng `60 s`
- Mẫu invalid dùng để kiểm tra half-open overlap: `5750`

## Hai profile được khóa theo protocol

| Profile | Mục đích | L | H | Overlap | Số window | Invalid windows trong case kiểm tra |
|---|---|---:|---:|---:|---:|---|
| `time_domain` | `rms_mav` | 500 | 250 | 0.50 | 239 | `[2, 3]` |
| `frequency_domain` | `psd_mdf_mnf` | 1000 | 500 | 0.50 | 119 | `[0, 1]` |

## Kiểm tra tính tay

| Kiểm tra | Kết quả |
|---|---|
| `phase_has_60000_samples` | PASS |
| `time_window_size_is_500` | PASS |
| `time_hop_is_250` | PASS |
| `time_window_count_is_239` | PASS |
| `time_first_window_is_5000_5500` | PASS |
| `time_last_window_ends_at_phase_end` | PASS |
| `time_masked_sample_affects_windows_2_3` | PASS |
| `frequency_window_size_is_1000` | PASS |
| `frequency_hop_is_500` | PASS |
| `frequency_window_count_is_119` | PASS |
| `frequency_first_window_is_5000_6000` | PASS |
| `frequency_last_window_ends_at_phase_end` | PASS |
| `frequency_masked_sample_affects_windows_0_1` | PASS |
| `no_partial_window_in_both_profiles` | PASS |

## Giới hạn

- Cửa sổ miền thời gian 500 ms, miền tần số 1000 ms và overlap 50% là mặc định kỹ thuật MVP-0 lấy từ protocol v0.1; chưa phải cấu hình tối ưu cho mọi cơ, task hoặc thiết bị.
- Quasi-stationarity trong mỗi cửa sổ là giả định phân tích, không phải sự thật được bảo đảm.
- Hann taper chưa được áp dụng ở tầng windowing; tầng MDF/MNF/Welch sẽ áp dụng sau.
- Cửa sổ invalid không được nội suy hoặc sửa im lặng trong v0.1.
- So sánh longitudinal chỉ hợp lệ khi protocol, preprocessing, windowing và feature versions tương thích.
