# Báo cáo kiểm chứng phân tích — Trend Features v0.1

## 1. Phạm vi

Báo cáo kiểm chứng việc fit xu hướng mô tả cho RMS, MAV, MDF và MNF theo `center_time_s`. Module không thực hiện kiểm định suy luận, không tạo p-value, confidence interval, fatigue status hoặc score.

## 2. Kết quả

- Chuỗi tuyến tính có nghiệm biết trước: slope/intercept/R²/RMSE đạt.
- Dịch gốc thời gian không làm đổi slope.
- Chuỗi hằng, thời gian không đều và input không hợp lệ được xử lý theo contract.
- Golden pipeline tạo đủ bốn trend cho một channel.
- RMS/MAV dùng native time-domain grid; MDF/MNF dùng native frequency-domain grid; không ghép bằng `window_index`.
- Upstream bị chặn: trend stage bị chặn.
- JSON Schema, provenance và deterministic hash: đạt.

## 3. Giới hạn

- Các cửa sổ overlap không độc lập; R² chỉ là chỉ số mô tả.
- Không có p-value hoặc tuyên bố ý nghĩa thống kê.
- Synthetic trend không phải bằng chứng lâm sàng.
- `clinical_validation_status` vẫn là `not_validated`.

## 4. Kết luận

`trend_features_v0.1` đạt kiểm chứng phân tích cho MVP-0 và có thể chuyển sang tầng structured evidence với các guardrail đã định nghĩa.
