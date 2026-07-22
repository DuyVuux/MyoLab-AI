# ADR-0013 — Trend mô tả, chưa suy diễn thống kê

Do overlapping windows không độc lập, Day 11 dùng OLS slope/R²/RMSE như descriptive metrics và không phát p-value/CI. Trend dùng `center_time_s`, không dùng window index.
