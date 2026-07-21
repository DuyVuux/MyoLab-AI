# Ghi chú xử lý tín hiệu Day 9

## Pipeline spectral

```text
frequency-domain window
→ detrend constant
→ Hann taper
→ Welch one-sided PSD
→ cắt 20–400 Hz
→ power/QA metrics
```

## Điều phải ghi rõ

- Outer overlap khác Welch internal overlap.
- RMS/MAV không dùng Hann.
- Peak frequency chỉ dùng QA.
- PSD pass không phải fatigue evidence.
- Parseval ratio dùng Hann-weighted reference.

## Quan sát từ verification

Ghi lại peak, power, leakage ratio và các numerical tolerance trên máy của mình.
