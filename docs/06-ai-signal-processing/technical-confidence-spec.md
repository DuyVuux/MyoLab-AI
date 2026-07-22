# Đặc tả Engineering Confidence và Explainability v0.1

## Mục tiêu

Đóng gói kết luận Day 13 cùng chất lượng pipeline, basis, counterevidence và guardrail wording thành `ExplainableInferenceResult v0.1`.

## Thành phần confidence

| Thành phần | Cách tính v0.1 |
|---|---|
| QC quality | pass=1, warning=0,75, fail=0 |
| Usable-window ratio | min(time-domain ratio, frequency-domain ratio) |
| Trend quality | trung bình R² đã clamp về [0,1] |
| Evidence consistency | mapping từ pattern category |

## Safety

- score không phải probability;
- `clinical_calibration_status=not_calibrated`;
- `clinical_use_allowed=false`;
- human review bắt buộc;
- không FRS, diagnosis, treatment hoặc return-to-play decision;
- wording guard phải pass trước downstream.
