# Bằng chứng kiểm chứng RMS/MAV — Day 8

**Trạng thái:** `passed`

| Case | RMS quan sát | RMS kỳ vọng | MAV quan sát | MAV kỳ vọng | Kết quả |
|---|---:|---:|---:|---:|---|
| hand_vector | 2.2360679775 | 2.2360679775 | 2 | 2 | PASS |
| constant_absolute_magnitude | 5 | 5 | 5 | 5 | PASS |
| integer_cycle_sine_80_hz | 70.7106781187 | 70.7106781187 | 63.5781793755 | 63.6619772368 | PASS |

## Thuộc tính

- `absolute_scaling_property`: PASS
- `rms_greater_or_equal_mav`: PASS
- `large_value_numerical_stability`: PASS

## Giới hạn

- Kiểm chứng dùng vector toán học và synthetic signals, không dùng dữ liệu bệnh nhân.
- Pass không có nghĩa RMS/MAV đã được xác nhận là biomarker lâm sàng độc lập.
- Không kiểm chứng MDF/MNF, slope, FRS hoặc mô hình ML trong Day 8.
