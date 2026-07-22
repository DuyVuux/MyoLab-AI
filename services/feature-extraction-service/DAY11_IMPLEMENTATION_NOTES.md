# Ghi chú triển khai Day 11 — Trend Features v0.1

- RMS/MAV và MDF/MNF được fit riêng trên native time grids.
- Biến độc lập là `center_time_s`, không phải `window_index`.
- OLS, R², RMSE, early/late median là mô tả; không có p-value hoặc ý nghĩa thống kê.
- Overlapping windows không được coi là quan sát độc lập.
- Output chưa phải fatigue evidence hoặc clinical inference.
