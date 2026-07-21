# Ghi chú triển khai Day 8 — Feature Extraction Service

## Luồng

```text
WindowingRunResult
→ kiểm tra upstream/version/profile
→ valid window: RMS/MAV
→ invalid window: not_computed row
→ deterministic result hash
```

## Quy tắc bất biến

- Chỉ profile `time_domain`, purpose `rms_mav`.
- Input phải từ `preprocess_v0.1` và `windowing_v0.1`.
- Không rectify, taper hoặc demean lại trong feature layer.
- Không MVC/baseline normalization.
- Không bỏ invalid row im lặng.
- Không chứa raw samples trong JSON/CSV.
- `RMS >= MAV >= 0` trong tolerance.
- Không tạo fatigue status, FRS, ML prediction hoặc khuyến nghị.

## Trạng thái xác nhận

```text
analytical_verification_status = passed khi checker pass
clinical_validation_status = not_validated
```
