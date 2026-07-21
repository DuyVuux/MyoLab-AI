# Kế hoạch kiểm thử Day 5 — Preprocessing v0.1

## Mục tiêu

Chứng minh implementation phù hợp specification trên synthetic fixtures, không chứng minh clinical validity.

## Test matrix

| ID | Trường hợp | Kỳ vọng |
|---|---|---|
| D5-T01 | DC offset + 80 Hz | Mean sau centering gần 0 |
| D5-T02 | High cutoff vượt Nyquist margin | Reject |
| D5-T03 | 5 Hz | Bị suy giảm mạnh |
| D5-T04 | 80 Hz | Được giữ tương đối |
| D5-T05 | 450 Hz | Bị suy giảm mạnh |
| D5-T06 | Cross-correlation 80 Hz | Lag gần 0 với zero-phase |
| D5-T07 | 50 Hz + QC powerline warning | Notch được áp dụng |
| D5-T08 | Golden QC pass | Completed; notch skipped |
| D5-T09 | QC fail flatline | Block trước filter |
| D5-T10 | NaN/Inf | Không nội suy; block/reject |
| D5-T11 | Chạy lại cùng input/config | Output hash giống nhau |
| D5-T12 | JSON output | Khớp schema v0.1 |

## Acceptance kỹ thuật

- 5 Hz dưới -20 dB theo đáp ứng zero-phase lý thuyết.
- 80 Hz trên -1 dB.
- 450 Hz dưới -20 dB.
- Notch 50 Hz dưới -20 dB khi kích hoạt.
- Không thay đổi sample count/time axis.
- QC fail không được gọi filter.
- Không có NaN/Inf trong output completed.

Các ngưỡng trên là test kỹ thuật cho config v0.1, không phải ngưỡng clinical performance.
