# Day 02 — Learning Objectives

## Mục tiêu chính
- Hiểu vì sao **protocol, input contract và quality gate** phải được chốt trước feature extraction.
- Phân biệt:
  - file đọc được;
  - tín hiệu hợp lệ;
  - dữ liệu đủ điều kiện phân tích.
- Hiểu metadata tối thiểu: sampling rate, unit, channel, muscle, side, protocol, duration.
- Hiểu vai trò của sampling rate, Nyquist, timestamp và windowing.
- Hiểu khi nào MFCV/CV được phép tính và khi nào phải trả `not_eligible`.
- Biết cách biểu diễn QC bằng `pass | warning | fail` và reason code.

## Kết quả cần đạt
- Đọc được protocol YAML và JSON Schema.
- Giải thích được input CSV + sidecar manifest.
- Tự kiểm tra được sampling rate từ timestamp.
- Giải thích được vì sao QC fail phải block analysis.
- Không nhầm `not_eligible_for_mfcv` với `signal_invalid`.