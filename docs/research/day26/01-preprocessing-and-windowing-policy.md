# Day 26 — Preprocessing, Windowing và Feature-Fitting Policy

## Scope

Tài liệu này là lớp tích hợp từ Feature Engineering Review và Validation Review. Nó không thay thế DSP specs Day 5–12.

## Window candidates

| Window | Mandatory? | Primary use |
|---:|---:|---|
| 150 ms | Yes | Task A latency arm |
| 200 ms | Yes | Task A primary arm |
| 250 ms | Yes | Task A primary arm |
| 500 ms | Yes | Task B/C spectral/context arm |
| 1000 ms | Yes | Task B/C stability stress-test |
| 100–125 ms | Optional | Fast-control literature comparator |
| 300 ms | Optional | A/B bridge comparator |

## Non-negotiable sequence

```text
raw registry
→ duplicate audit
→ grouped split
→ segmentation within partition
→ windows within partition
→ fit scaler/selector only in inner train
```

## Normalization policy

- No normalization: mandatory comparator.
- Training-fold per-channel z-score: optional baseline.
- Robust scaling: optional baseline.
- Rest/MVC normalization: site-confirmed only, not default.
- Per-session/adaptive normalization: later arm; only predeclared causal buffer/past data.
- Global full-dataset statistics: prohibited.

## Feature-selection policy

mRMR, MI, L1, sequential selection hoặc model importance chỉ được fit trong inner fold. Report selection frequency/stability; không gọi một feature “mandatory” chỉ vì xuất hiện trong một run.
