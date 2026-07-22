# Đặc tả Trend Features v0.1 — Day 11

## Pipeline

```text
RMS/MAV rows (500 ms)
           +
MDF/MNF rows (1000 ms)
           ↓
fit riêng từng feature theo center_time_s
           ↓
OLS slope + R² + RMSE + early/late median
```

Không nội suy time-domain rows sang frequency-domain rows và không merge từng window vì geometry khác nhau.

## Required features

- RMS, MAV: unit `uV`;
- MDF, MNF: unit `Hz`.

Một channel chỉ complete khi cả bốn trend tính được. Kết quả chưa có fatigue interpretation.
