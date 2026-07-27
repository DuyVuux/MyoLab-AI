# Hướng dẫn gán nhãn sEMG v0.2

## 1. Nguồn nhãn

Mỗi nhãn phải lưu:

```text
cue source
event/segment timing
reviewer role
review status
original label
corrected label
adjudication status
```

## 2. Không được suy diễn

- `unknown` không phải `rest`.
- Không có chuyển động quan sát được không mặc định là `not_attempted`.
- Cue label không mặc định là actual performed gesture.
- Self-perceived fatigue không mặc định là physiological ground truth.

## 3. Training eligibility

Chỉ label có:

```text
exact segment reference
+ approved taxonomy
+ acceptable QC
+ legal/consent scope
+ adjudication khi cần
```

mới được xem xét cho model-ready dataset.
